"""Run full native CPU appearance stress suites from a source-bound checkpoint."""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from dataset_protocol import atomic_json, digest

ROOT = Path(__file__).resolve().parents[1]


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def run(scene, output, blender):
    scene = scene.resolve()
    output = output.resolve()
    source_files = [scene]
    for directory in ['tools', 'wrapper', 'apollo_core', 'build']:
        source_files.extend(sorted((ROOT/directory).glob('*.py')))
        source_files.extend(sorted((ROOT/directory).glob('*.json')))
    bindings = {str(path): digest(path) for path in source_files}
    inputs = {'scene_sha256': digest(scene), 'sources': bindings,
              'blender_binary_sha256': digest(Path(blender)),
              'resolution': 1024, 'samples': 32, 'dataset_seed': 0}
    output.mkdir(parents=True, exist_ok=True)
    receipt_path = output/'run.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        if receipt['inputs'] != inputs:
            raise ValueError('Frozen test inputs changed. Choose a new output folder.')
    else:
        if any(output.iterdir()):
            raise ValueError('Output directory has no valid run receipt')
        receipt = {'inputs': inputs, 'started_utc': utc_now(), 'completed_stages': {}}
        atomic_json(receipt_path, receipt)

    def guard():
        for path in source_files:
            if digest(path) != bindings[str(path)]:
                raise ValueError('Frozen source changed during tests: '+str(path))

    def worker(script, *arguments):
        return [blender, '-b', '--factory-startup', scene, '--python-exit-code', '1',
                '-P', ROOT/script, '--', *arguments]

    def stage(name, command, artifacts):
        guard()
        previous = receipt['completed_stages'].get(name)
        if previous:
            for relative, expected in previous['outputs'].items():
                if digest(output/relative) != expected:
                    raise ValueError('Completed stage artifact changed: '+relative)
            print('Reused completed stage', name, flush=True)
            return
        atomic_json(output/'status.json', {'stage': name, 'updated_utc': utc_now()})
        start = time.monotonic()
        with (output/(name+'.log')).open('ab') as log:
            process = subprocess.Popen([str(arg) for arg in command], cwd=ROOT,
                                       stdout=log, stderr=subprocess.STDOUT)
            atomic_json(output/'status.json', {'stage': name, 'pid': process.pid,
                                               'updated_utc': utc_now()})
            result = process.wait()
        if result:
            raise RuntimeError(name+' failed. Inspect '+name+'.log')
        guard()
        files = []
        for artifact in artifacts:
            path = output/artifact
            if path.is_dir():
                files.extend(p for p in path.rglob('*') if p.is_file())
            elif path.is_file():
                files.append(path)
            else:
                raise ValueError('Missing stage artifact: '+artifact)
        receipt['completed_stages'][name] = {
            'elapsed_seconds': time.monotonic()-start, 'completed_utc': utc_now(),
            'outputs': {path.relative_to(output).as_posix(): digest(path) for path in files}}
        atomic_json(receipt_path, receipt)
        print(name, 'passed', flush=True)

    python = sys.executable
    try:
        stage('preflight', worker('tools/scene_preflight.py', '--out', output/'preflight.json'),
              ['preflight.json'])
        stage('visibility113', worker('tools/realism_visibility.py', '--folder', output/'poses113',
                                     '--masks', output/'masks113', '--limit', '113'),
              ['poses113', 'masks113'])
        stage('visibility-images', [python, ROOT/'tools/early_image_gate.py', output/'poses113',
                                   '--baseline', output/'poses113/renders/frame_000004.png', '--progress'],
              ['poses113/early-image-report.json'])
        stage('visibility-masks', [python, ROOT/'tools/analyze_visibility.py', output/'masks113'],
              ['masks113/report.json'])
        stage('dataset256', worker('tools/generate_dataset.py', '--folder', output/'dataset256',
                                  '--count', '256', '--seed', '0', '--samples', '32'), ['dataset256'])
        stage('dataset-analysis', [python, ROOT/'tools/analyze_dataset.py', output/'dataset256'],
              ['dataset256/analysis.json', 'dataset256/coverage.png', 'dataset256/anchors.png'])
        stage('dataset-images', [python, ROOT/'tools/early_image_gate.py', output/'dataset256',
                                '--baseline', output/'dataset256/renders/frame_000004.png', '--progress'],
              ['dataset256/early-image-report.json'])
        guard()
        receipt['completed_utc'] = utc_now()
        atomic_json(receipt_path, receipt)
        atomic_json(output/'status.json', {'stage': 'complete-awaiting-visual-review',
                                          'scene_sha256': inputs['scene_sha256'],
                                          'updated_utc': utc_now()})
    except Exception as error:
        atomic_json(output/'status.json', {'stage': 'failed', 'error': str(error),
                                          'updated_utc': utc_now()})
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--blender', default=os.environ.get('BLENDER_BIN') or shutil.which('blender'))
    arguments = parser.parse_args()
    if not arguments.blender:
        parser.error('Set BLENDER_BIN or provide --blender')
    run(arguments.scene, arguments.out, arguments.blender)
