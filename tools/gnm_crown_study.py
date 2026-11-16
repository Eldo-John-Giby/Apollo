"""Render a shorter, loosely side-parted crown on the fuller-brow portrait."""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_portrait_refine import aim, render, skin_tree, smooth


def restyle(head, scalp):
    evaluated = head.evaluated_get(bpy.context.evaluated_depsgraph_get())
    tree = skin_tree(head, np.array([vertex.co[:] for vertex in evaluated.data.vertices]))
    attr = scalp.data.attributes['position'].data
    flat = np.empty(len(attr)*3, dtype=np.float32)
    attr.foreach_get('vector', flat)
    curves = flat.reshape(-1, 12, 3)
    root_x, root_y, root_z = curves[:, 0].T
    crown = smooth((root_y-.357)/.025)
    rng = np.random.default_rng(21999)
    part_x = -.020 + .15*(root_z-.125)
    branch = np.tanh((root_x-part_x)/.005)
    lock_phase = 370*root_x + 140*root_z + 1.3*np.sin(117*root_z)
    lock = np.sin(lock_phase)
    strand_length = np.clip(.74+.11*lock+rng.normal(0,.10,len(curves)), .43, 1)
    steps = np.linspace(0, 1, curves.shape[1])
    for i in np.flatnonzero(crown > .02):
        row = curves[i].copy()
        strength = crown[i]
        shortened = steps*(1-strength*(1-strand_length[i]))
        path = np.column_stack([np.interp(shortened, steps, v) for v in row.T])
        for j, t in enumerate(steps[1:], 1):
            origin = Vector(path[j])
            hit, normal, _, _ = tree.find_nearest(origin)
            lift = max(.00012, (origin-hit).dot(normal))
            # Break the uniform sweep into unequal locks either side of the part.
            shift = strength*t*(.011*(branch[i]-1)+.004*lock[i])
            hit, normal, _, _ = tree.find_nearest(hit+Vector((shift, 0, 0)))
            envelope = .00045*np.sin(np.pi*t)
            height = lift*(1-strength*(.22-.18*lock[i])) + envelope
            curves[i, j] = hit+normal*float(height)
    attr.foreach_set('vector', flat)

    nodes = scalp.data.materials[0].node_tree.nodes
    links = scalp.data.materials[0].node_tree.links
    shader = next(node for node in nodes if node.type == 'BSDF_HAIR_PRINCIPLED')
    shader.inputs['Roughness'].default_value = .42
    random = nodes.new('ShaderNodeHairInfo')
    tone = nodes.new('ShaderNodeValToRGB')
    tone.color_ramp.elements[0].color = (.94, 1.77, 2.67, 1)
    tone.color_ramp.elements[1].color = (1.62, 2.56, 3.64, 1)
    links.new(random.outputs['Random'], tone.inputs['Fac'])
    links.new(tone.outputs['Color'], shader.inputs['Absorption Coefficient'])


def feather_hairline(head, grooms):
    evaluated = head.evaluated_get(bpy.context.evaluated_depsgraph_get())
    tree = skin_tree(head, np.array([vertex.co[:] for vertex in evaluated.data.vertices]))
    rng = np.random.default_rng(43085)
    for groom, points_per_strand in grooms:
        attributes = groom.data.attributes
        positions = np.empty((len(groom.data.points), 3), dtype=np.float32)
        radii = np.empty(len(positions), dtype=np.float32)
        attributes['position'].data.foreach_get('vector', positions.ravel())
        attributes['radius'].data.foreach_get('value', radii)
        curves = positions.reshape(-1, points_per_strand, 3)
        strand_radii = radii.reshape(-1, points_per_strand)
        x, y, z = curves[:, 0].T
        side = smooth((abs(x)-.047)/.035)
        front = smooth((z-.079)/.025)
        edge = .373139-.055*side
        distance = y-edge
        influence = front*np.exp(-(distance/.012)**2)
        # Broad asymmetry at the temples, with small irregular groups in between.
        offset = .0027*np.sin(93*x+.85)+.0012*np.sin(390*x-.4)
        offset += .00055*np.sin(970*x+.7) + rng.normal(0,.0013,len(curves))
        taper = np.linspace(1,.14,points_per_strand)
        for i in np.flatnonzero(influence > .10):
            delta = influence[i]*offset[i]
            for j, point in enumerate(curves[i]):
                current = Vector(point)
                surface, normal, _, _ = tree.find_nearest(current)
                height = max(.00002, (current-surface).dot(normal))
                surface, normal, _, _ = tree.find_nearest(
                    surface+Vector((0, delta*taper[j], 0)))
                point[:] = surface+normal*height
            feather = influence[i]*(1-smooth((distance[i]+.002)/.011))
            strand_radii[i] *= 1-.37*feather
        attributes['position'].data.foreach_set('vector', positions.ravel())
        attributes['radius'].data.foreach_set('value', radii)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--hairline-only', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    path = out/'portrait.blend'
    if path.exists():
        raise FileExistsError(path)
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    scalp = scene.objects['Portrait | swept chestnut hair']
    if args.hairline_only:
        feather_hairline(head, ((scalp, 12), (scene.objects['Peak | front hairline fibers'], 7)))
    else:
        restyle(head, scalp)
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
    render(scene, out, 'three-quarter', 850, 32)
    aim(scene.camera, (0, -.82, .03), (0, 0, -.025))
    render(scene, out, 'front', 850, 32)


if __name__ == '__main__':
    main()
