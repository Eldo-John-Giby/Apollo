"""Package the public GNM technical candidate after verifying its render receipts."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from PIL import Image, ImageChops, ImageDraw

from gnm_template import MODEL_SHA256
from submission_bundle import ROOT, VARIANTS, add_frames, png, read_json, sha256


def package(args):
    files = {}
    modes = add_frames(files, args.motion)
    resume_audit = args.motion / 'resume-audit.json'
    if read_json(resume_audit) != {
        'mode': 'left',
        'scene_sha256': modes['left']['settings']['scene_sha256'],
        'valid_frame_preserved': 1,
        'corrupt_frame_repaired': 2,
        'missing_frame_repaired': 3,
    }:
        raise ValueError('Resume test does not match the packaged Left timeline')
    files['evidence/resume-audit.json'] = resume_audit
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
    for tile in ('1001', '1002', '1004'):
        if len({variant[tile]['sha256'] for variant in textures.values()}) != len(VARIANTS):
            raise ValueError(f'Duplicate texture variants for GNM tile {tile}')
    if len({sha256(files[f'stills/{variant}.png'].read_bytes())
            for variant in VARIANTS}) != len(VARIANTS):
        raise ValueError('Duplicate GNM judging stills')
    reference = args.textures / 'rose-brown'
    side_udim = reference / 'side-udim.png'
    side_legacy = reference / 'side-legacy.png'
    with Image.open(side_udim) as udim, Image.open(side_legacy) as legacy:
        if udim.size != legacy.size:
            raise ValueError('UV comparison renders have different dimensions')
        differences = ImageChops.difference(udim.convert('RGB'), legacy.convert('RGB'))
        layout_error = max(high for _, high in differences.getextrema())
        if layout_error > 1:
            raise ValueError(f'UV layouts differ by {layout_error} RGB levels')
    files['evidence/rose-brown-side-udim.png'] = side_udim
    files['evidence/rose-brown-side-legacy.png'] = side_legacy
    for mode, mode_receipt in modes.items():
        path = args.motion / mode / 'reopen.json'
        reopened = read_json(path)
        expected = {tile: spec['sha256'] for tile, spec in textures['rose-brown'].items()}
        if (reopened['scene_sha256'] != mode_receipt['settings']['scene_sha256']
                or reopened['frames_checked'] != 192 or reopened['max_position_error_m'] > 1e-6
                or reopened['maps'] != expected or not reopened.get('camera_checks')):
            raise ValueError(f'{mode}: reopened timeline verification mismatch')
        files[f'timelines/{mode}/reopen.json'] = path
        files[f'timelines/{mode}/geometry.npz'] = args.motion / mode / 'geometry.npz'
    for path in ROOT.joinpath('tools').glob('gnm_*.py'):
        files[f'tools/{path.name}'] = path
    for name in ('docs/GNM_INTEGRATION.md', 'assets/ATTRIBUTION.md',
                 'milestones/eye-expression-2026-11-11/scene.blend',
                 'milestones/eye-expression-2026-11-11/ATTRIBUTION.md',
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
                'modes': modes, 'textures': textures,
                'side_layout_max_rgb_error': layout_error, 'sha256': {}}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=args.out.parent) as scratch:
        temporary = Path(scratch) / args.out.name
        sheet = Image.new('RGB', (300 * len(VARIANTS), 330), '#1a1c20')
        labels = ImageDraw.Draw(sheet)
        for index, variant in enumerate(VARIANTS):
            with Image.open(files[f'stills/{variant}.png']) as still:
                sheet.paste(still.convert('RGB').resize((300, 300), Image.Resampling.LANCZOS),
                            (index * 300, 0))
            labels.text((index * 300 + 10, 308), variant, fill='white')
        sheet_path = Path(scratch) / 'contact-sheet.png'
        sheet.save(sheet_path)
        files['stills/contact-sheet.png'] = sheet_path
        for variant in VARIANTS:
            with Image.open(files[f'stills/{variant}.png']) as still:
                width, height = still.size
                region = tuple(round(fraction * extent) for fraction, extent in
                               zip((.30, .30, .70, .43), (width, height, width, height)))
                crop = Path(scratch) / f'{variant}-eye-detail.png'
                still.crop(region).save(crop)
            files[f'evidence/eye-details/{variant}.png'] = crop
        blink = Image.new('RGB', (1500, 330), '#1a1c20')
        blink_labels = ImageDraw.Draw(blink)
        for index, (frame, label) in enumerate(((93, 'Before'), (105, 'Closing'),
                                                  (106, 'Closed'), (110, 'Reopening'),
                                                  (113, 'Open'))):
            name = f'timelines/generate-motion/frames/frame_{frame:04d}.png'
            with Image.open(files[name]) as still:
                blink.paste(still.convert('RGB').resize((300, 300), Image.Resampling.LANCZOS),
                            (index * 300, 0))
            blink_labels.text((index * 300 + 10, 308), f'{label} / frame {frame}', fill='white')
        blink_path = Path(scratch) / 'blink.png'
        blink.save(blink_path)
        files['evidence/blink.png'] = blink_path
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
