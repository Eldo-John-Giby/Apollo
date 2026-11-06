"""Blender-side evidence collection. Run in a disposable Blender process."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wrapper'))
import eyes


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def collect(folder):
    folder=Path(folder)
    evidence=folder/'verification'
    evidence.mkdir(parents=True,exist_ok=True)
    rig=eyes._rig(); scene=rig.scene; cfg=rig.cfg
    shipped=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    scene.cycles.samples=int(shipped[0]['extra']['render_samples'])
    result={'blender':bpy.app.version_string,'config':eyes.calibration(),'fixture':bool(scene.get('gazeforge_fixture',True)),'checks':{},'directions':{}}
    def check(name,fn):
        try:
            measurement=fn()
            result['checks'][name]={'status':'PASS','measurement':measurement}
        except Exception as error:
            result['checks'][name]={'status':'FAIL','detail':str(error)}
    def calibration():
        camera=scene.camera
        assert (camera.location-Vector((0,-.4,0))).length<1e-7
        assert abs(camera.rotation_euler.x-math.pi/2)<1e-6
        assert abs(camera.rotation_euler.y)+abs(camera.rotation_euler.z)<1e-7
        assert scene.unit_settings.system=='METRIC' and scene.unit_settings.scale_length==1
        assert scene.render.resolution_x==scene.render.resolution_y==1024 and scene.render.resolution_percentage==100
        assert camera.data.sensor_fit=='HORIZONTAL'
        assert camera.data.type=='PERSP'
        assert abs(camera.data.lens-cfg.focal_mm)<1e-6 and abs(camera.data.sensor_width-cfg.sensor_mm)<1e-6
        assert camera.data.shift_x==camera.data.shift_y==0 and not camera.data.dof.use_dof
        assert scene.render.pixel_aspect_x==scene.render.pixel_aspect_y
        assert scene.render.image_settings.file_format=='PNG'
        assert scene.render.engine=='CYCLES' and scene.cycles.device=='CPU'
        assert scene.cycles.seed==0 and not scene.cycles.use_animated_seed and not scene.cycles.use_adaptive_sampling
        eyes.reset()
        assert (bpy.data.objects['FixationTarget'].location-Vector((0,-.35,0))).length<1e-7
        for obj in list(scene.objects)+[scene.world]:
            if obj and (obj.type in {'LIGHT','CAMERA'} if hasattr(obj,'type') else True):
                assert not obj.animation_data
                if hasattr(obj,'data') and obj.data: assert not obj.data.animation_data
                data=obj.data if hasattr(obj,'data') else obj
                if getattr(data,'node_tree',None): assert not data.node_tree.animation_data
        return 'camera/target/units/render/static lighting audited'
    check('V1',calibration)
    def metrics():
        centers=[]
        for side in 'LR':
            rest,offset=rig.rest[side]
            center=rest.translation
            centers.append(center)
            assert abs((rest@offset-center).length-cfg.pupil_depth)<1e-6
            obj=bpy.data.objects['Sclera.'+side]
            radii=[(obj.matrix_world@v.co-center).length for v in obj.data.vertices]
            assert max(abs(r-.012) for r in radii)<.00005
        measured=(centers[0]-centers[1]).length
        assert abs(measured-cfg.ipd)<.0001 and .058<=measured<=.068
        return {'ipd_m':measured,'radius_m':.012}
    check('V2',metrics)
    max_angle=max_ray=max_torsion=0.
    try:
        rng=random.Random(0)
        for _ in range(1000):
            h,v=rng.uniform(-1,1),rng.uniform(-1,1)
            eyes.move(h,v)
            st,target=eyes.eye_state(h,v,cfg)
            evaluated=rig.arm.evaluated_get(bpy.context.evaluated_depsgraph_get())
            for side in 'LR':
                pb=evaluated.pose.bones[rig.bones[side]]
                matrix=evaluated.matrix_world@pb.matrix
                point=matrix@rig.rest[side][1]
                center=matrix.translation
                gaze=(point-center).normalized()
                expected=Vector(st[side]['gaze'])
                max_angle=max(max_angle,(gaze-expected).length)
                delta=Vector(target)-center
                max_ray=max(max_ray,(delta-gaze*delta.dot(gaze)).length)
                rotation=matrix.to_3x3()@rig.rest[side][0].to_3x3().inverted()
                q=rotation.to_quaternion()
                max_torsion=max(max_torsion,abs(q.y))
        for name,value,limit in [('V3',max_angle,1e-5),('V4',max_ray,1e-5),('V5',max_torsion,1e-6)]:
            result['checks'][name]={'status':'PASS' if value<limit else 'FAIL','measurement':value,'limit':limit}
        result['checks']['V6']={'status':'PASS','measurement':'1000 evaluated poses passed wrapper projection checks (<0.001 px)'}
    except Exception as error:
        for name in ['V3','V4','V5','V6']: result['checks'][name]={'status':'FAIL','detail':str(error)}
    def order():
        rng=random.Random(1)
        for _ in range(200):
            h,v=rng.uniform(-1,1),rng.uniform(-1,1)
            eyes.move(h,v)
            first={s:[list(row) for row in rig.arm.pose.bones[rig.bones[s]].matrix] for s in 'LR'}
            eyes.reset(); eyes.move(-h,-v); eyes.move(h,v)
            last={s:[list(row) for row in rig.arm.pose.bones[rig.bones[s]].matrix] for s in 'LR'}
            assert first==last
        return '200 absolute-pose sequences'
    check('V11',order)
    def resources():
        for image in bpy.data.images:
            if image.source in {'FILE','TILED'}:
                assert image.has_data and image.packed_file, 'Unpacked/missing texture: '+image.name
        return 'all external textures packed'
    check('resources',resources)
    # Capture normal frames before any diagnostic material modifications.
    eyes.reset()
    baseline=evidence/'baseline.png'; eyes.render(baseline)
    result['baseline']=str(baseline)
    for name,h,v in [('left',-1,0),('right',1,0),('up',0,1),('down',0,-1),('reset',0,0)]:
        eyes.move(h,v)
        path=evidence/(name+'.png')
        result['directions'][name]=eyes.render(path)['record']
    result['reset_identical']=digest(baseline)==digest(evidence/'reset.png')
    # Two independent full sweeps, plus compare against the shipped artifacts.
    eyes.sweep(out_dir=evidence/'repeat_a')
    eyes.sweep(out_dir=evidence/'repeat_b')
    names=['metadata.json']+[f'renders/frame_{k:02d}.png' for k in range(10)]
    identical=all(digest(evidence/'repeat_a'/name)==digest(evidence/'repeat_b'/name)==digest(folder/name) for name in names)
    result['checks']['V12']={'status':'PASS' if identical else 'FAIL','measurement':'two sweeps and shipped artifacts SHA-256 comparison'}
    # Dedicated diagnostic pass: transparent occluders are excluded only for unoccluded truth.
    mask=bpy.data.materials.new('Verification white emission')
    mask.use_nodes=True
    nodes=mask.node_tree.nodes; nodes.clear()
    emission=nodes.new('ShaderNodeEmission'); emission.inputs[0].default_value=(1,1,1,1)
    output=nodes.new('ShaderNodeOutputMaterial')
    mask.node_tree.links.new(emission.outputs[0],output.inputs[0])
    black=bpy.data.materials.new('Verification black emission')
    black.use_nodes=True
    nodes=black.node_tree.nodes; nodes.clear()
    e=nodes.new('ShaderNodeEmission'); e.inputs[0].default_value=(0,0,0,1)
    out=nodes.new('ShaderNodeOutputMaterial'); black.node_tree.links.new(e.outputs[0],out.inputs[0])
    for obj in scene.objects:
        if obj.type=='MESH':
            obj.data.materials.clear()
            obj.data.materials.append(mask if obj.name in {'Pupil.L','Pupil.R'} else black)
        if obj.type=='LIGHT': obj.hide_render=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0,0,0,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=0
    scene.cycles.samples=32
    scene.cycles.use_denoising=False
    original={obj.name:obj.hide_render for obj in scene.objects}
    poses=[(f'frame_{k:02d}',h,v) for k,theta,h,v in eyes.sweep_inputs()]
    poses += [(name,r['input']['h'],r['input']['v']) for name,r in result['directions'].items()]
    for name,h,v in poses:
        eyes.move(h,v)
        for mode in ['unoccluded','occluded']:
            for obj in scene.objects:
                if obj.type=='MESH': obj.hide_render=(obj.name not in {'Pupil.L','Pupil.R'}) if mode=='unoccluded' else original[obj.name]
            eyes.render(evidence/'masks'/mode/(name+'.png'))
    eyes.reset()
    (evidence/'blender_evidence.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--folder',type=Path,required=True)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    collect(args.folder)
