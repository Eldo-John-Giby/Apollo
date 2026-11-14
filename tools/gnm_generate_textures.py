"""Build five complete portable texture sets from an authenticated scan transfer."""
import argparse
import json
from pathlib import Path
import shutil

from gnm_eye_detail import generate as eyes
from gnm_skin_detail import surface_positions
from gnm_surface_maps import PALETTES, digest, generate


def build(template, source, out, size, variants):
    receipt = json.loads((source / 'scan-transfer.json').read_text())
    if (receipt['output_sha256'] != digest(source / 'color.1001.png')
            or receipt['template_sha256'] != digest(template)):
        raise ValueError('Scan transfer does not match source color or target template')
    out.mkdir(parents=True, exist_ok=False)
    fields = surface_positions(template, size, ('upper_lip', 'lower_lip'))
    for variant in variants:
        target = out / variant
        generate(template, source / 'color.1001.png', target, variant, size,
                 fields=fields, photographic=True)
        eyes(target, variant)
        shutil.copy2(source / 'color.1001.json', target / 'color.1001.json')
        print(f'Completed native skin/eye/surface maps: {variant}', flush=True)
    shutil.copy2(source / 'scan-transfer.json', out / 'scan-transfer.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('template', 'source', 'out'):
        parser.add_argument(f'--{name}', type=Path, required=True)
    parser.add_argument('--size', type=int, choices=(2048, 4096), default=4096)
    parser.add_argument('--variant', choices=tuple(PALETTES))
    args = parser.parse_args()
    build(args.template, args.source, args.out, args.size,
          [args.variant] if args.variant else tuple(PALETTES))
