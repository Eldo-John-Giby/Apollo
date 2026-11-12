"""Exercise face and eye color transfer onto a fresh, differently unwrapped local rig."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import bmesh
import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from submission_bake import bake
from submission_textures import apply_variant, fingerprint


def clone(obj, name):
    copy = obj.copy()
    copy.data = obj.data.copy()
    copy.name = name
    bpy.context.scene.collection.objects.link(copy)
    return copy


def change_uv(uv):
    for loop in uv.data:
        loop.uv = (1 - loop.uv.x, 1 - loop.uv.y)


def change_topology(mesh):
    # Keep the UVs interpolated while changing connectivity and the surface.
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=list(bm.faces))
        bm.normal_update()
        for vertex in bm.verts:
            vertex.co += .00008 * vertex.normal
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()


def prepare_target(obj, uv_name, changed_geometry):
    if changed_geometry:
        change_topology(obj.data)
    uv = obj.data.uv_layers[uv_name]
    change_uv(uv)
    return uv


def pixels(path):
    image = bpy.data.images.load(str(path))
    try:
        w, h = image.size
        return np.asarray(image.pixels[:], dtype=np.float32).reshape(h, w, 4)[..., :3]
    finally:
        bpy.data.images.remove(image)


def bake_copy(obj, role, uv_name, out, size, rotated, changed_geometry=False):
    source = clone(obj, f'{role} source')
    target = clone(obj, f'{role} target')
    try:
        uv = (prepare_target(target, uv_name, changed_geometry) if rotated
              else target.data.uv_layers[uv_name])
        sig = fingerprint(target.data, uv)
        # The fixture is only 80 microns off the source. A short cage
        # avoids picking up the opposite lid or lip on a nearby surface.
        cage, distance = (.00035, .001) if changed_geometry else (.002, .008)
        bake(SimpleNamespace(source=source.name, target=target.name, uv=uv_name,
                             out=out, size=size, cage=cage, distance=distance,
                             margin_type='EXTEND' if changed_geometry else 'ADJACENT_FACES'))
        return sig, len(target.data.polygons)
    finally:
        for copy in (source, target):
            bpy.data.objects.remove(copy, do_unlink=True)


def run(out, variant, size, changed_geometry=False):
    out.mkdir(parents=True, exist_ok=False)
    pristine = bpy.data.filepath
    original = json.loads(variant.read_text(encoding='utf-8'))
    apply_variant(variant)
    bindings = []
    results = {}
    for entry in original['maps']:
        role, uv_name = entry['role'], entry['uv']
        obj = bpy.context.scene.objects[entry['object']]
        baseline = out / f'{role}-reference.png'
        transfer = out / f'{role}.png'
        reference_sig, source_faces = bake_copy(obj, role, uv_name, baseline, size, False, changed_geometry)
        target_sig, target_faces = bake_copy(obj, role, uv_name, transfer, size, True,
                                             changed_geometry)
        if changed_geometry and target_faces <= source_faces:
            raise RuntimeError(f'{role} did not change mesh topology')
        if target_sig == reference_sig:
            raise RuntimeError(f'{role} did not change UV layouts')
        first, second = pixels(baseline), pixels(transfer)[::-1, ::-1]
        # Compare only texels covered in both bakes. Test overlap separately
        # so a missing island or mostly empty bake cannot pass on color error.
        a = first.max(axis=2) > .02
        b = second.max(axis=2) > .02
        union = np.count_nonzero(a | b)
        overlap = np.count_nonzero(a & b) / union if union else 0.
        if overlap < .98:
            raise RuntimeError(f'{role} baked coverage overlap {overlap:.3f} < 0.98')
        mae = float(np.abs(first[a & b] - second[a & b]).mean())
        if mae > .02:
            raise RuntimeError(f'{role} baked color MAE {mae:.4f} > 0.02')
        results[role] = {'source_uv_sha256': reference_sig, 'target_uv_sha256': target_sig,
                         'source_faces': source_faces, 'target_faces': target_faces,
                         'coverage_overlap': overlap, 'color_mae': mae}
        bindings.append({'role': role, 'object': obj.name, 'uv': uv_name,
                         'slot': entry['slot'], 'all_slots': entry.get('replace_on_all_slots', False),
                         'mesh_uv_sha256': target_sig, 'file': transfer.name,
                         'sha256': hashlib.sha256(transfer.read_bytes()).hexdigest()})
    bpy.ops.wm.open_mainfile(filepath=pristine)
    for binding in bindings:
        obj = bpy.context.scene.objects[binding['object']]
        prepare_target(obj, binding['uv'], changed_geometry)
    manifest = out / 'variant.json'
    label = ('Subdivided and triangulated MPFB with rotated UV coordinates'
             if changed_geometry else 'MPFB with rotated UV coordinates')
    manifest.write_text(json.dumps({'target': label,
                                    'provenance': original['provenance'], 'maps': bindings},
                                   indent=2) + '\n', encoding='utf-8')
    apply_variant(manifest)
    for binding in bindings:
        obj = bpy.context.scene.objects[binding['object']]
        if fingerprint(obj.data, obj.data.uv_layers[binding['uv']]) != binding['mesh_uv_sha256']:
            raise RuntimeError(f"{obj.name} UVs changed during assignment")
        slots = obj.material_slots if binding['all_slots'] else [obj.material_slots[binding['slot']]]
        for slot in slots:
            image = next(n.image for n in slot.material.node_tree.nodes if n.type == 'TEX_IMAGE')
            if Path(bpy.path.abspath(image.filepath)).resolve() != out / binding['file']:
                raise RuntimeError(f'{obj.name} was not bound to the transferred map')
    scene = bpy.context.scene
    scene.cycles.device = 'CPU'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(out / 'rebound.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'rebound.blend'), compress=True)
    (out / 'report.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(results, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--size', type=int, default=2048)
    parser.add_argument('--changed-geometry', action='store_true',
                        help='Subdivide, triangulate and offset the local target surface')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    run(args.out.resolve(), args.variant.resolve(), args.size, args.changed_geometry)


if __name__ == '__main__':
    main()
