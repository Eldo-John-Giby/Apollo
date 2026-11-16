"""Iterative portrait look development: skin relief, optics and contact anatomy."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from gnm_portrait_refine import aim, render, skin_tree, strands

RECIPE_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def new_node(nt,kind,label):
    node=nt.nodes.new(kind);node.label=label;node.name='Peak | '+label
    return node


def wet_material(name,ior=1.376):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    nt=mat.node_tree;nt.nodes.clear()
    glass=new_node(nt,'ShaderNodeBsdfGlass','clear refractive film')
    glass.inputs['Color'].default_value=(1,1,1,1)
    glass.inputs['Roughness'].default_value=.018;glass.inputs['IOR'].default_value=ior
    transparent=new_node(nt,'ShaderNodeBsdfTransparent','transparent shadow approximation')
    path=new_node(nt,'ShaderNodeLightPath','shadow rays')
    mix=new_node(nt,'ShaderNodeMixShader','retain transmitted eye illumination')
    nt.links.new(path.outputs['Is Shadow Ray'],mix.inputs[0])
    nt.links.new(glass.outputs[0],mix.inputs[1]);nt.links.new(transparent.outputs[0],mix.inputs[2])
    out=new_node(nt,'ShaderNodeOutputMaterial','surface');nt.links.new(mix.outputs[0],out.inputs['Surface'])
    return mat


def skin(head,maps):
    nt=head.data.materials[0].node_tree
    shader=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    for node in nt.nodes:
        if node.type=='TEX_IMAGE' and node.image:
            if 'height' in node.name.lower():
                path=maps/'height.1001.png'
                image=bpy.data.images.load(str(path.resolve()),check_existing=False)
                image.colorspace_settings.name='Non-Color';image.pack();node.image=image
                assert bytes(image.packed_file.data)==path.read_bytes()
    shader.inputs['Subsurface Weight'].default_value=.65
    shader.inputs['Subsurface Scale'].default_value=.0011
    shader.inputs['Subsurface Radius'].default_value=(1,.48,.27)
    if shader.inputs.get('Subsurface IOR'):
        shader.inputs['Subsurface IOR'].default_value=1.4
    shader.inputs['Specular IOR Level'].default_value=.5
    rough=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and 'roughness' in n.name)
    remap=new_node(nt,'ShaderNodeMapRange','regional oil and roughness')
    remap.inputs['From Min'].default_value=.32;remap.inputs['From Max'].default_value=.72
    remap.inputs['To Min'].default_value=.28;remap.inputs['To Max'].default_value=.60
    nt.links.new(rough.outputs['Color'],remap.inputs['Value']);nt.links.new(remap.outputs[0],shader.inputs['Roughness'])
    bump=next(n for n in nt.nodes if n.type=='BUMP' and 'physical' in n.name)
    bump.inputs['Distance'].default_value=.00025;bump.inputs['Strength'].default_value=.65
    lip_path=maps/'lip-mask.1001.png'
    if lip_path.exists():
        lip=new_node(nt,'ShaderNodeTexImage','native vermilion mask')
        lip.image=bpy.data.images.load(str(lip_path.resolve()));lip.image.colorspace_settings.name='Non-Color';lip.image.pack()
        uv=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and n!=lip).inputs['Vector'].links[0].from_socket
        nt.links.new(uv,lip.inputs['Vector'])
        gain=new_node(nt,'ShaderNodeMath','satin lip breakup');gain.operation='MULTIPLY';gain.inputs[1].default_value=.09
        nt.links.new(lip.outputs['Color'],gain.inputs[0])
        add=new_node(nt,'ShaderNodeMath','regional satin roughness');add.operation='ADD'
        nt.links.new(remap.outputs[0],add.inputs[0]);nt.links.new(gain.outputs[0],add.inputs[1]);nt.links.new(add.outputs[0],shader.inputs['Roughness'])
        depth=new_node(nt,'ShaderNodeMapRange','lip striation depth')
        depth.inputs['To Min'].default_value=.00025;depth.inputs['To Max'].default_value=.00060
        nt.links.new(lip.outputs[0],depth.inputs[0]);nt.links.new(depth.outputs[0],bump.inputs['Distance'])


def optics(head,maps):
    for ix in [2,4]:
        head.data.materials[ix]=wet_material('Peak | cornea '+str(ix))
    for ix in [1,3]:
        nt=head.data.materials[ix].node_tree
        path=maps/f'color.{1001+ix}.png'
        if path.exists():
            node=next(n for n in nt.nodes if n.type=='TEX_IMAGE')
            node.image=bpy.data.images.load(str(path.resolve()),check_existing=False);node.image.pack()
        p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
        p.inputs['Specular IOR Level'].default_value=.08
        p.inputs['Roughness'].default_value=.42
    s=bpy.context.scene
    s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
    s.cycles.caustics_reflective=False;s.cycles.caustics_refractive=False


def micro_skin(head):
    """Physical-scale pore normals independent of the atlas texel density."""
    nt=head.data.materials[0].node_tree
    p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    old=p.inputs['Normal'].links[0].from_socket
    coords=new_node(nt,'ShaderNodeTexCoord','meter-space microrelief')
    cells=new_node(nt,'ShaderNodeTexVoronoi','irregular 0.3mm follicle spacing')
    cells.feature='F1';cells.inputs['Scale'].default_value=3200
    nt.links.new(coords.outputs['Object'],cells.inputs['Vector'])
    ramp=new_node(nt,'ShaderNodeValToRGB','soft pore depressions')
    ramp.color_ramp.elements[0].position=.07;ramp.color_ramp.elements[0].color=(0,0,0,1)
    ramp.color_ramp.elements[1].position=.28;ramp.color_ramp.elements[1].color=(1,1,1,1)
    nt.links.new(cells.outputs['Distance'],ramp.inputs['Fac'])
    bump=new_node(nt,'ShaderNodeBump','14 micron maximum follicle relief')
    bump.inputs['Distance'].default_value=.000040;bump.inputs['Strength'].default_value=.35
    nt.links.new(ramp.outputs['Color'],bump.inputs['Height']);nt.links.new(old,bump.inputs['Normal'])
    nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])


def contact_anatomy(head,tree):
    wet=wet_material('Peak | tear meniscus',1.336)
    count=0
    for sign in [-1,1]:
        line=[]
        for x0 in np.linspace(.0195,.043,120):
            x=sign*x0;yy=np.linspace(.294,.3025,180)
            hits=[tree.ray_cast(Vector((x,y,.3)),Vector((0,0,-1)))[0] for y in yy]
            zz=np.array([h.z for h in hits]);j=int(np.argmin(np.diff(zz)))
            if zz[j+1]-zz[j]>-.001:continue
            loc,n,_,_=tree.find_nearest(hits[j]);line.append(np.array(loc)+np.array(n)*.000025)
        if not line:continue
        # One smooth, fitted tube with small radius; never a white painted line.
        data=bpy.data.curves.new('Peak tearline '+str(sign),'CURVE');data.dimensions='3D'
        data.bevel_depth=.000065;data.bevel_resolution=2;data.resolution_u=2
        sp=data.splines.new('BEZIER');sp.bezier_points.add(len(line)-1)
        for i,(pt,co) in enumerate(zip(sp.bezier_points,line)):
            pt.co=co;pt.handle_left_type=pt.handle_right_type='AUTO'
            pt.radius=.35+.65*np.sin(np.pi*(i+.5)/len(line))**.5
        ob=bpy.data.objects.new('Peak | lower tear meniscus '+str(sign),data)
        bpy.context.scene.collection.objects.link(ob);ob.matrix_world=head.matrix_world.copy();data.materials.append(wet)
        count+=len(line)
    mat=bpy.data.materials.new('Peak | inner canthus tissue');mat.use_nodes=True
    p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(.27,.095,.078,1)
    p.inputs['Roughness'].default_value=.32;p.inputs['Coat Weight'].default_value=.18
    p.inputs['Subsurface Weight'].default_value=.35;p.inputs['Subsurface Scale'].default_value=.0004
    for sign in [-1,1]:
        loc,n,_,_=tree.ray_cast(Vector((sign*.0188,.3004,.3)),Vector((0,0,-1)))
        if loc is None:continue
        center=np.array(loc)+np.array(n)*.000045
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1)
        ob=bpy.context.object;ob.name='Peak | inner canthus '+str(sign)
        v=np.array([v.co[:] for v in ob.data.vertices])*np.array((.00040,.00055,.00024))+center
        ob.data.vertices.foreach_set('co',v.astype(np.float32).ravel());ob.matrix_world=head.matrix_world.copy()
        for f in ob.data.polygons:f.use_smooth=True
        ob.data.materials.append(mat)
    return count


def hair_variation():
    ob=bpy.data.objects['Portrait | swept chestnut hair'];nt=ob.data.materials[0].node_tree
    shader=next(n for n in nt.nodes if n.type=='BSDF_HAIR_PRINCIPLED')
    info=new_node(nt,'ShaderNodeHairInfo','individual strand variation')
    remap=new_node(nt,'ShaderNodeMapRange','brown strand diversity')
    remap.inputs['To Min'].default_value=.68;remap.inputs['To Max'].default_value=1.3
    nt.links.new(info.outputs['Random'],remap.inputs[0])
    scale=new_node(nt,'ShaderNodeVectorMath','melanin variation');scale.operation='SCALE'
    scale.inputs[0].default_value=(1.25,2.10,3.10)
    nt.links.new(remap.outputs[0],scale.inputs['Scale']);nt.links.new(scale.outputs[0],shader.inputs['Absorption Coefficient'])
    rough=new_node(nt,'ShaderNodeMapRange','strand roughness diversity')
    rough.inputs['To Min'].default_value=.29;rough.inputs['To Max'].default_value=.43
    nt.links.new(info.outputs['Random'],rough.inputs[0]);nt.links.new(rough.outputs[0],shader.inputs['Roughness'])
    data=ob.data;buf=np.empty(len(data.points)*3,dtype=np.float32)
    data.attributes['position'].data.foreach_get('vector',buf);p=buf.reshape(-1,12,3)
    rng=np.random.default_rng(27011);mask=rng.random(len(p))<.14
    t=np.linspace(0,1,12);amp=rng.uniform(.0002,.0014,(mask.sum(),1))
    p[mask,:,0]+=(amp*np.sin(np.pi*t)[None,:]).astype(np.float32)
    p[mask,:,1]+=(amp*.45*np.sin(np.pi*t)[None,:]).astype(np.float32)
    data.attributes['position'].data.foreach_set('vector',p.ravel())


def vellus(head,co):
    """Sparse, short translucent facial fibers; exclude orifices and brows."""
    tri=[]
    for f in head.data.polygons:
        if f.material_index==0:
            v=list(f.vertices);tri.extend([(v[0],v[1],v[2]),(v[0],v[2],v[3])])
    tri=np.array(tri);q=co[tri];centers=q.mean(1)
    n=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);area=np.linalg.norm(n,axis=1)
    n/=np.maximum(area[:,None],1e-12)
    x,y,z=centers.T
    valid=(y>.214)&(y<.380)&(abs(x)<.074)&(z>.035)&(n[:,2]>.40)
    valid&=~(((abs(x)-.031)/.025)**2+((y-.305)/.022)**2<1)
    valid&=~((abs(x)<.031)&(abs(y-.235)<.018))
    valid&=~((abs(x)<.018)&(y>.252)&(y<.283))
    tri,n,area=tri[valid],n[valid],area[valid]
    rng=np.random.default_rng(3711);idx=rng.choice(len(tri),10000,p=area/area.sum())
    w=rng.random((len(idx),2));w=np.where((w.sum(1)>1)[:,None],1-w,w)
    w=np.column_stack((1-w.sum(1),w));roots=(co[tri[idx]]*w[...,None]).sum(1)
    normal=n[idx].copy();tree=skin_tree(head,co)
    # Match Blender's evaluated surface triangulation, including non-planar
    # quads whose alternate diagonal would leave short fibers floating.
    for i,root in enumerate(roots):
        loc,nor,_,_=tree.find_nearest(Vector(root));roots[i]=loc;normal[i]=nor
    down=np.broadcast_to(np.array((0.,-1.,0.)),normal.shape).copy()
    down-=normal*(down*normal).sum(1)[:,None];down/=np.maximum(np.linalg.norm(down,axis=1)[:,None],1e-8)
    t=np.linspace(0,1,4);length=rng.uniform(.00025,.00065,len(idx))
    points=(roots[:,None,:]+normal[:,None,:]*(.000008+.48*length[:,None]*t)[...,None]
            +down[:,None,:]*(.55*length[:,None]*t)[...,None])
    radii=rng.uniform(.000003,.000006,len(idx))[:,None]*(1-.94*t)[None,:]
    mat=bpy.data.materials.new('Peak | fine vellus');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear()
    p=new_node(nt,'ShaderNodeBsdfHairPrincipled','translucent fine facial fibers');p.parametrization='COLOR'
    p.inputs['Color'].default_value=(.23,.16,.10,1);p.inputs['Roughness'].default_value=.60
    out=new_node(nt,'ShaderNodeOutputMaterial','surface');nt.links.new(p.outputs[0],out.inputs['Surface'])
    strands('Peak | facial vellus',head,points,radii,mat)
    return len(idx)


def orbital_folds(head):
    """Fit soft upper-lid folds to the actual opening, on a reversible key."""
    ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    co=np.array([v.co[:] for v in mesh.vertices]);normal=np.array([v.normal[:] for v in mesh.vertices]);ev.to_mesh_clear()
    tree=skin_tree(head,co);delta=np.zeros_like(co)
    skin_ids=np.array(sorted({i for f in head.data.polygons if f.material_index==0 for i in f.vertices}))
    for sign in [-1,1]:
        xx=np.linspace(.020,.0425,80);upper=[];lower=[]
        for x0 in xx:
            yy=np.linspace(.294,.310,241)
            hits=[tree.ray_cast(Vector((sign*x0,y,.3)),Vector((0,0,-1)))[0] for y in yy]
            zz=np.array([h.z for h in hits]);upper.append(yy[np.argmax(np.diff(zz))+1]);lower.append(yy[np.argmin(np.diff(zz))])
        p=co[skin_ids];x,y,z=p.T
        center=np.interp(sign*x,xx,upper)+.0023
        below=np.interp(sign*x,xx,lower)-.0027
        taper=np.exp(-((sign*x-.031)/.012)**6)
        front=np.clip((z-.085)/.020,0,1)*(sign*x>0)
        crease=-.00025*np.exp(-((y-center)/.00085)**2)
        roll=.00010*np.exp(-((y-center+.0013)/.0010)**2)
        lower_fold=-.00009*np.exp(-((y-below)/.0011)**2)
        depth=(crease+roll+lower_fold)*taper*front*(.94 if sign==1 else 1.0)
        delta[skin_ids]+=normal[skin_ids]*depth[:,None]
    basis=np.array([p.co[:] for p in head.data.shape_keys.key_blocks[0].data])
    key=head.shape_key_add(name='Peak | fitted orbital anatomy')
    key.data.foreach_set('co',(basis+delta).astype(np.float32).ravel());key.value=1
    return float(np.linalg.norm(delta,axis=1).max()*1000)


def main(a):
    a.out.mkdir(parents=True,exist_ok=True);source=Path(bpy.data.filepath)
    head=bpy.context.scene.objects['GNM Head'];s=bpy.context.scene
    skin(head,a.maps);optics(head,a.maps);hair_variation()
    if a.micro_skin:micro_skin(head)
    fold_mm=orbital_folds(head) if a.orbital_folds else 0
    ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    co=np.array([v.co[:] for v in me.vertices]);ev.to_mesh_clear()
    contacts=contact_anatomy(head,skin_tree(head,co))
    vellus_count=vellus(head,co)
    s.cycles.device='CPU';s.cycles.samples=128
    bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str((a.out/'portrait.blend').resolve()),compress=True)
    camera=s.camera
    aim(camera,(0,-.55,.018),(0,0,-.010));camera.data.lens=115
    render(s,a.out,'detail',1000,48)
    if not a.detail_only:
        aim(camera,(0,-.82,.03),(0,0,-.025));camera.data.lens=85
        render(s,a.out,'front',1000,48)
        aim(camera,(.40,-.72,.03),(0,0,-.025));camera.data.lens=85
        render(s,a.out,'three-quarter',1000,48)
    if a.grazing:
        aim(camera,(0,-.55,.018),(0,0,-.010));camera.data.lens=115
        light=s.objects['Key'];aim(light,(-.35,-.15,.10),(0,0,-.01));light.data.size=.12;light.data.energy=7
        s.objects['Fill'].data.energy=.65;s.objects['Rim'].data.energy=1.2
        render(s,a.out,'grazing-detail',1000,64)
    if a.micro_skin:
        aim(camera,(.025,-.53,-.01),(.025,0,-.033));camera.data.lens=180
        render(s,a.out,'skin-macro',1024,96)
    height=next(n.image for n in head.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and 'height' in n.name.lower())
    report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'recipe_sha256':RECIPE_SHA256,'scene_sha256':hashlib.sha256((a.out/'portrait.blend').read_bytes()).hexdigest(),'height_payload_sha256':hashlib.sha256(bytes(height.packed_file.data)).hexdigest(),'height_payload_bytes':height.packed_file.size,'tearline_samples':contacts,'vellus_strands':vellus_count,'orbital_fold_mm':fold_mm,'micro_skin':a.micro_skin,'status':'unqualified realism look-development candidate'}
    (a.out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+json.dumps(report),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--maps',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--orbital-folds',action='store_true')
    p.add_argument('--grazing',action='store_true')
    p.add_argument('--micro-skin',action='store_true')
    p.add_argument('--detail-only',action='store_true')
    main(p.parse_args(sys.argv[sys.argv.index('--')+1:]))
