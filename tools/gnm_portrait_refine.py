"""Build and inspect a reversible still-portrait candidate from current-work.blend.

Run in factory-startup Blender 4.5+. Never overwrites the supplied source scene.
The groom is a static portrait groom, not a qualified motion asset.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def smooth(a):
    a=np.clip(a,0,1); return a*a*(3-2*a)


def aim(obj, position, target):
    obj.location=position
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def skin_tree(head, co):
    faces=[list(f.vertices) for f in head.data.polygons if f.material_index==0]
    return BVHTree.FromPolygons([Vector(p) for p in co],faces,all_triangles=False)


def sculpt(head):
    co=np.array([v.co[:] for v in head.data.vertices])
    ids=np.array(sorted({i for f in head.data.polygons if f.material_index==0 for i in f.vertices}))
    p=co[ids];x,y,z=p.T
    delta=np.zeros_like(p)
    def field(cx,cy,cz,rx,ry,rz):
        return np.exp(-((abs(x)-cx)/rx)**2-((y-cy)/ry)**2-((z-cz)/rz)**2)
    # Soft tissue over zygoma and masseter; no planar cuts or global smoothing.
    cheek=field(.047,.281,.092,.019,.014,.035)
    hollow=field(.046,.255,.097,.020,.019,.030)
    jaw=field(.058,.214,.065,.017,.019,.043)
    chin=field(0,.194,.105,.025,.016,.023)
    delta[:,0]+=np.sign(x)*(.0015*cheek+.0024*jaw-.00035*hollow)
    delta[:,2]+=.0014*cheek-.0010*hollow+.0020*chin+.00045*jaw
    nose=field(.014,.261,.130,.006,.010,.019)
    delta[:,0]-=np.sign(x)*.00065*nose
    # Preserve complete orbital geometry: sculpt tapers out before the lid rims.
    orbital=np.exp(-((abs(x)-.031)/.023)**6-((y-.303)/.014)**6)
    delta*=1-orbital[:,None]
    upper_lid=field(.031,.3062,.114,.013,.0017,.004)
    delta[:,1]+=.00045*upper_lid
    head.shape_key_add(name='Basis')
    key=head.shape_key_add(name='Portrait | cheek jaw nose refinement')
    target=co.copy();target[ids]+=delta
    key.data.foreach_set('co',target.astype(np.float32).ravel());key.value=1
    asym=head.shape_key_add(name='Portrait | subtle living asymmetry')
    offset=np.zeros_like(co)
    offset[ids,2]=.00020*np.exp(-((x-.035)/.022)**2-((y-.276)/.025)**2-((z-.10)/.035)**2)
    offset[ids,1]=.00018*np.exp(-((x+.022)/.010)**2-((y-.232)/.010)**2-((z-.12)/.016)**2)
    asym.data.foreach_set('co',(co+offset).astype(np.float32).ravel());asym.value=1
    return co,target+offset,{'max_sculpt_mm':float(np.linalg.norm(delta,axis=1).max()*1000),'max_asymmetry_mm':float(np.linalg.norm(offset,axis=1).max()*1000)}


def fiber_material(name, value=1):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    nodes=mat.node_tree.nodes;nodes.clear()
    shader=nodes.new('ShaderNodeBsdfHairPrincipled');shader.parametrization='ABSORPTION'
    # Real hair curves supply a strand tangent; beveled mesh tubes did not.
    shader.inputs['Absorption Coefficient'].default_value=(1.25/value,2.10/value,3.1/value)
    shader.inputs['Roughness'].default_value=.34
    shader.inputs['Radial Roughness'].default_value=.42
    output=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(shader.outputs[0],output.inputs['Surface'])
    return mat


def strands(name, head, points, radii, material):
    data=bpy.data.hair_curves.new(name)
    data.add_curves([points.shape[1]]*len(points))
    data.attributes['position'].data.foreach_set('vector',points.astype(np.float32).ravel())
    radius=data.attributes.get('radius') or data.attributes.new('radius','FLOAT','POINT')
    radius.data.foreach_set('value',radii.astype(np.float32).ravel())
    ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world=head.matrix_world.copy();ob.data.materials.append(material)
    ob['portrait_static_groom']=True
    return ob


def groom(head, co, tree):
    rng=np.random.default_rng(20261117)
    old=bpy.data.objects.get('GNM optional short hair')
    if old: old.hide_render=True;old.hide_set(True)
    triangles=[]
    for f in head.data.polygons:
        if f.material_index==0:
            v=list(f.vertices);triangles.extend([(v[0],v[1],v[2]),(v[0],v[2],v[3])])
    tri=np.asarray(triangles);xyz=co[tri]
    normals=np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0])
    area=np.linalg.norm(normals,axis=1);normals/=np.maximum(area[:,None],1e-12)
    midpoint=np.array((0,.303139,.098933))
    centers=xyz.mean(1)-midpoint
    eligible=centers[:,1]>.005
    tri,area,normals=tri[eligible],area[eligible],normals[eligible]
    choice=rng.choice(len(tri),400000,p=area/area.sum())
    w=rng.random((len(choice),2));w=np.where((w.sum(1)>1)[:,None],1-w,w)
    w=np.column_stack((1-w.sum(1),w));roots=(co[tri[choice]]*w[...,None]).sum(1)
    n=normals[choice];p=roots-midpoint;x,y,z=p.T
    front=smooth((z+.10)/.07);side=smooth((abs(x)-.047)/.035)
    line=-.025+front*(.095-.055*side)
    irregular=.0010*np.sin(x*630)+.00055*np.sin(x*1700+z*700)
    density=smooth((y-line+.0022+irregular)/.008)
    keep=(rng.random(len(roots))<density)&(y>-.012)
    roots,n,p=roots[keep][:48000],n[keep][:48000],p[keep][:48000]
    top=smooth((p[:,1]-.035)/.045)
    length=rng.uniform(.008,.016,len(p))*(1-top)+rng.uniform(.043,.068,len(p))*top
    flow=np.column_stack(((.8+.18*np.sin(p[:,0]*180))*top+.08*(1-top),-.65*(1-top),-np.ones(len(p))))
    tangent=flow-n*(flow*n).sum(1)[:,None];tangent/=np.linalg.norm(tangent,axis=1)[:,None]
    across=np.cross(n,tangent)
    t=np.linspace(0,1,12)
    points=roots[:,None,:]+t[None,:,None]*length[:,None,None]*tangent[:,None,:]
    # Follow the actual scalp, then lift an arc. Every tip stays outside skin.
    flat=points.reshape(-1,3)
    hit=np.empty_like(flat);normal=np.empty_like(flat)
    for i,v in enumerate(flat):
        loc,nor,_,_=tree.find_nearest(Vector(v));hit[i]=loc;normal[i]=nor
    clump=.78+.22*np.sin(p[:,0]*900+p[:,2]*270)
    lift=.00008+(.0014+.020*top[:,None])*clump[:,None]*(np.sin(np.pi*t)[None,:]**.85)
    lift+=.00035*(t[None,:]**2)
    points=hit.reshape(points.shape)+normal.reshape(points.shape)*lift[...,None]
    phase=p[:,0]*700+p[:,2]*300+rng.normal(0,.2,len(p))
    wave=np.sin(phase[:,None]+t[None,:]*5)*np.sin(np.pi*t)[None,:]
    points+=across[:,None,:]*wave[...,None]*.0011
    radius=rng.uniform(.000025,.000037,len(p))[:,None]*(1-.96*t[None,:])**.7
    hair=strands('Portrait | swept chestnut hair',head,points,radius,fiber_material('Portrait chestnut hair'))
    # Brows: short rising medial hairs flow outward and flatten into tapered tails.
    brows=[];br=[];miss=0
    for sign in [-1,1]:
        for i in range(950):
            u=rng.beta(1.3,1.5);x=sign*(.014+.040*u)
            y=.303139+.0135+.004*np.sin(np.pi*u)-.002*u*u
            y+=rng.normal(0,.00135)*(1-.65*u*u)+(.0003 if sign==1 else 0)
            root,nor,_,_=tree.ray_cast(Vector((x,y,.3)),Vector((0,0,-1)))
            if root is None:miss+=1;continue
            length=rng.uniform(.0015,.0032)*(1-.25*u)
            direction=Vector((sign*(.25+.75*u),.85-1.05*u,0)).normalized()
            row=[]
            for t0 in np.linspace(0,1,6):
                q=root+direction*length*t0
                loc,n0,_,_=tree.ray_cast(Vector((q.x,q.y,.3)),Vector((0,0,-1)))
                if loc is None:loc,n0=root,nor
                row.append(np.array(loc)+np.array(n0)*(.00005+.00024*np.sin(t0*np.pi*.9)))
            brows.append(row);br.append(rng.uniform(.000023,.000039)*(1-.94*np.linspace(0,1,6))**.7)
    brow=strands('Portrait | fitted directional brows',head,np.array(brows),np.array(br),fiber_material('Portrait brown brow fibers',.72))
    # Detect the actual upper lid silhouette from the anterior ray depth jump.
    lashes=[];lr=[]
    for sign in [-1,1]:
        for x0 in np.linspace(.021,.042,72):
            x=sign*(x0+rng.normal(0,.00009))
            yy=np.linspace(.300,.309,181)
            hits=[tree.ray_cast(Vector((x,y0,.3)),Vector((0,0,-1)))[0] for y0 in yy]
            zz=np.array([v.z for v in hits]);j=int(np.argmax(np.diff(zz)))+1
            if zz[j]-zz[j-1]<.001:continue
            root=np.array(hits[j]);length=rng.uniform(.0015,.0031)
            row=[]
            for t0 in np.linspace(0,1,6):
                row.append(root+np.array((sign*.3*length*t0,length*(.18*t0+.35*t0*t0),length*.8*t0)))
            lashes.append(row);lr.append(.000018*(1-.96*np.linspace(0,1,6)))
    strands('Portrait | subtle upper lashes',head,np.array(lashes),np.array(lr),fiber_material('Portrait lash brown',.55))
    return {'scalp_strands':len(roots),'brow_strands':len(brows),'lash_strands':len(lashes),'brow_missed_rays':miss,'scalp_points':int(points.size/3),'static_only':True}


def materials(head,maps):
    mat=head.data.materials[0];nt=mat.node_tree
    shader=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    for node in nt.nodes:
        if node.type=='TEX_IMAGE' and node.image:
            name=Path(node.image.filepath.replace('\\','/')).name or node.image.name
            path=maps/name
            if path.is_file():
                image=bpy.data.images.load(str(path.resolve()),check_existing=False)
                image.colorspace_settings.name='sRGB' if name.startswith('color') else 'Non-Color'
                image.pack();node.image=image
    shader.inputs['Specular IOR Level'].default_value=.36
    shader.inputs['Subsurface Weight'].default_value=.065
    shader.inputs['Subsurface Scale'].default_value=.0012
    shader.inputs['Subsurface Radius'].default_value=(1,.45,.25)
    for node in nt.nodes:
        if node.type=='BUMP':
            node.inputs['Strength'].default_value=.35 if 'physical' in node.name else .10
            node.inputs['Distance'].default_value=.00008 if 'physical' in node.name else .000025
    for ix in [1,3]:
        shader=next(n for n in head.data.materials[ix].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        shader.inputs['Roughness'].default_value=.38
        shader.inputs['Specular IOR Level'].default_value=.12
    for ix in [2,4]:
        for node in head.data.materials[ix].node_tree.nodes:
            if node.type=='MIX_SHADER':node.inputs[0].default_value=.026
            if node.type in ['BSDF_GLOSSY','BSDF_ANISOTROPIC']:node.inputs['Roughness'].default_value=.075


def render(scene,out,name,size=768,samples=32):
    scene.render.resolution_x=scene.render.resolution_y=size;scene.render.resolution_percentage=100
    scene.cycles.samples=samples;scene.cycles.use_denoising=True
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str((out/(name+'.png')).resolve())
    bpy.ops.render.render(write_still=True)
    print('RENDER '+name,flush=True)


def main(a):
    source=Path(bpy.data.filepath).resolve()
    if source==a.out.resolve()/'portrait.blend':raise ValueError('Build from original scene')
    a.out.mkdir(parents=True,exist_ok=True)
    scene=bpy.context.scene;head=scene.objects['GNM Head']
    source_uv={uv.name:np.array([v.uv[:] for v in uv.data]) for uv in head.data.uv_layers}
    original,co,sculpt_report=sculpt(head)
    groom_report=groom(head,co,skin_tree(head,co))
    materials(head,a.maps)
    protected=sorted({i for f in head.data.polygons if f.material_index in [1,2,3,4] for i in f.vertices})
    assert np.array_equal(original[protected],co[protected])
    for uv in head.data.uv_layers:
        np.testing.assert_array_equal(source_uv[uv.name],np.array([v.uv[:] for v in uv.data]))
    head['portrait_refinement']='Reversible shape keys; native eye vertices and UVs unchanged'
    scene['portrait_status']='Unqualified still appearance candidate'
    scene.cycles.device='CPU';scene.cycles.samples=64
    scene.render.resolution_x=scene.render.resolution_y=1200
    scene.render.resolution_percentage=100
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str((a.out/'portrait.blend').resolve()))
    report={'source':str(source),'source_sha256':digest(source),'scene_sha256':digest(a.out/'portrait.blend'),'recipe_sha256':digest(__file__),'blender':bpy.app.version_string,'sculpt':sculpt_report,'groom':groom_report,'native_eye_positions_unchanged':True,'uvs_unchanged':True,'source_vertices':len(original),'source_quads':len(head.data.polygons),'qualification':'Static appearance only; motion and organizer scoring not tested'}
    (a.out/'build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    render(scene,a.out,'front-matched',a.size,a.samples)
    cam=scene.camera
    aim(cam,(.29,-.51,.015),(0,0,-.035));cam.data.lens=64
    render(scene,a.out,'three-quarter',a.size,a.samples)
    aim(cam,(.58,-.035,.005),(0,0,-.035));cam.data.lens=64
    render(scene,a.out,'profile',a.size,a.samples)
    # A separate neutral studio setup judges structure without the hot source rim.
    for light in [o for o in scene.objects if o.type=='LIGHT']:
        if light.name=='Key':
            aim(light,(-.25,-.32,.17),(0,0,-.015));light.data.energy=7;light.data.size=.24
        elif light.name=='Fill':
            aim(light,(.23,-.30,.045),(0,0,-.02));light.data.energy=1.8;light.data.size=.28
        elif light.name=='Rim':
            aim(light,(-.18,.12,.17),(0,0,.02));light.data.energy=2.2;light.data.size=.20
        light.data.color=(1,1,1)
    scene.view_settings.exposure=-.2
    neutral=bpy.data.objects.new('Portrait | neutral 85mm',bpy.data.cameras.new('Portrait | neutral 85mm'))
    scene.collection.objects.link(neutral);neutral.data.lens=85
    scene.camera=neutral
    aim(neutral,(0,-.82,.03),(0,0,-.025))
    scene.render.resolution_x=scene.render.resolution_y=1400;scene.cycles.samples=96
    bpy.ops.wm.save_as_mainfile(filepath=str((a.out/'portrait.blend').resolve()))
    render(scene,a.out,'neutral-front',1400,96)
    aim(neutral,(.40,-.72,.03),(0,0,-.025))
    render(scene,a.out,'neutral-three-quarter',1400,96)
    aim(neutral,(0,-.55,.018),(0,0,-.010));neutral.data.lens=115
    render(scene,a.out,'eye-skin-detail',1200,96)
    report['scene_sha256']=digest(a.out/'portrait.blend')
    (a.out/'build.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(report),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--maps',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--size',type=int,default=768);p.add_argument('--samples',type=int,default=32)
    main(p.parse_args(sys.argv[sys.argv.index('--')+1:]))
