"""Versioned realism overhaul for the latest packed haired portrait."""
import argparse
import json
from pathlib import Path
import sys
from time import monotonic

import bpy
import bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_blink_polish import matte_regions
from gnm_feedback_still import coords
from gnm_portrait_refine import aim, skin_tree, smooth, strands

ROOT = Path(bpy.data.filepath).resolve().parent
sys.path.insert(0, str(ROOT/'realism_pass'))
from realism_helpers import add_shape_key, crop_render, quick_render, save_version

scene = bpy.context.scene
head = scene.objects['GNM Head']


def surface(object):
    evaluated=object.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return coords(evaluated.data.vertices)


def gauss(x, y, z, cx, cy, cz, sx, sy, sz):
    return np.exp(-((x-cx)/sx)**2-((y-cy)/sy)**2-((z-cz)/sz)**2)


def shape_fields():
    basis = coords(head.data.shape_keys.reference_key.data)
    x, y, z = basis.T
    a = abs(x)
    sign = np.sign(x)
    front = smooth((z-.050)/.042)
    zero = np.zeros(len(x))
    g = lambda cx, cy, cz, sx, sy, sz: gauss(a,y,z,cx,cy,cz,sx,sy,sz)
    jaw = g(.052,.219,.073,.026,.036,.052)
    forehead = g(0,.359,.108,.065,.036,.066)
    cheek = g(.046,.279,.105,.028,.017,.039)
    hollow = g(.058,.249,.095,.030,.018,.044)
    lip = g(0,.233,.132,.029,.009,.024)
    corners = g(.023,.232,.125,.013,.007,.019)
    chin = g(0,.196,.108,.029,.014,.030)
    nose = g(.012,.267,.139,.012,.014,.032)
    bridge = g(.005,.287,.137,.009,.021,.020)
    orbital = g(.032,.295,.111,.033,.013,.027)
    ear = smooth((a-.063)/.020)*g(.085,.274,.057,.034,.070,.048)
    lobe = ear*np.exp(-((y-.245)/.015)**2)
    neck = g(.028,.162,.073,.014,.033,.034)
    adams = g(0,.151,.090,.012,.020,.018)
    lid_x = (a-.031)/.015
    upper = np.exp(-(lid_x**2)-((y-(.305+.0014*np.cos(lid_x*1.6)))/.0038)**2)*front
    lower = np.exp(-(lid_x**2)-((y-.295)/.0065)**2)*front
    fields = {
        'face_width': (-x*.075*jaw - x*.026*cheek, zero, zero),
        'forehead_height': (zero, -.0045*forehead*smooth((y-.326)/.025),
                            .0014*g(.025,.334,.115,.018,.016,.045)-.001*forehead),
        'jaw_chin': (.0012*sign*jaw, -.00055*chin, .0015*chin + .0007*jaw),
        'cheekbones': (zero, .0012*cheek, .0025*cheek-.0016*hollow),
        'nose': (.0008*sign*nose, .00042*nose, .0011*bridge+.0007*nose),
        'lips': (zero, .0007*corners + np.where(y<.233,-.0006,.00035)*lip,
                 .0014*g(.008,.229,.134,.023,.007,.022)+.0008*lip),
        'eyelids': (zero, .00058*upper, .00032*upper+.00053*lower),
        'ears': (.0011*sign*ear, -.0006*lobe, .00115*ear*np.sin((y-.235)*105)+.0012*lobe),
        'neck': (.0005*sign*neck, zero, .0013*neck+.00125*adams),
        'asymmetry': (zero, sign*(.00055*orbital+.0006*ear+.00032*corners),
                      sign*(.0005*nose+.00045*cheek)),
        'resting_expression': (zero, np.where(y>.234,.00028,-.00045)*lip+.00048*corners,
                               .00024*cheek),
    }
    skin = {i for f in head.data.polygons if f.material_index == 0 for i in f.vertices}
    eyes = {i for f in head.data.polygons if f.material_index in (1,2,3,4) for i in f.vertices}
    omit = sorted(set(range(len(x)))-(skin-eyes))
    for name, axes in fields.items():
        delta = np.column_stack(axes)
        delta[omit] = 0
        key = add_shape_key(head, name, 1)
        key.data.foreach_set('co', (basis+delta).astype(np.float32).ravel())
    bpy.context.view_layer.update()


