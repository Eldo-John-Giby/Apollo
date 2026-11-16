"""Compare attached upper lashes with a more visible curl and outward splay."""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_portrait_refine import aim, render, smooth


def reshape_lashes(groom):
    data = groom.data
    position = data.attributes['position'].data
    flat = np.empty(len(position)*3, dtype=np.float32)
    position.foreach_get('vector', flat)
    curves = flat.reshape(-1, 6, 3)
    roots = curves[:, 0].copy()
    rng = np.random.default_rng(2721)
    t = np.linspace(0, 1, curves.shape[1])
    along = smooth((abs(roots[:, 0])-.020)/.022)
    # Mid-outer lashes are longest; the inner corner and tapered tail are shorter.
    length = rng.uniform(.0033, .0057, len(curves))
    length *= .70 + .40*np.sin(np.pi*along*.73)
    lift = (.66+.22*rng.random(len(curves)))[:, None]
    fan = np.sign(roots[:, 0])*(.40*along-.10)
    curves[:, :, 0] = roots[:, 0, None]+length[:, None]*fan[:, None]*t**1.2
    curves[:, :, 1] = roots[:, 1, None]+length[:, None]*(-.18*t+lift*t**3)
    curves[:, :, 2] = roots[:, 2, None]+length[:, None]*(1.05*t-.17*t**3)
    position.foreach_set('vector', flat)
    radius = rng.uniform(.000040, .000056, len(curves))[:, None]*(1-.99*t)**.64
    data.attributes['radius'].data.foreach_set('value', radius.astype(np.float32).ravel())


def eye_crop(scene, out, name):
    scene.render.use_border = True
    scene.render.use_crop_to_border = True
    scene.render.border_min_x = .27
    scene.render.border_max_x = .73
    scene.render.border_min_y = .505
    scene.render.border_max_y = .655
    render(scene, out, name, 1400, 48)
    scene.render.use_border = False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args(sys.argv[sys.argv.index('--')+1:]).out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    path = out/'portrait.blend'
    if path.exists():
        raise FileExistsError(path)
    scene = bpy.context.scene
    aim(scene.camera, (0, -.82, .03), (0, 0, -.025))
    eye_crop(scene, out, 'eyes-before')
    reshape_lashes(scene.objects['Portrait | subtle upper lashes'])
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
    eye_crop(scene, out, 'eyes-after')
    render(scene, out, 'front', 850, 32)


if __name__ == '__main__':
    main()
