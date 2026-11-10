"""Refine the packed adult character while protecting calibrated eye geometry."""
import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT/'build/appearance_v3_config.json'
CONFIG = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
sys.path.insert(0, str(ROOT/'wrapper'))
sys.path.insert(0, str(ROOT/'build'))
import eyes
from realism_scene import material, tube


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gaussian(value, center, width):
    return math.exp(-((value-center)/width)**2)


def protected_geometry():
    return {
        name: hashlib.sha256(json.dumps([list(v.co) for v in bpy.data.objects[name].data.vertices]).encode()).hexdigest()
        for side in 'LR' for name in ['Pupil.'+side, 'Iris.'+side, 'Sclera.'+side]
    }


def refine_face():
    human = bpy.data.objects['Apollo_Face']
    inverse = human.matrix_world.inverted()
    half_ipd = eyes.calibration()['ipd']/2
    max_displacement = 0
    for vertex in human.data.vertices:
        point = human.matrix_world@vertex.co
        original = point.copy()
        x, y, z = point
        front = gaussian(y, -.018, .028)
        cheek = gaussian(abs(x), .041, .022)*gaussian(z, -.031, .025)*front
        point.y -= CONFIG['cheek_lift_m']*cheek
        jaw = gaussian(abs(x), .055, .018)*gaussian(z, -.083, .024)*front
        point.x -= math.copysign(CONFIG['jaw_softening_m']*jaw, x)
        lip = gaussian(x, 0, .024)*gaussian(z, -.073, .011)*gaussian(y, -.024, .012)
        point.y -= CONFIG['lip_projection_m']*lip
        upper = gaussian(z, -.067, .003)*gaussian(x, 0, .020)*front
        lower = gaussian(z, -.079, .0035)*gaussian(x, 0, .020)*front
        point.z += CONFIG['lip_volume_m']*(upper-lower)
        bow = gaussian(abs(x), .006, .004)*gaussian(z, -.065, .003)*front
        point.z += .0003*bow
        corners = gaussian(abs(x), .022, .006)*gaussian(z, -.073, .006)*front
        point.z += CONFIG['mouth_corner_lift_m']*corners
        # Keep a generous central clearance corridor for the physical pupils.
        radial_x = min(abs(x-half_ipd), abs(x+half_ipd))
        lid = gaussian(radial_x, 0, .010)*gaussian(z, .0055, .003)*gaussian(y, -.009, .009)
        if z > .0038:
            point.z -= CONFIG['upper_lid_drop_m']*lid
        max_displacement = max(max_displacement, (point-original).length)
        vertex.co = inverse@point
    human.data.update()
    bpy.context.view_layer.update()
    return {'maximum_body_vertex_displacement_m': max_displacement}


def refit_lids():
    for name in ['Apollo lid wet margins', 'Apollo tapered eyelashes', 'Apollo upper lid crease',
                 'Apollo tear duct.L', 'Apollo tear duct.R']:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    import realism_scene
    source = (ROOT/'build/realism_scene.py').read_text(encoding='utf-8')
    start = source.index('    tree = BVHTree.FromObject')
    end = source.index('    iris = bpy.data.materials', start)
    fitter = "def refit(config):\n    human=bpy.data.objects['Apollo_Face']\n"+source[start:end]
    fitter = fitter.replace('upper=p.z>0', 'upper=p.z>0\n            if rng.random()<.18:continue\n            p=p.lerp(points[(i+1)%len(points)],rng.uniform(0,.5))')
    fitter = fitter.replace('rng.uniform(.65,1.15)', 'rng.uniform(.5,1.1)')
    namespace = dict(vars(realism_scene))
    exec(compile(fitter, '<v3 orbital cosmetics>', 'exec'), namespace)
    config = json.loads((ROOT/'build/realism_config.json').read_text(encoding='utf-8'))
    config['seed'] = CONFIG['seed']
    namespace['refit'](config)


