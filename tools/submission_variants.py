"""Generate MPFB development variants and assemble a matched render contact sheet."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
import numpy as np

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


# Local MPFB face landmarks in UV coordinates. Values control cheek warmth,
# nose warmth and temple tone independently of the atlas-wide palette.
SKIN_REGIONS = {
    'rose-brown': (.065, .030, -.012),
    'golden-hazel': (.021, .012, .026),
    'olive-amber': (.014, .034, -.031),
    'neutral-deep': (.033, .019, .015),
    'cool-grey': (.046, .025, -.022),
}
IRIS_DETAILS = {
    'rose-brown': ((14, -19), (.18, .06, -.05), .070),
    'golden-hazel': ((31, -12), (.34, .25, -.12), .065),
    'olive-amber': ((-22, 38), (.25, .31, -.12), .084),
    'neutral-deep': ((43, -35), (.08, .02, -.09), .076),
    'cool-grey': ((-48, 24), (-.12, .14, .38), .088),
}


def complexion(image, variant):
    u = np.linspace(0, 1, image.width, dtype=np.float32)[None, :]
    v = np.linspace(1, 0, image.height, dtype=np.float32)[:, None]

    def region(x, y, width, height):
        return np.exp(-((u - x) / width) ** 2 - ((v - y) / height) ** 2)

    cheek, nose, temple = SKIN_REGIONS[variant]
    warmth = cheek * (region(.863, .518, .018, .024)
                      + .91 * region(.863, .449, .018, .024))
    warmth += nose * region(.861, .483, .021, .014)
    shading = temple * (region(.818, .534, .022, .017)
                        + region(.818, .432, .022, .017))
    detail = image.filter(ImageFilter.UnsharpMask(radius=1.5, percent=28, threshold=3))
    color = np.asarray(detail, dtype=np.float32)
    color *= 1 + warmth[..., None] * np.array((1, -.42, -.22), dtype=np.float32)
    color *= 1 + shading[..., None]
    return Image.fromarray(np.clip(np.rint(color), 0, 255).astype(np.uint8))


def color_variant(source, gain):
    curves = [[min(255, round(value * scale)) for value in range(256)] for scale in gain]
    return source.convert('RGB').point(sum(curves, []))


def reference_iris(image, variant, side):
    # The local shader samples the upper-right iris of this stock atlas.
    # Rotate its fibers within a feathered annulus, leaving pupil and limbus fixed.
    center = (.708 * image.width, .292 * image.height)
    y, x = np.ogrid[:image.height, :image.width]
    radius = np.hypot(x - center[0], y - center[1]) / image.width
    annulus = np.clip((radius - .041) / .018, 0, 1)
    annulus *= np.clip((.113 - radius) / .018, 0, 1)
    angles, tint, ring_radius = IRIS_DETAILS[variant]
    fibers = image.rotate(angles[side - 1], Image.Resampling.BICUBIC, center=center)
    fibers = fibers.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=2))
    ring = np.exp(-((radius - ring_radius) / .015) ** 2)
    color = np.asarray(fibers, dtype=np.float32)
    color *= 1 + ring[..., None] * np.array(tint, dtype=np.float32)
    fibers = Image.fromarray(np.clip(np.rint(color), 0, 255).astype(np.uint8))
    return Image.composite(fibers, image, Image.fromarray((annulus * 255).astype(np.uint8)))


def generate(out, polished_reference=False):
    with Image.open(ASSETS / FACE) as face, Image.open(ASSETS / EYE) as iris:
        palettes = {'rose-brown': PALETTES['rose-brown']} if polished_reference else PALETTES
        for name, (skin, eye) in palettes.items():
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
                image = (complexion(image, name) if index == 0
                         else reference_iris(image, name, index))
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
                    'method': 'CC0 derivatives with regional skin tones and distinct iris fibers.',
                    'recipe': 'regional-mpfb-v1',
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
    parser.add_argument('--polished-reference', action='store_true',
                        help='Generate only the rose-brown reference with extra texture detail')
    args = parser.parse_args()
    if args.action == 'generate':
        generate(args.directory, args.polished_reference)
    elif args.out:
        contact_sheet(args.directory, args.out)
    else:
        parser.error('sheet requires --out')


if __name__ == '__main__':
    main()
