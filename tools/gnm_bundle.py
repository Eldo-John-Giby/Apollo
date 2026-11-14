"""Package the public GNM technical candidate after verifying its render receipts."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from PIL import Image, ImageChops, ImageDraw

from gnm_template import MODEL_SHA256
from submission_bundle import ROOT, VARIANTS, add_frames, png, read_json, sha256
from gnm_run import surface_files
import numpy as np


def verify_hold_receipts(directory):
    """Check every copied frame against the upstream pose sequence and its source."""
    with np.load(directory / 'geometry.npz', allow_pickle=False) as clip:
        sequence = clip['sequence']
    records = read_json(directory / 'frames/render-receipt.json')['frames']
    if len(sequence) != len(records):
        raise ValueError(f'{directory.name}: geometry and render receipt lengths differ')
    for index, pose in enumerate(sequence, 1):
        record = records[f'frame_{index:04d}.png']
        source = record['reused_frame']
        if source is None:
            continue
        if (type(source) is not int or not 1 <= source <= len(sequence) or source == index
                or sequence[source - 1] != pose
                or records[f'frame_{source:04d}.png']['sha256'] != record['sha256']):
            raise ValueError(f'{directory.name}: invalid hold reuse for frame {index}')


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
        side = source / 'side-udim.png'
        png(side, (640, 640))
        files[f'evidence/side-light/{variant}.png'] = side
        legacy = source / 'side-legacy.png'
        if legacy.is_file():
            png(legacy, (640, 640))
            with Image.open(side) as native, Image.open(legacy) as alternate:
                difference = ImageChops.difference(native.convert('RGB'), alternate.convert('RGB'))
                if max(high for _, high in difference.getextrema()) > 1:
                    raise ValueError(f'{variant}: native and legacy fresh-wrap renders differ')
            files[f'evidence/side-light-legacy/{variant}.png'] = legacy
        for name, size in (('angle-neutral', 640), ('front-oblique', 640), ('eyes', 1024)):
            path = source / f'{name}.png'
            if path.exists():
                png(path, (size, size))
                files[f'evidence/{name}/{variant}.png'] = path
        coverage = read_json(source / 'color.1001.json')
        if coverage['projection_coverage'] < .995:
            raise ValueError(f'{variant}: insufficient raw skin coverage')
        files[f'textures/{variant}/coverage.json'] = source / 'color.1001.json'
        detail = source / 'color.1001.detail.json'
        if detail.exists():
            if read_json(detail)['output_sha256'] != sha256((source / 'color.1001.png').read_bytes()):
                raise ValueError(f'{variant}: surface-detail receipt does not match skin map')
            files[f'textures/{variant}/surface-detail.json'] = detail
        entries = {}
        for tile, size in ((1001, None), (1002, 1024), (1004, 1024)):
            name = f'color.{tile}.png'
            path = source / name
            if size is None:
                with Image.open(path) as image:
                    size = image.width
                if size not in (2048, 4096):
                    raise ValueError('Skin map must be native 2K or authored 4K')
            png(path, (size, size))
            files[f'textures/{variant}/{name}'] = path
            entries[str(tile)] = {'file': name, 'sha256': sha256(path.read_bytes())}
        textures[variant] = entries
        for role, path in surface_files(source).items():
            with Image.open(source / 'color.1001.png') as image:
                dimensions = image.size
            png(path, dimensions)
            if read_json(detail)['maps'][path.name] != sha256(path.read_bytes()):
                raise ValueError(f'{variant}: {role} provenance does not match map')
            files[f'textures/{variant}/{path.name}'] = path
        eye_detail = source / 'eye-detail.json'
        if eye_detail.exists():
            eye_receipt = read_json(eye_detail)
            for tile in ('1002', '1004'):
                if eye_receipt['maps'][tile]['sha256'] != entries[tile]['sha256']:
                    raise ValueError(f'{variant}: iris-detail receipt does not match map')
            files[f'textures/{variant}/eye-detail.json'] = eye_detail
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
        verify_hold_receipts(args.motion / mode)
        path = args.motion / mode / 'reopen.json'
        reopened = read_json(path)
        expected = {tile: spec['sha256'] for tile, spec in textures['rose-brown'].items()}
        expected_surface = {role: sha256(path.read_bytes())
                            for role, path in surface_files(reference).items()}
        if (reopened['scene_sha256'] != mode_receipt['settings']['scene_sha256']
                or reopened['frames_checked'] != 192 or reopened['max_position_error_m'] > 1e-6
                or reopened['maps'] != expected or not reopened.get('camera_checks')
                or reopened.get('resource_checks', {}).get('linked_libraries') != 0
                or reopened.get('resource_checks', {}).get('unpacked_file_images') != 0
                or reopened.get('resource_checks', {}).get('blender_online_access') is not False
                or reopened.get('surface_maps', {}) != expected_surface):
            raise ValueError(f'{mode}: reopened timeline verification mismatch')
        files[f'timelines/{mode}/reopen.json'] = path
        files[f'timelines/{mode}/geometry.npz'] = args.motion / mode / 'geometry.npz'
    for path in ROOT.joinpath('tools').glob('gnm_*.py'):
        files[f'tools/{path.name}'] = path
    for path in ROOT.joinpath('assets/gnm-scan').glob('*'):
        if path.is_file():
            files[f'assets/gnm-scan/{path.name}'] = path
    transfer = args.textures / 'scan-transfer.json'
    if transfer.exists():
        receipt = read_json(transfer)
        scan_source = ROOT / 'assets/gnm-scan'
        if (receipt['source'] != read_json(scan_source / 'source.json')
                or receipt['template_sha256'] != sha256((args.template / 'template.npz').read_bytes())):
            raise ValueError('Scan transfer provenance does not match the build inputs')
        for name, spec in receipt['source']['files'].items():
            if sha256((scan_source / name).read_bytes()) != spec['sha256']:
                raise ValueError(f'Scan source checksum mismatch: {name}')
        for variant in VARIANTS:
            detail_receipt = read_json(args.textures / variant / 'color.1001.detail.json')
            if detail_receipt['source_sha256'] != receipt['output_sha256']:
                raise ValueError(f'{variant}: skin map was built from a different scan transfer')
        files['evidence/scan-transfer.json'] = transfer
    comparison = args.comparison or args.textures / 'rose-brown-matched.png'
    if args.comparison or comparison.is_file():
        png(comparison, (1280, 1340))
        files['evidence/rose-brown-matched.png'] = comparison
    for name in ('docs/GNM_INTEGRATION.md', 'docs/GNM_QUICKSTART.md', 'docs/SCORE_IMPROVEMENT.md',
                 'requirements-gnm-build.txt', 'assets/ATTRIBUTION.md',
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
        side_sheet = Image.new('RGB', (300 * len(VARIANTS), 330), '#1a1c20')
        side_labels = ImageDraw.Draw(side_sheet)
        for index, variant in enumerate(VARIANTS):
            with Image.open(files[f'evidence/side-light/{variant}.png']) as still:
                side_sheet.paste(still.convert('RGB').resize((300, 300), Image.Resampling.LANCZOS),
                                 (index * 300, 0))
            side_labels.text((index * 300 + 10, 308), variant, fill='white')
        side_sheet_path = Path(scratch) / 'side-light-contact-sheet.png'
        side_sheet.save(side_sheet_path)
        files['evidence/side-light/contact-sheet.png'] = side_sheet_path
        for variant in VARIANTS:
            with Image.open(files[f'stills/{variant}.png']) as still:
                width, height = still.size
                region = tuple(round(fraction * extent) for fraction, extent in
                               zip((.30, .30, .70, .43), (width, height, width, height)))
                crop = Path(scratch) / f'{variant}-eye-detail.png'
                still.crop(region).save(crop)
            files[f'evidence/eye-details/{variant}.png'] = crop
            with Image.open(files[f'stills/{variant}.png']) as still:
                crop = Path(scratch) / f'{variant}-skin-detail.png'
                still.crop((575, 430, 665, 545)).save(crop)
            files[f'evidence/skin-details/{variant}.png'] = crop
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
    parser.add_argument('--comparison', type=Path, help='Matched baseline and candidate stills')
    package(parser.parse_args())
