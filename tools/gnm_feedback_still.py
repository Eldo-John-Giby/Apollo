"""Apply the portrait review notes to a separate packed Blender scene."""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_portrait_refine import aim, render, skin_tree, smooth, strands


def coords(collection):
    return np.array([point.co[:] for point in collection])


def jaw_offset(points):
    x, y, z = points.T
    side = np.abs(x)
    delta = np.zeros_like(points)
    # Strengthen the angle behind the masseter and bring the chin forward.
    angle = np.exp(-((side-.054)/.015)**2-((y-.211)/.013)**2-((z-.061)/.034)**2)
    hollow = np.exp(-((side-.049)/.014)**2-((y-.242)/.016)**2-((z-.090)/.031)**2)
    chin = np.exp(-(x/.026)**2-((y-.197)/.013)**2-((z-.107)/.023)**2)
    mask = 1-smooth((y-.250)/.018)
    delta[:, 0] = np.sign(x) * (.0030*angle-.0013*hollow) * mask
    delta[:, 1] = (-.0013*angle-.0012*chin) * mask
    delta[:, 2] = (.0013*angle-.0021*hollow+.0024*chin) * mask
    return delta


def expression_anatomy(scene, head):
    basis = head.data.shape_keys.reference_key
    positions = coords(basis.data)
    delta = jaw_offset(positions)
    eye_ids = {i for face in head.data.polygons if face.material_index in (1, 2, 3, 4) for i in face.vertices}
    assert not np.any(delta[sorted(eye_ids)])
    shape = head.shape_key_add(name='Portrait | jaw definition', from_mix=False)
    shape.relative_key = basis
    shape.data.foreach_set('co', (positions + delta).astype(np.float32).ravel())
    shape.value = 1
    bpy.context.view_layer.update()
    evaluated = head.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    surface = coords(mesh.vertices)
    evaluated.to_mesh_clear()
    tree = skin_tree(head, surface)
    for name in ('Peak | facial vellus', 'Peak | short beard stubble', 'Peak | denser beard stubble'):
        data = scene.objects[name].data
        field = data.attributes['position'].data
        flat = np.empty(len(field)*3, dtype=np.float32)
        field.foreach_get('vector', flat)
        rows = flat.reshape(-1, 4, 3)
        roots = rows[:, 0].copy()
        offsets = jaw_offset(roots)
        for i in np.flatnonzero(np.linalg.norm(offsets, axis=1) > 1e-6):
            point, normal, _, _ = tree.find_nearest(Vector(roots[i]+offsets[i]))
            rows[i] += np.asarray(point+normal*.000010)-roots[i]
        field.foreach_set('vector', flat)
    return tree


def product(nodes, links, source, factor):
    node = nodes.new('ShaderNodeMath')
    node.operation = 'MULTIPLY'
    links.new(source, node.inputs[0])
    if isinstance(factor, (float, int)):
        node.inputs[1].default_value = factor
    else:
        links.new(factor, node.inputs[1])
    return node.outputs[0]


