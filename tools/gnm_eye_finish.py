"""Photographic iris-sector transfer and anatomically fitted eye framing trials."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def smooth(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)


def maps(a):
    import shutil
    from PIL import Image
    from scipy.ndimage import map_coordinates
    recipe=sha(__file__)
    source=np.asarray(Image.open(a.photo).convert('RGB'),dtype=np.float32)/255
    a.out.mkdir(parents=True,exist_ok=True)
    for f in a.maps.glob('*.png'):shutil.copy2(f,a.out/f.name)
    n=2048;x,y=np.meshgrid((np.arange(n)+.5)/n-.5,(np.arange(n)+.5)/n-.5)
    radius=np.sqrt(x*x+y*y)
    pupil_radius=.043
    r=np.clip((radius-pupil_radius)/(.1849-pupil_radius),0,1)
    for tile,phase in [(1002,.23),(1004,.81)]:
        theta=np.arctan2(y,x)+phase
        # Only lateral photographic sectors are unoccluded by lids/lashes.
        # Continuous angular quilting reconstructs the hidden sectors. These
        # are authored reconstructions, not recovered photographic pixels.
        right=.22+.32*np.sin(theta+.15*np.sin(3*theta))
        left=2.91+.24*np.sin(2*theta+.25*np.sin(5*theta))
        radial=64+144*r
        def sample(angle):
            xx=736+radial*np.cos(angle);yy=640+radial*np.sin(angle)
            return np.stack([map_coordinates(source[...,c],(yy,xx),order=1,mode='nearest') for c in range(3)],-1)
        weight=.5+.45*np.sin(3*theta+.2)
        color=sample(right)*(1-weight[...,None])+sample(left)*weight[...,None]
        lum=color@np.array((.2126,.7152,.0722))
        color=lum[...,None]+.45*(color-lum[...,None])
        annulus=(radius>.06)&(radius<.17)
        color*=.29/np.median(lum[annulus])
        color*= (1-.20*np.exp(-((r-.97)/.05)**2))[...,None]
        pupil=smooth((radius-pupil_radius+.0005)/.0015)
        old=np.asarray(Image.open(a.maps/f'color.{tile}.png').convert('RGB').resize((n,n),Image.Resampling.BICUBIC),dtype=np.float32)/255
        sclera=smooth((radius-.205)/.18)*.12
        old=old*(1-sclera[...,None])+np.array((.62,.45,.42))*sclera[...,None]
        # Keep the previous texture's finer radial detail where angular
        # reconstruction would otherwise read as concentric streaks.
        photo_weight=.48*smooth((radius-.047)/.014)*smooth((.185-radius)/.017)
        color=color*photo_weight[...,None]+old*(1-photo_weight[...,None])
        color=color*pupil[...,None]+np.array((.002,.0018,.0018))*(1-pupil[...,None])
        mask=smooth((.187-radius)/.006)
        output=color*mask[...,None]+old*(1-mask[...,None])
        Image.fromarray(np.rint(np.clip(output,0,1)*255).astype(np.uint8)).save(a.out/f'color.{tile}.png')
        # Small authored relief inferred from texture contrast, not a measured
        # biological height map. The photographed pupil and flash are absent.
        height=.5+np.clip(lum/np.median(lum[annulus])-1,-.8,.8)*.06
        height=.5+(height-.5)*photo_weight
        Image.fromarray(np.rint(np.clip(height,0,1)*65535).astype(np.uint16)).save(a.out/f'iris-height.{tile}.png')
    report={'photo_sha256':sha(a.photo),'recipe_sha256':recipe,'source_native_pixels':[1463,1269],'visible_iris_diameter_px_approx':440,'photo_license':'CC0 1.0, Kookaaa, Wikimedia Commons','source_maps':{f.name:sha(f) for f in a.maps.glob('*.png')},'outputs':{f.name:sha(f) for f in a.out.glob('*.png')},'reconstruction':'Unoccluded lateral sectors sampled; hidden sectors angularly quilted; flash/pupil excluded; grey-blue colour normalized; depth is authored from contrast.'}
    (a.out/'eyes.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+str(a.out),flush=True)


def fit_eye_framing(head,scene):
    from mathutils import Vector
    from mathutils.kdtree import KDTree
    from gnm_portrait_refine import skin_tree,strands
    upper=scene.objects['Portrait | subtle upper lashes'];data=upper.data
    points=np.empty(len(data.points)*3,dtype=np.float32);data.attributes['position'].data.foreach_get('vector',points)
    points=points.reshape(-1,6,3);roots=points[:,:1,:].copy();points[:]=roots+(points-roots)*1.6
    data.attributes['position'].data.foreach_set('vector',points.ravel())
    radius=np.empty(len(data.points),dtype=np.float32);data.attributes['radius'].data.foreach_get('value',radius)
    data.attributes['radius'].data.foreach_set('value',radius*1.5)
    ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    co=np.array([v.co[:] for v in mesh.vertices]);ev.to_mesh_clear();tree=skin_tree(head,co)
    rng=np.random.default_rng(51219);lower=[];radii=[];rim_points=[]
    for ob in scene.objects:
        if ob.type!='CURVE' or not ob.name.startswith('Peak | lower tear meniscus'):continue
        row=np.array([p.co[:] for p in ob.data.splines[0].bezier_points]);rim_points.extend(row)
        for root in row[4:-4:4]:
            loc,n,_,_=tree.find_nearest(Vector(root));root=np.array(loc)+np.array(n)*.000025
            sign=np.sign(root[0]);length=rng.uniform(.0014,.0024);t=np.linspace(0,1,5)
            p=root[None,:]+np.column_stack((sign*.17*length*t,-length*(.50*t+.2*t*t),length*.60*t))
            lower.append(p);radii.append(rng.uniform(.000010,.000016)*(1-.95*t))
    if lower:strands('Peak | fine lower lashes',head,np.array(lower),np.array(radii),upper.data.materials[0])
    # A narrow anatomical pigment variation, not a painted shadow, softens
    # the white/skin transition at the moist lower rim.
    kd=KDTree(len(rim_points))
    for i,p in enumerate(rim_points):kd.insert(Vector(p),i)
    kd.balance();values=np.zeros(len(co),dtype=np.float32)
    skin_ids=sorted({i for f in head.data.polygons if f.material_index==0 for i in f.vertices})
    for i in skin_ids:
        _,_,dist=kd.find(Vector(co[i]));values[i]=.17*np.exp(-(dist/.00075)**2)
    attr=head.data.attributes.new('peak_lid_pigment','FLOAT','POINT');attr.data.foreach_set('value',values)
    nt=head.data.materials[0].node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    old=p.inputs['Base Color'].links[0].from_socket
    attribute=nt.nodes.new('ShaderNodeAttribute');attribute.attribute_name='peak_lid_pigment'
    mix=nt.nodes.new('ShaderNodeMixRGB');mix.label='Natural lower waterline pigment'
    nt.links.new(attribute.outputs['Fac'],mix.inputs[0]);nt.links.new(old,mix.inputs[1])
    mix.inputs[2].default_value=(.33,.095,.075,1);nt.links.new(mix.outputs[0],p.inputs['Base Color'])
    return len(lower)


def finish(a):
    import bpy
    from gnm_portrait_refine import aim,render
    recipe=sha(__file__);source=Path(bpy.data.filepath)
    a.out.mkdir(parents=True,exist_ok=True)
    scene=bpy.context.scene;head=scene.objects['GNM Head']
    for ix in [1,3]:
        tile=1001+ix;nt=head.data.materials[ix].node_tree
        p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
        tex=p.inputs['Base Color'].links[0].from_node
        tex.image=bpy.data.images.load(str((a.maps/f'color.{tile}.png').resolve()),check_existing=False);tex.image.pack()
        height=next((n for n in nt.nodes if n.label=='Photographic crypt contrast, authored relief'),None)
        if height is None:
            height=nt.nodes.new('ShaderNodeTexImage')
            height.label='Photographic crypt contrast, authored relief'
        height.image=bpy.data.images.load(str((a.maps/f'iris-height.{tile}.png').resolve()))
        height.image.colorspace_settings.name='Non-Color';height.image.pack()
        nt.links.new(tex.inputs['Vector'].links[0].from_socket,height.inputs['Vector'])
        bump=next((n for n in nt.nodes if n.label=='Delicate stromal relief'),None)
        if bump is None:
            bump=nt.nodes.new('ShaderNodeBump')
            bump.label='Delicate stromal relief'
        bump.inputs['Distance'].default_value=.00012;bump.inputs['Strength'].default_value=.25
        nt.links.new(height.outputs['Color'],bump.inputs['Height'])
        p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    lower_count=0 if a.replace_iris else fit_eye_framing(head,scene)
    bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str((a.out/'portrait.blend').resolve()),compress=True)
    camera=scene.camera;aim(camera,(0,-.55,.018),(0,0,-.010));camera.data.lens=115
    if a.eye_crop:
        scene.render.use_border=True
        scene.render.use_crop_to_border=True
        scene.render.border_min_x=.19
        scene.render.border_max_x=.81
        scene.render.border_min_y=.49
        scene.render.border_max_y=.74
    render(scene,a.out,'eye-detail',1100,a.samples)
    if not a.eye_crop:
        aim(camera,(0,-.82,.03),(0,0,-.025));camera.data.lens=85;render(scene,a.out,'front',1100,a.samples)
        aim(camera,(.40,-.72,.03),(0,0,-.025));render(scene,a.out,'three-quarter',1000,48)
    report={'source_sha256':sha(source),'recipe_sha256':recipe,'scene_sha256':sha(a.out/'portrait.blend'),'maps_sha256':sha(a.maps/'eyes.json'),'added_lower_lashes':lower_count,'upper_lash_length_gain':1.6,'status':'unqualified photographic-iris portrait trial'}
    (a.out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+json.dumps(report),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--maps-only',action='store_true')
    p.add_argument('--maps',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--photo',type=Path)
    p.add_argument('--eye-crop',action='store_true')
    p.add_argument('--replace-iris',action='store_true')
    p.add_argument('--samples',type=int,default=64)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    maps(a) if a.maps_only else finish(a)
