"""Check release payloads and provenance against staged or committed Git bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def check(release, delivery, revision='HEAD'):
    release = Path(release).resolve()
    delivery = Path(delivery).resolve()
    for folder in (release, delivery):
        assert folder.is_relative_to(ROOT), 'Release must be in the repository'
    expected = {}

    def expect(path, sha):
        path = path.resolve()
        assert path.is_relative_to(ROOT), 'Evidence path escapes the repository'
        name = path.relative_to(ROOT).as_posix()
        assert path.is_file() and digest(path) == sha, name
        assert path.stat().st_size < 100 * 1024 * 1024, name
        if name in expected:
            assert expected[name] == sha, 'Conflicting provenance: ' + name
        expected[name] = sha

    manifest = release / 'MANIFEST.json'
    expect(manifest, digest(manifest))
    for name, sha in load(manifest).items():
        path = (release / name).resolve()
        assert path.is_relative_to(release), 'Invalid manifest path'
        expect(path, sha)
    for path in release.rglob('*.zip'):
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None, path

    report = load(delivery / 'verification_report.json')
    assert report['passed'] and report['production']
    for name, sha in report['artifact_hashes'].items():
        expect(delivery / name, sha)
    for path in delivery.rglob('*'):
        if path.is_file():
            expect(path, digest(path))
    for name, sha in report['verifier_sha256'].items():
        expect(ROOT / name, sha)
    expect(ROOT / 'wrapper/eyes.py', report['artifact_hashes']['wrapper/eyes.py'])
    run = load(release / 'dataset-256/dataset.json')['run']
    for field, name in {
        'generator_sha256': 'tools/generate_dataset.py',
        'protocol_sha256': 'tools/dataset_protocol.py',
        'reference_sha256': 'tools/reference_geometry.py',
    }.items():
        expect(ROOT / name, run[field])
    for name, sha in load(release / 'dataset-analysis.json')['analysis_sources'].items():
        expect(ROOT / 'tools' / name, sha)
    rebuild = load(release / 'look-rebuild-report.json')
    recipe = 'realism_scene.py' if 'config_sha256' in rebuild else 'upgrade_looks.py'
    expect(ROOT / 'build' / recipe, rebuild['recipe_source_sha256'])
    if 'config_sha256' in rebuild:
        expect(ROOT / 'build/realism_config.json', rebuild['config_sha256'])

    git = ['git', '-c', 'safe.directory=' + ROOT.as_posix()]
    process = subprocess.Popen(git + ['cat-file', '--batch'], cwd=ROOT,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for name, sha in expected.items():
            query = ':' + name if revision == ':' else revision + ':' + name
            process.stdin.write((query + '\n').encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            assert len(header) == 3 and header[1] == b'blob', (name, header)
            remaining = int(header[2])
            actual = hashlib.sha256()
            while remaining:
                data = process.stdout.read(min(remaining, 1024 * 1024))
                assert data, name
                actual.update(data)
                remaining -= len(data)
            assert process.stdout.read(1) == b'\n'
            assert actual.hexdigest() == sha, 'Git bytes differ: ' + name
    finally:
        process.stdin.close()
        if process.poll() is None:
            process.terminate()
        process.wait()
    print(f'{revision}: verified {len(expected)} payload/source Git blobs and ZIP integrity')
    return len(expected)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release', type=Path)
    parser.add_argument('--delivery', type=Path, required=True)
    parser.add_argument('--revision', default='HEAD', help="Use ':' for the staged index")
    args = parser.parse_args()
    check(args.release, args.delivery, args.revision)
