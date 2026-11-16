"""Ear-safe scalp pigment and tapered nape strands for the isolated portrait."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def smooth(v):
    v=np.clip(v,0,1);return v*v*(3-2*v)


def scalp_coverage(p):
    x,y,z=p.T
    front=smooth((z+.10)/.07);side=smooth((abs(x)-.047)/.035)
    line=-.025+front*(.095-.055*side)
    old=smooth((y-line)/.007)
    posterior=smooth((-.015-z)/.055)
    jitter=.0010*np.sin(x*630)+.0006*np.sin(x*1730+z*500)
    fade=smooth((y+.010+jitter)/.055)
    return old*(1-posterior)+fade*posterior,old,posterior


def maps(a):
    import shutil
    from PIL import Image
    from scipy.ndimage import distance_transform_edt
    from gnm_skin_detail import surface_positions
    from gnm_surface_maps import noise
    a.out.mkdir(parents=True,exist_ok=True)
    for f in a.maps.glob('*.png'):shutil.copy2(f,a.out/f.name)
    fields=surface_positions(a.template,4096,('ears',))
    valid=np.isfinite(fields[...,0]);p=fields[valid,:3];x,y,z=p.T
    ear=smooth(fields[valid,3])
    current=np.asarray(Image.open(a.maps/'color.1001.png').convert('RGB'),dtype=np.float32)/255
    bare=np.asarray(Image.open(a.uncapped).convert('RGB'),dtype=np.float32)[valid]/255
    bare*=np.array((.82*.87,.79*.83,.75*.79))
    region=smooth((-.015-z)/.055)*smooth((.065-y)/.020)
    region=np.maximum(region,ear)
    density=scalp_coverage(p)[0]*(1-ear)
    root=np.empty_like(bare)
    for start in range(0,len(p),160000):
        sl=slice(start,start+160000);grain=noise(p[sl],4500,1611)
        root[sl]=np.array((.055*.87,.032*.83,.020*.79))*(.75+.5*grain[:,None])
    target=bare*(1-.94*density[:,None])+root*(.94*density[:,None])
    old=current[valid];current[valid]=old*(1-region[:,None])+target*region[:,None]
    nearest=distance_transform_edt(~valid,return_distances=False,return_indices=True)
    current=current[tuple(nearest)]
    Image.fromarray(np.rint(np.clip(current,0,1)*255).astype(np.uint8)).save(a.out/'color.1001.png')
    (a.out/'groom-map.json').write_text(json.dumps({'uncapped_source_sha256':sha(a.uncapped),'template_sha256':sha(a.template),'prior_color_sha256':sha(a.maps/'color.1001.png'),'output_sha256':sha(a.out/'color.1001.png'),'recipe_sha256':sha(__file__),'changes':['exclude native ears from scalp pigment','soften posterior density transition using uncapped source complexion']},indent=2)+'\n')
    print('RESULT '+str(a.out),flush=True)


def groom(a):
    import bpy
    from mathutils import Vector
    from gnm_portrait_refine import skin_tree,strands,aim,render
    source=Path(bpy.data.filepath);recipe=sha(__file__)
    a.out.mkdir(parents=True,exist_ok=True)
    head=bpy.context.scene.objects['GNM Head'];scene=bpy.context.scene
    ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    co=np.array([v.co[:] for v in mesh.vertices]);ev.to_mesh_clear()
    with np.load(a.template) as d:ears=d['ears'].astype(float)
    assert len(ears)==len(co)
    faces=np.array([f.vertices[:] for f in head.data.polygons if f.material_index==0])
    ear_face=ears[faces].max(1)>.4;tree=skin_tree(head,co)
    scalp=scene.objects['Portrait | swept chestnut hair'];data=scalp.data
    if a.scalp_source:
        with bpy.data.libraries.load(str(a.scalp_source.resolve()),link=False) as (src,dst):
            dst.objects=[scalp.name]
        original=dst.objects[0]
        if original is None:
            raise ValueError('Scalp source has no matching swept groom')
        scalp.data=original.data
        bpy.data.objects.remove(original,do_unlink=True)
        data=scalp.data
        nape=scene.objects.get('Peak | tapered nape hair')
        if nape:
            bpy.data.objects.remove(nape,do_unlink=True)
    pos=np.empty(len(data.points)*3,dtype=np.float32);data.attributes['position'].data.foreach_get('vector',pos);pos=pos.reshape(-1,12,3)
    radii=np.empty(len(data.points),dtype=np.float32);data.attributes['radius'].data.foreach_get('value',radii);radii=radii.reshape(-1,12)
    ear_keep=np.array([not ear_face[tree.find_nearest(Vector(p[0]))[2]] for p in pos])
    removed=int((~ear_keep).sum())
    root_local=pos[:,0,:]-np.array((0,.303139,.098933))
    cover,old_cover,posterior=scalp_coverage(root_local)
    fade_region=posterior*smooth((.065-root_local[:,1])/.020)
    probability=np.where(fade_region>.001,np.clip(cover/np.maximum(old_cover,.01),0,1),1)
    rng=np.random.default_rng(84711)
    keep=ear_keep&(rng.random(len(pos))<probability)
    fade_removed=int(np.count_nonzero(ear_keep&~keep))
    # Shorten the remaining lower-back population as it approaches skin.
    factor=1-fade_region*(1-(.25+.75*cover))
    selected=np.flatnonzero(keep&(factor<.995))
    for i in selected:
        row=pos[i];root=row[0].copy();row[:]=root+(row-root)*factor[i]
        flatten=fade_region[i]*(1-.72*cover[i])
        for j in range(1,len(row)):
            loc,nor,_,_=tree.find_nearest(Vector(row[j]))
            lift=.000035+.00030*cover[i]*np.sin(np.pi*j/(len(row)-1))
            normal=np.array(nor)
            surface=np.array(loc)+normal*lift
            row[j]=(1-flatten)*row[j]+flatten*surface
            if np.dot(row[j]-surface,normal)<0:
                row[j]=surface
    if removed or fade_removed or len(selected):
        replacement=strands('Peak | ear-safe scalp temporary',head,pos[keep],radii[keep],data.materials[0])
        scalp.data=replacement.data;bpy.data.objects.remove(replacement,do_unlink=True)
    # A separate population blends from short nape stubble into the existing
    # swept groom. Native ear membership excludes the helix and ear bowls.
    triangles=np.concatenate((faces[:,[0,1,2]],faces[:,[0,2,3]]))
    q=co[triangles];n=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);area=np.linalg.norm(n,axis=1)
    n/=np.maximum(area[:,None],1e-12);p=q.mean(1)-np.array((0,.303139,.098933))
    eligible=(p[:,2]<-.025)&(p[:,1]>-.040)&(p[:,1]<.040)&(ears[triangles].max(1)<.2)
    triangles,n,area=triangles[eligible],n[eligible],area[eligible]
    rng=np.random.default_rng(38110);idx=rng.choice(len(triangles),70000,p=area/area.sum())
    w=rng.random((len(idx),2));w=np.where((w.sum(1)>1)[:,None],1-w,w);w=np.column_stack((1-w.sum(1),w))
    roots=(co[triangles[idx]]*w[...,None]).sum(1);normal=n[idx];p=roots-np.array((0,.303139,.098933))
    den=scalp_coverage(p)[0]
    keep=(rng.random(len(p))<den)&(p[:,1]<.037)
    roots,normal,p=roots[keep][:16000],normal[keep][:16000],p[keep][:16000]
    blend=smooth((p[:,1]+.025)/.060);length=rng.uniform(.0010,.0020,len(p))+.005*blend
    flow=np.broadcast_to(np.array((.08,-1.,-.2)),normal.shape).copy()
    flow-=normal*(flow*normal).sum(1)[:,None];flow/=np.maximum(np.linalg.norm(flow,axis=1)[:,None],1e-10)
    t=np.linspace(0,1,8);points=roots[:,None,:]+flow[:,None,:]*(length[:,None]*t)[...,None]
    for i,row in enumerate(points):
        for j,point in enumerate(row):
            loc,nor,face_id,_=tree.find_nearest(Vector(point))
            if ear_face[face_id] and j>0:
                loc,nor,_,_=tree.find_nearest(Vector(row[j-1]))
            row[j]=np.array(loc)+np.array(nor)*(.000030+(.00015+.00035*blend[i])*np.sin(np.pi*t[j]))
    radius=rng.uniform(.000016,.000028,len(p))[:,None]*(1-.95*t)[None,:]
    strands('Peak | tapered nape hair',head,points,radius,scalp.data.materials[0])
    # The base atlas can feed either the skin shader or the waterline tint.
    nt=head.data.materials[0].node_tree
    textures=[
        node for node in nt.nodes
        if node.type=='TEX_IMAGE' and node.image
        and node.image.filepath.replace('\\','/').rsplit('/',1)[-1]=='color.1001.png'
    ]
    if len(textures)!=1:
        raise ValueError('Expected one native skin color atlas')
    tex=textures[0]
    path=a.maps/'color.1001.png';image=bpy.data.images.load(str(path.resolve()),check_existing=False)
    image.colorspace_settings.name='sRGB';image.pack();tex.image=image
    assert bytes(image.packed_file.data)==path.read_bytes()
    bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str((a.out/'portrait.blend').resolve()),compress=True)
    camera=scene.camera;camera.data.lens=85
    aim(camera,(.40,-.72,.03),(0,0,-.025))
    render(scene,a.out,'three-quarter',a.size,a.samples)
    aim(camera,(.90,-.035,.02),(0,.045,-.025))
    render(scene,a.out,'profile',a.size,a.samples)
    if not a.side_views_only:
        aim(camera,(0,-.82,.03),(0,0,-.025));render(scene,a.out,'front',1000,48)
    report={'source_sha256':sha(source),'recipe_sha256':recipe,'scene_sha256':sha(a.out/'portrait.blend'),'removed_ear_strands':removed,'fade_removed_strands':fade_removed,'shortened_strands':len(selected),'nape_strands':len(roots),'color_sha256':sha(path),'status':'unqualified static groom refinement'}
    (a.out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+json.dumps(report),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--maps-only',action='store_true')
    p.add_argument('--maps',type=Path,required=True);p.add_argument('--template',type=Path,required=True)
    p.add_argument('--uncapped',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--side-views-only',action='store_true')
    p.add_argument('--scalp-source',type=Path)
    p.add_argument('--size',type=int,default=1000)
    p.add_argument('--samples',type=int,default=48)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    maps(a) if a.maps_only else groom(a)
