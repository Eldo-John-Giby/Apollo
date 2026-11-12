"""Bake a color map between two aligned mesh objects without editing their UVs."""
import argparse
from pathlib import Path
import sys

import bpy


def emission_material(material):
    result = material.copy()
    nodes = result.node_tree.nodes
    links = result.node_tree.links
    output = next(node for node in nodes if node.type == 'OUTPUT_MATERIAL'
                  and node.is_active_output)
    surface = output.inputs['Surface']
    if not surface.is_linked or surface.links[0].from_node.type != 'BSDF_PRINCIPLED':
        raise ValueError(f'{material.name}: expected a Principled surface')
    color = surface.links[0].from_node.inputs['Base Color']
    emission = nodes.new('ShaderNodeEmission')
    if color.is_linked:
        links.new(color.links[0].from_socket, emission.inputs['Color'])
    else:
        emission.inputs['Color'].default_value = color.default_value
    links.new(emission.outputs[0], surface)
    return result


def bake(args):
    scene = bpy.context.scene
    source, target = (scene.objects[name] for name in (args.source, args.target))
    if source == target or any(obj.type != 'MESH' for obj in (source, target)):
        raise ValueError('Choose two distinct, aligned mesh objects')
    if args.out.exists():
        raise FileExistsError(args.out)
    target.data.uv_layers.active = target.data.uv_layers[args.uv]
    for slot in source.material_slots:
        replacement = emission_material(slot.material)
        slot.link = 'OBJECT'
        slot.material = replacement
    image = bpy.data.images.new('Baked color', args.size, args.size, alpha=False)
    image.colorspace_settings.name = 'sRGB'
    material = bpy.data.materials.new('Color bake destination')
    material.use_nodes = True
    nodes = material.node_tree.nodes
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = image
    nodes.active = tex
    target.data.materials.clear()
    target.data.materials.append(material)
    for polygon in target.data.polygons:
        polygon.material_index = 0
    bpy.ops.object.select_all(action='DESELECT')
    source.select_set(True)
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    bpy.ops.object.bake(type='EMIT', use_selected_to_active=True, margin=16,
                        cage_extrusion=args.cage, max_ray_distance=args.distance,
                        uv_layer=args.uv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    image.filepath_raw = str(args.out.resolve())
    image.file_format = 'PNG'
    image.save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--uv', required=True)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--size', type=int, default=2048)
    parser.add_argument('--cage', type=float, default=.002)
    parser.add_argument('--distance', type=float, default=.008)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if args.size <= 0 or args.cage <= 0 or args.distance <= args.cage:
        parser.error('Choose a positive size and 0 < cage < distance')
    bake(args)


if __name__ == '__main__':
    main()
