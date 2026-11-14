"""Create authenticated rc.4/candidate still comparisons and native detail crops."""
import argparse
import hashlib
import json
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw

from gnm_run import VARIANTS, surface_files

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def compare(baseline, baseline_receipt, candidate, out):
    expected_archive = json.loads(baseline_receipt.read_text())['archive_sha256']
    if digest(baseline) != expected_archive:
        raise ValueError('Baseline archive differs from its published qualification receipt')
    out.mkdir(parents=True, exist_ok=False)
    report = {'baseline_archive_sha256': expected_archive, 'variants': {}, 'outputs': {}}
    with ZipFile(baseline) as package:
        manifest = json.loads(package.read('manifest.json'))
        for variant in VARIANTS:
            directory = candidate / variant
            maps = {str(tile): directory / f'color.{tile}.png' for tile in (1001, 1002, 1004)}
            maps.update(surface_files(directory))
            map_hashes = {role: digest(path) for role, path in maps.items()}
            board = Image.new('RGB', (1280, 1340), '#191b20')
            labels = ImageDraw.Draw(board)
            images = {}
            sources = {}
            for row, (view, entry) in enumerate((
                    ('front', f'stills/{variant}.png'),
                    ('side-udim', f'evidence/side-light/{variant}.png'))):
                old_data = package.read(entry)
                old_hash = hashlib.sha256(old_data).hexdigest()
                if old_hash != manifest['sha256'][entry]:
                    raise ValueError(f'Baseline image hash mismatch: {entry}')
                path = directory / f'{view}.png'
                rendered = json.loads(path.with_suffix('.render.json').read_text())
                if (rendered['output_sha256'] != digest(path) or rendered['maps'] != map_hashes
                        or rendered['scene_sha256'] != manifest['sha256']['model/neutral.blend']):
                    raise ValueError(f'Stale candidate comparison image: {path}')
                old = Image.open(BytesIO(old_data)).convert('RGB')
                with Image.open(path) as image:
                    new = image.convert('RGB')
                if old.size != new.size:
                    raise ValueError(f'Comparison dimensions differ: {variant}/{view}')
                sources[view] = {'baseline_sha256': old_hash,
                                 'candidate_sha256': rendered['output_sha256'],
                                 'candidate_render': rendered}
                for column, (image, label) in enumerate(((old, 'Apollo rc.4'),
                                                        (new, 'Detailed scan candidate'))):
                    x, y = column * 640, row * 670
                    board.paste(image.resize((640, 640), Image.Resampling.LANCZOS), (x, y + 28))
                    labels.text((x + 10, y + 8), f'{variant} / {label}', fill='white')
                if view == 'front':
                    images = {'baseline': old, 'candidate': new}
            board.save(out / f'{variant}-matched.png')
            for name, bounds in (('eyes', (300, 320, 720, 425)),
                                 ('skin', (575, 430, 665, 545))):
                width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
                detail = Image.new('RGB', (width * 2, height + 28), '#191b20')
                detail_labels = ImageDraw.Draw(detail)
                for column, (key, label) in enumerate((('baseline', 'rc.4'),
                                                       ('candidate', 'Candidate'))):
                    detail.paste(images[key].crop(bounds), (column * width, 28))
                    detail_labels.text((column * width + 7, 8), label, fill='white')
                detail.save(out / f'{variant}-{name}.png')
            report['variants'][variant] = sources
    for path in sorted(out.glob('*.png')):
        report['outputs'][path.name] = digest(path)
    (out / 'comparison.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--baseline-receipt', type=Path,
                        default=ROOT / 'milestones/gnm-final-candidate/receipt.json')
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    compare(args.baseline, args.baseline_receipt, args.candidate, args.out)
