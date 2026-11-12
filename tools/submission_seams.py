"""Bake and rebind a texture set after introducing new UV seams on the local rig."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from submission_bake import bake
from submission_textures import apply_variant, fingerprint
from submission_uv_rehearsal import clone, pixels


def repack(mesh, name, cut):
    uv = mesh.uv_layers[name]
    groups = {}
    source, target = [], []
    for polygon in mesh.polygons:
        ids = list(polygon.loop_indices)
        corners = [tuple(uv.data[index].uv) for index in ids]
        u, v = (sum(values) / len(values) for values in zip(*corners))
        tile = int(v >= cut)
        offset = .025 + .5 * tile
        source.append((u, v))
        target.append((.45 * u + offset, .9 * v + .05))
        for start, end in zip(ids, ids[1:] + ids[:1]):
            a, b = mesh.loops[start].vertex_index, mesh.loops[end].vertex_index
            pair = sorted(((a, tuple(uv.data[start].uv)), (b, tuple(uv.data[end].uv))))
            edge = tuple((vertex, round(x, 6), round(y, 6)) for vertex, (x, y) in pair)
            groups.setdefault(edge, set()).add(tile)
        for index, (u0, v0) in zip(ids, corners):
            uv.data[index].uv = (.45 * u0 + offset, .9 * v0 + .05)
    # Edge endpoint UVs must be read before any loop of that polygon changes.
    seams = sum(len(tiles) == 2 for tiles in groups.values())
    return uv, np.asarray(source), np.asarray(target), seams


def sample(image, coordinates):
    h, w, _ = image.shape
    xy = np.clip(coordinates, 0., 1.) * (w, h) - .5
    xy = np.clip(xy, (0, 0), (w - 1, h - 1))
    x, y = xy.astype(int).T
    fx, fy = (xy - xy.astype(int)).T[:, :, None]
    xx, yy = np.minimum(x + 1, w - 1), np.minimum(y + 1, h - 1)
    return (image[y, x] * (1 - fx) * (1 - fy) + image[y, xx] * fx * (1 - fy)
            + image[yy, x] * (1 - fx) * fy + image[yy, xx] * fx * fy)


def transfer(obj, uv_name, cut, directory, role, repacked, size):
    source = clone(obj, f'{role} source')
    target = clone(obj, f'{role} target')
    file = directory / f"{role}{'' if repacked else '-reference'}.png"
    try:
        layout = repack(target.data, uv_name, cut) if repacked else None
        bake(SimpleNamespace(source=source.name, target=target.name, uv=uv_name,
                             out=file, size=size, cage=.00035, distance=.001,
                             margin_type='EXTEND'))
        sig = fingerprint(target.data, target.data.uv_layers[uv_name])
        return file, layout, sig
    finally:
        for item in (source, target):
            bpy.data.objects.remove(item, do_unlink=True)


def run(out, variant, size):
    out.mkdir(parents=True, exist_ok=False)
    source_scene = bpy.data.filepath
    apply_variant(variant)
    original = json.loads(variant.read_text(encoding='utf-8'))
    report = {}
    bindings = []
    for entry in original['maps']:
        role, uv_name = entry['role'], entry['uv']
        obj = bpy.context.scene.objects[entry['object']]
        cut = .483 if role == 'face' else .5
        ref, _, ref_sig = transfer(obj, uv_name, cut, out, role, False, size)
        mapped, (_, source_uv, new_uv, seams), sig = transfer(obj, uv_name, cut, out, role,
                                                            True, 2 * size)
        if seams == 0 or sig == ref_sig:
            raise ValueError(f'{role} did not acquire new seams')
        a, b = sample(pixels(ref), source_uv), sample(pixels(mapped), new_uv)
        expected = a.max(axis=1) > .02
        covered = expected & (b.max(axis=1) > .02)
        count = int(expected.sum())
        coverage = int(covered.sum()) / count if count else 0.
        error = float(np.abs(a[covered] - b[covered]).mean()) if covered.any() else 1.
        if coverage < .98 or error > .035:
            raise ValueError(f'{role} failed seam transfer: coverage={coverage:.4f}, MAE={error:.4f}')
        report[role] = {'introduced_seam_edges': seams, 'source_uv_sha256': ref_sig,
                        'target_uv_sha256': sig, 'source_samples': count,
                        'sample_coverage': coverage, 'color_mae': error}
        bindings.append({'role': role, 'object': obj.name, 'uv': uv_name, 'slot': entry['slot'],
                         'all_slots': entry.get('replace_on_all_slots', False),
                         'mesh_uv_sha256': sig, 'file': mapped.name,
                         'sha256': hashlib.sha256(mapped.read_bytes()).hexdigest()})
    bpy.ops.wm.open_mainfile(filepath=source_scene)
    for entry in bindings:
        obj = bpy.context.scene.objects[entry['object']]
        repack(obj.data, entry['uv'], .483 if entry['role'] == 'face' else .5)
    manifest = out / 'variant.json'
    manifest.write_text(json.dumps({'target': 'MPFB with split and repacked UVs',
                                    'provenance': original['provenance'], 'maps': bindings},
                                   indent=2) + '\n', encoding='utf-8')
    apply_variant(manifest)
    for entry in bindings:
        obj = bpy.context.scene.objects[entry['object']]
        if fingerprint(obj.data, obj.data.uv_layers[entry['uv']]) != entry['mesh_uv_sha256']:
            raise RuntimeError('Applying the texture changed its target UVs')
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'rebound.blend'), compress=True)
    scene = bpy.context.scene
    scene.cycles.device = 'CPU'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(out / 'rebound.png')
    bpy.ops.render.render(write_still=True)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--variant', required=True, type=Path)
    parser.add_argument('--size', type=int, default=1024)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if args.size < 128:
        parser.error('Use a reference size of at least 128 pixels')
    run(args.out.resolve(), args.variant.resolve(), args.size)


if __name__ == '__main__':
    main()
