"""Compare source and extracted compact scenes in Blender without modifying either."""
import bpy
import hashlib
import json
import sys
from pathlib import Path

import numpy as np


def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.context.scene
    images = {}
    for image in bpy.data.images:
        if image.source != 'FILE':
            continue
        data = bytes(image.packed_file.data) if image.packed_file else Path(bpy.path.abspath(image.filepath)).read_bytes()
        images[image.name] = {'sha256': hashlib.sha256(data).hexdigest(), 'colorspace': image.colorspace_settings.name}
    frames = {}
    for frame in (1, 26, 102, 192):
        scene.frame_set(frame)
        graph = bpy.context.evaluated_depsgraph_get()
        objects = {}
        for obj in sorted(scene.objects, key=lambda o: o.name):
            if obj.type != 'MESH':
                continue
            evaluated = obj.evaluated_get(graph)
            mesh = evaluated.to_mesh()
            coords = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
            mesh.vertices.foreach_get('co', coords)
            materials = np.empty(len(mesh.polygons), dtype=np.int32)
            mesh.polygons.foreach_get('material_index', materials)
            uv = {}
            for layer in mesh.uv_layers:
                values = np.empty(len(layer.data) * 2, dtype=np.float32)
                layer.data.foreach_get('uv', values)
                uv[layer.name] = hashlib.sha256(values.tobytes()).hexdigest()
            objects[obj.name] = {'geometry': hashlib.sha256(coords.tobytes()).hexdigest(), 'materials': hashlib.sha256(materials.tobytes()).hexdigest(), 'uv': uv, 'matrix': [list(row) for row in obj.matrix_world], 'hidden': obj.hide_render}
            evaluated.to_mesh_clear()
        frames[str(frame)] = objects
    return {'images': images, 'frames': frames, 'camera': [list(row) for row in scene.camera.matrix_world] if scene.camera else None, 'lens': scene.camera.data.lens if scene.camera else None, 'samples': scene.cycles.samples, 'size': [scene.render.resolution_x, scene.render.resolution_y], 'frame_range': [scene.frame_start, scene.frame_end]}


args = sys.argv[sys.argv.index('--') + 1:]
source, compact, report = map(Path, args)
result = {}
for relative in ['model/neutral.blend', 'model/character.blend'] + [f'timelines/{mode}/expression.blend' for mode in ('left', 'right', 'generate-motion')]:
    a, b = snapshot(source / relative), snapshot(compact / relative)
    assert a == b, 'Lossless comparison failed: ' + relative
    result[relative] = {'identical': True, 'snapshot_sha256': hashlib.sha256(json.dumps(a, sort_keys=True).encode()).hexdigest(), 'image_count': len(a['images']), 'sampled_frames': list(a['frames'])}
    report.write_text(json.dumps(result, indent=2) + '\n')
    print('IDENTICAL', relative, flush=True)
