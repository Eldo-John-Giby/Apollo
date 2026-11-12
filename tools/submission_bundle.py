"""Build and verify the CPU MakeHuman fallback bundle from completed artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MODES = ('left', 'right', 'generate-motion')
VARIANTS = ('rose-brown', 'golden-hazel', 'olive-amber', 'neutral-deep', 'cool-grey')
ROLES = {'face', 'iris_left', 'iris_right'}
SOURCE = 'milestones/eye-expression-2026-11-11'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def png(path, dimensions):
    with Image.open(path) as image:
        if image.format != 'PNG' or image.size != dimensions:
            raise ValueError(f'Expected PNG at {dimensions}: {path}')
        image.verify()


def add_frames(files, motion):
    modes = {}
    expected = {f'frame_{i:04d}.png' for i in range(1, 193)}
    for mode in MODES:
        directory = motion / mode
        timeline = directory / 'expression.blend'
        receipt = directory / 'frames' / 'render-receipt.json'
        state = read_json(receipt)
        run = state['run']
        if (run['scene_sha256'] != sha256(timeline.read_bytes()) or run['mode'] != mode
                or run['resolution'] != [1024, 1024] or run['samples'] != 32
                or run['fps'] != 24 or run['range'] != [1, 192]):
            raise ValueError(f'{mode} does not match the full-quality timeline')
        if set(state['frames']) != expected:
            raise ValueError(f'{mode} does not have exactly 192 frame receipts')
        modes[mode] = {'frame_count': len(expected), 'settings': run}
        files[f'timelines/{mode}/expression.blend'] = timeline
        files[f'timelines/{mode}/frames/{receipt.name}'] = receipt
        for name in sorted(expected):
            path = receipt.parent / name
            png(path, (1024, 1024))
            if sha256(path.read_bytes()) != state['frames'][name]['sha256']:
                raise ValueError(f'Frame receipt mismatch: {path}')
            files[f'timelines/{mode}/frames/{name}'] = path
    return modes


def add_textures(files, textures):
    for variant in VARIANTS:
        manifest = textures / 'variants' / variant / 'variant.json'
        spec = read_json(manifest)
        entries = spec['maps']
        if spec['variant'] != variant or len(entries) != 3 or {m['role'] for m in entries} != ROLES:
            raise ValueError(f'Invalid variant manifest: {manifest}')
        files[f'variants/{variant}/variant.json'] = manifest
        for entry in entries:
            name = entry['file']
            if Path(name).name != name:
                raise ValueError(f'Expected a simple texture filename: {name}')
            path = manifest.parent / name
            size = (2048, 2048) if entry['role'] == 'face' else (1024, 1024)
            png(path, size)
            if sha256(path.read_bytes()) != entry['sha256']:
                raise ValueError(f'Texture receipt mismatch: {path}')
            files[f'variants/{variant}/{name}'] = path
        for light in ('neutral', 'oblique'):
            path = textures / light / f'{variant}.png'
            png(path, (1024, 1024))
            files[f'stills/{light}/{variant}.png'] = path
    for light in ('neutral', 'oblique'):
        files[f'stills/{light}/contact-sheet.png'] = textures / light / 'contact-sheet.png'


def package(motion, textures, seams, output):
    files = {}
    modes = add_frames(files, motion)
    add_textures(files, textures)
    for name in ('report.json', 'rebound.png', 'variant.json', 'face.png',
                 'iris_left.png', 'iris_right.png', 'rebound.blend'):
        files[f'seam-rehearsal/{name}'] = seams / name
    files['motion-report.json'] = motion / 'motion-report.json'
    for name in (
        f'{SOURCE}/scene.blend', f'{SOURCE}/ATTRIBUTION.md',
        'assets/ATTRIBUTION.md', 'assets/photorealism-v2/ATTRIBUTION.md',
        'assets/photorealism-v2/young_lightskinned_female_diffuse3.png',
        'assets/photorealism-v2/brown_eye.png', 'requirements.txt',
        'docs/SUBMISSION_PIPELINE.md', 'wrapper/eyes.py',
        'tools/submission_motion.py', 'tools/submission_motion_check.py',
        'tools/submission_render.py', 'tools/submission_variants.py',
        'tools/submission_textures.py', 'tools/submission_uv_rehearsal.py',
        'tools/submission_bake.py', 'tools/submission_seams.py',
        'tools/submission_bundle.py',
    ):
        files[name] = ROOT / name
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix('.partial')
    manifest = {'target': 'Apollo MPFB fallback', 'modes': modes, 'sha256': {}}
    try:
        with ZipFile(temp, 'x', compression=ZIP_STORED) as archive:
            for name, path in sorted(files.items()):
                data = path.read_bytes()
                manifest['sha256'][name] = sha256(data)
                archive.writestr(name, data)
            archive.writestr('manifest.json', json.dumps(manifest, indent=2) + '\n')
        with ZipFile(temp) as archive:
            for name, expected in manifest['sha256'].items():
                if sha256(archive.read(name)) != expected:
                    raise ValueError(f'Archive verification failed: {name}')
        temp.replace(output)
    finally:
        temp.unlink(missing_ok=True)
    print(f'Verified {output} with 576 full-quality frames, 15 texture maps and ten stills')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--motion', type=Path, required=True)
    parser.add_argument('--textures', type=Path, required=True)
    parser.add_argument('--seams', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    package(args.motion, args.textures, args.seams, args.out)


if __name__ == '__main__':
    main()
