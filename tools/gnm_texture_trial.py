"""Render a native-layout GNM texture trial from a neutral or animated Blender scene."""
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
            shader.inputs['Roughness'].default_value = .54 if tile == 1001 else .31
            if tile == 1001:
                shader.inputs['Specular IOR Level'].default_value = .28
                coords = nodes.new('ShaderNodeTexCoord')
                pores = nodes.new('ShaderNodeTexNoise')
                pores.inputs['Scale'].default_value = 420
                pores.inputs['Detail'].default_value = 2
                bump = nodes.new('ShaderNodeBump')
                bump.inputs['Strength'].default_value = .18
                bump.inputs['Distance'].default_value = .00006
                links.new(coords.outputs['Generated'], pores.inputs['Vector'])
                links.new(pores.outputs['Fac'], bump.inputs['Height'])
                links.new(bump.outputs['Normal'], shader.inputs['Normal'])
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
    camera.data.lens = 115 if args.eye_crop else 64
    if args.eye_crop:
        aim(camera, camera.location.copy(), (0, 0, -.012))
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
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.exposure = -.85
    scene.render.resolution_x = scene.render.resolution_y = args.size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(args.out.resolve())
    if args.save_scene:
        if args.save_scene.exists():
            raise FileExistsError(args.save_scene)
        scene.render.filepath = '//frames/frame_'
        scene.frame_set(scene.frame_start)
        bpy.ops.file.pack_all()
        args.save_scene.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(args.save_scene.resolve()), compress=True)
    if args.save_only:
        return
    frames = args.frame or [None]
    for frame in frames:
        if frame is not None:
            if not scene.frame_start <= frame <= scene.frame_end:
                raise ValueError(f'Frame {frame} outside the timeline')
            scene.frame_set(frame)
            scene.render.filepath = str(args.out.resolve().with_name(
                f'{args.out.stem}-{frame:04d}{args.out.suffix}'))
        else:
            scene.render.filepath = str(args.out.resolve())
        bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maps', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--layout', choices=['udim', 'legacy'], default='udim')
    parser.add_argument('--frame', type=int, action='append')
    parser.add_argument('--save-scene', type=Path)
    parser.add_argument('--save-only', action='store_true')
    parser.add_argument('--eye-crop', action='store_true')
    parser.add_argument('--angle', action='store_true')
    parser.add_argument('--side-light', action='store_true')
    parser.add_argument('--samples', type=int, default=8)
    parser.add_argument('--size', type=int, default=640)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if args.save_only and not args.save_scene:
        parser.error('--save-only requires --save-scene')
    render(args)