def spatial_mask(nodes, links, position, center, widths):
    subtract = nodes.new('ShaderNodeVectorMath')
    subtract.operation = 'SUBTRACT'
    subtract.inputs[1].default_value = center
    links.new(position, subtract.inputs[0])
    normalize = nodes.new('ShaderNodeVectorMath')
    normalize.operation = 'DIVIDE'
    normalize.inputs[1].default_value = widths
    links.new(subtract.outputs[0], normalize.inputs[0])
    dot = nodes.new('ShaderNodeVectorMath')
    dot.operation = 'DOT_PRODUCT'
    links.new(normalize.outputs[0], dot.inputs[0])
    links.new(normalize.outputs[0], dot.inputs[1])
    negate = nodes.new('ShaderNodeMath')
    negate.operation = 'MULTIPLY'
    negate.inputs[1].default_value = -1
    links.new(dot.outputs['Value'], negate.inputs[0])
    exponent = nodes.new('ShaderNodeMath')
    exponent.operation = 'EXPONENT'
    links.new(negate.outputs[0], exponent.inputs[0])
    return exponent.outputs[0]


def refine_materials():
    human = bpy.data.objects['Apollo_Face']
    lip_index = next(i for i, mat in enumerate(human.data.materials) if mat.name.endswith('.lips'))
    membership = [set() for vertex in human.data.vertices]
    for polygon in human.data.polygons:
        for index in polygon.vertices:
            membership[index].add(polygon.material_index)
    boundary = [i for i, groups in enumerate(membership) if lip_index in groups and len(groups) > 1]
    if not boundary:
        raise ValueError('Cannot locate lip material boundary')
    tree = KDTree(len(boundary))
    for index, vertex_index in enumerate(boundary):
        tree.insert(human.matrix_world@human.data.vertices[vertex_index].co, index)
    tree.balance()
    attribute = human.data.attributes.new('apollo_lip_interior', 'FLOAT', 'POINT')
    for i, vertex in enumerate(human.data.vertices):
        if lip_index in membership[i]:
            distance = tree.find(human.matrix_world@vertex.co)[2]
            weight = min(1, distance/.0018)
            attribute.data[i].value = weight*weight*(3-2*weight)
    for mat in human.data.materials:
        if not mat:
            continue
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        shader = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
        colour = shader.inputs['Base Color'].links[0].from_socket
        geometry = nodes.new('ShaderNodeNewGeometry')
        position = geometry.outputs['Position']
        tint = nodes.new('ShaderNodeMixRGB')
        tint.blend_type = 'SOFT_LIGHT'
        tint.inputs[0].default_value = CONFIG['skin_colour_blend']
        tint.inputs[2].default_value = (.58, .40, .34, 1)
        links.new(colour, tint.inputs[1])
        colour = tint.outputs[0]
        for x in [-.040, .040]:
            mask = spatial_mask(nodes, links, position, (x, -.015, -.034), (.023, .025, .018))
            strength = nodes.new('ShaderNodeMath')
            strength.operation = 'MULTIPLY'
            strength.inputs[1].default_value = CONFIG['cheek_tint_strength']
            links.new(mask, strength.inputs[0])
            blush = nodes.new('ShaderNodeMixRGB')
            blush.inputs[2].default_value = (.43, .19, .16, 1)
            links.new(strength.outputs[0], blush.inputs[0])
            links.new(colour, blush.inputs[1])
            colour = blush.outputs[0]
        if mat.name.endswith('.lips'):
            lip_mask = spatial_mask(nodes, links, position, (0, -.025, -.073), (.027, .017, .012))
            interior = nodes.new('ShaderNodeAttribute')
            interior.attribute_name = 'apollo_lip_interior'
            fade = nodes.new('ShaderNodeMath')
            fade.operation = 'MULTIPLY'
            links.new(interior.outputs['Fac'], fade.inputs[0])
            links.new(lip_mask, fade.inputs[1])
            strength = nodes.new('ShaderNodeMath')
            strength.operation = 'MULTIPLY'
            strength.inputs[1].default_value = CONFIG['lip_tint_strength']
            links.new(fade.outputs[0], strength.inputs[0])
            lip_colour = nodes.new('ShaderNodeMixRGB')
            lip_colour.inputs[2].default_value = (.36, .115, .105, 1)
            links.new(strength.outputs[0], lip_colour.inputs[0])
            links.new(colour, lip_colour.inputs[1])
            colour = lip_colour.outputs[0]
            texture = nodes.new('ShaderNodeTexNoise')
            texture.inputs['Scale'].default_value = 1
            texture.inputs['Detail'].default_value = 2
            scale = nodes.new('ShaderNodeVectorMath')
            scale.operation = 'MULTIPLY'
            scale.inputs[1].default_value = (6500, 120, 450)
            links.new(position, scale.inputs[0])
            links.new(scale.outputs[0], texture.inputs['Vector'])
            bump = nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value = .11
            bump.inputs['Distance'].default_value = .000012
            links.new(texture.outputs['Fac'], bump.inputs['Height'])
            if shader.inputs['Normal'].is_linked:
                links.new(shader.inputs['Normal'].links[0].from_socket, bump.inputs['Normal'])
            links.new(bump.outputs[0], shader.inputs['Normal'])
            for link in list(shader.inputs['Roughness'].links):
                links.remove(link)
            roughness = nodes.new('ShaderNodeMapRange')
            roughness.inputs['To Min'].default_value = .46
            roughness.inputs['To Max'].default_value = .36
            links.new(fade.outputs[0], roughness.inputs['Value'])
            links.new(roughness.outputs[0], shader.inputs['Roughness'])
            coat = nodes.new('ShaderNodeMath')
            coat.operation = 'MULTIPLY'
            coat.inputs[1].default_value = .06
            links.new(fade.outputs[0], coat.inputs[0])
            links.new(coat.outputs[0], shader.inputs['Coat Weight'])
        links.new(colour, shader.inputs['Base Color'])
        shader.inputs['Subsurface Weight'].default_value = .055
    for side in 'LR':
        shader = next(n for n in bpy.data.objects['Iris.'+side].data.materials[0].node_tree.nodes
                      if n.type == 'BSDF_PRINCIPLED')
        shader.inputs['Roughness'].default_value = .28
        shader.inputs['Coat Weight'].default_value = .12


