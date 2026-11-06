"""Build a development-only articulated eye fixture; run with Blender -b -P."""
import sys
import math
import json
from pathlib import Path
from dataclasses import asdict
import bpy
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from apollo_core.core import Config


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = .65
    shader.inputs['Specular IOR Level'].default_value = 0.
    return mat


def mesh(name, verts, faces, mat, arm=None, bone=None):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    if arm:
        group = obj.vertex_groups.new(name=bone)
        group.add(list(range(len(verts))), 1., 'REPLACE')
        modifier = obj.modifiers.new('Eye articulation', 'ARMATURE')
        modifier.object = arm
    return obj


def build(output=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cfg = Config()
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    data = bpy.data.armatures.new('FixtureRig')
    arm = bpy.data.objects.new('FixtureRig', data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for side, x in [('L', cfg.ipd / 2), ('R', -cfg.ipd / 2)]:
        bone = data.edit_bones.new('eye.' + side)
        bone.head = (x, 0, 0)
        bone.tail = (x, -.012, 0)
    bpy.ops.object.mode_set(mode='OBJECT')
    white = material('Sclera', (.8, .8, .75))
    iris = material('Light iris', (.12, .55, .35))
    black = material('Pupil', (.001, .001, .001))
    skin = material('Development proxy', (.48, .29, .19))
    mesh('Face proxy', [(-.09,.012,-.06),(.09,.012,-.06),(.09,.012,.06),(-.09,.012,.06)], [(0,1,2,3)], skin)
    for side, x in [('L', cfg.ipd/2), ('R', -cfg.ipd/2)]:
        bone = 'eye.' + side
        # Open spherical shell: front aperture exposes the iris and pupil plane.
        verts, faces = [], []
        rings, segments = 24, 128
        for j in range(rings + 1):
            theta = .56 + (math.pi - .56) * j / rings
            for i in range(segments):
                phi = 2 * math.pi * i / segments
                verts.append((x + .012*math.sin(theta)*math.cos(phi), -.012*math.cos(theta), .012*math.sin(theta)*math.sin(phi)))
        for j in range(rings):
            for i in range(segments):
                a = j*segments+i; b = j*segments+(i+1)%segments
                faces.append((a,b,b+segments,a+segments))
        mesh('Sclera.'+side, verts, faces, white, arm, bone)
        # Iris annulus surrounds, rather than overlaps, the coplanar pupil disc.
        verts = []
        for radius in [.002, .0065]:
            verts.extend((x+radius*math.cos(2*math.pi*i/128), -.01, radius*math.sin(2*math.pi*i/128)) for i in range(128))
        mesh('Iris.'+side, verts, [(i,(i+1)%128,(i+1)%128+128,i+128) for i in range(128)], iris, arm, bone)
        verts = [(x, -.01, 0)] + [(x+.002*math.cos(2*math.pi*i/128), -.01, .002*math.sin(2*math.pi*i/128)) for i in range(128)]
        mesh('Pupil.'+side, verts, [(0,i+1,(i+1)%128+1) for i in range(128)], black, arm, bone)
        pb = arm.pose.bones[bone]
        pb['gf_pupil_local'] = list(pb.bone.matrix_local.inverted() @ Vector((x,-.01,0)))
    camdata = bpy.data.cameras.new('Camera.Gaze')
    camera = bpy.data.objects.new('Camera.Gaze', camdata)
    bpy.context.collection.objects.link(camera)
    camera.location = (0,-cfg.cam_dist,0)
    camera.rotation_euler = (math.pi/2,0,0)
    camdata.lens = cfg.focal_mm
    camdata.sensor_width = cfg.sensor_mm
    camdata.sensor_fit = 'HORIZONTAL'
    camdata.clip_start = .05
    camdata.clip_end = 5
    scene.camera = camera
    for name, location in [('EyeMidpoint',(0,0,0)),('FixationTarget',(0,-.35,0))]:
        obj = bpy.data.objects.new(name, None)
        bpy.context.collection.objects.link(obj)
        obj.location = location
    world = bpy.data.worlds.new('Static world')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (.25,.25,.25,1)
    scene.world = world
    for name, pos, energy, size in [('Key',(-.12,-.18,.16),.15,.15),('Fill',(.15,-.12,.04),.04,.12)]:
        light = bpy.data.lights.new(name, 'AREA')
        light.energy, light.size = energy, size
        obj = bpy.data.objects.new(name, light)
        bpy.context.collection.objects.link(obj)
        obj.location = pos
        obj.rotation_euler = (-obj.location).to_track_quat('-Z','Y').to_euler()
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 32
    scene.cycles.seed = 0
    scene.cycles.use_animated_seed = False
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False
    scene.render.resolution_x = scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'
    scene.view_settings.view_transform = 'Standard'
    scene['apollo_calibration'] = json.dumps(asdict(cfg))
    scene['apollo_armature'] = arm.name
    scene['apollo_bones'] = json.dumps({'L':'eye.L','R':'eye.R'})
    scene['apollo_fixture'] = True
    sys.path.insert(0, str(ROOT / 'wrapper'))
    import eyes
    eyes.reset()
    output = Path(output) if output else ROOT / 'out/fixture/scene.blend'
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    print('Development fixture saved:', output)

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path)
    args = p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    build(args.out)
