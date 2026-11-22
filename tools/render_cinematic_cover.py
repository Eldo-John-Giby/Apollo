"""Render a derived cinematic camera/light study without altering v22 geometry."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector


def geometry_digest(head):
    evaluated = head.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    values = np.empty(len(mesh.vertices)*3, dtype=np.float32)
    mesh.vertices.foreach_get('co', values)
    evaluated.to_mesh_clear()
    return hashlib.sha256(values.tobytes()).hexdigest()


def main(args):
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    source = Path(bpy.data.filepath)
    before = geometry_digest(head)
    for obj in scene.objects:
        if obj.type == 'LIGHT':
            obj.hide_render = True
    def aim(obj, target):
        obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()
    detail = args.style == 'detail'
    target = Vector((0, -.014, .005) if detail else (-.018, -.015, .004))
    cam_data = bpy.data.cameras.new('Apollo cinematic macro camera')
    camera = bpy.data.objects.new('Apollo cinematic macro camera', cam_data)
    scene.collection.objects.link(camera)
    camera.location = (0, -.260, .020) if detail else (-.105, -.235, .025)
    aim(camera, target)
    cam_data.lens = 75 if detail else 95
    cam_data.sensor_width = 36
    cam_data.clip_start = .001
    cam_data.clip_end = 10
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = (camera.location-Vector((0, -.015, .001) if detail else (-.0308, -.015, .001))).length
    cam_data.dof.aperture_fstop = 16 if detail else 11
    scene.camera = camera
    def light(name, location, energy, color, size):
        data = bpy.data.lights.new(name, 'AREA')
        data.energy, data.color, data.shape, data.size = energy, color, 'DISK', size
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = location
        aim(obj, (-.025, -.01, .005))
    light('Apollo macro warm key', (-.17, -.20, .12) if detail else (-.16, -.12, .10), 4.0 if detail else 3.5, (1.0, .94, .87) if detail else (1.0, .76, .53), .16 if detail else .10)
    light('Apollo macro cool fill', (.14, -.20, .05), .75 if detail else .12, (.83, .91, 1.0), .20)
    light('Apollo macro edge', (-.12, .04, .08), .8, (.80, .88, 1.0), .09)
    if scene.world and scene.world.use_nodes:
        for node in scene.world.node_tree.nodes:
            if node.type == 'BACKGROUND':
                node.inputs['Strength'].default_value = .01 if detail else .003
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = .025 if args.samples <= 64 else .015
    scene.render.resolution_x = args.width
    scene.render.resolution_y = round(args.width*9/16)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = -.35 if detail else -.75
    args.out.parent.mkdir(parents=True, exist_ok=True)
    after = geometry_digest(head)
    assert before == after, 'Cinematic study changed evaluated head geometry'
    scene.render.filepath = str(args.out.resolve())
    bpy.ops.render.render(write_still=True)
    receipt = {'style': args.style, 'source_scene_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'evaluated_geometry_sha256_before': before, 'evaluated_geometry_sha256_after': after, 'geometry_unchanged': before == after, 'blender': bpy.app.version_string, 'samples': args.samples, 'resolution': [scene.render.resolution_x, scene.render.resolution_y], 'lens_mm': cam_data.lens, 'fstop': cam_data.dof.aperture_fstop, 'camera_location': list(camera.location), 'camera_target': list(target), 'image_sha256': hashlib.sha256(args.out.read_bytes()).hexdigest(), 'scope': 'Separate cinematic beauty camera and lighting. Appearance materials and head geometry unchanged; no new motion or scoring qualification.'}
    args.out.with_suffix('.render.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print('CINEMATIC_RENDER '+json.dumps(receipt), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--width', type=int, default=1920)
    parser.add_argument('--samples', type=int, default=256)
    parser.add_argument('--style', choices=['cinematic', 'detail'], default='cinematic')
    main(parser.parse_args(sys.argv[sys.argv.index('--')+1:]))
