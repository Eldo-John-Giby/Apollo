"""Render the isolated owner-review trial; never replaces qualified artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0,str(Path(__file__).resolve().parent))
import gnm_texture_trial as base


def smooth(v):
    v=np.clip(v,0,1);return v*v*(3-2*v)


def density(p):
    x,y,z=p.T
    front=smooth((z+.10)/.07)
    side=smooth((abs(x)-.047)/.035)
    line=-.025+front*(.095-.055*side)
    return smooth((y-line)/.007)


def hair(head, count=50000):
    vertices=np.array([v.co[:] for v in head.data.vertices],dtype=float)
    normals=np.array([v.normal[:] for v in head.data.vertices],dtype=float)
    # GNM's native eye midpoint defines the surface-space scalp field used
    # by the exported pigment mask. Receiver topology stays untouched.
    # Exact joint midpoint is provided by the pinned template, not inferred
    # from the visible eyeball surface's center of mass.
    with np.load(ARGS.template,allow_pickle=False) as data:
        ids=[list(data['joint_names']).index(s+'_eye') for s in ['left','right']]
        midpoint=data['joints'][ids].mean(axis=0)
    p=vertices-midpoint
    triangles=[]
    for polygon in head.data.polygons:
        if polygon.material_index!=0:continue
        ids=list(polygon.vertices)
        for ix in [(0,1,2),(0,2,3)]:
            triangle=[ids[i] for i in ix]
            if density(p[triangle]).max()>.01:triangles.append(triangle)
    triangles=np.asarray(triangles)
    xyz=vertices[triangles]
    area=np.linalg.norm(np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0]),axis=1)
    rng=np.random.default_rng(20261116)
    choices=rng.choice(len(triangles),count*2,p=area/area.sum())
    uv=rng.uniform(size=(count*2,2));uv=np.where((uv.sum(axis=1)>1)[:,None],1-uv,uv)
    weights=np.column_stack((1-uv.sum(axis=1),uv))
    ids=triangles[choices]
    roots=np.sum(vertices[ids]*weights[...,None],axis=1)
    n=np.sum(normals[ids]*weights[...,None],axis=1);n/=np.linalg.norm(n,axis=1)[:,None]
    keep=rng.random(len(roots))<density(roots-midpoint)
    roots,n=roots[keep][:count],n[keep][:count]
    data=bpy.data.curves.new('GNM short scalp strands','CURVE');data.dimensions='3D'
    data.resolution_u=1;data.bevel_depth=.000037;data.bevel_resolution=0;data.resolution_u=1
    for value in [.7,.9,1.1,1.3]:
        material=bpy.data.materials.new(f'Natural hair {value}');material.use_nodes=True
        nodes=material.node_tree.nodes;nodes.clear()
        shader=nodes.new('ShaderNodeBsdfHairPrincipled');shader.parametrization='COLOR'
        shader.inputs['Color'].default_value=(.032*value,.017*value,.009*value,1)
        shader.inputs['Roughness'].default_value=.38
        output=nodes.new('ShaderNodeOutputMaterial');material.node_tree.links.new(shader.outputs[0],output.inputs['Surface'])
        data.materials.append(material)
    direction=np.array((.08,-.18,-1.))
    for i,(root,normal) in enumerate(zip(roots,n)):
        tangent=direction-normal*np.dot(direction,normal)
        if np.linalg.norm(tangent)<1e-5:tangent=np.array((1.,0.,0.))
        tangent/=np.linalg.norm(tangent)
        length=rng.uniform(.007,.017)
        spline=data.splines.new('POLY');spline.points.add(6);spline.material_index=i%4
        phase=rng.uniform(0,2*np.pi)
        across=np.cross(normal,tangent)
        for j,point in enumerate(spline.points):
            t=j/6
            position=(root+normal*(.00015+length*(.37*np.sin(np.pi*t*.8)))
                      +tangent*length*t*.85+across*.00035*np.sin(t*4+phase)*t)
            point.co=(*position,1);point.radius=(1-t)**.75*.85+.025
    obj=bpy.data.objects.new('GNM optional short hair',data);bpy.context.scene.collection.objects.link(obj)
    obj.matrix_world=head.matrix_world.copy()
    return len(roots)


def natural_bind(head,maps,layout):
    before=np.array([v.co[:] for v in head.data.vertices])
    ORIGINAL_BIND(head,maps,layout)
    skin=head.data.materials[0].node_tree.nodes.get('Principled BSDF')
    skin.inputs['Subsurface Weight'].default_value=.018
    skin.inputs['Specular IOR Level'].default_value=.22
    for tile in [1002,1004]:
        eye=head.data.materials[tile-1001].node_tree.nodes.get('Principled BSDF')
        eye.inputs['Specular IOR Level'].default_value=.02;eye.inputs['Roughness'].default_value=.65
    for tile in [1003,1005]:
        nodes=head.data.materials[tile-1001].node_tree.nodes
        for node in nodes:
            if node.type=='MIX_SHADER':node.inputs[0].default_value=.018
            if node.type in ('BSDF_GLOSSY','BSDF_ANISOTROPIC'):node.inputs['Roughness'].default_value=.11
    if not ARGS.no_hair:
        bpy.context.scene['natural_trial_hair_strands']=hair(head)
    np.testing.assert_array_equal(before,np.array([v.co[:] for v in head.data.vertices]))


def receipt(output,args,scene):
    ORIGINAL_RECEIPT(output,args,scene)
    p=output.with_suffix('.render.json');r=json.loads(p.read_text(encoding='utf-8'))
    head=scene.objects['GNM Head']
    with np.load(ARGS.template,allow_pickle=False) as data:
        pupil={}
        for side in ['left','right']:
            indices=np.flatnonzero(data['pupils']&data[side+'_eye'])
            center=np.mean([head.data.vertices[int(i)].co[:] for i in indices],axis=0)
            projected=world_to_camera_view(scene,scene.camera,head.matrix_world@Vector(center))
            pupil[side]=[projected.x*scene.render.resolution_x,(1-projected.y)*scene.render.resolution_y]
    r.update({'status':'unqualified_appearance_trial','experimental_recipe_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'hair_strands':scene.get('natural_trial_hair_strands',0),'groom_preserves_head_positions':True,'native_pose':ARGS.pose_name if ARGS.poses else 'neutral template','pupils_px':pupil,'feedback_case':'A01'})
    p.write_bytes((json.dumps(r,indent=2)+'\n').encode())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maps',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--template',type=Path,required=True);parser.add_argument('--no-hair',action='store_true')
    parser.add_argument('--eye-crop',action='store_true')
    parser.add_argument('--poses',type=Path);parser.add_argument('--pose-name',default='center')
    parser.add_argument('--layout',choices=['udim','legacy'],default='udim')
    parser.add_argument('--angle',action='store_true');parser.add_argument('--side-light',action='store_true')
    parser.add_argument('--size',type=int,default=1024);parser.add_argument('--samples',type=int,default=32)
    parser.add_argument('--lens',type=float,default=64)
    ARGS=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    ARGS.target=None;ARGS.save_scene=None;ARGS.save_only=False;ARGS.frame=None
    if ARGS.poses:
        with np.load(ARGS.poses,allow_pickle=False) as data:
            coordinates=data[ARGS.pose_name]
        head=bpy.context.scene.objects['GNM Head']
        if coordinates.shape!=(len(head.data.vertices),3):raise ValueError('Native pose vertex count differs')
        head.data.vertices.foreach_set('co',coordinates.ravel());head.data.update()
    ORIGINAL_BIND=base.bind_surface;ORIGINAL_RECEIPT=base.render_receipt
    base.bind_surface=natural_bind;base.render_receipt=receipt
    base.render(ARGS)
