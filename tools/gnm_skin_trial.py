"""Prepare a disposable aligned MPFB source and bake a GNM skin map."""
import argparse
from pathlib import Path
import sys
from types import SimpleNamespace

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from submission_bake import bake
from submission_textures import apply_variant


def skin_only(head):
    mesh = head.data.copy()
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index != 0],
                         context='FACES')
        loose = [v for v in bm.verts if not v.link_faces]
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
        bm.to_mesh(mesh)
    finally:
        bm.free()
    target = bpy.data.objects.new('GNM skin receiver', mesh)
    bpy.context.scene.collection.objects.link(target)
    target.matrix_world = head.matrix_world
    return target


def run(args):
    apply_variant(args.variant)
    source = bpy.context.scene.objects['Apollo_Face']
    # Fit the neutral MPFB proportion to the public GNM head. The mouth
    # and lower face sit lower relative to the eye midpoint on GNM.
    transform = source.matrix_world.copy()
    inverse = transform.inverted()
    # Bake the disposable base surface without evaluating the original
    # rig or shape-key deformation.
    source.shape_key_clear()
    source.modifiers.clear()
    for vertex in source.data.vertices:
        x, y, z = transform @ vertex.co
        vertex.co = inverse @ Vector((x * .98, y * 1.12 + .002,
                                      z * (1.16 if z < 0 else 1.03)))
    with bpy.data.libraries.load(str(args.gnm.resolve()), link=False) as (incoming, loaded):
        if 'GNM Head' not in incoming.objects:
            raise ValueError('GNM Head object missing from the neutral template')
        loaded.objects = ['GNM Head']
    head = loaded.objects[0]
    bpy.context.scene.collection.objects.link(head)
    bpy.context.view_layer.update()
    target = skin_only(head)
    bpy.data.objects.remove(head, do_unlink=True)
    bpy.context.view_layer.update()
    bpy.context.scene.cycles.samples = 1
    bake(SimpleNamespace(source=source.name, target=target.name, uv='GNM Region',
                         out=args.out, size=args.size, cage=args.cage, distance=args.distance,
                         margin_type='EXTEND'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gnm', type=Path, required=True)
    parser.add_argument('--variant', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--size', type=int, default=2048)
    parser.add_argument('--cage', type=float, default=.035)
    parser.add_argument('--distance', type=float, default=.115)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if not 0 < args.cage < args.distance:
        parser.error('Expected 0 < cage < distance')
    run(args)