def refit_curves(before, after):
    head.data.calc_loop_triangles()
    tris = np.array([p.vertices[:] for p in head.data.loop_triangles
                     if head.data.polygons[p.polygon_index].material_index==0])
    tree = BVHTree.FromPolygons(before.tolist(), tris.tolist(), all_triangles=True)
    for obj in scene.objects:
        if obj.type != 'CURVES':
            continue
        values = obj.data.attributes['position'].data
        points = np.empty((len(values),3), dtype=np.float32)
        values.foreach_get('vector', points.ravel())
        for curve in obj.data.curves:
            i = curve.first_point_index
            hit, _, face, _ = tree.find_nearest(Vector(points[i]))
            ids = tris[face]
            old = [Vector(v) for v in before[ids]]
            new = [Vector(v) for v in after[ids]]
            shift = np.array(barycentric_transform(hit,*old,*new)-hit)
            points[i:i+curve.points_length] += shift
        values.foreach_set('vector', points.ravel())


def add_collar():
    mesh = head.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    points, faces = [], []
    for f in mesh.polygons:
        if f.material_index != 0:
            continue
        polygon = [(np.array(mesh.vertices[i].co), np.array(mesh.vertices[i].normal)) for i in f.vertices]
        def field(v):
            return v[1]-(.150+.029*smooth(abs(v[0])/.084))
        clipped = []
        for (a,n),(b,m) in zip(polygon, polygon[1:]+polygon[:1]):
            fa, fb = field(a), field(b)
            if fa <= 0:
                clipped.append(a+.0012*n)
            if (fa<=0) != (fb<=0):
                t=fa/(fa-fb)
                clipped.append(a+t*(b-a)+.0012*(n+t*(m-n)))
        if len(clipped) >= 3:
            faces.append(tuple(range(len(points),len(points)+len(clipped))))
            points.extend(clipped)
    data=bpy.data.meshes.new('Portrait crew neckline')
    data.from_pydata(points, [], faces)
    weld_collar(data)
    obj=bpy.data.objects.new('Portrait crew neckline', data)
    scene.collection.objects.link(obj)
    obj.matrix_world=head.matrix_world.copy()
    mat=bpy.data.materials.new('Charcoal cotton knit')
    mat.use_nodes=True
    nt=mat.node_tree
    bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value=(.029,.035,.042,1)
    bsdf.inputs['Roughness'].default_value=.79
    bsdf.inputs['Sheen Weight'].default_value=.18
    tex=nt.nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value=195
    tex.inputs['Detail'].default_value=2
    bump=nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.2
    bump.inputs['Distance'].default_value=.00012
    nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    data.materials.append(mat)
    for p in data.polygons:
        p.use_smooth=True


def weld_collar(data):
    mesh = bmesh.new()
    mesh.from_mesh(data)
    bmesh.ops.remove_doubles(mesh, verts=list(mesh.verts), dist=.00001)
    mesh.to_mesh(data)
    mesh.free()
    data.update()


def copied_material(slot, name):
    material=head.data.materials[slot].copy()
    material.name=name
    head.data.materials[slot]=material
    return material


