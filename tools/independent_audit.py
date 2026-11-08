"""Disposable Blender audit of actual deformed geometry against an independent oracle."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'wrapper'))
from reference_geometry import reference,fit_sphere,surface_centroid
import eyes
LIGHTING_BASELINE=None


def lighting_signature():
    lights=[]
    for obj in sorted(bpy.context.scene.objects,key=lambda o:o.name):
        if obj.type=='LIGHT':
            lights.append((obj.name,[list(row) for row in obj.matrix_world],obj.data.energy,list(obj.data.color),obj.hide_render))
    world=bpy.context.scene.world
    nodes=[]
    if world and world.use_nodes:
        for node in world.node_tree.nodes:
            for socket in node.inputs:
                if hasattr(socket,'default_value'):
                    value=socket.default_value
                    try:value=list(value)
                    except TypeError:pass
                    nodes.append((node.type,socket.name,value))
    return json.dumps([lights,nodes,bpy.context.scene.view_settings.exposure,bpy.context.scene.view_settings.gamma],sort_keys=True)


def points(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh()
    try:
        vertices=np.array([list(evaluated.matrix_world@v.co) for v in mesh.vertices])
        mesh.calc_loop_triangles()
        triangles=[list(t.vertices) for t in mesh.loop_triangles]
        return vertices,triangles
    finally:evaluated.to_mesh_clear()


def check(h,v,record=None,swap=False):
    scene=bpy.context.scene
    assert np.linalg.norm(np.array(scene.camera.matrix_world.translation)-[0,-.4,0])<1e-7,'camera distance'
    assert abs(scene.camera.data.lens-100)<1e-6,'camera lens'
    assert scene.camera.data.sensor_fit=='HORIZONTAL','sensor fit'
    assert abs(scene.camera.data.sensor_width-36)<1e-6,'sensor width'
    assert np.allclose(np.array(scene.camera.matrix_world.to_3x3()),[[1,0,0],[0,0,-1],[0,1,0]],atol=1e-6),'camera orientation'
    assert scene.render.resolution_x==scene.render.resolution_y==1024 and scene.render.resolution_percentage==100,'resolution'
    assert scene.camera.data.shift_x==scene.camera.data.shift_y==0,'camera shift'
    assert scene.render.pixel_aspect_x==scene.render.pixel_aspect_y,'pixel aspect'
    if LIGHTING_BASELINE is not None:assert lighting_signature()==LIGHTING_BASELINE,'lighting changed'
    for material in bpy.data.materials:
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type=='TEX_IMAGE':
                    assert node.image is not None,'missing referenced texture'
                    assert len(node.image.pixels)>0 and node.image.packed_file,'unpacked/missing image pixels'
    centers={}
    for side in 'LR':
        label=({'L':'R','R':'L'}[side] if swap else side)
        sphere,_=points(bpy.data.objects['Sclera.'+label]);center,radius=fit_sphere(sphere)
        centers[side]=center
        assert center[0]*(1 if side=='L' else -1)>0,'anatomical eye mapping'
        assert abs(radius-.012)<.00005,'sphere radius'
    ipd=np.linalg.norm(centers['L']-centers['R'])
    assert .058<=ipd<=.068,'eye spacing'
    maxima={'pupil_world_m':0.,'surface_world_m':0.,'annotation_px':0.}
    for side in 'LR':
        expected=reference(side,h,v,ipd=ipd)
        assert np.linalg.norm(centers[side]-expected['center'])<1e-6,'physical center'
        obj=bpy.data.objects['Pupil.'+side];vertices,triangles=points(obj)
        measured=surface_centroid(vertices,triangles)
        residual=float(np.linalg.norm(measured-expected['pupil']))
        assert residual<1e-6,f'pupil surface convergence: {residual}'
        rest=np.array([list(obj.matrix_world@vert.co) for vert in obj.data.vertices])
        predicted=(expected['rotation']@(rest-expected['center']).T).T+expected['center']
        surface_error=float(np.max(np.linalg.norm(vertices-predicted,axis=1)))
        assert surface_error<1e-6,f'spherical rotation: {surface_error}'
        maxima['pupil_world_m']=max(maxima['pupil_world_m'],residual)
        maxima['surface_world_m']=max(maxima['surface_world_m'],surface_error)
        if record is not None:
            error=float(np.linalg.norm(expected['pixel']-record['pupil_center_2D_'+side]))
            assert error<.001,f'annotation projection: {error}'
            maxima['annotation_px']=max(maxima['annotation_px'],error)
    return maxima


def run(output,count):
    global LIGHTING_BASELINE
    source=Path(bpy.data.filepath);scene=bpy.context.scene
    LIGHTING_BASELINE=lighting_signature()
    rng=random.Random(20261107)
    poses=[(h,v) for h in [-1.,0.,1.] for v in [-1.,0.,1.]]+[(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(count)]
    maximum={'pupil_world_m':0.,'surface_world_m':0.,'annotation_px':0.}
    for h,v in poses:
        record=eyes.move(h,v)
        for key,value in check(h,v,record).items():maximum[key]=max(maximum[key],value)
    mutations={}
    def reject(name,action):
        try:action()
        except (AssertionError,ValueError) as exc:mutations[name]={'detected':True,'reason':str(exc)}
        else:mutations[name]={'detected':False}
    def wrong_command(h,v):eyes.move(h,v);check(.7,.4)
    reject('reversed_horizontal',lambda:wrong_command(-.7,.4))
    reject('reversed_vertical',lambda:wrong_command(.7,-.4))
    reject('disabled_movement',lambda:wrong_command(0,0))
    reject('wrong_target_bounds',lambda:wrong_command(.35,.2))
    eyes.move(.7,.4);reject('swapped_anatomical_labels',lambda:check(.7,.4,swap=True))
    camera=scene.camera
    original=camera.location.copy();camera.location.y=-.3;bpy.context.view_layer.update()
    reject('wrong_camera_distance',lambda:check(.7,.4));camera.location=original
    lens=camera.data.lens;camera.data.lens=85
    reject('wrong_lens',lambda:check(.7,.4));camera.data.lens=lens
    rotation=camera.rotation_euler.copy();camera.rotation_euler.z+=.1;bpy.context.view_layer.update()
    reject('wrong_camera_orientation',lambda:check(.7,.4));camera.rotation_euler=rotation
    eyes.move(.7,.4)
    bone=eyes._rig().arm.pose.bones['eye.R'];original=bone.matrix.copy();bone.matrix_basis.identity();bpy.context.view_layer.update()
    reject('one_eye_disabled',lambda:check(.7,.4));bone.matrix=original
    eyes.move(.7,.4)
    bone=eyes._rig().arm.pose.bones['eye.L'];original=bone.matrix.copy();matrix=original.copy();matrix.translation.x+=.003;bone.matrix=matrix;bpy.context.view_layer.update()
    reject('displaced_rotation_pivot',lambda:check(.7,.4));bone.matrix=original
    record=eyes.move(.7,.4);record['pupil_center_2D_L'][0]+=5
    reject('bad_annotation',lambda:check(.7,.4,record))
    pupil=bpy.data.objects['Pupil.L'];original=pupil.location.copy();pupil.location.x+=.003;bpy.context.view_layer.update()
    reject('displaced_pupil_geometry',lambda:check(.7,.4));pupil.location=original
    eyes.move(.7,.4)
    material=next(m for m in bpy.data.materials if m.use_nodes and any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes))
    node=next(n for n in material.node_tree.nodes if n.type=='TEX_IMAGE');image=node.image;node.image=None
    reject('missing_texture_reference',lambda:check(.7,.4));node.image=image
    light=bpy.data.objects['Key'].data;energy=light.energy;light.energy*=1.1
    reject('changed_lighting',lambda:check(.7,.4));light.energy=energy
    eyes.reset()
    report={'passed':all(x['detected'] for x in mutations.values()),'blender':bpy.app.version_string,'poses':len(poses),'maxima':maximum,'mutations':mutations,'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,ROOT/'wrapper/eyes.py',Path(__file__),ROOT/'tools/reference_geometry.py']},'limits':'Geometry/projection audit only; image visibility, lighting and archive checks remain separate.'}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2));assert report['passed'],'Undetected injected defect'


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--random',type=int,default=100)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);run(args.out,args.random)
