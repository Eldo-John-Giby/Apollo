"""Synthesize distinct bilateral iris and sclera albedo in native GNM eye UVs.

No illumination or catchlights are baked into these maps. Native pupil and
limbal radii come from the pinned template's concentric UV boundaries.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from gnm_surface_maps import digest, noise, smooth

COLORS = {
    'rose-brown': ((.34, .19, .105), (.54, .33, .15)),
    'golden-hazel': ((.29, .33, .18), (.59, .39, .12)),
    'olive-amber': ((.41, .28, .095), (.64, .43, .16)),
    'neutral-deep': ((.19, .115, .065), (.32, .19, .085)),
    'cool-grey': ((.23, .34, .39), (.40, .43, .30)),
}


def generate(out, variant, seed=20261114, size=1024):
    out.mkdir(parents=True, exist_ok=True)
    reports = {}
    y, x = np.mgrid[:size, :size].astype(np.float32)
    x, y = (x + .5) / size - .5, .5 - (y + .5) / size
    radius, angle = np.hypot(x, y), np.arctan2(y, x)
    r = np.clip((radius - .04985) / (.184924 - .04985), 0, 1)
    xyz = np.stack((x, y, np.zeros_like(x)), -1)
    for side, tile in enumerate((1002, 1004)):
        path = out / f'color.{tile}.png'
        if path.exists():
            raise FileExistsError(path)
        native_seed = seed + list(COLORS).index(variant) * 101 + side * 7919
        rng = np.random.default_rng(native_seed)
        phase = rng.uniform(-np.pi, np.pi, 10)
        warp = angle + .013 * np.sin(angle * 13 + phase[0]) + .018 * np.sin(r * 13 + angle * 7)
        fibers = (.43 * np.sin(warp * 179 + 3 * r + phase[1])
                  + .28 * np.sin(warp * 313 - 7 * r + phase[2])
                  + .18 * np.sin(warp * 557 + 9 * r + phase[3]))
        radial = np.sin(r * 70 + 2 * np.sin(angle * 23 + phase[4]))
        collarette = np.exp(-((r - .28 - .035 * np.sin(angle * 19 + phase[5])) / .075)**2)
        crypt = smooth((noise(xyz, 110, native_seed) - .51) / .21) * collarette
        outer, inner = np.asarray(COLORS[variant], dtype=np.float32)
        center = np.exp(-((r - .18) / .24)**2)
        iris = outer * (1 - center[..., None]) + inner * center[..., None]
        iris *= (1 + .25 * fibers + .035 * radial - .37 * crypt)[..., None]
        # A feathered, irregular limbal transition and dark pupillary frill.
        limbus = smooth((r - .86 - .009 * np.sin(angle * 37)) / .14)
        iris *= (1 - .55 * limbus)[..., None]
        frill = np.exp(-((r - .024) / .033)**2)
        iris *= (1 - .52 * frill)[..., None]
        peripheral = smooth((radius - .205) / .30)
        sclera = np.empty((*radius.shape, 3), dtype=np.float32)
        sclera[:] = (.83, .815, .785)
        sclera += peripheral[..., None] * np.array((-.015, -.10, -.11))
        vessels = np.zeros_like(radius)
        for _ in range(28):
            origin, phase_v = rng.uniform(-np.pi, np.pi), rng.uniform(0, 7)
            curve = origin + .025 * np.sin(radius * 39 + phase_v) + .012 * np.sin(radius * 91 + phase_v)
            distance = np.arctan2(np.sin(angle - curve), np.cos(angle - curve)) * radius
            taper = smooth((radius - rng.uniform(.20, .34)) / .10)
            vessels += np.exp(-(distance / rng.uniform(.00035, .0008))**2) * taper
        sclera *= 1 - np.minimum(vessels, 1)[..., None] * np.array((.015, .17, .15))
        boundary = smooth((radius - .1838) / .0022)
        color = iris * (1 - boundary[..., None]) + sclera * boundary[..., None]
        pupil = smooth((radius - .0486) / .0015)
        color = color * pupil[..., None] + np.array((.006, .004, .003)) * (1 - pupil[..., None])
        Image.fromarray(np.rint(np.clip(color, 0, 1) * 255).astype(np.uint8)).save(path)
        reports[str(tile)] = {'sha256': digest(path), 'seed': native_seed,
                              'anatomical_side': 'left' if side == 0 else 'right'}
    report = {'recipe': 'native-iris-fibers-v1', 'variant': variant,
              'license': 'Project-authored procedural maps', 'color_space': 'sRGB',
              'pupil_uv_radius': .04985, 'limbus_uv_radius': .184924,
              'baked_illumination': False, 'maps': reports}
    (out / 'eye-detail.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--variant', choices=tuple(COLORS), required=True)
    args = parser.parse_args()
    print(json.dumps(generate(args.out, args.variant), indent=2))
