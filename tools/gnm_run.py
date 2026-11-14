"""Render one GNM still or one of the three packed timelines from an extracted bundle."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MODES = ('left', 'right', 'generate-motion')
VARIANTS = ('rose-brown', 'golden-hazel', 'olive-amber', 'neutral-deep', 'cool-grey')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('still', *MODES))
    parser.add_argument('--blender', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--variant', choices=VARIANTS, default='rose-brown')
    parser.add_argument('--layout', choices=('udim', 'legacy'), default='udim')
    parser.add_argument('--first', type=int)
    parser.add_argument('--last', type=int)
    args = parser.parse_args()
    root = ROOT
    if args.mode == 'still':
        if args.first is not None or args.last is not None:
            parser.error('Frame limits apply only to motion')
        scene = root / 'model/neutral.blend'
        tool = 'gnm_texture_trial.py'
        flags = ['--maps', str(root / 'textures' / args.variant), '--layout', args.layout,
                 '--out', str(args.out.resolve()), '--size', '1024', '--samples', '32']
    else:
        scene = root / 'timelines' / args.mode / 'expression.blend'
        if args.variant != 'rose-brown' or args.layout != 'udim':
            maps = root / 'textures' / args.variant
            identity = {'source_sha256': hashlib.sha256(scene.read_bytes()).hexdigest(),
                        'layout': args.layout,
                        'maps': {str(tile): hashlib.sha256(
                            (maps / f'color.{tile}.png').read_bytes()).hexdigest()
                                 for tile in (1001, 1002, 1004)}}
            key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
            cache = args.out.resolve() / 'scene'
            result = subprocess.run([
                str(args.blender.resolve()), '-b', '--factory-startup', str(scene),
                '--python-exit-code', '1', '-P', str(root / 'tools/gnm_motion_variant.py'),
                '--', '--maps', str(maps), '--layout', args.layout, '--out', str(cache)], cwd=root)
            if result.returncode:
                return result.returncode
            scene = cache / f'variant-{key}.blend'
        tool = 'submission_render.py'
        flags = ['--out', str(args.out.resolve()), '--reuse-holds']
        for name in ('first', 'last'):
            value = getattr(args, name)
            if value is not None:
                flags.extend((f'--{name}', str(value)))
    if not scene.is_file():
        parser.error(f'Expected an extracted GNM technical bundle. Missing {scene}')
    return subprocess.run([str(args.blender.resolve()), '-b', '--factory-startup', str(scene),
                           '--python-exit-code', '1', '-P', str(root / 'tools' / tool),
                           '--', *flags], cwd=root).returncode


if __name__ == '__main__':
    sys.exit(main())