def finish_skin(head):
    tree = head.data.materials[0].node_tree
    nodes, links = tree.nodes, tree.links
    shader = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
    shader.inputs['Specular IOR Level'].default_value = .29
    shader.inputs['Subsurface Weight'].default_value = .35
    shader.inputs['Subsurface Scale'].default_value = .00085
    shader.inputs['Coat Weight'].default_value = 0
    regional = next(node for node in nodes if node.label == 'regional oil and roughness')
    regional.inputs['To Min'].default_value = .47
    regional.inputs['To Max'].default_value = .69
    lip = next(node for node in nodes if node.label == 'native vermilion mask')
    texture = nodes.new('ShaderNodeTexCoord')
    stretch = nodes.new('ShaderNodeVectorMath')
    stretch.operation = 'MULTIPLY'
    stretch.inputs[1].default_value = (1950, 175, 290)
    links.new(texture.outputs['Object'], stretch.inputs[0])
    variation = nodes.new('ShaderNodeTexNoise')
    variation.inputs['Scale'].default_value = 450
    variation.inputs['Detail'].default_value = 1.3
    links.new(texture.outputs['Object'], variation.inputs['Vector'])
    bend = nodes.new('ShaderNodeVectorMath')
    bend.operation = 'SCALE'
    bend.inputs['Scale'].default_value = .48
    links.new(variation.outputs['Color'], bend.inputs[0])
    warp = nodes.new('ShaderNodeVectorMath')
    warp.operation = 'ADD'
    links.new(stretch.outputs[0], warp.inputs[0])
    links.new(bend.outputs[0], warp.inputs[1])
    grooves = nodes.new('ShaderNodeTexVoronoi')
    grooves.feature = 'DISTANCE_TO_EDGE'
    grooves.inputs['Scale'].default_value = 1
    links.new(warp.outputs[0], grooves.inputs['Vector'])
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.label = 'Fine vertical vermilion fissures'
    ramp.color_ramp.elements[0].position = .025
    ramp.color_ramp.elements[1].position = .18
    links.new(grooves.outputs['Distance'], ramp.inputs[0])
    bump = nodes.new('ShaderNodeBump')
    bump.label = 'Matte lip creases'
    bump.inputs['Distance'].default_value = .000069
    links.new(product(nodes, links, lip.outputs['Color'], .66), bump.inputs['Strength'])
    links.new(ramp.outputs['Color'], bump.inputs['Height'])
    links.new(shader.inputs['Normal'].links[0].from_socket, bump.inputs['Normal'])
    links.new(bump.outputs['Normal'], shader.inputs['Normal'])
    # Give the grooves a small pigment contrast so they read in soft light.
    gain = nodes.new('ShaderNodeMixRGB')
    gain.inputs[1].default_value = (.83, .75, .71, 1)
    gain.inputs[2].default_value = (1, 1, 1, 1)
    links.new(ramp.outputs['Color'], gain.inputs[0])
    tint = nodes.new('ShaderNodeMixRGB')
    tint.blend_type = 'MULTIPLY'
    links.new(lip.outputs['Color'], tint.inputs[0])
    links.new(shader.inputs['Base Color'].links[0].from_socket, tint.inputs[1])
    links.new(gain.outputs[0], tint.inputs[2])
    links.new(tint.outputs[0], shader.inputs['Base Color'])

    x, y, z = coords(head.data.vertices).T
    orbital = smooth((np.abs(x)-.025)/.016)*smooth((.064-np.abs(x))/.019)
    orbital *= np.exp(-((y-.297)/.010)**2)*smooth((z-.065)/.032)
    mask = head.data.attributes.new('Fine periocular crease mask', 'FLOAT', 'POINT')
    mask.data.foreach_set('value', orbital.astype(np.float32))
    attr = nodes.new('ShaderNodeAttribute')
    attr.attribute_name = mask.name
    direction = nodes.new('ShaderNodeVectorMath')
    direction.operation = 'MULTIPLY'
    direction.inputs[1].default_value = (150, 1600, 220)
    links.new(texture.outputs['Object'], direction.inputs[0])
    detail = nodes.new('ShaderNodeTexNoise')
    detail.inputs['Scale'].default_value = 1
    detail.inputs['Detail'].default_value = 2
    links.new(direction.outputs[0], detail.inputs['Vector'])
    crease = nodes.new('ShaderNodeBump')
    crease.label = 'Fine creases at the outer and lower lids'
    crease.inputs['Distance'].default_value = .000104
    links.new(product(nodes, links, attr.outputs['Fac'], .48), crease.inputs['Strength'])
    links.new(detail.outputs['Fac'], crease.inputs['Height'])
    links.new(bump.outputs['Normal'], crease.inputs['Normal'])
    links.new(crease.outputs['Normal'], shader.inputs['Normal'])


def lash_shape(scene):
    rng = np.random.default_rng(6493)
    data = scene.objects['Portrait | subtle upper lashes'].data
    positions = data.attributes['position'].data
    flat = np.empty(len(positions)*3, dtype=np.float32)
    positions.foreach_get('vector', flat)
    rows = flat.reshape(-1, 6, 3)
    roots = rows[:, 0].copy()
    t = np.linspace(0, 1, 6)
    outer = smooth((abs(roots[:, 0])-.020)/.023)
    length = rng.uniform(.0031, .0054, len(rows))*(.80+.35*outer)
    splay = np.sign(roots[:, 0])*(.10+.40*outer)
    rows[:, :, 0] = roots[:, 0, None]+length[:, None]*splay[:, None]*t**1.4
    rows[:, :, 1] = roots[:, 1, None]+length[:, None]*(.04*t+.53*t**2.5)
    rows[:, :, 2] = roots[:, 2, None]+length[:, None]*(.88*t-.15*t**3)
    positions.foreach_set('vector', flat)
    radii = rng.uniform(.000030, .000044, len(rows))[:, None]*(1-t*.98)**.73
    data.attributes['radius'].data.foreach_set('value', radii.astype(np.float32).ravel())


