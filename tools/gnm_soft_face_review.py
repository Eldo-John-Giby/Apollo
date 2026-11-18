"""Soften the latest portrait jaw and increase upper and lower lash density."""
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_feedback_still import coords
from gnm_portrait_refine import render, skin_tree, strands


def surface(head):
    obj = head.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = obj.to_mesh()
    result = coords(mesh.vertices)
    obj.to_mesh_clear()
    return result


def main():
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    root = Path(bpy.data.filepath).parent
    target = root/'portrait_v17.blend'
    if target.exists():
        raise FileExistsError(target)
    keys = head.data.shape_keys.key_blocks
    keys['Portrait | jaw definition'].value = .30
    keys['jaw_chin'].value = .35
    bpy.context.view_layer.update()
    tree = skin_tree(head, surface(head))
    # Refit existing facial fibers to the softer surface without deleting them.
    for name in ('Peak | facial vellus', 'Peak | short beard stubble',
                 'Peak | denser beard stubble'):
        groom = scene.objects.get(name)
        if not groom:
            continue
        data = groom.data
        attr = data.attributes['position'].data
        flat = np.empty(len(attr)*3, dtype=np.float32)
        attr.foreach_get('vector', flat)
        points = flat.reshape(-1, 3)
        for curve in data.curves:
            section = points[curve.first_point_index:curve.first_point_index+curve.points_length]
            if section[0, 1] > .25:
                continue
            hit, normal, _, _ = tree.find_nearest(Vector(section[0]))
            section += np.asarray(hit+normal*.000012)-section[0]
        attr.foreach_set('vector', flat)

    rng = np.random.default_rng(1717)
    t = np.linspace(0, 1, 9)
    for upper, name, count in ((True, 'Realism upper lashes', 170),
                               (False, 'Realism lower lashes', 82)):
        old = scene.objects[name]
        roots = np.array([old.data.attributes['position'].data[c.first_point_index].vector[:]
                          for c in old.data.curves])
        rows, radii = [], []
        for side in (-1, 1):
            samples = roots[roots[:, 0]*side > 0]
            samples = samples[np.argsort(abs(samples[:, 0]))]
            u = np.linspace(.015, .985, count)+rng.uniform(-.002, .002, count)
            for frac in u:
                seed = Vector([np.interp(frac, np.linspace(0, 1, len(samples)), samples[:, j])
                               for j in range(3)])
                hit, normal, _, _ = tree.find_nearest(seed)
                anchor = np.asarray(hit+normal*.000025)
                envelope = np.sin(np.pi*frac)**.75
                length = ((.0020+.0042*envelope) if upper else (.0011+.0022*envelope))
                length *= rng.uniform(.78, 1.18)
                fan = side*(.62*frac-.10+rng.uniform(-.09, .09))
                vertical = (-.23*t+.85*t**2) if upper else (-.68*t-.16*t**2)
                forward = .98*t-.17*t**3
                rows.append(anchor+length*np.column_stack((fan*t, vertical, forward)))
                radius = rng.uniform(.000050, .000086) if upper else rng.uniform(.000040, .000061)
                radii.append(radius*(1-.997*t)**.73)
        old.hide_render = True
        old.hide_set(True)
        strands('Natural v17 upper lashes' if upper else 'Natural v17 lower lashes',
                head, np.array(rows), np.array(radii), old.data.materials[0])

    for side in (-1, 1):
        corner = scene.objects[f'Peak | inner canthus {side}']
        current = surface(corner)
        center = current.mean(0)
        basis = coords(corner.data.shape_keys.reference_key.data)
        delta = (current-center)*np.array((.25, .20, .10))
        delta[:, 2] += .00010
        key = corner.shape_key_add(name='Natural v17 tear corner visibility')
        key.data.foreach_set('co', (basis+delta).astype(np.float32).ravel())
        key.value = 1
        material = corner.data.materials[0].copy()
        material.name = f'Natural v17 tear tissue {side}'
        corner.data.materials[0] = material
        shader = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        shader.inputs['Base Color'].default_value = (.34, .105, .089, 1)
        shader.inputs['Roughness'].default_value = .38
        shader.inputs['Coat Weight'].default_value = .09

    out = root/'realism_pass'/'17_review'
    out.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = '//realism_pass/17_review/final.png'
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


if __name__ == '__main__':
    main()
