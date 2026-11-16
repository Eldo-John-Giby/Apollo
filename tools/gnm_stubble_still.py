"""Compare two levels of surface-fitted beard stubble in a still portrait."""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_portrait_refine import aim, fiber_material, render, skin_tree, smooth, strands


def beard_density(points):
    x, y, z = points.T
    x = np.abs(x)
    cheek = np.exp(-((x - .051) / .018)**2 - ((y - .231) / .023)**2)
    chin = np.exp(-(x / .030)**2 - ((y - .209) / .014)**2)
    lip_clearance = 1 - smooth((.031 - x) / .010) * smooth((y - .217) / .007)
    anterior = smooth((z - .044) / .030)
    return np.maximum(.67 * cheek, chin) * lip_clearance * anterior


def lift_baked_shadow(head):
    positions = np.array([v.co[:] for v in head.data.vertices])
    attribute = head.data.attributes.new('Beard pigment lift', 'FLOAT', 'POINT')
    attribute.data.foreach_set('value', beard_density(positions).astype(np.float32))
    tree = head.data.materials[0].node_tree
    shader = next(node for node in tree.nodes if node.type == 'BSDF_PRINCIPLED')
    color = shader.inputs['Base Color']
    mask = tree.nodes.new('ShaderNodeAttribute')
    mask.attribute_name = attribute.name
    gain = tree.nodes.new('ShaderNodeMath')
    gain.operation = 'MULTIPLY_ADD'
    gain.inputs[1].default_value = .30
    gain.inputs[2].default_value = 1
    tree.links.new(mask.outputs['Fac'], gain.inputs[0])
    mix = tree.nodes.new('ShaderNodeMixRGB')
    mix.label = 'Ease baked beard shadow'
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 1
    tree.links.new(color.links[0].from_socket, mix.inputs[1])
    tree.links.new(gain.outputs[0], mix.inputs[2])
    tree.links.new(mix.outputs[0], color)


def build_stubble(head):
    evaluated = head.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    positions = np.array([v.co[:] for v in mesh.vertices])
    mesh.calc_loop_triangles()
    triangles = np.array([t.vertices[:] for t in mesh.loop_triangles if t.material_index == 0])
    evaluated.to_mesh_clear()
    tree = skin_tree(head, positions)
    vertices = positions[triangles]
    areas = np.linalg.norm(np.cross(vertices[:, 1] - vertices[:, 0], vertices[:, 2] - vertices[:, 0]), axis=1)
    candidates = beard_density(vertices.mean(axis=1)) > .025
    vertices, areas = vertices[candidates], areas[candidates]
    rng = np.random.default_rng(79941)
    chosen = rng.choice(len(vertices), 18000, p=areas / areas.sum())
    uv = rng.random((len(chosen), 2))
    uv = np.where((uv.sum(axis=1) > 1)[:, None], 1 - uv, uv)
    weights = np.column_stack((1 - uv.sum(axis=1), uv))
    roots = (vertices[chosen] * weights[..., None]).sum(axis=1)
    density = beard_density(roots)
    roots = roots[rng.random(len(roots)) < density]
    fitted, normals = [], []
    for root in roots:
        point, normal, _, _ = tree.find_nearest(Vector(root))
        if point is not None and normal.z > .10:
            fitted.append(point)
            normals.append(normal)
    normals = np.array(normals)
    fitted = np.array(fitted)
    tangent = np.tile((0., -1., 0.), (len(fitted), 1))
    tangent -= normals * np.sum(tangent * normals, axis=1)[:, None]
    tangent /= np.maximum(np.linalg.norm(tangent, axis=1)[:, None], 1e-9)
    t = np.linspace(0, 1, 4)
    length = rng.uniform(.00016, .00052, len(fitted))
    direction = normals[:, None, :] * (.68 * t)[None, :, None]
    direction += tangent[:, None, :] * (.75 * t ** 1.4)[None, :, None]
    points = (fitted + normals * .00001)[:, None, :] + direction * length[:, None, None]
    radii = rng.uniform(.000013, .000024, len(fitted))[:, None] * (1 - .88 * t)
    material = fiber_material('Portrait | beard stubble', .8)
    split = len(points) // 2
    light = strands('Peak | short beard stubble', head, points[:split], radii[:split], material)
    extra = strands('Peak | denser beard stubble', head, points[split:], radii[split:], material)
    return light, extra


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--balance-pigment', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    destination = out / 'portrait.blend'
    if destination.exists():
        raise FileExistsError(destination)
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    light, extra = build_stubble(head)
    print(f'Light stubble: {len(light.data.curves)}. Extra stubble: {len(extra.data.curves)}.', flush=True)
    aim(scene.camera, (.40, -.72, .03), (0, 0, -.025))
    scene.camera.data.lens = 85
    if args.balance_pigment:
        lift_baked_shadow(head)
        bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
        render(scene, out, 'three-quarter', 850, 32)
        return
    extra.hide_render = True
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
    render(scene, out, 'light', 850, 32)
    extra.hide_render = False
    render(scene, out, 'dense', 850, 32)
    light.hide_render = extra.hide_render = True
    render(scene, out, 'baseline', 850, 32)


if __name__ == '__main__':
    main()
