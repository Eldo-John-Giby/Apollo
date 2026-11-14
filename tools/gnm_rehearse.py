"""Rehearse a verified GNM archive from a clean extraction."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

import numpy as np
from PIL import Image


def pixels(path):
    with Image.open(path) as image:
        return np.asarray(image.convert('RGB'), dtype=np.int16)


def rehearse(archive, blender, out):
    out.mkdir(parents=True, exist_ok=False)
    out = out.resolve()
    with ZipFile(archive) as bundle:
        manifest = json.loads(bundle.read('manifest.json'))
        expected = manifest['sha256']
        entries = bundle.namelist()
        if len(entries) != len(expected) + 1 or set(entries) != set(expected) | {'manifest.json'}:
            raise ValueError('Archive contents do not match its manifest')
        for name, digest in expected.items():
            path = (out / name).resolve()
            if not path.is_relative_to(out):
                raise ValueError(f'Unsafe archive path: {name}')
            data = bundle.read(name)
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError(f'Hash mismatch: {name}')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    def run(scene, tool, *options):
        subprocess.run([str(blender), '-b', '--factory-startup', scene,
                        '--python-exit-code', '1', '-P', f'tools/{tool}', '--',
                        *options], cwd=out, check=True)

    subprocess.run([sys.executable, 'tools/gnm_run.py', 'still', '--blender', str(blender),
                    '--out', 'reproduction/still.png'], cwd=out, check=True)
    pairs = [('stills/rose-brown.png', 'reproduction/still.png')]
    for layout in ('udim', 'legacy'):
        reproduced = f'reproduction/side-{layout}.png'
        run('model/neutral.blend', 'gnm_texture_trial.py', '--maps', 'textures/rose-brown',
            '--layout', layout, '--out', reproduced, '--angle', '--side-light')
        pairs.append((f'evidence/rose-brown-side-{layout}.png', reproduced))
    for mode in ('left', 'right', 'generate-motion'):
        root = f'timelines/{mode}'
        run(f'{root}/expression.blend', 'gnm_verify.py', '--maps', 'textures/rose-brown',
            '--template', 'model/template.npz', '--clip', f'{root}/geometry.npz',
            '--out', f'reproduction/{mode}.json')
    run('timelines/left/expression.blend', 'submission_render.py',
        '--out', 'reproduction/left', '--first', '21', '--last', '22')
    for frame in (21, 22):
        name = f'frame_{frame:04d}.png'
        pairs.append((f'timelines/left/frames/{name}', f'reproduction/left/{name}'))
    report = {}
    for reference, reproduced in pairs:
        difference = int(np.max(np.abs(pixels(out / reference) - pixels(out / reproduced))))
        report[reference] = {'max_rgb_error': difference}
        if difference > 1:
            raise ValueError(f'{reference} reproduction differs by {difference} RGB levels')
    (out / 'reproduction/report.json').write_text(json.dumps(report, indent=2) + '\n',
                                                  encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('archive', 'blender', 'out'):
        parser.add_argument(f'--{name}', type=Path, required=True)
    args = parser.parse_args()
    rehearse(args.archive, args.blender.resolve(), args.out)
