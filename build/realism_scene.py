"""Reproducible, isolated appearance checkpoints; never changes gaze geometry."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'wrapper'))
import eyes


def shader(material):
    return next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def material(name, color, roughness):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = shader(m); p.inputs['Base Color'].default_value = color
    p.inputs['Roughness'].default_value = roughness
    return m


def tube(name, paths, radius, mat):
    curve = bpy.data.curves.new(name, 'CURVE'); curve.dimensions = '3D'
    curve.bevel_depth = radius; curve.bevel_resolution = 0
    for points, closed in paths:
        s = curve.splines.new('POLY'); s.points.add(len(points)-1)
        for i, point in enumerate(points):
            s.points[i].co = (*point, 1)
            s.points[i].radius = 1 if closed else max(.06, (1-i/(len(points)-1))**.7)
        s.use_cyclic_u = closed
    obj = bpy.data.objects.new(name, curve); bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    # Mesh cosmetics participate in the existing real-occlusion mask renderer.
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.context.view_layer.objects.active = obj; bpy.ops.object.convert(target='MESH')
    return bpy.context.object


def anatomy(config):
    human = bpy.data.objects['Apollo_Face']
    for side in ['left', 'right']:
        human.data.shape_keys.key_blocks['eye-'+side+'-opened-up'].value = config['lid_opening']
    bpy.context.view_layer.update()
    from bl_ext.blender_org.mpfb.services.clothesservice import ClothesService
    ClothesService.fit_clothes_to_human(bpy.data.objects['Apollo_Face.eyelashes01'], human, set_parent=False)
    bpy.context.view_layer.update()
    tree = BVHTree.FromObject(human, bpy.context.evaluated_depsgraph_get())
    inverse = human.matrix_world.inverted()
    def front(x, z):
        origin = inverse @ Vector((x, -.25, z))
        direction = (inverse.to_3x3() @ Vector((0, 1, 0))).normalized()
        hit = tree.ray_cast(origin, direction)[0]
        return human.matrix_world @ hit if hit is not None else None
    contours = []
    for side, cx in [('L', eyes.calibration()['ipd']/2), ('R', -eyes.calibration()['ipd']/2)]:
        points = []
        for i in range(96):
            angle = i*2*math.pi/96
            def sample(r):
                x, z = cx+r*math.cos(angle), r*math.sin(angle)
                p = front(x, z)
                sphere_y = -math.sqrt(max(0, .012**2-r*r))
                return p, p.y-sphere_y if p is not None else 1
            previous = .001
            bracket = None
            for j in range(2, 40):
                r = .001+j*.0003
                p, delta = sample(r)
                if delta < 0:
                    bracket = (previous, r); break
                previous = r
            if bracket is None:
                raise ValueError(f'Cannot locate actual lid/sphere intersection: {side}/{i}')
            lo, hi = bracket
            for _ in range(12):
                mid = (lo+hi)/2
                if sample(mid)[1] > 0: lo = mid
                else: hi = mid
            # At an open lid edge the first-hit depth is discontinuous. Use the
            # exterior/front bracket, never an averaged radius that hits the
            # rear socket wall and buries the lashes behind the eyeball.
            p = sample(hi)[0]; p.y -= .00008; points.append(p)
        contours.append((points, True))
        corner = min(points,key=lambda p:abs(p.x)).copy();corner.y -= .0001
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.00055,location=corner)
        duct=bpy.context.object;duct.name='Apollo tear duct.'+side;duct.scale=(1.3,.65,.8)
        duct.data.materials.append(material('Apollo tear duct material.'+side,(.27,.12,.10,1),.32))
    tube('Apollo lid wet margins', contours, config['rim_radius_m'],
         material('Apollo moist lid margin', (.26,.105,.085,1), .26))
    bpy.data.objects['Apollo_Face.eyelashes01'].hide_render=True
    rng=random.Random(config['seed']);lashes=[];creases=[]
    for points,_ in contours:
        cx=sum(p.x for p in points)/len(points)
        for i,p in enumerate(points):
            upper=p.z>0
            if not upper and i%2:continue
            direction=Vector(((p.x-cx)*55,-.5,p.z*160+(.15 if upper else -.1))).normalized()
            length=(.0045 if upper else .002)*rng.uniform(.65,1.15)
            strand=[p+direction*(length*t)+Vector((0,.0004*t*t,.0004*t*t if upper else 0)) for t in [0,.25,.5,.75,1]]
            for j,q in enumerate(strand):
                surface=front(q.x,q.z)
                if surface is not None:
                    q.y=min(q.y,surface.y-.0004-.001*math.sin(math.pi*j/4))
            lashes.append((strand,False))
        crease=[]
        for p in points[5:44]:
            q=front(p.x,p.z+.0014)
            if q is not None:q.y-=.000025;crease.append(q)
        if len(crease)>2:creases.append((crease,False))
    tube('Apollo tapered eyelashes',lashes,.000055,material('Apollo lash fibers',(.018,.009,.006,1),.48))
    tube('Apollo upper lid crease',creases,.000045,material('Apollo crease tone',(.20,.10,.07,1),.65))
    iris = bpy.data.materials['Apollo radial hazel iris']
    for side in 'LR':
        mesh=bpy.data.objects['Iris.'+side].data
        if mesh.polygons[0].normal.y>0:mesh.flip_normals();mesh.update()
    iris.node_tree.nodes['Color Ramp.002'].color_ramp.elements[0].position = .45
    iris.node_tree.nodes['Color Ramp.002'].color_ramp.elements[1].position = .50
    iris.node_tree.nodes['Mix (Legacy).002'].inputs[2].default_value = config['sclera_color']
    iris.node_tree.nodes['Mix (Legacy).001'].inputs[2].default_value = (.17,.17,.10,1)
    fibers = iris.node_tree.nodes['Color Ramp'].color_ramp
    fibers.elements[0].color = (.055,.085,.04,1)
    fibers.elements[1].color = (.22,.16,.055,1)
    collar=iris.node_tree.nodes['Color Ramp.001'].color_ramp
    collar.elements[0].color=(1.3,1.2,1.0,1)
    collar.elements[1].color=(1.3,1.2,1.0,1);collar.elements[1].position=.38
    for m in bpy.data.objects['Apollo_Face.eyelashes01'].data.materials:
        p = shader(m)
        if p.inputs['Alpha'].is_linked:
            alpha = p.inputs['Alpha'].links[0].from_socket
            multiply = m.node_tree.nodes.new('ShaderNodeMath'); multiply.operation = 'MULTIPLY'
            multiply.inputs[1].default_value = .72
            m.node_tree.links.new(alpha, multiply.inputs[0]);m.node_tree.links.new(multiply.outputs[0], p.inputs['Alpha'])
    p = shader(iris); p.inputs['Roughness'].default_value = .36
    p.inputs['Specular IOR Level'].default_value = .2
    nodes, links = iris.node_tree.nodes, iris.node_tree.links
    base = p.inputs['Base Color'].links[0].from_socket
    noise = nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 95
    noise.inputs['Detail'].default_value = 3
    uv = next(n for n in nodes if n.type == 'TEX_COORD')
    links.new(uv.outputs['UV'], noise.inputs['Vector'])
    bump = nodes.new('ShaderNodeBump'); bump.inputs['Distance'].default_value = .000015
    bump.inputs['Strength'].default_value = .22
    links.new(noise.outputs['Fac'], bump.inputs['Height']); links.new(bump.outputs[0], p.inputs['Normal'])
    separate=nodes.new('ShaderNodeSeparateXYZ');links.new(uv.outputs['UV'],separate.inputs[0])
    normal_color=nodes.new('ShaderNodeCombineXYZ');normal_color.inputs['Z'].default_value=1
    links.new(separate.outputs['X'],normal_color.inputs['X']);links.new(separate.outputs['Y'],normal_color.inputs['Y'])
    normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.6
    links.new(normal_color.outputs[0],normal.inputs['Color']);links.new(normal.outputs['Normal'],bump.inputs['Normal'])
    p.inputs['Coat Weight'].default_value=.16;p.inputs['Coat Roughness'].default_value=.09
    links.new(normal.outputs['Normal'],p.inputs['Coat Normal'])
    # Preserve the qualified iris brightness floor: dark irises previously failed tracking.
    mix = nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = .12
    links.new(base, mix.inputs[1]); links.new(noise.outputs['Color'], mix.inputs[2])
    links.new(mix.outputs[0], p.inputs['Base Color'])
    sclera_material=bpy.data.materials['Sclera'];sclera = shader(sclera_material)
    sclera.inputs['Base Color'].default_value = config['sclera_color']
    sclera.inputs['Roughness'].default_value = .27
    sclera.inputs['Specular IOR Level'].default_value = .28
    nodes=sclera_material.node_tree.nodes;links=sclera_material.node_tree.links
    coord=nodes.new('ShaderNodeTexCoord');cells=nodes.new('ShaderNodeTexVoronoi')
    cells.feature='DISTANCE_TO_EDGE';cells.inputs['Scale'].default_value=12
    links.new(coord.outputs['Generated'],cells.inputs['Vector'])
    thin=nodes.new('ShaderNodeMath');thin.operation='LESS_THAN';thin.inputs[1].default_value=.025
    links.new(cells.outputs['Distance'],thin.inputs[0])
    peripheral=nodes.new('ShaderNodeSeparateXYZ');links.new(coord.outputs['Generated'],peripheral.inputs[0])
    amplitude=nodes.new('ShaderNodeMath');amplitude.operation='MULTIPLY'
    links.new(thin.outputs[0],amplitude.inputs[0]);links.new(peripheral.outputs['Y'],amplitude.inputs[1])
    faint=nodes.new('ShaderNodeMath');faint.operation='MULTIPLY';faint.inputs[1].default_value=.12
    links.new(amplitude.outputs[0],faint.inputs[0])
    veins=nodes.new('ShaderNodeMixRGB');veins.inputs[1].default_value=config['sclera_color']
    veins.inputs[2].default_value=(.38,.18,.16,1)
    links.new(faint.outputs[0],veins.inputs[0]);links.new(veins.outputs[0],sclera.inputs['Base Color'])


def surfaces(config):
    for m in bpy.data.objects['Apollo_Face'].data.materials:
        if not m or not m.use_nodes: continue
        p = shader(m); nodes = m.node_tree.nodes; links = m.node_tree.links
        p.inputs['Subsurface Weight'].default_value = config['skin_subsurface']
        p.inputs['Subsurface Radius'].default_value = (1, .45, .25)
        p.inputs['Subsurface Scale'].default_value = .001
        p.inputs['Specular IOR Level'].default_value = .3
        tex = nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = 5000
        tex.inputs['Detail'].default_value = 2
        coord = nodes.new('ShaderNodeTexCoord'); links.new(coord.outputs['Object'], tex.inputs['Vector'])
        bump = nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .22
        bump.inputs['Distance'].default_value = config['skin_bump_m']
        links.new(tex.outputs['Fac'], bump.inputs['Height']); links.new(bump.outputs[0], p.inputs['Normal'])
        rough = nodes.new('ShaderNodeMapRange'); rough.inputs['To Min'].default_value = config['skin_roughness']-.09
        rough.inputs['To Max'].default_value = config['skin_roughness']+.09
        links.new(tex.outputs['Fac'], rough.inputs['Value']); links.new(rough.outputs[0], p.inputs['Roughness'])
        geometry=nodes.new('ShaderNodeNewGeometry');position=nodes.new('ShaderNodeSeparateXYZ')
        links.new(geometry.outputs['Position'],position.inputs[0])
        region=nodes.new('ShaderNodeMapRange');region.clamp=True
        region.inputs['From Min'].default_value=-.025;region.inputs['From Max'].default_value=.035
        region.inputs['To Min'].default_value=config['skin_roughness']+.06
        region.inputs['To Max'].default_value=config['skin_roughness']-.06
        links.new(position.outputs['Z'],region.inputs['Value'])
        variation=nodes.new('ShaderNodeMath');variation.operation='MULTIPLY_ADD'
        variation.inputs[1].default_value=.08;variation.inputs[2].default_value=-.04
        links.new(tex.outputs['Fac'],variation.inputs[0])
        total=nodes.new('ShaderNodeMath');total.operation='ADD'
        links.new(region.outputs[0],total.inputs[0]);links.new(variation.outputs[0],total.inputs[1])
        links.new(total.outputs[0],p.inputs['Roughness'])
    scene = bpy.context.scene
    scene.cycles.max_bounces = 6; scene.cycles.diffuse_bounces = 3
    scene.cycles.glossy_bounces = 3
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = config['world_strength']
    for name, position, energy, size in [('Key',(-.14,-.22,.17),config['key_energy'],.19),('Fill',config['fill_position'],config['fill_energy'],.20)]:
        light = bpy.data.objects[name]; light.location = position
        light.rotation_euler = (-light.location).to_track_quat('-Z','Y').to_euler()
        light.data.energy = energy; light.data.size = size
    data=bpy.data.lights.new('Apollo separation','AREA');data.energy=config['rim_energy'];data.size=.12
    light=bpy.data.objects.new('Apollo separation',data);bpy.context.collection.objects.link(light)
    light.location=(.12,.10,.10);light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()


def grooming(config):
    rng = random.Random(config['seed']); human = bpy.data.objects['Apollo_Face']
    tree = BVHTree.FromObject(human, bpy.context.evaluated_depsgraph_get())
    center = Vector((0,.025,.045)); inv = human.matrix_world.inverted()
    def scalp(direction):
        start = center+direction*.25
        hit = tree.ray_cast(inv@start, (inv.to_3x3()@-direction).normalized())[0]
        return human.matrix_world@hit if hit is not None else None
    paths = []
    for _ in range(config['hair_strands']*3):
        z = rng.uniform(.1,1); a = rng.uniform(-math.pi,math.pi)
        n = Vector((math.sqrt(1-z*z)*math.cos(a), math.sqrt(1-z*z)*math.sin(a), z))
        root = scalp(n)
        if root is None: continue
        hairline = .065-.012*min(abs(root.x)/.075,1)**1.5+rng.uniform(-.001,.001)
        if root.z < (hairline if n.y < -.2 else .025): continue
        points=[]
        for j in range(12):
            t=j/11; d=(n+Vector((.35*t,.85*t,.18*math.sin(math.pi*t)))).normalized()
            p=scalp(d)
            if p is None: break
            points.append(p+d*(.0005+.002*math.sin(math.pi*t)))
        if len(points)==12: paths.append((points,False))
        if len(paths)>=config['hair_strands']: break
    if len(paths)<config['hair_strands']//2: raise ValueError('Insufficient scalp roots')
    tube('Apollo swept back groom', paths, config['hair_radius_m'],
         material('Apollo natural dark brown hair', (.025,.012,.007,1), .36))


def run(folder, config_path, stage):
    source = Path(bpy.data.filepath).resolve(); folder=Path(folder).resolve()
    if folder.exists(): raise ValueError('Use a new checkpoint directory')
    if source == folder/'scene.blend': raise ValueError('Never overwrite source')
    config=json.loads(Path(config_path).read_text()); eyes.reset()
    recipe_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    config_hash=hashlib.sha256(Path(config_path).read_bytes()).hexdigest()
    original=eyes.calibration()
    def eye_mesh_hash():
        data={name:[list(v.co) for v in bpy.data.objects[name].data.vertices]
              for side in 'LR' for name in ['Pupil.'+side,'Iris.'+side,'Sclera.'+side]}
        return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
    geometry_hash=eye_mesh_hash()
    anatomy(config)
    if stage in ['surface','finished']: surfaces(config)
    if stage == 'finished': grooming(config)
    assert eyes.calibration()==original
    assert eye_mesh_hash()==geometry_hash,'Appearance builder changed physical eye meshes'
    scene=bpy.context.scene; scene.cycles.samples=config['samples']; scene.cycles.seed=config['seed']
    scene.cycles.use_denoising = config['denoising']
    folder.mkdir(parents=True); eyes.reset(); bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),compress=True)
    eyes.render(folder/'center.png')
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==recipe_hash,'Recipe changed during build'
    assert hashlib.sha256(Path(config_path).read_bytes()).hexdigest()==config_hash,'Config changed during build'
    receipt={'stage':stage,'config':config,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'eye_mesh_sha256':geometry_hash,'eye_meshes_unchanged':True,
             'config_sha256':config_hash,
             'recipe_sha256':recipe_hash,
             'scene_sha256':hashlib.sha256((folder/'scene.blend').read_bytes()).hexdigest(),
             'qualified':False,'status':'Visual checkpoint; requires all acceptance gates'}
    (folder/'build.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--folder',type=Path,required=True)
    parser.add_argument('--config',type=Path,default=ROOT/'build/realism_config.json')
    parser.add_argument('--stage',choices=['anatomy','surface','finished'],default='finished')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);run(args.folder,args.config,args.stage)