def fuller_brows(scene, head, tree):
    rng = np.random.default_rng(16041)
    t = np.linspace(0, 1, 6)
    points, radii = [], []
    for side in (-1, 1):
        for u in rng.beta(1.35, 2.0, 800):
            x = side * (.014 + .040*u)
            center_y = .316639 + .004*np.sin(np.pi*u) - .002*u*u
            spread = (.0022 - .00165*u*u)
            y = center_y + rng.uniform(-1, 1)*spread - .00033
            length = rng.uniform(.0017, .0034)*(1-.25*u)
            dx = side * (.40+.60*u)*length
            dy = (.75-.94*u)*length
            row = []
            for step in t:
                ray = Vector((x+dx*step, y+dy*step, .3))
                hit, normal, _, _ = tree.ray_cast(ray, Vector((0, 0, -1)))
                if hit is None:
                    break
                row.append(np.asarray(hit+normal*(.00004+.00020*np.sin(.85*np.pi*step))))
            if len(row) == len(t):
                points.append(row)
                radii.append(rng.uniform(.000019, .000032)*(1-.94*t)**.7)
    material = scene.objects['Portrait | fitted directional brows'].data.materials[0]
    return strands('Portrait | fuller brow fibers', head, np.array(points), np.array(radii), material)


def groom_shape(scene, tree):
    hair = scene.objects['Portrait | swept chestnut hair'].data
    data = hair.attributes['position'].data
    flat = np.empty(len(data)*3, dtype=np.float32)
    data.foreach_get('vector', flat)
    rows = flat.reshape(-1, 12, 3)
    x, y, z = rows[:, 0].T
    weight = smooth((y-.343)/.030)
    # Bring down the broad quiff and vary the direction of its locks.
    t = np.linspace(0, 1, rows.shape[1])
    spread = (.0028*np.sin(x*112+z*73)+.0017*np.sin(x*259-z*104))*weight
    for i in np.flatnonzero(weight > .01):
        row = rows[i]
        for j in range(1, len(row)):
            source = Vector(row[j])
            hit, normal, _, _ = tree.find_nearest(source)
            lift = (source-hit).dot(normal)
            if lift > .0002:
                row[j] -= np.asarray(normal)*lift*.32*weight[i]
            row[j, 0] += spread[i]*np.sin(np.pi*t[j])
    data.foreach_set('vector', flat)
    material = hair.materials[0]
    shader = next(node for node in material.node_tree.nodes if node.type == 'BSDF_HAIR_PRINCIPLED')
    shader.inputs['Radial Roughness'].default_value = .56


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    path = out/'portrait.blend'
    if path.exists():
        raise FileExistsError(path)
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    tree = expression_anatomy(scene, head)
    finish_skin(head)
    lash_shape(scene)
    fuller_brows(scene, head, tree)
    groom_shape(scene, tree)
    scene.render.use_border = False
    aim(scene.camera, (.40, -.72, .03), (0, 0, -.025))
    scene.camera.data.lens = 85
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
    render(scene, out, 'three-quarter', 850, 32)
    aim(scene.camera, (0, -.82, .03), (0, 0, -.025))
    scene.camera.data.lens = 85
    render(scene, out, 'front', 850, 32)
    aim(scene.camera, (.23, -.52, .018), (0, 0, -.024))
    scene.camera.data.lens = 120
    scene.render.use_border = True
    scene.render.use_crop_to_border = True
    scene.render.border_min_x = .16
    scene.render.border_max_x = .89
    scene.render.border_min_y = .10
    scene.render.border_max_y = .80
    render(scene, out, 'detail', 950, 32)


if __name__ == '__main__':
    main()
