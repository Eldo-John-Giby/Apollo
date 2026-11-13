"""Import the upstream GNM topology and both native UV layouts into Blender."""
import argparse
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector


def import_template(template, out):
    if out.exists():
        raise FileExistsError(out)
    with np.load(template, allow_pickle=False) as data:
        vertices, faces = data['vertices'], data['quads']
        mesh = bpy.data.meshes.new('GNM Head v3')
        mesh.from_pydata(vertices.tolist(), [], faces.tolist())
        mesh.update()
        indices = np.empty(len(mesh.loops), dtype=np.int32)
        mesh.loops.foreach_get('vertex_index', indices)
        np.testing.assert_array_equal(indices, faces.ravel())
        for name, key in [('GNM UDIM', 'udim'), ('GNM Region', 'legacy')]:
            layer = mesh.uv_layers.new(name=name)
            coordinates = np.asarray(data[key], dtype=np.float32).ravel()
            layer.uv.foreach_set('vector', coordinates)
            readback = np.empty_like(coordinates)
            layer.uv.foreach_get('vector', readback)
            np.testing.assert_array_equal(readback, coordinates)
        mesh.uv_layers.active_index = 0
        for tile in range(1001, 1008):
            mesh.materials.append(bpy.data.materials.new(f'GNM {tile}'))
        mesh.polygons.foreach_set('material_index', (data['tiles'] - 1001).astype(np.int32))
        mesh.polygons.foreach_set('use_smooth', np.ones(len(faces), dtype=bool))
        obj = bpy.data.objects.new('GNM Head', mesh)
        bpy.context.scene.collection.objects.link(obj)
        for name in data.files:
            mask = data[name]
            if mask.dtype == bool and mask.shape == (len(vertices),):
                group = obj.vertex_groups.new(name=name)
                group.add(np.flatnonzero(mask).tolist(), 1., 'REPLACE')
        joints = dict(zip(data['joint_names'], data['joints'].tolist()))
        midpoint = Vector(joints['left_eye']).lerp(Vector(joints['right_eye']), .5)
        # Upstream +Y is up and +Z is forward. Apollo uses +Z and -Y.
        basis = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0))).to_4x4()
        obj.matrix_world = basis @ Matrix.Translation(-midpoint)
        obj['gnm_joints_local'] = json.dumps(joints)
        bpy.context.scene.unit_settings.system = 'METRIC'
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out.resolve()), compress=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import_template(args.template, args.out)
