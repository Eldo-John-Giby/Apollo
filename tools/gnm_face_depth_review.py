"""Add reversible anatomical depth to the softened portrait without changing eyes."""
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_feedback_still import coords
from gnm_soft_face_review import surface
from gnm_portrait_refine import aim, render, skin_tree, smooth


def main():
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    root = Path(bpy.data.filepath).parent
    target = root/'portrait_v18.blend'
    if target.exists():
        raise FileExistsError(target)
    basis = coords(head.data.shape_keys.reference_key.data)
    current = surface(head)
    x, y, z = current.T
    a = abs(x)
    front = smooth((z-.084)/.033)
    skin = {i for f in head.data.polygons if f.material_index == 0 for i in f.vertices}
    protected = {i for f in head.data.polygons if f.material_index in (1, 2, 3, 4)
                 for i in f.vertices}
    mask = np.zeros(len(x))
    mask[list(skin-protected)] = 1
    mask *= front
    g = lambda cx, cy, sx, sy: np.exp(-((a-cx)/sx)**2-((y-cy)/sy)**2)
    lid_height = .3120+.0014*np.cos((a-.031)/.014)
    lid = -.00048*np.exp(-((a-.031)/.014)**6-((y-lid_height)/.0020)**2)
    cheek = .00085*g(.044, .277, .019, .015)-.00032*g(.035, .291, .017, .004)
    # Shallow nasolabial transition and alar groove, fading out above the mouth.
    fold_x = .017+(.269-y)*.27
    fold = -.00058*np.exp(-((a-fold_x)/.0022)**2-((y-.257)/.014)**4)
    alar = -.00045*g(.0145, .266, .0022, .006)
    philtrum = .00038*g(.0038, .244, .0017, .0055)-.00022*g(0, .244, .0022, .0055)
    seam_y = .2333-.00065*np.exp(-(x/.006)**2)
    seam = -.00042*np.exp(-(a/.022)**6-((y-seam_y)/.0013)**2)
    lower = -.00038*g(0, .2175, .022, .0028)+.00035*g(0, .2235, .020, .0035)
    fields = {'Orbital lid crease': lid, 'Cheek plane transition': cheek,
              'Nose cheek transition': fold+alar, 'Philtrum and lip relief': philtrum+seam+lower}
    for name, depth in fields.items():
        delta = np.zeros_like(basis)
        delta[:, 2] = depth*mask
        key = head.shape_key_add(name=f'Natural depth | {name}')
        key.data.foreach_set('co', (basis+delta).astype(np.float32).ravel())
        key.value = 1
    bpy.context.view_layer.update()
    tree = skin_tree(head, surface(head))
    # Keep the visible fuzz attached to the updated skin surface.
    for name in ('Peak | facial vellus', 'Peak | short beard stubble', 'Peak | denser beard stubble'):
        obj = scene.objects.get(name)
        if not obj:
            continue
        attr = obj.data.attributes['position'].data
        flat = np.empty(len(attr)*3, dtype=np.float32)
        attr.foreach_get('vector', flat)
        points = flat.reshape(-1, 3)
        for curve in obj.data.curves:
            section = points[curve.first_point_index:curve.first_point_index+curve.points_length]
            hit, normal, _, _ = tree.find_nearest(Vector(section[0]))
            section += np.asarray(hit+normal*.000012)-section[0]
        attr.foreach_set('vector', flat)
    out = root/'realism_pass'/'18_review'
    out.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = '//realism_pass/18_review/final.png'
    bpy.ops.wm.save_as_mainfile(filepath=str(target), compress=True)
    scene.use_nodes = False
    scene.cycles.time_limit = 0
    scene.cycles.adaptive_threshold = .04
    scene.render.use_border = False
    render(scene, out, 'final', 900, 48)
    scene.render.use_border = True
    scene.render.use_crop_to_border = True
    scene.render.border_min_x = .27
    scene.render.border_max_x = .77
    scene.render.border_min_y = .53
    scene.render.border_max_y = .86
    render(scene, out, 'upper-face', 1560, 64)
    scene.render.use_border = False
    aim(scene.camera, (.36, -.75, .035), (0, 0, -.025))
    render(scene, out, 'three-quarter', 850, 40)


if __name__ == '__main__':
    main()
