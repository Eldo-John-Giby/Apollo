"""Isolated v2 appearance construction; preserves the calibrated eye system."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
CONFIG_PATH=ROOT/'build/photorealism_config.json'
CONFIG=json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
sys.path.insert(0,str(ROOT/'wrapper'))
import eyes

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def organize():
    scene=bpy.context.scene
    groups={name:bpy.data.collections.get(name) or bpy.data.collections.new(name) for name in ['Apollo Face','Apollo Eyes','Apollo Groom','Apollo Lighting','Apollo Helpers']}
    for group in groups.values():
        if group.name not in scene.collection.children:scene.collection.children.link(group)
    for obj in list(scene.objects):
        if obj.type=='LIGHT' or obj.type=='CAMERA':key='Apollo Lighting'
        elif obj.name.startswith(('Pupil.','Iris.','Sclera.')):key='Apollo Eyes'
        elif obj.type in {'ARMATURE','EMPTY'} or obj.hide_render:key='Apollo Helpers'
        elif any(s in obj.name.lower() for s in ['groom','eyelash','eyebrow']):key='Apollo Groom'
        else:key='Apollo Face'
        target=groups[key]
        if obj.name not in target.objects:target.objects.link(obj)
        for collection in list(obj.users_collection):
            if collection!=target:collection.objects.unlink(obj)
        if obj.hide_render:obj.hide_set(True)
        obj.select_set(False)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.overlay.show_overlays=False
                area.spaces.active.region_3d.view_perspective='CAMERA'
    scene.cycles.seed=0;scene.cycles.use_animated_seed=False;scene.cycles.use_adaptive_sampling=False

def anatomy():
    from mathutils import Vector,Matrix
    from bl_ext.blender_org.mpfb.entities.objectproperties import HumanObjectProperties
    from bl_ext.blender_org.mpfb.services.targetservice import TargetService
    human=bpy.data.objects['Apollo_Face']
    def evaluated_points():
        ev=human.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        points=[human.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear();return points
    old=evaluated_points();groups=[]
    for cx in [-eyes.calibration()['ipd']/2,eyes.calibration()['ipd']/2]:
        ids=[i for i,p in enumerate(old) if .012<((p.x-cx)**2+p.z*p.z)**.5<.019 and -.02<p.y<.012]
        if len(ids)<10:raise ValueError('Insufficient orbital anchors')
        groups.append(ids)
    centers=[sum((old[i] for i in ids),Vector())/len(ids) for ids in groups]
    HumanObjectProperties.set_value('gender',CONFIG['gender'],entity_reference=human)
    HumanObjectProperties.set_value('age',CONFIG['age'],entity_reference=human)
    TargetService.reapply_macro_details(human);bpy.context.view_layer.update()
    new=evaluated_points()
    if len(new)!=len(old):raise ValueError('Morph changed evaluated topology')
    nc=[sum((new[i] for i in ids),Vector())/len(ids) for ids in groups]
    scale=(centers[1]-centers[0]).length/(nc[1]-nc[0]).length
    oldmid=(centers[0]+centers[1])/2;newmid=(nc[0]+nc[1])/2
    human.matrix_world=Matrix.Translation(oldmid)@Matrix.Scale(scale,4)@Matrix.Translation(-newmid)@human.matrix_world
    for obj in bpy.data.objects:
        if 'groom' in obj.name.lower():obj.hide_set(True);obj.hide_render=True
    from bl_ext.blender_org.mpfb.services.locationservice import LocationService
    target=Path(LocationService.get_mpfb_data('targets'))/'expression/units/asian/mouth-open.target.gz'
    TargetService.load_target(human,str(target),weight=0.0)
    mouth=human.data.shape_keys.key_blocks['mouth-open'];mouth.slider_min=-.25;mouth.value=CONFIG['mouth_close']
    # Preserve the original socket contact zone while baking the adult morph.
    # Blend into the female face outside the orbital ring; eye meshes stay intact.
    bpy.context.view_layer.update()
    deps=bpy.context.evaluated_depsgraph_get();ev=human.evaluated_get(deps)
    baked=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps)
    if len(baked.vertices)!=len(old):raise ValueError('Cannot preserve orbital topology')
    inverse=human.matrix_world.inverted()
    for i,vertex in enumerate(baked.vertices):
        previous=old[i]
        radius=min(((previous.x-cx)**2+previous.z**2)**.5 for cx in [-eyes.calibration()['ipd']/2,eyes.calibration()['ipd']/2])
        if radius<.032 and -.025<previous.y<.025:
            weight=max(0,min(1,(.032-radius)/.014))
            weight=weight*weight*(3-2*weight)
            current=human.matrix_world@vertex.co
            vertex.co=inverse@(current.lerp(previous,weight))
    for modifier in list(human.modifiers):human.modifiers.remove(modifier)
    human.data=baked
    for name in ['Apollo lid wet margins','Apollo tapered eyelashes','Apollo upper lid crease','Apollo tear duct.L','Apollo tear duct.R']:
        obj=bpy.data.objects.get(name)
        if obj:bpy.data.objects.remove(obj,do_unlink=True)
    sys.path.insert(0,str(ROOT/'build'))
    import realism_scene
    config=json.loads((ROOT/'build/realism_config.json').read_text(encoding='utf-8'))
    # Reuse only the proven contour geometry fitter, not its MPFB proxy/shader edits.
    legacy_source=(ROOT/'build/realism_scene.py').read_text(encoding='utf-8')
    start=legacy_source.index('    tree = BVHTree.FromObject')
    end=legacy_source.index("    iris = bpy.data.materials",start)
    fitter="def refit(config):\n    human=bpy.data.objects['Apollo_Face']\n"+legacy_source[start:end]
    # Preserve the contour fitter while breaking its evenly spaced lash comb.
    fitter=fitter.replace('upper=p.z>0', 'upper=p.z>0\n            if rng.random()<.13:continue\n            p=p.lerp(points[(i+1)%len(points)],rng.uniform(0,.45))')
    fitter=fitter.replace('rng.uniform(.65,1.15)', 'rng.uniform(.55,1.25)')
    namespace=dict(vars(realism_scene));exec(compile(fitter,'<v2 socket fitter>','exec'),namespace)
    namespace['refit'](config)
    bpy.context.view_layer.update()
    return {'macro':TargetService.get_macro_info_dict_from_basemesh(human),'orbital_alignment_scale':scale,'orbital_anchor_counts':[len(g) for g in groups]}


def surfaces():
    human=bpy.data.objects['Apollo_Face']
    asset=ROOT/'assets/photorealism-v2/young_lightskinned_female_diffuse3.png'
    image=bpy.data.images.load(str(asset),check_existing=True)
    for mat in human.data.materials:
        if not mat:continue
        mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
        output=nodes.new('ShaderNodeOutputMaterial');p=nodes.new('ShaderNodeBsdfPrincipled')
        links.new(p.outputs[0],output.inputs['Surface'])
        texture=nodes.new('ShaderNodeTexImage');texture.image=image
        # Retain UV-aligned detail but attenuate broad baked color mottling.
        tone=nodes.new('ShaderNodeHueSaturation');tone.inputs['Saturation'].default_value=.9
        links.new(texture.outputs['Color'],tone.inputs['Color'])
        soften=nodes.new('ShaderNodeMixRGB');soften.inputs[0].default_value=CONFIG['skin_color_softening']
        soften.inputs[2].default_value=(.46,.28,.20,1)
        links.new(tone.outputs[0],soften.inputs[1]);links.new(soften.outputs[0],p.inputs['Base Color'])
        p.inputs['Subsurface Weight'].default_value=CONFIG['skin_subsurface'];p.inputs['Subsurface Scale'].default_value=.001
        p.inputs['Subsurface Radius'].default_value=(1,.45,.25)
        p.inputs['Specular IOR Level'].default_value=.28
        coord=nodes.new('ShaderNodeTexCoord');noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=6500;noise.inputs['Detail'].default_value=2
        links.new(coord.outputs['Object'],noise.inputs['Vector'])
        bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=CONFIG['skin_bump_strength'];bump.inputs['Distance'].default_value=CONFIG['skin_bump_m']
        links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],p.inputs['Normal'])
        rough=nodes.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.39 if 'lips' not in mat.name else .29
        rough.inputs['To Max'].default_value=.53 if 'lips' not in mat.name else .37
        links.new(noise.outputs['Fac'],rough.inputs['Value']);links.new(rough.outputs[0],p.inputs['Roughness'])
    bpy.data.objects['Fill'].data.energy=CONFIG['fill_energy']
    return {'albedo_sha256':digest(asset),'native_albedo_resolution':list(image.size),'license':'CC0; see assets/photorealism-v2/ATTRIBUTION.md'}


def eye_surfaces():
    material=bpy.data.materials.new('Apollo v2 textured brown iris');material.use_nodes=True
    nodes=material.node_tree.nodes;nodes.clear();links=material.node_tree.links
    coord=nodes.new('ShaderNodeTexCoord');atlas=nodes.new('ShaderNodeTexImage')
    atlas.image=bpy.data.images.load(str(ROOT/'assets/photorealism-v2/brown_eye.png'),check_existing=True)
    scaled=nodes.new('ShaderNodeVectorMath');scaled.operation='MULTIPLY';scaled.inputs[1].default_value=(.25,.25,1);links.new(coord.outputs['UV'],scaled.inputs[0])
    offset=nodes.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.583,.583,0);links.new(scaled.outputs[0],offset.inputs[0]);links.new(offset.outputs[0],atlas.inputs['Vector'])
    tone=nodes.new('ShaderNodeHueSaturation');tone.inputs['Saturation'].default_value=.75;tone.inputs['Value'].default_value=1.25;links.new(atlas.outputs['Color'],tone.inputs['Color'])
    lift=nodes.new('ShaderNodeMixRGB');lift.blend_type='ADD';lift.inputs[0].default_value=1;lift.inputs[2].default_value=(*CONFIG['iris_lift_linear'],1);links.new(tone.outputs[0],lift.inputs[1])
    shader=nodes.new('ShaderNodeBsdfPrincipled');links.new(lift.outputs[0],shader.inputs['Base Color'])
    shader.inputs['Roughness'].default_value=.28;shader.inputs['Specular IOR Level'].default_value=.24;shader.inputs['Coat Weight'].default_value=.12
    noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=85;noise.inputs['Detail'].default_value=3;links.new(coord.outputs['UV'],noise.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.08;bump.inputs['Distance'].default_value=.000008;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],shader.inputs['Normal'])
    output=nodes.new('ShaderNodeOutputMaterial');links.new(shader.outputs[0],output.inputs['Surface'])
    for side in 'LR':
        bpy.data.objects['Iris.'+side].data.materials.clear();bpy.data.objects['Iris.'+side].data.materials.append(material)
        # Normal interpolation removes polygon-ring shading without moving any
        # measured vertex, physical pupil boundary or eye pivot.
        sclera=bpy.data.objects['Sclera.'+side]
        for poly in sclera.data.polygons:poly.use_smooth=True
        for mat in sclera.data.materials:
            principled=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            principled.inputs['Roughness'].default_value=.27
    return {'refractive_cornea':False,'method':'CC0 stock iris atlas with organic fibers and limbus, restrained micro-normal and non-refractive coat','atlas_sha256':digest(ROOT/'assets/photorealism-v2/brown_eye.png')}


def brows():
    import random,numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    sys.path.insert(0,str(ROOT/'build'))
    from realism_scene import tube,material
    source=bpy.data.objects['Apollo_Face.eyebrow001'];human=bpy.data.objects['Apollo_Face']
    image=next(n.image for m in source.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
    pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape(image.size[1],image.size[0],4)
    source.data.calc_loop_triangles();triangles=list(source.data.loop_triangles);uv=source.data.uv_layers.active.data
    tree=BVHTree.FromObject(human,bpy.context.evaluated_depsgraph_get());inverse=human.matrix_world.inverted();rng=random.Random(CONFIG['groom_seed']+1)
    def front(x,z):
        hit=tree.ray_cast(inverse@Vector((x,-.25,z)),(inverse.to_3x3()@Vector((0,1,0))).normalized())[0]
        return human.matrix_world@hit if hit is not None else None
    paths=[]
    for attempt in range(24000):
        tri=rng.choice(triangles);a=rng.random();b=rng.random()
        if a+b>1:a=1-a;b=1-b
        weights=[1-a-b,a,b]
        tex=sum((uv[i].uv*w for i,w in zip(tri.loops,weights)),Vector((0,0)))
        x=min(image.size[0]-1,max(0,int(tex.x*image.size[0])));y=min(image.size[1]-1,max(0,int(tex.y*image.size[1])))
        if pixels[y,x,3]<.3:continue
        root=sum((source.matrix_world@source.data.vertices[i].co*w for i,w in zip(tri.vertices,weights)),Vector())
        point=front(root.x,root.z)
        if point is None:continue
        length=rng.uniform(.0015,.0033);sign=1 if point.x>0 else -1
        slope=max(-.45,min(1.1,(.033-abs(point.x))*45))+rng.uniform(-.08,.08);direction=Vector((sign,.0,slope)).normalized()
        strand=[]
        for j in range(4):
            t=j/3;q=point+direction*length*t;surface=front(q.x,q.z)
            if surface is not None:q.y=surface.y-.00014-.00012*__import__('math').sin(__import__('math').pi*t)
            strand.append(q)
        paths.append((strand,False))
        if len(paths)>=CONFIG['brow_strands']:break
    if len(paths)<300:raise ValueError('Eyebrow texture sampling failed')
    source.hide_render=True;source.hide_set(True)
    tube('Apollo v2 individual brows',paths,.000025,material('Apollo v2 brow fibers',(.035,.018,.010,1),.5))
    return {'strands':len(paths),'source_alpha_image':image.name}


def grooming():
    import math,random
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    sys.path.insert(0,str(ROOT/'build'))
    from realism_scene import tube,material
    human=bpy.data.objects['Apollo_Face'];tree=BVHTree.FromObject(human,bpy.context.evaluated_depsgraph_get())
    inverse=human.matrix_world.inverted();center=Vector((0,.025,.055));rng=random.Random(CONFIG['groom_seed'])
    for obj in list(bpy.data.objects):
        if 'groom' in obj.name.lower():bpy.data.objects.remove(obj,do_unlink=True)
    def scalp(n,lift=.001):
        hit=tree.ray_cast(inverse@(center+n*.25),(inverse.to_3x3()@-n).normalized())[0]
        return human.matrix_world@hit+n*lift if hit is not None else None
    def direction(theta,z):return Vector((math.sqrt(max(0,1-z*z))*math.cos(theta),math.sqrt(max(0,1-z*z))*math.sin(theta),z))
    def line(theta):
        # Continuous frontal hairline, lower at the temples and occiput.
        lo,hi=-.6,.99
        for _ in range(15):
            z=(lo+hi)/2;n=direction(theta,z);p=scalp(n)
            front=max(0,min(1,(.35-n.y)/.8));front=front*front*(3-2*front)
            irregular=.0009*math.sin(theta*9+.7)+.0005*math.sin(theta*17)
            limit=front*(.072-.016*min(abs(p.x)/.075,1)+irregular)+(1-front)*.008
            if p.z<limit:lo=z
            else:hi=z
        return hi
    columns,rows=160,32;limits=[line(2*math.pi*i/columns) for i in range(columns)];vertices=[]
    for j in range(rows+1):
        t=.035+.965*j/rows
        for i in range(columns):
            theta=2*math.pi*i/columns;z=limits[i]+(1-limits[i])*t
            vertices.append(scalp(direction(theta,z),.001+.002*math.sin(math.pi*t)))
    faces=[]
    for j in range(rows):
        for i in range(columns):
            a=j*columns+i;b=j*columns+(i+1)%columns
            faces.append((a,b,b+columns,a+columns))
    mesh=bpy.data.meshes.new('V2 scalp foundation');mesh.from_pydata(vertices,[],faces);mesh.update()
    uv=mesh.uv_layers.new(name='Groom flow')
    for poly in mesh.polygons:
        column=poly.index%columns
        for loop_index in poly.loop_indices:
            vertex=mesh.loops[loop_index].vertex_index;row,index=divmod(vertex,columns)
            uv.data[loop_index].uv=((columns if column==columns-1 and index==0 else index)/columns,row/rows)
    cap=bpy.data.objects.new('Apollo v2 scalp foundation',mesh);bpy.context.collection.objects.link(cap)
    hair=material('Apollo v2 dark brown hair',(.022,.010,.006,1),CONFIG['hair_roughness']);
    next(n for n in hair.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Specular IOR Level'].default_value=.28;
    cap.data.materials.append(hair)
    nodes=hair.node_tree.nodes;links=hair.node_tree.links;shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    geometry=nodes.new('ShaderNodeNewGeometry');separate=nodes.new('ShaderNodeSeparateXYZ');links.new(geometry.outputs['Position'],separate.inputs[0])
    shift=nodes.new('ShaderNodeMath');shift.operation='MULTIPLY_ADD';shift.inputs[1].default_value=-.10;shift.inputs[2].default_value=.018;links.new(separate.outputs['Y'],shift.inputs[0])
    add=nodes.new('ShaderNodeMath');add.operation='ADD';links.new(separate.outputs['X'],add.inputs[0]);links.new(shift.outputs[0],add.inputs[1])
    absolute=nodes.new('ShaderNodeMath');absolute.operation='ABSOLUTE';links.new(add.outputs[0],absolute.inputs[0])
    stripe=nodes.new('ShaderNodeMapRange');stripe.clamp=True;stripe.inputs['From Min'].default_value=.00035;stripe.inputs['From Max'].default_value=.0012;stripe.inputs['To Min'].default_value=1;stripe.inputs['To Max'].default_value=0;links.new(absolute.outputs[0],stripe.inputs['Value'])
    upper=nodes.new('ShaderNodeMath');upper.operation='GREATER_THAN';upper.inputs[1].default_value=.075;links.new(separate.outputs['Z'],upper.inputs[0])
    mask=nodes.new('ShaderNodeMath');mask.operation='MULTIPLY';links.new(stripe.outputs[0],mask.inputs[0]);links.new(upper.outputs[0],mask.inputs[1])
    front=nodes.new('ShaderNodeMath');front.operation='LESS_THAN';front.inputs[1].default_value=.075;links.new(separate.outputs['Y'],front.inputs[0])
    frontmask=nodes.new('ShaderNodeMath');frontmask.operation='MULTIPLY';links.new(front.outputs[0],frontmask.inputs[0]);links.new(mask.outputs[0],frontmask.inputs[1])
    mix=nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.022,.010,.006,1);mix.inputs[2].default_value=(.18,.095,.060,1);links.new(frontmask.outputs[0],mix.inputs[0]);links.new(mix.outputs[0],shader.inputs['Base Color'])
    coord=nodes.new('ShaderNodeTexCoord');scale=nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(420,7,1);links.new(coord.outputs['UV'],scale.inputs[0])
    fibers=nodes.new('ShaderNodeTexNoise');fibers.inputs['Scale'].default_value=1;fibers.inputs['Detail'].default_value=2;links.new(scale.outputs[0],fibers.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00009;bump.inputs['Strength'].default_value=.22;links.new(fibers.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],shader.inputs['Normal'])
    rough=nodes.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.34;rough.inputs['To Max'].default_value=.54;links.new(fibers.outputs['Fac'],rough.inputs['Value']);links.new(rough.outputs[0],shader.inputs['Roughness'])
    shader.inputs['Anisotropic'].default_value=.35
    for poly in mesh.polygons:poly.use_smooth=True
    paths=[]
    for i in range(CONFIG['scalp_strands']):
        theta=rng.uniform(-math.pi,math.pi);low=line(theta);z=rng.uniform(low,.995);n=direction(theta,z)
        strand=[]
        for j in range(9):
            t=j/8
            # Flow away from an offset part and toward the back of the head.
            lateral=.25 if n.x>-.25 else -.25
            d=(n+Vector((lateral*t,1.15*t,.18*math.sin(math.pi*t)))).normalized()
            point=scalp(d,.0012+.003*math.sin(math.pi*t))
            strand.append(point)
        paths.append((strand,False))
    for group in range(5):
        strand_material=hair.copy();strand_material.name='Apollo v2 strand tone '+str(group)
        strand_mix=next(n for n in strand_material.node_tree.nodes if n.type=='MIX_RGB')
        factor=.65+.22*group;strand_mix.inputs[1].default_value=(.022*factor,.010*factor,.006*factor,1)
        tube('Apollo v2 pulled back strands '+str(group),paths[group::5],.000030+.000003*group,strand_material)
    # Mid-scale overlapping locks survive native-resolution denoising where
    # individual subpixel fibers disappear. Their raised centers catch light.
    lock_vertices=[];lock_faces=[]
    for index,(points,_) in enumerate(paths[::40]):
        width=rng.uniform(.00045,.00105)
        for j,p in enumerate(points):
            tangent=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized()
            normal=(p-center).normalized();across=tangent.cross(normal).normalized()
            taper=.2+.8*math.sin(math.pi*(.08+.84*j/(len(points)-1)))
            for lateral in [-1,0,1]:
                q=p+across*width*taper*lateral+normal*(.00025 if lateral==0 else -.00005)
                lock_vertices.append(q)
            if j:
                a=len(lock_vertices)-6
                lock_faces.extend([(a,a+1,a+4,a+3),(a+1,a+2,a+5,a+4)])
    lock_mesh=bpy.data.meshes.new('V2 overlapping hair locks');lock_mesh.from_pydata(lock_vertices,[],lock_faces);lock_mesh.update()
    locks=bpy.data.objects.new('Apollo v2 overlapping hair locks',lock_mesh);bpy.context.collection.objects.link(locks)
    for i in range(5):locks.data.materials.append(bpy.data.materials['Apollo v2 strand tone '+str(i)])
    for poly in lock_mesh.polygons:poly.use_smooth=True;poly.material_index=(poly.index//16)%5
    baby=[]
    for i in range(1100):
        theta=rng.uniform(-math.pi,0);low=line(theta);z=low+rng.uniform(-.025,.045);n=direction(theta,z);points=[]
        for j in range(6):
            t=j/5;d=(n+Vector((.08*t,.25*t,.13*t))).normalized()
            points.append(scalp(d,.00045+.0007*math.sin(math.pi*t)))
        baby.append((points,False))
    tube('Apollo v2 feathered hairline',baby,.000019,hair)
    back=scalp(Vector((0,1,.1)).normalized());bun_center=back+Vector((0,.018,-.015))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=bun_center)
    bun=bpy.context.object;bun.name='Apollo v2 compact bun';bun.scale=(.027,.027,.031);bun.data.materials.append(hair)
    for poly in bun.data.polygons:poly.use_smooth=True
    coils=[]
    for i in range(360):
        a=2*math.pi*i/360;strand=[]
        for j in range(17):
            t=j/16;phi=a+5*t;latitude=-1.3+2.6*t
            strand.append(bun_center+Vector((.0273*math.cos(latitude)*math.cos(phi),.0273*math.cos(latitude)*math.sin(phi),.0313*math.sin(latitude))))
        coils.append((strand,False))
    tube('Apollo v2 bun fibers',coils,.000035,hair)
    return {'seed':CONFIG['groom_seed'],'scalp_strands':CONFIG['scalp_strands'],'bun_strands':360,'style':'pulled back, offset flow and compact bun','runtime_geometry':'baked mesh strands for real occlusion checks'}


def build(folder,stage='baseline'):
    folder=Path(folder).resolve()
    if folder.exists():raise ValueError('Use a new output folder')
    source=Path(bpy.data.filepath);source_sha=digest(source)
    recipe_sha=digest(Path(__file__));config_sha=digest(CONFIG_PATH)
    assert CONFIG['render_seed']==0
    bpy.context.scene.cycles.samples=CONFIG['samples']
    before=eyes.calibration();eyes.reset()
    protected={name:hashlib.sha256(json.dumps([list(v.co) for v in bpy.data.objects[name].data.vertices]).encode()).hexdigest() for side in 'LR' for name in ['Pupil.'+side,'Iris.'+side,'Sclera.'+side]}
    organize()
    morph=anatomy() if stage in ['anatomy','surface','finished'] else None
    skin=surfaces() if stage in ['surface','finished'] else None
    eye=eye_surfaces() if stage in ['surface','finished'] else None
    groom=grooming() if stage=='finished' else None
    brow=brows() if stage=='finished' else None
    organize()
    for name,want in protected.items():
        actual=hashlib.sha256(json.dumps([list(v.co) for v in bpy.data.objects[name].data.vertices]).encode()).hexdigest()
        assert actual==want,'Changed protected eye mesh: '+name
    assert eyes.calibration()==before
    deps=bpy.context.evaluated_depsgraph_get()
    stats={'evaluated_polygons':sum(len(o.evaluated_get(deps).data.polygons) for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render)}
    assert stats['evaluated_polygons']<=1000000,'Geometry budget exceeded'
    folder.mkdir(parents=True)
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),compress=True)
    sys.path.insert(0,str(ROOT/'tools'))
    from scene_preflight import run
    run(folder/'scene-preflight.json')
    assert digest(Path(__file__))==recipe_sha and digest(CONFIG_PATH)==config_sha,'Build inputs changed'
    (folder/'build.json').write_text(json.dumps({'stage':stage,'source_sha256':source_sha,'scene_sha256':digest(folder/'scene.blend'),'recipe_sha256':recipe_sha,'config_sha256':config_sha,'config':CONFIG,'asset_sha256':{p.name:digest(p) for p in (ROOT/'assets/photorealism-v2').iterdir() if p.is_file()},'socket_fitter_sha256':digest(ROOT/'build/realism_scene.py'),'protected_eye_mesh_sha256':protected,'anatomy':morph,'skin':skin,'groom':groom,'brows':brow,'eye_shading':eye,'geometry_stats':stats,'qualified':False,'scope':'Development checkpoint; final visual, geometry, visibility and CPU acceptance remain required'},indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--folder',required=True,type=Path);parser.add_argument('--stage',choices=['baseline','anatomy','surface','finished'],default='baseline')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);build(args.folder,args.stage)
