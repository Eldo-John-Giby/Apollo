"""Author portable physical-scale skin detail in the original GNM UV layout.

The photograph supplies low-frequency complexion. New pores, pigment and lip
striations are authored synthesis, never described as recovered scan detail.
All fields use native surface positions, so UV splits share the same recipe.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, map_coordinates
from scipy.spatial import cKDTree

from gnm_skin_detail import brow_field, surface_positions

PALETTES = {
    'rose-brown': ((1., .97, .96), (155, 86, 79), .045, 1101),
    'golden-hazel': ((.94, .85, .73), (140, 80, 64), .22, 2202),
    'olive-amber': ((.79, .73, .60), (122, 73, 63), .025, 3303),
    'neutral-deep': ((.49, .40, .34), (87, 48, 43), .018, 4404),
    'cool-grey': ((1.02, .99, 1.), (165, 92, 92), .075, 5505),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def smooth(a):
    a = np.clip(a, 0, 1)
    return a * a * (3 - 2 * a)


def hash3(p, seed):
    # Integer lattice hash: stable in every process and independent of UVs.
    p = np.asarray(p, dtype=np.int64)
    with np.errstate(over='ignore'):
        n = (p[..., 0] * 73856093) ^ (p[..., 1] * 19349663) ^ (p[..., 2] * 83492791) ^ seed
        n = (n ^ (n >> 13)) * 1274126177
        n ^= n >> 16
    return (n & 0xffffff).astype(np.float32) / 16777215


def noise(p, scale, seed):
    q = p * scale
    cell = np.floor(q).astype(np.int64)
    f = smooth(q - cell)
    result = np.zeros(p.shape[:-1], dtype=np.float32)
    for x in (0, 1):
        for y in (0, 1):
            for z in (0, 1):
                weight = np.prod(np.where((x, y, z), f, 1 - f), axis=-1)
                result += weight * hash3(cell + (x, y, z), seed)
    return result


def pores(p, seed, spacing=.00055):
    """Jittered cellular follicles with 0.07â€“0.14 mm radii, in meters."""
    q = p / spacing
    cell = np.floor(q).astype(np.int64)
    distance = np.full(len(p), 100., dtype=np.float32)
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            for z in (-1, 0, 1):
                c = cell + (x, y, z)
                jitter = np.stack([hash3(c, seed + i * 47) for i in range(3)], -1)
                d = np.sum((q - c - jitter) ** 2, -1)
                distance = np.minimum(distance, d)
    return np.exp(-distance / .045)


def generate(template, source, out, variant, size, fields=None, photographic=False):
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    if fields is None:
        fields = surface_positions(template, size, ('upper_lip', 'lower_lip'))
    valid = np.isfinite(fields[..., 0])
    flat = fields[valid]
    p, lip = flat[:, :3], smooth(np.max(flat[:, 3:], axis=-1))
    with Image.open(source) as image:
        source_size = image.size
        color = np.asarray(image.convert('RGB').resize((size, size), Image.Resampling.BICUBIC),
                           dtype=np.float32)[valid] / 255
    x, y, z = p.T
    anterior = smooth((z + .005) / .015)
    # Remove the transferred source mouth pigment, whose vermilion outline
    # differs from GNM. Restore nearby skin before adding native lip color.
    if not photographic:
        mouth = np.exp(-(x / .034)**6 - ((y + .071) / .019)**6) * anterior
        clean = (mouth < .015) & (abs(x) < .055) & (abs(y + .071) < .045) & (z > .005)
        if not clean.any():
            raise ValueError('No clean skin surrounding the native mouth')
        selected = mouth > .005
        nearest = cKDTree(p[clean]).query(p[selected], k=16)[1]
        replacement = color[clean][nearest].mean(axis=1)
        color[selected] = color[selected] * (1 - mouth[selected, None]) + replacement * mouth[selected, None]
        # The portrait source has eyelid and nostril colors at different anatomical
        # positions. Attenuate those transferred features using surrounding skin;
        # GNM geometry supplies the actual folds and nostril shadows at runtime.
        eye_x = .030
        sockets = np.exp(-((abs(x) - eye_x) / .022)**4 - ((y + .0015) / .012)**4) * anterior
        nose_base = np.exp(-(x / .024)**6 - ((y + .043) / .013)**6) * anterior
        repair = np.maximum(.90 * sockets, .82 * nose_base)
        clean = (sockets < .015) & (nose_base < .015) & (mouth < .015) & anterior.astype(bool)
        selected = repair > .005
        nearest = cKDTree(p[clean]).query(p[selected], k=16)[1]
        replacement = color[clean][nearest].mean(axis=1)
        color[selected] = color[selected] * (1 - repair[selected, None]) + replacement * repair[selected, None]
    gain, lip_color, freckles, seed = PALETTES[variant]
    color *= gain
    roughness = np.empty(len(p), dtype=np.float32)
    height = np.empty(len(p), dtype=np.float32)
    # Chunking bounds memory use for 4K maps, without changing sampled fields.
    for start in range(0, len(p), 160000):
        stop = min(start + 160000, len(p))
        xyz = p[start:stop]
        xx, yy, zz = xyz.T
        l = lip[start:stop]
        front = anterior[start:stop]
        broad = noise(xyz, 110, seed) - .5
        fine = noise(xyz, 1700, seed + 7) - .5
        pore = pores(xyz, seed + 19)
        cheek = np.exp(-((abs(xx) - .036) / .024)**2 - ((yy + .027) / .023)**2) * front
        nose = np.exp(-(xx / .017)**2 - ((yy + .028) / .025)**2) * front
        forehead = np.exp(-(xx / .044)**2 - ((yy - .040) / .027)**2) * front
        grain = .035 * fine + .045 * broad - .032 * pore
        if freckles >= .1:
            # Dense visible freckles need rounded follicles with irregular
            # spacing. Thresholded lattice noise leaves angular pigment cells.
            patch = pores(xyz, seed + 53, spacing=.0024)
        else:
            patch = smooth((noise(xyz, 1350, seed + 53) - .63) / .20)
        pigment = patch * freckles * (cheek + .35 * nose)
        c = color[start:stop]
        c *= 1 + grain[:, None] * (1 - l[:, None])
        c *= 1 - pigment[:, None] * np.array((1., 1.8, 2.1))
        c *= 1 + ((.045 * cheek + .032 * nose) * (1 - l))[:, None] * np.array((.5, -.55, -.40))
        # Native lip membership prevents pigment from crossing the vermilion
        # border. Irregular vertical striations also affect portable height.
        ridge = np.sin(xx * 18000 + 8 * noise(xyz, 1300, seed))
        ridge *= .3 + .7 * noise(xyz, 870, seed + 71)
        lip_detail = .018 * ridge + .065 * fine
        target = np.asarray(lip_color) / 255 * (1 + lip_detail[:, None])
        if not photographic:
            c[:] = c * (1 - .69 * l[:, None]) + target * (.69 * l[:, None])
        roughness[start:stop] = (.53 + .07 * broad + .035 * fine - .09 * nose - .045 * forehead) * (1 - l) + (.36 + .025 * fine) * l
        height[start:stop] = .5 + (.035 * fine - .15 * pore * (1 + .35 * nose)) * (1 - l) + .020 * ridge * l
    # Reuse the established surface-space brow placement, with a stronger
    # pigment floor for legibility in the portable color map.
    brow, bounds = brow_field()
    u = (x - bounds[0]) / (bounds[1] - bounds[0]) * (brow.shape[1] - 1)
    v = (bounds[3] - y) / (bounds[3] - bounds[2]) * (brow.shape[0] - 1)
    opacity = map_coordinates(brow, (v, u), order=1, mode='constant', cval=0) * anterior
    pigment = np.array((43, 29, 23)) / 255 * np.mean(gain)**.3
    if not photographic:
        color = color * (1 - opacity[:, None]) + pigment * opacity[:, None]
    # Extend every field outside islands from nearest valid texel. All island
    # samples remain unchanged; bilinear filtering cannot reveal blank borders.
    index = distance_transform_edt(~valid, return_distances=False, return_indices=True)
    outputs = {}
    for name, values in [('color.1001.png', color), ('roughness.1001.png', roughness),
                         ('height.1001.png', height)]:
        shape = (size, size, 3) if values.ndim == 2 else (size, size)
        atlas = np.zeros(shape, dtype=np.float32)
        atlas[valid] = values
        atlas = atlas[tuple(index)]
        if name.startswith('height'):
            encoded = np.rint(np.clip(atlas, 0, 1) * 65535).astype(np.uint16)
        else:
            encoded = np.rint(np.clip(atlas, 0, 1) * 255).astype(np.uint8)
        path = out / name
        Image.fromarray(encoded).save(path)
        outputs[name] = digest(path)
    report = {'recipe': 'native-surface-v2' if freckles >= .1 else 'native-surface-v1',
              'variant': variant, 'seed': seed,
              'template_sha256': digest(template), 'source_sha256': digest(source),
              'source_dimensions': list(source_size), 'output_dimensions': [size, size],
              'detail_origin': 'Source photograph plus authored physical-scale synthesis; resizing adds no photographic detail',
              'pore_spacing_m': .00055, 'bump_distance_m': .00009,
              'color_space': {'color': 'sRGB', 'roughness': 'Non-Color', 'height': 'Non-Color'},
              'output_sha256': outputs['color.1001.png'], 'maps': outputs,
              'valid_texels': int(valid.sum()),
              'license': 'CC-BY-3.0 scan derivative, CC0 fallback and project-authored detail' if photographic else 'CC0 source derivative and project-authored procedural detail'}
    (out / 'color.1001.detail.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('template', 'source', 'out'):
        parser.add_argument(f'--{name}', type=Path, required=True)
    parser.add_argument('--size', type=int, choices=(1024, 2048, 4096), default=4096)
    parser.add_argument('--variant', choices=tuple(PALETTES), default='rose-brown')
    parser.add_argument('--photographic', action='store_true', help='Preserve registered scan features and brows')
    args = parser.parse_args()
    print(json.dumps(generate(args.template, args.source, args.out, args.variant, args.size, photographic=args.photographic), indent=2))
