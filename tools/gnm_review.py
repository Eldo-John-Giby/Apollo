"""Prepare anonymous direction comparisons from authenticated GNM frame receipts."""
import argparse
import hashlib
import json
from pathlib import Path
import random
from zipfile import ZipFile

from PIL import Image, ImageDraw


def prepare(motion, out, textures=None):
    out.mkdir(parents=True, exist_ok=False)
    reviewer = out / 'reviewer'
    reviewer.mkdir()
    modes = ['left', 'right']
    random.Random(20261114).shuffle(modes)
    key = {}
    responses = {'reviewer': '', 'directions': {},
                 'motion': {'smooth': None, 'blink_plausible': None, 'notes': ''}}
    if textures:
        variants = ['rose-brown', 'golden-hazel', 'olive-amber', 'neutral-deep', 'cool-grey']
        random.Random(20261115).shuffle(variants)
        responses['appearance'] = {}
        for index, variant in enumerate(variants, 1):
            case = f'A{index:02d}'
            board = Image.new('RGB', (1280, 1336), '#1a1c20')
            labels = ImageDraw.Draw(board)
            hashes = {}
            for cell, name in enumerate(('front', 'side-udim', 'front-oblique', 'eyes')):
                source = textures / variant / f'{name}.png'
                digest = hashlib.sha256(source.read_bytes()).hexdigest()
                receipt = json.loads(source.with_suffix('.render.json').read_text())
                if receipt['output_sha256'] != digest:
                    raise ValueError(f'Stale appearance review still: {source}')
                hashes[name] = digest
                x, y = (cell % 2) * 640, (cell // 2) * 668
                with Image.open(source) as image:
                    board.paste(image.convert('RGB').resize((640, 640), Image.Resampling.LANCZOS),
                                (x, y + 28))
                labels.text((x + 10, y + 7), f'{case} / {name}', fill='white')
            board.save(reviewer / f'{case}.png')
            key[case] = {'variant': variant, 'images': hashes}
            responses['appearance'][case] = {
                'skin_natural_1_to_5': None, 'iris_detail_1_to_5': None,
                'seams_visible': None, 'notes': ''}
    for index, mode in enumerate(modes, 1):
        case = f'C{index:02d}'
        source = motion / mode / 'frames'
        receipt = json.loads((source / 'render-receipt.json').read_text(encoding='utf-8'))
        board = Image.new('RGB', (2048, 1072), '#1a1c20')
        labels = ImageDraw.Draw(board)
        hashes = {}
        for column, frame in enumerate((1, 26)):
            name = f'frame_{frame:04d}.png'
            path = source / name
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != receipt['frames'][name]['sha256']:
                raise ValueError(f'Frame receipt mismatch: {path}')
            hashes[name] = digest
            with Image.open(path) as image:
                if image.size != (1024, 1024):
                    raise ValueError('Expected the actual 1024-pixel judging framing')
                board.paste(image.convert('RGB'), (column * 1024, 48))
            labels.text((column * 1024 + 16, 16),
                        f'{case}: ' + ('Neutral reference' if column == 0 else 'Judgment frame'),
                        fill='white')
        board.save(reviewer / f'{case}.png')
        key[case] = {'expected': mode, 'scene_sha256': receipt['run']['scene_sha256'],
                     'frames': hashes}
        responses['directions'][case] = {'direction': None, 'confidence_1_to_5': None, 'notes': ''}
    (reviewer / 'responses.json').write_text(json.dumps(responses, indent=2) + '\n', encoding='utf-8')
    (reviewer / 'REVIEW_INSTRUCTIONS.md').write_text(
        '# Blind teammate review\n\n'
        'Use a teammate who did not tune the scene. View C01.png and C02.png at '
        '100% zoom. The left panel is neutral; judge the right panel in screen '
        'space as left, right or unclear. Record confidence from 1 to 5 and any '
        'visible defects in responses.json. Do not consult the assessor key.\n\n'
        'For motion quality, open timelines/generate-motion/expression.blend '
        'from the full technical ZIP in Blender 4.5.15 LTS. Use Render > View '
        'Animation to play the existing PNG frames at the saved 24 fps. This '
        'plays the delivered sequence without encoding a video. Review '
        'smoothness, readable fixations, lid contact and blink believability. '
        'Record smooth and blink_plausible as true or false, with notes. '
        'Inspect blink frames 103-113 individually if needed.\n\n'
        'If A01-A05 are included, inspect all four views in each image. Rate '
        'skin naturalness and iris detail from 1 to 5, note visible seams and '
        'record distracting pigment, pore or reflection patterns. These are '
        'anonymous texture variants.\n\n'
        'Return the text responses. Note any visible eye slit, sharp fold, '
        'uneven contact or distracting highlight during closure.\n',
        encoding='utf-8')
    (out / 'assessor-key.json').write_text(json.dumps(key, indent=2) + '\n', encoding='utf-8')
    archive = out / 'apollo-gnm-blind-review.zip'
    with ZipFile(archive, 'x') as package:
        for path in sorted(reviewer.iterdir()):
            package.write(path, path.name)
    print(f'Prepared {archive}; keep assessor-key.json separate from reviewers')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--motion', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--textures', type=Path)
    args = parser.parse_args()
    prepare(args.motion, args.out, args.textures)
