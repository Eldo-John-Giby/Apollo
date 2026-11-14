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


def surface_files(maps):
    paths = {name: Path(maps) / f'{name}.1001.png' for name in ('roughness', 'height')}
    present = [p.exists() for p in paths.values()]
    if any(present) and not all(present):
        raise ValueError('Skin surface maps require both roughness.1001.png and height.1001.png')
    return paths if all(present) else {}


def variant_identity(scene, maps, layout):
    inputs = {str(tile): Path(maps) / f'color.{tile}.png' for tile in (1001, 1002, 1004)}
    inputs.update(surface_files(maps))
    recipe = b''.join((ROOT / 'tools' / name).read_bytes()
                      for name in ('gnm_materials.py', 'gnm_motion_variant.py'))
    return {'source_sha256': hashlib.sha256(Path(scene).read_bytes()).hexdigest(),
            'layout': layout, 'maps': {role: hashlib.sha256(path.read_bytes()).hexdigest()
                                     for role, path in inputs.items()},
            'material_recipe_sha256': hashlib.sha256(recipe).hexdigest()}


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
            identity = variant_identity(scene, maps, args.layout)
            key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
            cache = args.out.resolve() / 'scene'
            result = subprocess.run([
                str(args.blender.resolve()), '--offline-mode', '-b', '--factory-startup', str(scene),
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
    return subprocess.run([str(args.blender.resolve()), '--offline-mode', '-b', '--factory-startup', str(scene),
                           '--python-exit-code', '1', '-P', str(root / 'tools' / tool),
                           '--', *flags], cwd=root).returncode


if __name__ == '__main__':
    sys.exit(main())
