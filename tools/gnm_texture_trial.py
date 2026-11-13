"""Render a native-layout GNM texture trial from a fresh neutral scene."""
import argparse
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def aim(obj, position, target):
    obj.location = position
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def render(args):
    head = bpy.context.scene.objects['GNM Head']
    for tile in range(1001, 1008):
        material = head.data.materials[tile - 1001]
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        shader = nodes.get('Principled BSDF')
        if tile in (1001, 1002, 1004):
            image = nodes.new('ShaderNodeTexImage')
            image.image = bpy.data.images.load(str((args.maps / f'color.{tile}.png').resolve()))
            uv = nodes.new('ShaderNodeUVMap')
            uv.uv_map = 'GNM UDIM' if args.layout == 'udim' else 'GNM Region'
            if args.layout == 'udim':
                offset = nodes.new('ShaderNodeVectorMath')
                offset.operation = 'SUBTRACT'
                offset.inputs[1].default_value = (tile - 1001, 0, 0)
                links.new(uv.outputs['UV'], offset.inputs[0])
                links.new(offset.outputs[0], image.inputs['Vector'])
            else:
                links.new(uv.outputs['UV'], image.inputs['Vector'])
            links.new(image.outputs['Color'], shader.inputs['Base Color'])
            shader.inputs['Roughness'].default_value = .48 if tile == 1001 else .28
        elif tile in (1003, 1005):
            transparent = nodes.new('ShaderNodeBsdfTransparent')
            glass = nodes.new('ShaderNodeBsdfGlossy')
            glass.inputs['Roughness'].default_value = .055
            mix = nodes.new('ShaderNodeMixShader')
            mix.inputs[0].default_value = .045
            links.new(transparent.outputs[0], mix.inputs[1])
            links.new(glass.outputs[0], mix.inputs[2])
            links.new(mix.outputs[0], nodes.get('Material Output').inputs['Surface'])
        else:
            shader.inputs['Base Color'].default_value = (.30, .12, .10, 1.)
    scene = bpy.context.scene
    camera = bpy.data.objects.new('GNM Camera', bpy.data.cameras.new('GNM Camera'))
    scene.collection.objects.link(camera)
    aim(camera, (.16 if args.angle else 0, -.58, .015), (0, 0, -.045))
    camera.data.lens = 64
    scene.camera = camera
    for name, position, power, size in [
        ('Key', (.22 if args.side_light else -.13, -.29, .22), 10, .20),
        ('Fill', (.20, -.33, .04), 4, .24),
        ('Rim', (-.14, .10, .18), 8, .16),
    ]:
        lamp = bpy.data.lights.new(name, 'AREA')
        lamp.energy, lamp.size = power, size
        light = bpy.data.objects.new(name, lamp)
        scene.collection.objects.link(light)
        aim(light, position, (0, 0, -.035))
    scene.world = bpy.data.worlds.new('GNM World')
    scene.world.color = (.07, .07, .07)
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = args.size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(args.out.resolve())
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maps', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--layout', choices=['udim', 'legacy'], default='udim')
    parser.add_argument('--angle', action='store_true')
    parser.add_argument('--side-light', action='store_true')
    parser.add_argument('--samples', type=int, default=8)
    parser.add_argument('--size', type=int, default=640)
    render(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
