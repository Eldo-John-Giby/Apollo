"""Validate mesh/UV fingerprints and apply a face-and-eye texture manifest."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

import bpy
from mathutils import Vector


def fingerprint(mesh, uv):
    digest = hashlib.sha256()
    digest.update(struct.pack('<II', len(mesh.vertices), len(mesh.polygons)))
    for polygon in mesh.polygons:
        digest.update(struct.pack('<I', polygon.loop_total))
        for index in polygon.loop_indices:
            digest.update(struct.pack('<Iff', mesh.loops[index].vertex_index,
                                      *uv.data[index].uv))
    return digest.hexdigest()


def resolve(binding):
    obj = bpy.context.scene.objects[binding['object']]
    if obj.type != 'MESH':
        raise ValueError(f'{obj.name} must be a mesh')
    uv = obj.data.uv_layers[binding['uv']]
    if binding['slot'] >= len(obj.material_slots) or binding['slot'] < 0:
        raise ValueError(f'Invalid material slot on {obj.name}')
    return obj, uv


def apply_variant(path):
    path = path.resolve()
    spec = json.loads(path.read_text(encoding='utf-8'))
    if {entry['role'] for entry in spec['maps']} != {'face', 'iris_left', 'iris_right'}:
        raise ValueError('Provide face, iris_left and iris_right maps')
    if len(spec['maps']) != 3 or not spec['provenance']:
        raise ValueError('Provide one binding per map and texture provenance')
    prepared = []
    for binding in spec['maps']:
        obj, uv = resolve(binding)
        if fingerprint(obj.data, uv) != binding['mesh_uv_sha256']:
            raise ValueError(f'Mesh/UV mismatch on {obj.name}')
        asset = (path.parent / binding['file']).resolve()
        if not asset.is_relative_to(path.parent):
            raise ValueError('Map must be inside the variant directory')
        if hashlib.sha256(asset.read_bytes()).hexdigest() != binding['sha256']:
            raise ValueError(f'Texture hash mismatch: {asset.name}')
        slots = [obj.material_slots[binding['slot']]]
        source = binding.get('replace_image')
        if binding.get('all_slots') or (source and binding.get('replace_on_all_slots')):
            slots = list(obj.material_slots)
        for slot in slots:
            node = None
            if source:
                nodes = [node.name for node in slot.material.node_tree.nodes
                         if node.type == 'TEX_IMAGE' and node.image
                         and re.fullmatch(re.escape(source) + r'(\.\d+)?', node.image.name)]
                if len(nodes) != 1:
                    raise ValueError(f'{obj.name} needs exactly one image node for {source}')
                node = nodes[0]
            prepared.append((binding, slot, asset, node))
    for binding, slot, asset, node in prepared:
        image = bpy.data.images.load(str(asset), check_existing=True)
        image.colorspace_settings.name = 'sRGB'
        if node:
            material = slot.material.copy()
            material.node_tree.nodes[node].image = image
        else:
            material = bpy.data.materials.new(f"Submission {binding['role']}")
            material.use_nodes = True
            nodes = material.node_tree.nodes
            links = material.node_tree.links
            tex = nodes.new('ShaderNodeTexImage')
            tex.image = image
            uv_node = nodes.new('ShaderNodeUVMap')
            uv_node.uv_map = binding['uv']
            links.new(uv_node.outputs['UV'], tex.inputs['Vector'])
            links.new(tex.outputs['Color'], nodes.get('Principled BSDF').inputs['Base Color'])
        slot.link = 'OBJECT'
        slot.material = material


def inventory():
    return {obj.name: {
        'uv': {uv.name: fingerprint(obj.data, uv) for uv in obj.data.uv_layers},
        'slots': [
            {'material': slot.material.name, 'images': [
                node.image.name for node in slot.material.node_tree.nodes
                if node.type == 'TEX_IMAGE' and node.image
            ] if slot.material.use_nodes else []} if slot.material else None
            for slot in obj.material_slots
        ],
    } for obj in bpy.context.scene.objects if obj.type == 'MESH' and obj.data.uv_layers}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', type=Path)
    parser.add_argument('--inventory', action='store_true')
    parser.add_argument('--oblique-light', action='store_true',
                        help='Move the Apollo Key light for a texture inspection still')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if args.inventory:
        print(json.dumps(inventory(), indent=2))
        return
    if not args.variant or not args.out:
        parser.error('Rendering requires --variant and --out')
    apply_variant(args.variant)
    scene = bpy.context.scene
    scene.cycles.device = 'CPU'
    if args.oblique_light:
        key = scene.objects['Key']
        key.location.x += .16
        key.rotation_euler = (-Vector(key.location)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.image_settings.file_format = 'PNG'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(args.out.resolve())
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    main()
