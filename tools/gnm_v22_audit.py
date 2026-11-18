"""Hash-guarded, read-only v22 inventory and optional reference stills in Blender."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

SELECTED = 'f648bbaff98edbb3254a386047a4909aa8bb20ba7e79c949985b0b43f8833cfd'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def coords(items):
    result = np.empty(len(items) * 3, dtype=np.float32)
    items.foreach_get('co', result)
    return result.reshape(-1, 3)


def main(args):
    source = Path(bpy.data.filepath)
    if sha(source) != SELECTED:
        raise ValueError('Expected immutable, user-selected v22')
    args.out.mkdir(parents=True, exist_ok=True)
    head = bpy.context.scene.objects['GNM Head']
    scene = bpy.context.scene
    evaluated = head.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    neutral = coords(mesh.vertices)
    evaluated.to_mesh_clear()
    basis = coords(head.data.shape_keys.reference_key.data)
    eyes = sorted({i for face in head.data.polygons if face.material_index in (1, 2, 3, 4)
                   for i in face.vertices})
    np.testing.assert_array_equal(neutral[eyes], basis[eyes])
    np.savez_compressed(args.out / 'identity.npz', basis=basis, neutral=neutral,
                        delta=neutral-basis, eyes=np.asarray(eyes, dtype=np.int32))
    objects = []
    for obj in scene.objects:
        entry = dict(name=obj.name, type=obj.type, hidden_render=obj.hide_render,
                     visible_viewport=obj.visible_get(), parent=obj.parent.name if obj.parent else None,
                     matrix_world=[list(row) for row in obj.matrix_world],
                     modifiers=[dict(name=m.name, type=m.type) for m in obj.modifiers],
                     animated=bool(obj.animation_data))
        if obj.type == 'MESH':
            entry.update(vertices=len(obj.data.vertices), polygons=len(obj.data.polygons))
        if obj.type == 'CURVES':
            entry.update(strands=len(obj.data.curves), points=len(obj.data.points),
                         surface=obj.data.surface.name if obj.data.surface else None)
        if obj.type == 'LIGHT':
            entry.update(energy=obj.data.energy, color=list(obj.data.color), light_type=obj.data.type)
        if obj.type == 'CAMERA':
            entry.update(lens=obj.data.lens)
        objects.append(entry)
    materials = []
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        nodes = []
        for node in mat.node_tree.nodes:
            entry = dict(name=node.name, type=node.type)
            if node.type == 'TEX_IMAGE' and node.image:
                entry['image'] = node.image.name
            if node.type == 'UVMAP':
                entry['uv_map'] = node.uv_map
            entry['inputs'] = {socket.name: str(socket.default_value)
                               for socket in node.inputs if hasattr(socket, 'default_value') and not socket.is_linked}
            nodes.append(entry)
        materials.append(dict(name=mat.name, nodes=nodes,
                              links=[(l.from_node.name, l.from_socket.name, l.to_node.name, l.to_socket.name)
                                     for l in mat.node_tree.links]))
    images = []
    for image in bpy.data.images:
        images.append(dict(name=image.name, source=image.source, size=list(image.size),
                           colorspace=image.colorspace_settings.name, filepath=image.filepath,
                           packed=bool(image.packed_file),
                           sha256=hashlib.sha256(bytes(image.packed_file.data)).hexdigest()
                           if image.packed_file else None))
    report = dict(source_sha256=SELECTED, blender=bpy.app.version_string,
                  vertices=len(basis), polygons=len(head.data.polygons),
                  native_eyes_exact=True, max_identity_mm=float(np.linalg.norm(neutral-basis, axis=1).max()*1000),
                  identity_sha256=sha(args.out/'identity.npz'),
                  keys=[dict(name=k.name, value=k.value, mute=k.mute, relative=k.relative_key.name)
                        for k in head.data.shape_keys.key_blocks],
                  uv_layouts=[u.name for u in head.data.uv_layers],
                  objects=objects, materials=materials, images=images,
                  camera=scene.camera.name, engine=scene.render.engine,
                  samples=scene.cycles.samples, exposure=scene.view_settings.exposure,
                  view_transform=scene.view_settings.view_transform,
                  qualification='Inventory only; no motion or texture-only qualification.')
    if args.render:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from gnm_portrait_refine import aim, render
        views = {'saved-camera': None, 'front': ((0,-.82,.03),(0,0,-.025)),
                 'three-quarter': ((.36,-.75,.035),(0,0,-.025)),
                 'profile': ((.82,-.035,.02),(0,0,-.025)),
                 'eye-detail': ((0,-.55,.018),(0,0,-.010))}
        for name in args.views.split(','):
            if name not in views:
                raise ValueError('Unknown reference view '+name)
            if views[name]:
                aim(scene.camera, *views[name])
            if name == 'eye-detail':
                scene.camera.data.lens = 115
            render(scene, args.out, name, args.size, args.samples)
        report['references'] = {p.name: sha(p) for p in args.out.glob('*.png')}
    if sha(source) != SELECTED:
        raise ValueError('Selected source changed during audit')
    (args.out/'audit.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('RESULT '+json.dumps(dict(report=str(args.out/'audit.json'), source_unchanged=True)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--size', type=int, default=1000)
    parser.add_argument('--samples', type=int, default=40)
    parser.add_argument('--views', default='saved-camera,front,three-quarter,profile,eye-detail')
    main(parser.parse_args(sys.argv[sys.argv.index('--')+1:]))
