"""Try a subtle asymmetric expression on the packed still portrait."""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_portrait_refine import aim, render, skin_tree


def expression_offset(points):
    """Local metres. X runs across the face, Y up and Z forward."""
    x, y, z = points.T
    delta = np.zeros_like(points)
    # Move each commissure and nearby skin as one patch, with a softer
    # response in the cheek. Compact weights leave the lids and nose alone.
    for side, lift in [(-1, .00047), (1, .00094)]:
        def weight(center_x, center_y, width, height):
            radius = ((x - side * center_x) / width)**2 + ((y - center_y) / height)**2
            profile = np.maximum(0.0, 1.0 - radius)**2
            return profile * np.clip((z - .094) / .022, 0.0, 1.0)

        corner = weight(.023, .232, .017, .014)
        cheek = weight(.036, .244, .018, .015)
        delta[:, 0] += side * .38 * lift * corner
        delta[:, 1] += lift * corner + .38 * lift * cheek
        delta[:, 2] += -.18 * lift * corner + .48 * lift * cheek
    return delta


def fit_vellus(scene, tree):
    curves = scene.objects['Peak | facial vellus'].data
    points = np.empty(len(curves.points) * 3, dtype=np.float32)
    curves.attributes['position'].data.foreach_get('vector', points)
    strands = points.reshape(-1, 4, 3)
    roots = strands[:, 0, :].copy()
    offsets = expression_offset(roots)
    for index in np.flatnonzero(np.linalg.norm(offsets, axis=1) > 0):
        location, normal, _, _ = tree.find_nearest(Vector(roots[index] + offsets[index]))
        strands[index] += np.asarray(location + normal * .000008) - roots[index]
    curves.attributes['position'].data.foreach_set('vector', points)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.out.mkdir(parents=True, exist_ok=True)
    destination = (args.out / 'portrait.blend').resolve()
    if destination.exists():
        raise FileExistsError(destination)
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    basis = head.data.shape_keys.reference_key
    positions = np.array([vertex.co[:] for vertex in basis.data])
    delta = expression_offset(positions)
    eye_ids = {i for face in head.data.polygons if face.material_index in (1, 2, 3, 4) for i in face.vertices}
    assert not np.any(delta[sorted(eye_ids)])
    key = head.shape_key_add(name='Portrait | relaxed asymmetric expression', from_mix=False)
    key.relative_key = basis
    key.data.foreach_set('co', (positions + delta).astype(np.float32).ravel())
    key.value = 1
    bpy.context.view_layer.update()
    evaluated = head.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    surface = np.array([vertex.co[:] for vertex in mesh.vertices])
    evaluated.to_mesh_clear()
    fit_vellus(scene, skin_tree(head, surface))
    scene.render.use_border = False
    aim(scene.camera, (0, -.82, .03), (0, 0, -.025))
    scene.camera.data.lens = 85
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
    render(scene, args.out, 'front', 900, 32)


if __name__ == '__main__':
    main()
