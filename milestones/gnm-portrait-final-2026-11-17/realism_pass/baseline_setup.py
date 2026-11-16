"""Capture baseline renders and geometry measurements without editing the head."""
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

folder = Path(__file__).resolve().parent
sys.path.insert(0, str(folder))
from realism_helpers import crop_render, quick_render, save_version


def camera(scene, name, position):
    data = bpy.data.cameras.new(name)
    data.lens = 85
    data.sensor_width = 36
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector((0, 0, -.025))-obj.location).to_track_quat('-Z', 'Y').to_euler()
    return obj


def audit(scene, head):
    mesh = head.data
    evaluated = head.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    xyz = np.array([v.co[:] for v in evaluated.vertices])
    def indices(name):
        group = head.vertex_groups[name].index
        return {v.index for v in mesh.vertices if any(g.group == group for g in v.groups)}
    pupils = indices('pupils')
    eye_groups = [indices(name) for name in ('left_eye', 'right_eye')]
    centers = [xyz[sorted(pupils & eye)].mean(0) for eye in eye_groups]
    eye_mm = [float(np.ptp(xyz[sorted(group), 0])*1000) for group in eye_groups]
    uv_stats = {}
    for layer in mesh.uv_layers:
        seams = {}
        areas = []
        for face in mesh.polygons:
            if face.material_index != 0:
                continue
            points = np.array([layer.data[i].uv[:] for i in face.loop_indices])
            uv_area = .5*abs(np.dot(points[:,0],np.roll(points[:,1],-1))-
                              np.dot(points[:,1],np.roll(points[:,0],-1)))
            if face.area > 0:
                areas.append(np.sqrt(uv_area/face.area))
            for j, u in enumerate(face.vertices):
                k = (j+1)%len(face.vertices)
                edge = tuple(sorted((u, face.vertices[k])))
                pair = (tuple(points[j]), tuple(points[k]))
                if edge[0] != u:
                    pair = pair[::-1]
                seams.setdefault(edge, set()).add(pair)
        density = np.percentile(areas, (10,50,90))
        uv_stats[layer.name] = dict(skin_density_uv_per_meter=density.tolist(),
                                    split_skin_edges=sum(len(values)>1 for values in seams.values()))
    return dict(blender=bpy.app.version_string, vertices=len(xyz), polygons=len(mesh.polygons),
                quads=sum(len(f.vertices)==4 for f in mesh.polygons),
                pupil_spacing_mm=float(np.linalg.norm(centers[0]-centers[1])*1000),
                eye_group_width_mm=eye_mm, uv=uv_stats, units=scene.unit_settings.scale_length,
                shape_keys=[k.name for k in mesh.shape_keys.key_blocks],
                shape_key_drivers=len(mesh.shape_keys.animation_data.drivers) if mesh.shape_keys.animation_data else 0,
                armatures=[o.name for o in scene.objects if o.type=='ARMATURE'],
                lights=[o.name for o in scene.objects if o.type=='LIGHT'],
                cameras=[o.name for o in scene.objects if o.type=='CAMERA'],
                modifiers={o.name:[m.type for m in o.modifiers] for o in scene.objects if len(o.modifiers)},
                head_materials=[m.name for m in mesh.materials],
                hair_objects=[o.name for o in scene.objects if o.type=='CURVES'],
                visible_additions=[o.name for o in scene.objects if o.type=='MESH' and o!=head and not o.hide_render])


scene = bpy.context.scene
head = scene.objects['GNM Head']
summary = audit(scene, head)
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
scene.render.engine = 'CYCLES'
scene.render.resolution_x = scene.render.resolution_y = 1400
scene.render.resolution_percentage = 50
scene.render.use_border = False
scene.render.image_settings.file_format = 'PNG'
cycles = scene.cycles
cycles.device = 'CPU'
cycles.samples = 64
cycles.use_adaptive_sampling = True
cycles.adaptive_threshold = .05
cycles.use_denoising = True
cycles.denoiser = 'OPENIMAGEDENOISE'
cycles.max_bounces, cycles.diffuse_bounces, cycles.glossy_bounces = 12, 4, 4
cycles.transmission_bounces, cycles.volume_bounces = 8, 0
cycles.caustics_reflective = cycles.caustics_refractive = False
cycles.sample_clamp_indirect = 10
front = camera(scene, 'CAM_EVAL', (0, -.82, .03))
left = camera(scene, 'CAM_EVAL_LEFT', (.40, -.72, .03))
right = camera(scene, 'CAM_EVAL_RIGHT', (-.40, -.72, .03))
scene.camera = front
helper = bpy.data.texts.new('realism_helpers.py')
helper.write((folder/'realism_helpers.py').read_text(encoding='utf-8'))
save_version(folder.parent/'portrait_v01.blend')
output = folder/'00_baseline'
(folder/'mesh_audit.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
for name, view in (('front',front), ('three-quarter-left',left), ('three-quarter-right',right)):
    scene.camera = view
    quick_render(scene, output/f'{name}.png')
scene.camera = front
for name, bounds in (('eyes',(.30,.70,.507,.647)), ('mouth',(.39,.61,.30,.43)),
                     ('hairline',(.27,.73,.69,.84))):
    crop_render(scene, output/f'{name}.png', bounds)