def build_brows():
    old = bpy.data.objects['Apollo v2 individual brows']
    bpy.data.objects.remove(old, do_unlink=True)
    human = bpy.data.objects['Apollo_Face']
    tree = BVHTree.FromObject(human, bpy.context.evaluated_depsgraph_get())
    inverse = human.matrix_world.inverted()
    rng = random.Random(CONFIG['seed'])
    paths = [[], [], []]
    def skin(x, z):
        point = tree.ray_cast(inverse@Vector((x, -.25, z)),
                              (inverse.to_3x3()@Vector((0, 1, 0))).normalized())[0]
        if point is None:
            raise ValueError('Brow root missed face')
        return human.matrix_world@point

    for side in [-1, 1]:
        for index in range(CONFIG['brow_hairs_per_side']):
            t = rng.betavariate(1.35, 1.65)
            x = side*(.014+.043*t)
            center_z = .0105+.006*math.sin(math.pi*.9*t)-.007*t**3
            thickness = CONFIG['brow_thickness_m']*(.78+.25*math.sin(math.pi*t))*(1-.75*t**3)
            z = center_z+rng.uniform(-.5, .5)*thickness
            root = skin(x, z)
            length = rng.uniform(.0018, .0030)*(1-.3*t)
            growth = Vector((side*(.25+.75*t), 0, .90-1.5*t)).normalized()
            strand = []
            for j in range(5):
                u = j/4
                point = root+growth*length*u
                front = skin(point.x, point.z)
                point.y = front.y-.00010-.00014*math.sin(math.pi*u)
                strand.append(point)
            paths[index%3].append((strand, False))
    for i, group in enumerate(paths):
        colour = [(.025, .012, .007, 1), (.038, .019, .010, 1), (.052, .028, .015, 1)][i]
        tube('Apollo v3 shaped brow fibers '+str(i), group, .000029,
             material('Apollo v3 brow tone '+str(i), colour, .5))