def skin_finish():
    tree=copied_material(0,'skin_v2').node_tree
    nodes, links=tree.nodes, tree.links
    bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.subsurface_method='RANDOM_WALK_SKIN'
    for name,value in {'Subsurface Weight':.24,'Subsurface Scale':.0022,
                       'Subsurface Radius':(1,.25,.1),'IOR':1.4,'Sheen Weight':.08,
                       'Sheen Roughness':.51}.items():
        bsdf.inputs[name].default_value=value
    x,y,z=coords(head.data.vertices).T
    a=abs(x)
    front=smooth((z-.073)/.032)
    cheeks=gauss(a,y,z,.044,.272,.118,.037,.030,.065)*front
    dot=0
    for side in (-1,1):
        dot=dot+gauss(x,y,z,side*.041,.244,.115,.004,.005,.034)
    temple=gauss(a,y,z,.044,.342,.1,.045,.042,.060)*front
    def mask(name,field):
        attr=head.data.attributes.new(name,'FLOAT','POINT')
        attr.data.foreach_set('value',np.clip(field,0,1).astype(np.float32))
        n=nodes.new('ShaderNodeAttribute')
        n.attribute_name=attr.name
        return n.outputs['Fac']
    def tint(source,factor,name,value,operation='MULTIPLY'):
        n=nodes.new('ShaderNodeMixRGB')
        n.label=name
        n.blend_type=operation
        n.inputs[2].default_value=(*value,1)
        links.new(source,n.inputs[1])
        links.new(factor,n.inputs[0])
        return n.outputs[0]
    color=bsdf.inputs['Base Color'].links[0].from_socket
    color=tint(color,mask('Soft cheek pigment correction',.74*cheeks+.26*dot),
               'Reduce cheek-red contrast',(.85,1.01,1.03))
    color=tint(color,mask('Temple undertone',temple*.5),'Soft golden forehead',(1.01,.99,.94))
    color=tint(color,mask('Beard undertone',.30*gauss(a,y,z,.038,.223,.100,.048,.029,.080)*front),
               'Cooler beard area',(.84,.91,1))
    links.new(color,bsdf.inputs['Base Color'])
    # Extremely faint elongated forehead creases over the existing scan relief.
    tex=nodes.new('ShaderNodeTexCoord')
    stretch=nodes.new('ShaderNodeVectorMath')
    stretch.operation='MULTIPLY'
    stretch.inputs[1].default_value=(85,2300,190)
    links.new(tex.outputs['Object'],stretch.inputs[0])
    noise=nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=1
    noise.inputs['Detail'].default_value=2.4
    links.new(stretch.outputs[0],noise.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump')
    bump.label='Faint forehead lines'
    bump.inputs['Distance'].default_value=.000049
    links.new(mask('Forehead crease strength',temple*.29),bump.inputs['Strength'])
    links.new(noise.outputs['Fac'],bump.inputs['Height'])
    links.new(bsdf.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
    links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    matte_regions(head,coords(head.data.vertices))


def lashes():
    tree=skin_tree(head,surface(head))
    rng=np.random.default_rng(601)
    material=bpy.data.materials.new('Lash_v2 deep brown')
    material.diffuse_color=(.027,.013,.008,1)
    material.use_nodes=True
    bsdf=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value=material.diffuse_color
    bsdf.inputs['Specular IOR Level'].default_value=.14
    bsdf.inputs['Roughness'].default_value=.58
    for upper, name, count in (
        (True,'Portrait | subtle upper lashes',118),
        (False,'Peak | fine lower lashes',46),
    ):
        original=scene.objects[name]
        original.hide_render=True
        original.hide_set(True)
        roots=np.array([original.data.attributes['position'].data[c.first_point_index].vector[:]
                        for c in original.data.curves])
        t=np.linspace(0,1,9)
        u=np.linspace(.04,.96,count)+rng.uniform(-.003,.003,count)
        grouped=np.sin(np.pi*u)**.74
        length=(.0020+.0041*grouped if upper else .00085+.0015*grouped)
        length*=rng.uniform(.75,1.22,count)
        main=np.arange(count)%4==1
        sizes=np.where(main,.000105,.000064) if upper else np.where(main,.000065,.000043)
        radii=sizes[:,None]*rng.uniform(.85,1.15,count)[:,None]*(1-.995*t)**.64
        rows=[]
        for side in (-1,1):
            samples=roots[side*roots[:,0]>0]
            samples=samples[np.argsort(abs(samples[:,0]))]
            for i,(frac,l) in enumerate(zip(u,length)):
                xx=np.interp(frac,np.linspace(0,1,len(samples)),abs(samples[:,0]))
                seed=Vector([np.interp(xx,abs(samples[:,0]),samples[:,j]) for j in range(3)])
                hit,n,_,_=tree.find_nearest(seed)
                root=np.array(hit+n*.000025)
                fan=side*(.59*frac-.09+.045*np.sin(frac*105))
                ym=(-.24*t+.84*t**2 if upper else -.54*t-.18*t**2)
                zm=.98*t-.17*t**3
                rows.append(root+l*np.column_stack((fan*t,ym,zm)))
        strands('Realism upper lashes' if upper else 'Realism lower lashes',head,
                np.array(rows),np.concatenate((radii,radii)),material)


def eye_finish():
    for slot in (1,2,3,4):
        copied_material(slot,f'eye_v2_{slot}')
    # Preserve the existing inner-corner gradient and make corneal reflections softer.
    for slot in (2,4):
        tree=head.data.materials[slot].node_tree
        glass=next(n for n in tree.nodes if n.type=='BSDF_GLASS')
        glass.inputs['IOR'].default_value=1.376
        glass.inputs['Roughness'].default_value=.024
    for slot in (1,3):
        tree=head.data.materials[slot].node_tree
        bsdf=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
        bsdf.inputs['Specular IOR Level'].default_value=.045
    lashes()


def scalp_finish():
    obj=scene.objects['Portrait | swept chestnut hair']
    source=obj.data.materials[0]
    material=source.copy()
    material.name='Scalp_v2 brunette'
    tree=material.node_tree
    hair=next(n for n in tree.nodes if n.type=='BSDF_HAIR_PRINCIPLED')
    hair.model='HUANG'
    hair.parametrization='MELANIN'
    info=tree.nodes.new('ShaderNodeHairInfo')
    variation=tree.nodes.new('ShaderNodeMapRange')
    variation.inputs['To Min'].default_value=.64
    variation.inputs['To Max'].default_value=.82
    tree.links.new(info.outputs['Random'],variation.inputs['Value'])
    tree.links.new(variation.outputs[0],hair.inputs['Melanin'])
    for name,value in {'Melanin Redness':.33,'Roughness':.42,'IOR':1.55,
                       'Radial Roughness':.41,'Coat':.03}.items():
        if name in hair.inputs:
            hair.inputs[name].default_value=value
    for groom in scene.objects:
        if groom.type=='CURVES' and len(groom.data.materials) and groom.data.materials[0]==source:
            groom.data.materials[0]=material


def beauty_setup():
    eval_collection=bpy.data.collections.new('LIGHTS_EVAL')
    beauty=bpy.data.collections.new('LIGHTS_BEAUTY')
    scene.collection.children.link(eval_collection)
    scene.collection.children.link(beauty)
    names=('Key','Fill','Rim')
    for name in names:
        obj=scene.objects[name]
        eval_collection.objects.link(obj)
        for collection in list(obj.users_collection):
            if collection!=eval_collection:
                collection.objects.unlink(obj)
    for name,position,size,energy,color in (
        ('Beauty key',(-.62,-.63,.48),.67,58,(1.0,.94,.87)),
        ('Beauty fill',(.60,-.36,.08),.78,14,(.87,.93,1)),
        ('Beauty rim',(.28,.43,.42),.68,22,(.86,.93,1)),
    ):
        data=bpy.data.lights.new(name,'AREA')
        data.shape='DISK' if name=='Beauty rim' else 'RECTANGLE'
        data.size=size
        if data.shape=='RECTANGLE':
            data.size_y=size*.86
        data.energy=energy
        data.color=color
        obj=bpy.data.objects.new(name,data)
        beauty.objects.link(obj)
        aim(obj,position,(0,0,-.02))
    cam=bpy.data.objects.new('Portrait beauty 85mm',scene.objects['CAM_EVAL'].data.copy())
    scene.collection.objects.link(cam)
    aim(cam,(.108,-.78,.015),(0,0,-.036))
    cam.data.dof.use_dof=True
    cam.data.dof.focus_distance=.78
    cam.data.dof.aperture_fstop=5.6
    cam.rotation_euler.rotate_axis('Z', .035)
    return cam,eval_collection,beauty


def phase(name,version):
    save_version(ROOT/f'portrait_v{version:02d}.blend')
    scene.render.resolution_percentage=50
    scene.cycles.samples=64
    scene.cycles.adaptive_threshold=.05
    quick_render(scene, output/f'{name}.png')


def final_look():
    scene.objects['Beauty key'].data.energy=43
    scene.objects['Beauty fill'].data.energy=9
    scene.objects['Beauty rim'].data.energy=9
    cloth=scene.objects['Portrait crew neckline'].data.materials[0]
    cloth_bsdf=next(n for n in cloth.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    cloth_bsdf.inputs['Base Color'].default_value=(.013,.017,.023,1)
    cloth_bsdf.inputs['Specular IOR Level'].default_value=.22
    groom=scene.objects['Realism upper lashes']
    attr=groom.data.attributes['radius'].data
    values=np.empty(len(attr),dtype=np.float32)
    attr.foreach_get('value',values)
    attr.foreach_set('value',values*1.17)
    original=scene.world
    scene.world=original.copy()
    scene.world.name='Portrait gradient world'
    scene.world.use_nodes=True
    nt=scene.world.node_tree
    nodes,links=nt.nodes,nt.links
    world_out=next(n for n in nodes if n.type=='OUTPUT_WORLD')
    original_shader=world_out.inputs['Surface'].links[0].from_socket
    if not original.use_nodes:
        original_shader.node.inputs['Color'].default_value=(*original.color,1)
    coordinates=nodes.new('ShaderNodeTexCoord')
    separate=nodes.new('ShaderNodeSeparateXYZ')
    links.new(coordinates.outputs['Normal'],separate.inputs[0])
    factor=nodes.new('ShaderNodeMapRange')
    factor.inputs['From Min'].default_value=-.19
    factor.inputs['From Max'].default_value=.21
    links.new(separate.outputs['Z'],factor.inputs['Value'])
    color=nodes.new('ShaderNodeMixRGB')
    color.inputs[1].default_value=(.034,.042,.054,1)
    color.inputs[2].default_value=(.10,.109,.121,1)
    links.new(factor.outputs[0],color.inputs[0])
    background=nodes.new('ShaderNodeBackground')
    links.new(color.outputs[0],background.inputs['Color'])
    rays=nodes.new('ShaderNodeLightPath')
    mix=nodes.new('ShaderNodeMixShader')
    links.new(rays.outputs['Is Camera Ray'],mix.inputs[0])
    links.new(original_shader,mix.inputs[1])
    links.new(background.outputs[0],mix.inputs[2])
    links.new(mix.outputs[0],world_out.inputs['Surface'])
    return original


parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--beauty-only',action='store_true')
parser.add_argument('--lighting-only',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
output=ROOT/'realism_pass'
if not args.beauty_only and not args.lighting_only:
    before=surface(head)
    shape_fields()
    refit_curves(before,surface(head))
    add_collar()
    phase('01_geometry',2)
    skin_finish()
    phase('02_skin',3)
    eye_finish()
    phase('03_eyes',4)
    scalp_finish()
    phase('04_hair',5)
if not args.beauty_only:
    weld_collar(scene.objects['Portrait crew neckline'].data)
    cam,eval_lights,beauty_lights=beauty_setup()
    eval_lights.hide_render=True
    scene.camera=cam
    phase('06_beauty_review',6)
    eval_lights.hide_render=False
    beauty_lights.hide_render=True
    scene.camera=scene.objects['CAM_EVAL']
    scene.render.resolution_percentage=100
    scene.cycles.samples=256
    scene.cycles.adaptive_threshold=.02
    scene.cycles.time_limit=170
    quick_render(scene,output/'05_eval.png')
else:
    weld_collar(scene.objects['Portrait crew neckline'].data)
    original_world=final_look()
    scene.cycles.samples=1024
    scene.cycles.adaptive_threshold=.01
    scene.cycles.max_bounces=10
    scene.cycles.diffuse_bounces=3
    scene.cycles.glossy_bounces=3
    scene.cycles.denoising_input_passes='RGB_ALBEDO_NORMAL'
    scene.cycles.time_limit=540
    scene.render.use_persistent_data=True
    scene.render.resolution_percentage=100
    scene.render.filepath='//realism_pass/final.png'
    save_version(ROOT/'portrait_v07.blend')
    start=monotonic()
    quick_render(scene,output/'final.png')
    (output/'final_timing.json').write_text(json.dumps({'seconds':monotonic()-start,
        'sample_ceiling':1024,'noise_threshold':.01,'time_limit':540},indent=2)+'\n')
    scene.camera=scene.objects['CAM_EVAL']
    scene.world=original_world
    bpy.data.collections['LIGHTS_BEAUTY'].hide_render=True
    bpy.data.collections['LIGHTS_EVAL'].hide_render=False
    scene.cycles.samples=64
    scene.cycles.adaptive_threshold=.035
    scene.cycles.time_limit=75
    for name,bounds in (
        ('eyes',(.30,.70,.507,.647)),('mouth',(.39,.61,.30,.43)),
        ('cheek',(.55,.70,.37,.52)),('hairline',(.27,.73,.69,.84)),
    ):
        crop_render(scene,output/f'final_{name}.png',bounds)
