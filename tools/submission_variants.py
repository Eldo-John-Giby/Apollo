"""Generate MPFB development variants and assemble a matched render contact sheet."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/photorealism-v2'
FACE = 'young_lightskinned_female_diffuse3.png'
EYE = 'brown_eye.png'
BINDINGS = (
    ('face', 'Apollo_Face', 'UVMap',
     '1348145f0a5e621a7a066852c0c4307de91ad8615949d5f510469f3f643b2ec8'),
    ('iris_left', 'Iris.L', 'Iris polar coordinates',
     '3672d47296e696514323c58d4ab8e3ca5d989d57973b110521c177a25da3415d'),
    ('iris_right', 'Iris.R', 'Iris polar coordinates',
     '5c67f3307fc5a50a86e64f5c916569741f9c4e4ae47c711b9f819579d5d2988b'),
)
PALETTES = {
    'rose-brown': ((1.03, .98, .98), (1.02, 1., .93)),
    'golden-hazel': ((1.02, .95, .86), (1.16, 1.25, .90)),
    'olive-amber': ((.86, .82, .73), (1.38, 1.18, .81)),
    'neutral-deep': ((.66, .61, .60), (.86, .82, .79)),
    'cool-grey': ((.96, .94, .97), (.91, 1.19, 1.59)),
}


def color_variant(source, gain):
    curves = [[min(255, round(value * scale)) for value in range(256)] for scale in gain]
    return source.convert('RGB').point(sum(curves, []))


def generate(out):
    with Image.open(ASSETS / FACE) as face, Image.open(ASSETS / EYE) as iris:
        for name, (skin, eye) in PALETTES.items():
            directory = out / name
            directory.mkdir(parents=True, exist_ok=False)
            maps = []
            for index, (role, obj, uv, fingerprint) in enumerate(BINDINGS):
                source_name = FACE if index == 0 else EYE
                if index == 0:
                    image = color_variant(face, skin)
                else:
                    gain = eye if index == 1 else (eye[0] * .985, eye[1], eye[2] * 1.025)
                    image = color_variant(iris, gain)
                file = directory / f'{role}.png'
                image.save(file)
                maps.append({
                    'role': role, 'object': obj, 'uv': uv, 'slot': 0,
                    'replace_image': source_name, 'replace_on_all_slots': index == 0,
                    'mesh_uv_sha256': fingerprint, 'file': file.name,
                    'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                })
            manifest = {
                'variant': name, 'target': 'Apollo MPFB development rig',
                'provenance': {
                    'license': 'CC0', 'attribution': 'assets/photorealism-v2/ATTRIBUTION.md',
                    'sources': {name: hashlib.sha256((ASSETS / name).read_bytes()).hexdigest()
                                for name in (FACE, EYE)},
                    'method': 'Color variants of the existing skin and stock eye atlas.',
                },
                'maps': maps,
            }
            (directory / 'variant.json').write_text(json.dumps(manifest, indent=2) + '\n',
                                                    encoding='utf-8')


def contact_sheet(root, out):
    width = 300
    sheet = Image.new('RGB', (width * len(PALETTES), width + 34), '#17191f')
    labels = ImageDraw.Draw(sheet)
    crops = out.parent / 'eye-crops'
    crops.mkdir(parents=True, exist_ok=True)
    for index, variant in enumerate(PALETTES):
        with Image.open(root / f'{variant}.png') as image:
            w, h = image.size
            image.crop((round(.13 * w), round(.35 * h), round(.87 * w),
                        round(.58 * h))).save(crops / f'{variant}.png')
            tile = image.convert('RGB')
            tile.thumbnail((width, width), Image.Resampling.LANCZOS)
            sheet.paste(tile, (index * width + (width - tile.width) // 2, 0))
        labels.text((index * width + 10, width + 8), variant, fill='white')
    sheet.save(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('generate', 'sheet'))
    parser.add_argument('directory', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.action == 'generate':
        generate(args.directory)
    elif args.out:
        contact_sheet(args.directory, args.out)
    else:
        parser.error('sheet requires --out')


if __name__ == '__main__':
    main()