def soften_groom():
    # Reduce ridge-like locks and the broad painted scalp stripe.
    locks = bpy.data.objects['Apollo v2 overlapping hair locks']
    for vertex in locks.data.vertices:
        point = vertex.co
        # Bring the ridges slightly inward, preserving the underlying scalp.
        normal = (point-Vector((0, .025, .055))).normalized()
        vertex.co -= normal*.00013
    for mat in bpy.data.materials:
        if mat.name.startswith(('Apollo v2 dark brown hair', 'Apollo v2 strand tone')) and mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'MAP_RANGE' and abs(node.inputs['From Max'].default_value-.0012) < .00001:
                    node.inputs['From Min'].default_value = .00012
                    node.inputs['From Max'].default_value = .00065
    human = bpy.data.objects['Apollo_Face']
    tree = BVHTree.FromObject(human, bpy.context.evaluated_depsgraph_get())
    inverse = human.matrix_world.inverted()
    rng = random.Random(CONFIG['seed']+2)
    paths = []
    for sign in [-1, 1]:
        for i in range(60):
            x = sign*rng.uniform(.061, .068)
            z = rng.uniform(.042, .055)
            points = []
            length = rng.uniform(.007, .013)
            for j in range(7):
                u = j/6
                xx = x+sign*.0015*math.sin(math.pi*u)
                zz = z-length*u
                hit = tree.ray_cast(inverse@Vector((xx, -.2, zz)),
                                    (inverse.to_3x3()@Vector((0, 1, 0))).normalized())[0]
                if hit is None:
                    break
                point = human.matrix_world@hit
                point.y -= .00025+.0006*math.sin(math.pi*u)
                points.append(point)
            if len(points) > 3:
                paths.append((points, False))
    tube('Apollo v3 fine temple strands', paths, .000024,
         material('Apollo v3 temple hair', (.025, .012, .007, 1), .48))


def build(folder):
    folder = folder.resolve()
    if folder.exists():
        raise ValueError('Choose a new output folder')
    source = Path(bpy.data.filepath)
    input_hash = digest(source)
    recipe_hash = digest(__file__)
    config_hash = digest(CONFIG_PATH)
    original = protected_geometry()
    calibration = eyes.calibration()
    eyes.reset()
    face = refine_face()
    refit_lids()
    refine_materials()
    build_brows()
    soften_groom()
    assert protected_geometry() == original
    assert eyes.calibration() == calibration
    scene = bpy.context.scene
    scene.cycles.samples = CONFIG['samples']
    scene.cycles.device = 'CPU'
    scene.cycles.seed = 0
    scene.cycles.use_animated_seed = False
    scene.cycles.use_adaptive_sampling = False
    scene.camera.data.dof.use_dof = False
    from photorealism_scene import organize
    organize()
    groom_collection = bpy.data.collections['Apollo Groom']
    for obj in scene.objects:
        if obj.hide_render or obj.type != 'MESH':
            continue
        if any(word in obj.name.lower() for word in ['hair', 'brow', 'strand', 'scalp', 'bun', 'eyelash']):
            if obj.name not in groom_collection.objects:
                groom_collection.objects.link(obj)
            for collection in list(obj.users_collection):
                if collection != groom_collection:
                    collection.objects.unlink(obj)
    deps = bpy.context.evaluated_depsgraph_get()
    polygons = sum(len(o.evaluated_get(deps).data.polygons) for o in scene.objects
                   if o.type == 'MESH' and not o.hide_render)
    assert polygons < 1000000
    folder.mkdir(parents=True)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'), compress=True)
    assert digest(__file__) == recipe_hash and digest(CONFIG_PATH) == config_hash
    receipt = {'source_sha256': input_hash, 'scene_sha256': digest(folder/'scene.blend'),
               'recipe_sha256': recipe_hash, 'config_sha256': config_hash,
               'socket_fitter_sha256': digest(ROOT/'build/realism_scene.py'),
               'dependency_sha256': {name: digest(ROOT/name) for name in [
                   'build/realism_config.json', 'build/photorealism_scene.py',
                   'build/photorealism_config.json', 'wrapper/eyes.py']},
               'protected_eye_mesh_sha256': original, 'config': CONFIG,
               'face': face, 'evaluated_polygons': polygons, 'qualified': False}
    (folder/'build.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    sys.path.insert(0, str(ROOT/'tools'))
    from scene_preflight import run
    run(folder/'preflight.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    build(args.folder)
