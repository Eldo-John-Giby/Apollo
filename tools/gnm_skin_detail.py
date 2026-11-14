"""Author deterministic brow fibers directly into the unchanged GNM skin UV atlas."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import map_coordinates


def brow_field():
    # Anterior projection in meters relative to the eye midpoint. Fibers are
    # authored color, independent of illumination and render camera.
    width, height = 2400, 640
    bounds = (-.075, .075, .003, .043)
    mask = Image.new('L', (width, height))
    draw = ImageDraw.Draw(mask)
    rng = np.random.default_rng(20261114)

    def pixel(x, y):
        return ((x - bounds[0]) / (bounds[1] - bounds[0]) * (width - 1),
                (bounds[3] - y) / (bounds[3] - bounds[2]) * (height - 1))

    for side in (-1, 1):
        for _ in range(950):
            t = rng.uniform(0, 1)
            center = .017 + .005 * np.sin(np.pi * t) - .004 * t * t
            thickness = .0022 * (1 - .82 * t * t)
            x = side * (.014 + .046 * t)
            y = center + rng.normal(0, .48) * thickness
            length = rng.uniform(.0012, .0036) * (1 - .35 * t)
            dx = side * length * (.15 + .75 * t)
            dy = length * (.85 - 1.10 * t)
            curve = [pixel(x, y), pixel(x + .55 * dx, y + .65 * dy),
                     pixel(x + dx, y + dy)]
            draw.line(curve, fill=int(rng.integers(110, 235)), width=2, joint='curve')
    mask = mask.filter(ImageFilter.GaussianBlur(.35))
    x, y = np.meshgrid(np.linspace(bounds[0], bounds[1], width),
                       np.linspace(bounds[3], bounds[2], height))
    t = (np.abs(x) - .014) / .046
    u = np.clip(t, 0, 1)
    center = .017 + .005 * np.sin(np.pi * u) - .004 * u * u
    thickness = .0022 * (1 - .82 * u * u)
    taper = np.clip(t / .12, 0, 1) * np.clip((1 - t) / .18, 0, 1)
    base = .27 * np.exp(-((y - center) / thickness)**4) * taper
    fibers = np.asarray(mask, dtype=np.float32) / 255
    fibers *= np.clip(t / .07, 0, 1) * np.clip((1 - t) / .10, 0, 1)
    return base + fibers * (1 - base), bounds


def surface_positions(template, size):
    """Interpolate native vertices at atlas texel centers without changing UVs."""
    positions = np.full((size, size, 3), np.nan, dtype=np.float32)
    with np.load(template, allow_pickle=False) as data:
        selected = data['tiles'] == 1001
        faces, uv = data['quads'][selected], data['legacy'][selected]
        vertices = data['vertices']
        eye = np.mean([data['joints'][list(data['joint_names']).index(f'{s}_eye')]
                       for s in ('left', 'right')], axis=0)
    for face, coordinates in zip(faces, uv):
        for corners in ((0, 1, 2), (0, 2, 3)):
            indices = list(corners)
            triangle = coordinates[indices] * size - .5
            low = np.maximum(0, np.floor(triangle.min(axis=0)).astype(int))
            high = np.minimum(size - 1, np.ceil(triangle.max(axis=0)).astype(int))
            if np.any(high < low):
                continue
            matrix = np.column_stack((triangle[1] - triangle[0], triangle[2] - triangle[0]))
            if abs(np.linalg.det(matrix)) < 1e-12:
                continue
            xx, yy = np.meshgrid(np.arange(low[0], high[0] + 1),
                                 np.arange(low[1], high[1] + 1))
            weight = (np.stack((xx, yy), axis=-1) - triangle[0]) @ np.linalg.inv(matrix).T
            inside = (weight >= -1e-5).all(axis=-1) & (weight.sum(axis=-1) <= 1 + 1e-5)
            points = vertices[face[indices]] - eye
            interpolated = points[0] + weight[..., :1] * (points[1] - points[0])
            interpolated += weight[..., 1:] * (points[2] - points[0])
            positions[size - 1 - yy[inside], xx[inside]] = interpolated[inside]
    return positions


def detail(template, source, out, positions=None):
    with Image.open(source) as image:
        color = np.asarray(image.convert('RGB'), dtype=np.float32)
    if color.shape[0] != color.shape[1]:
        raise ValueError('Expected a square GNM skin atlas')
    if positions is None:
        positions = surface_positions(template, color.shape[0])
    if positions.shape[:2] != color.shape[:2]:
        raise ValueError('Skin map dimensions differ from the rasterized template')
    mask, bounds = brow_field()
    x, y, z = positions.transpose(2, 0, 1)
    valid = np.isfinite(x) & (z > -.002)
    u = np.nan_to_num((x - bounds[0]) / (bounds[1] - bounds[0]) * (mask.shape[1] - 1), nan=-1)
    v = np.nan_to_num((bounds[3] - y) / (bounds[3] - bounds[2]) * (mask.shape[0] - 1), nan=-1)
    opacity = map_coordinates(mask, (v, u), order=1, mode='constant', cval=0) * valid
    pigment = np.array((55, 36, 27), dtype=np.float32)
    result = color * (1 - opacity[..., None]) + pigment * opacity[..., None]
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise FileExistsError(out)
    Image.fromarray(np.rint(result).astype(np.uint8)).save(out)
    report = {'recipe': 'gnm-authored-brow-fibers-v2', 'seed': 20261114,
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'template_sha256': hashlib.sha256(template.read_bytes()).hexdigest(),
              'output_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
              'affected_texels': int(np.count_nonzero(np.any(np.rint(result) != color, axis=-1))),
              'max_opacity': float(opacity.max()),
              'license': 'Project-authored procedural derivative; source license unchanged'}
    out.with_suffix('.detail.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('template', 'source', 'out'):
        parser.add_argument(f'--{name}', type=Path, required=True)
    args = parser.parse_args()
    if args.source.is_dir():
        from gnm_run import VARIANTS
        positions = surface_positions(args.template, 2048)
        for variant in VARIANTS:
            source = args.source / variant
            target = args.out / variant
            detail(args.template, source / 'color.1001.png', target / 'color.1001.png', positions)
            for name in ('color.1001.json', 'color.1002.png', 'color.1004.png'):
                shutil.copy2(source / name, target / name)
    else:
        detail(args.template, args.source, args.out)
