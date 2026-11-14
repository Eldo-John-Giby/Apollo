"""Package the public GNM technical candidate after verifying its render receipts."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from gnm_template import MODEL_SHA256
from submission_bundle import ROOT, VARIANTS, add_frames, png, read_json, sha256


def package(args):
    files = {}
    modes = add_frames(files, args.motion)
    template = args.template / 'template-receipt.json'
    if read_json(template)['model_sha256'] != MODEL_SHA256:
        raise ValueError('Unexpected GNM model receipt')
    files['model/template-receipt.json'] = template
    files['model/template.npz'] = args.template / 'template.npz'
    files['model/neutral.blend'] = args.template / 'neutral.blend'
    files['licenses/Google-GNM-LICENSE.txt'] = args.license
    textures = {}
    for variant in VARIANTS:
        source = args.textures / variant
        still = source / 'front.png'
        png(still, (1024, 1024))
        files[f'stills/{variant}.png'] = still
        coverage = read_json(source / 'color.1001.json')
        if coverage['projection_coverage'] < .995:
            raise ValueError(f'{variant}: insufficient raw skin coverage')
        files[f'textures/{variant}/coverage.json'] = source / 'color.1001.json'
        entries = {}
        for tile, size in ((1001, 2048), (1002, 1024), (1004, 1024)):
            name = f'color.{tile}.png'
            path = source / name
            png(path, (size, size))
            files[f'textures/{variant}/{name}'] = path
            entries[str(tile)] = {'file': name, 'sha256': sha256(path.read_bytes())}
        textures[variant] = entries
    for mode, mode_receipt in modes.items():
        path = args.motion / mode / 'reopen.json'
        reopened = read_json(path)
        expected = {tile: spec['sha256'] for tile, spec in textures['rose-brown'].items()}
        if (reopened['scene_sha256'] != mode_receipt['settings']['scene_sha256']
                or reopened['frames_checked'] != 192 or reopened['max_position_error_m'] > 1e-6
                or reopened['maps'] != expected):
            raise ValueError(f'{mode}: reopened timeline verification mismatch')
        files[f'timelines/{mode}/reopen.json'] = path
        files[f'timelines/{mode}/geometry.npz'] = args.motion / mode / 'geometry.npz'
    for path in ROOT.joinpath('tools').glob('gnm_*.py'):
        files[f'tools/{path.name}'] = path
    for name in ('docs/GNM_INTEGRATION.md', 'assets/ATTRIBUTION.md',
                 'assets/photorealism-v2/ATTRIBUTION.md',
                 'assets/photorealism-v2/young_lightskinned_female_diffuse3.png',
                 'assets/photorealism-v2/brown_eye.png', 'requirements.txt',
                 'tools/submission_render.py', 'tools/submission_bundle.py',
                 'tools/submission_motion.py', 'tools/submission_textures.py',
                 'tools/submission_bake.py', 'tools/submission_variants.py',
                 'apollo_core/submission_timing.py', 'apollo_core/__init__.py',
                 'wrapper/eyes.py'):
        files[name] = ROOT / name
    manifest = {'target': 'Google GNM Head v3', 'evaluator_match': 'unconfirmed',
                'modes': modes, 'textures': textures, 'sha256': {}}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=args.out.parent) as scratch:
        temporary = Path(scratch) / args.out.name
        with ZipFile(temporary, 'x') as archive:
            for name, path in sorted(files.items()):
                data = path.read_bytes()
                manifest['sha256'][name] = sha256(data)
                archive.writestr(name, data)
            archive.writestr('manifest.json', json.dumps(manifest, indent=2) + '\n')
        with ZipFile(temporary) as archive:
            for name, expected in manifest['sha256'].items():
                if sha256(archive.read(name)) != expected:
                    raise ValueError(f'Archive hash mismatch: {name}')
        if args.out.exists():
            raise FileExistsError(args.out)
        temporary.replace(args.out)
    print(f'Verified {args.out}: {len(files)} payload files')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('motion', 'textures', 'template', 'license', 'out'):
        parser.add_argument(f'--{name}', type=Path, required=True)
    package(parser.parse_args())
