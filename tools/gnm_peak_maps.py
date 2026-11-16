"""Native-UV scan-relief transfer and restrained ocular variation for portrait trials."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bake_scan(a):
    import bpy
    import numpy as np
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from gnm_skin_trial import skin_only
    head=bpy.context.scene.objects['GNM Head']
    with np.load(a.aligned) as d:
        mesh=bpy.data.meshes.new('Disposable registered relief source')
        mesh.from_pydata(d['vertices'].tolist(),[],d['triangles'].tolist());mesh.update()
        mesh.uv_layers.new(name='Scan UV').data.foreach_set('uv',d['uv'].ravel())
    source=bpy.data.objects.new('Disposable registered relief source',mesh)
    bpy.context.scene.collection.objects.link(source);source.matrix_world=head.matrix_world.copy()
    mat=bpy.data.materials.new('Scan relief data emission');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear()
    tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(a.scan.resolve()))
    tex.image.colorspace_settings.name='Non-Color'
    emit=nt.nodes.new('ShaderNodeEmission');out=nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(tex.outputs['Color'],emit.inputs['Color']);nt.links.new(emit.outputs[0],out.inputs['Surface']);mesh.materials.append(mat)
    target=skin_only(head);bpy.data.objects.remove(head,do_unlink=True)
    dest=bpy.data.images.new('Native scan relief',a.size,a.size,alpha=False,float_buffer=True)
    dest.colorspace_settings.name='Non-Color'
    mat=bpy.data.materials.new('Relief transfer destination');mat.use_nodes=True
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=dest;mat.node_tree.nodes.active=tex
    target.data.materials.clear();target.data.materials.append(mat)
    for p in target.data.polygons:p.material_index=0
    bpy.ops.object.select_all(action='DESELECT');source.select_set(True);target.select_set(True);bpy.context.view_layer.objects.active=target
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16
    bpy.ops.object.bake(type='EMIT',use_selected_to_active=True,margin=16,margin_type='EXTEND',cage_extrusion=.035,max_ray_distance=.115,uv_layer='GNM Region')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='16';s.render.image_settings.color_mode='BW'
    s.view_settings.view_transform='Raw';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
    dest.save_render(str(a.out.resolve()),scene=s)
    a.out.with_suffix('.json').write_text(json.dumps({'scan_sha256':sha(a.scan),'aligned_sha256':sha(a.aligned),'output_sha256':sha(a.out),'data_encoding':'16-bit non-color','size':a.size},indent=2)+'\n')
    print('RESULT '+str(a.out),flush=True)


def ocular_maps(source,out):
    import numpy as np
    from PIL import Image,ImageDraw,ImageFilter
    from scipy.ndimage import map_coordinates
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from gnm_surface_maps import smooth
    n=2048;x,y=np.meshgrid((np.arange(n)+.5)/n-.5,(np.arange(n)+.5)/n-.5)
    radius=np.sqrt(x*x+y*y)
    for tile,seed in [(1002,9103),(1004,9209)]:
        original=np.asarray(Image.open(source/f'color.{tile}.png').convert('RGB'),dtype=np.float32)/255
        # Slight pupil constriction under the bright studio key. The pupil
        # remains centered; the iris and scleral boundary stay in native UVs.
        src_radius=.049+(radius-.043)/(.1849-.043)*(.1849-.049)
        src_radius=np.where(radius>.1849,radius,np.maximum(src_radius,0))
        factor=src_radius/np.maximum(radius,1e-8)
        uv=((.5+y*factor)*original.shape[0]-.5,(.5+x*factor)*original.shape[1]-.5)
        rgb=np.stack([map_coordinates(original[...,c],uv,order=1,mode='nearest') for c in range(3)],-1)
        rng=np.random.default_rng(seed);mask=Image.new('L',(n,n));draw=ImageDraw.Draw(mask)
        def px(r,angle):return ((.5+r*np.cos(angle))*n,(.5+r*np.sin(angle))*n)
        for j in range(27):
            angle=rng.uniform(-np.pi,np.pi);r0=rng.uniform(.39,.49);r1=rng.uniform(.215,.30)
            phase=rng.uniform(0,6.28);row=[]
            for t in np.linspace(0,1,50):
                r=r0+(r1-r0)*t;phi=angle+.08*np.sin(phase+t*6)+.06*np.sin(t*13+phase)
                row.append(px(r,phi))
            draw.line(row,fill=int(rng.integers(15,45)),width=int(rng.integers(1,3)))
            if j%2==0:
                r=.5*(r0+r1);draw.line([px(r,angle),px(r-.03,angle+.09),px(r-.065,angle+.14)],fill=17,width=1)
        vein=np.asarray(mask.filter(ImageFilter.GaussianBlur(.65)),dtype=np.float32)/255
        vein*=smooth((radius-.195)/.025)
        rgb=rgb*(1-vein[...,None])+np.array((.50,.19,.17))*vein[...,None]
        Image.fromarray(np.rint(np.clip(rgb,0,1)*255).astype(np.uint8)).save(out/f'color.{tile}.png')


def compose(a):
    import shutil
    import numpy as np
    from PIL import Image
    from scipy.ndimage import gaussian_filter,distance_transform_edt
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from gnm_portrait_maps import read_data_image
    from gnm_skin_detail import surface_positions
    from gnm_surface_maps import smooth
    a.out.mkdir(parents=True,exist_ok=True)
    for f in a.maps.glob('*.png'):shutil.copy2(f,a.out/f.name)
    ocular_maps(a.maps,a.out)
    base=read_data_image(a.maps/'height.1001.png')
    raw=read_data_image(a.raw)
    raw=np.asarray(Image.fromarray(raw).resize((4096,4096),Image.Resampling.BICUBIC))
    valid=raw>.04;support=smooth(distance_transform_edt(valid)/12)
    highpass=raw-gaussian_filter(raw,7)
    fields=surface_positions(a.template,4096,('upper_lip','lower_lip'))
    x,y,z=fields[...,:3].transpose(2,0,1)
    anterior=smooth((z+.002)/.015)
    face=smooth((y+.112)/.025)*smooth((.072-y)/.025)*smooth((.082-abs(x))/.02)*anterior
    face=np.nan_to_num(face)
    detail=np.clip(highpass,-.12,.12)*support*face
    height=np.clip(base+detail*.85,0,1)
    Image.fromarray(np.rint(height*65535).astype(np.uint16)).save(a.out/'height.1001.png')
    # A dedicated lip mask controls specular breakup without changing the
    # native vermilion border or painting a broad white highlight.
    lip=np.nan_to_num(np.max(fields[...,3:],axis=-1));lip=smooth(lip)
    lipmap=np.clip(lip,0,1)
    Image.fromarray(np.rint(lipmap*255).astype(np.uint8)).save(a.out/'lip-mask.1001.png')
    report={'source_maps':{f.name:sha(f) for f in a.maps.glob('*.png')},'scan_relief_sha256':sha(a.raw),'recipe_sha256':sha(__file__),'outputs':{f.name:sha(f) for f in a.out.glob('*.png')},'scan_detail_max_added_normalized':float(abs(detail).max()*.85),'license':'Existing Infinite Scan CC-BY-3.0 derivative and CC0 sources; source attribution retained. Ocular veins are authored synthesis.'}
    (a.out/'maps.json').write_text(json.dumps(report,indent=2)+'\n');print('RESULT '+str(a.out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bake-scan',action='store_true');p.add_argument('--aligned',type=Path);p.add_argument('--scan',type=Path)
    p.add_argument('--maps',type=Path);p.add_argument('--raw',type=Path);p.add_argument('--template',type=Path)
    p.add_argument('--size',type=int,default=2048);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    bake_scan(a) if a.bake_scan else compose(a)
