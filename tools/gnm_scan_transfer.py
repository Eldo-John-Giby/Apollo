"""Register the attributed 4K Infinite Scan source and bake unchanged GNM UVs.

Build-time dependencies: Blender, NumPy, SciPy and Pillow. Runtime scenes need
Blender alone. The source model is deformed; the GNM receiver is never changed.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_mesh(source, out):
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str((source / 'Head.fbx').resolve()))
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if len(objects) != 1:
        raise ValueError('Expected exactly one pinned scan mesh')
    obj = objects[0]
    obj.data.calc_loop_triangles()
    faces = np.array([triangle.vertices[:] for triangle in obj.data.loop_triangles])
    uv = np.array([[obj.data.uv_layers.active.data[i].uv[:]
                    for i in triangle.loops] for triangle in obj.data.loop_triangles])
    vertices = np.array([obj.matrix_world @ v.co for v in obj.data.vertices])
    np.savez_compressed(out / 'source-mesh.npz', vertices=vertices, triangles=faces, uv=uv)


def align(template, out):
    from scipy.interpolate import LinearNDInterpolator, RBFInterpolator
    with np.load(out / 'source-mesh.npz') as scan:
        vertices = scan['vertices'][:, [0, 2, 1]] * (1, 1, -1)
        faces, uv = scan['triangles'], scan['uv']
    lookup = LinearNDInterpolator(uv.reshape(-1, 2), vertices[faces].reshape(-1, 3))
    # Reviewed on the original albedo: canthi, brow peaks, nose tip/wings,
    # mouth corners, upper/lower lip center and chin. Coordinates are scan UVs.
    landmarks = np.array([
        [.393, .704], [.454, .704], [.547, .704], [.608, .704],
        [.430, .749], [.570, .749], [.497, .599], [.466, .584], [.531, .584],
        [.443, .533], [.554, .533], [.500, .551], [.500, .513], [.500, .449]])
    source = lookup(landmarks)
    if not np.isfinite(source).all():
        raise ValueError('Scan landmarks fall outside the pinned UV surface')
    with np.load(template) as data:
        eye = np.mean([data['joints'][list(data['joint_names']).index(f'{s}_eye')]
                       for s in ('left', 'right')], axis=0)
        p = data['vertices'] - eye
        eye_distance = np.linalg.norm(data['joints'][list(data['joint_names']).index('left_eye')]
                                      - data['joints'][list(data['joint_names']).index('right_eye')])
        scale = eye_distance / abs((source[0, 0] + source[1, 0] - source[2, 0] - source[3, 0]) / 2)
        center = source[:4].mean(axis=0)
        vertices, source = (vertices - center) * scale, (source - center) * scale
        faces_skin = data['quads'][np.all(data['skin_exterior'][data['quads']], axis=1)]
        counts = Counter(tuple(sorted(e)) for face in faces_skin for e in zip(face, np.roll(face, -1)))
        boundary = np.array(sorted({i for edge, count in counts.items() if count == 1 for i in edge}))
        targets = []
        for side in ('right', 'left'):
            pivot = data['joints'][list(data['joint_names']).index(f'{side}_eye')] - eye
            rim = boundary[(abs(p[boundary, 0] - pivot[0]) < .019)
                           & (abs(p[boundary, 1]) < .012) & (p[boundary, 2] > .005)]
            if len(rim) < 20:
                raise ValueError('Target is not the supported GNM eye topology')
            targets.extend((p[rim[np.argmin(p[rim, 0])]], p[rim[np.argmax(p[rim, 0])]]))
        targets = list(np.array(targets)[np.argsort(np.array(targets)[:, 0])])
        for x, y in ((-.032, .020), (.032, .020), (0, -.026), (-.013, -.039), (.013, -.039),
                     (-.024, -.071), (.024, -.071), (0, -.063), (0, -.080), (0, -.106)):
            if y == -.071:
                ids = np.flatnonzero(data['upper_lip'])
                index = np.argmin(p[ids, 0]) if x < 0 else np.argmax(p[ids, 0])
            elif y in (-.063, -.080):
                ids = np.flatnonzero(data['upper_lip' if y == -.063 else 'lower_lip'] & (abs(p[:, 0]) < .002))
                index = np.argmax(p[ids, 1]) if y == -.063 else np.argmin(p[ids, 1])
            else:
                ids = np.flatnonzero((abs(p[:, 0] - x) < .004) & (abs(p[:, 1] - y) < .004))
                index = np.argmax(p[ids, 2])
            targets.append(p[ids[index]])
    targets = np.array(targets)
    if source[0, 0] > source[3, 0]:
        vertices[:, 0] *= -1
        source[:, 0] *= -1
    # Peripheral constraints keep the scalp/neck stable under central fitting.
    ids = np.flatnonzero((vertices[:, 2] < -.015) | (vertices[:, 1] > .075) | (vertices[:, 1] < -.135))
    ids = ids[::max(1, len(ids) // 90)]
    anchors = np.vstack((source, vertices[ids]))
    destinations = np.vstack((targets, vertices[ids]))
    warp = RBFInterpolator(anchors, destinations - anchors, kernel='thin_plate_spline', smoothing=1e-7)
    aligned = vertices + warp(vertices)
    np.savez_compressed(out / 'aligned.npz', vertices=aligned + eye, triangles=faces, uv=uv)
    return {'scan_uv_landmarks': landmarks.tolist(), 'source_landmarks_m': source.tolist(),
            'target_landmarks_m': targets.tolist(), 'source_scale': float(scale),
            'fit_smoothing': 1e-7, 'target_mesh_changed': False}


def bake_scan(source, out, size):
    import bpy
    from types import SimpleNamespace
    from gnm_skin_trial import skin_only
    from submission_bake import bake
    head = bpy.context.scene.objects['GNM Head']
    with np.load(out / 'aligned.npz') as data:
        mesh = bpy.data.meshes.new('Disposable aligned scan')
        mesh.from_pydata(data['vertices'].tolist(), [], data['triangles'].tolist())
        mesh.update()
        mesh.uv_layers.new(name='Scan UV').data.foreach_set('uv', data['uv'].ravel())
    mesh.polygons.foreach_set('use_smooth', np.ones(len(mesh.polygons), dtype=bool))
    obj = bpy.data.objects.new('Disposable aligned scan', mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.matrix_world = head.matrix_world.copy()
    material = bpy.data.materials.new('Attributed scan albedo')
    material.use_nodes = True
    tex = material.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(str((source / 'lambertian.jpg').resolve()))
    material.node_tree.links.new(tex.outputs['Color'], material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
    mesh.materials.append(material)
    target = skin_only(head)
    bpy.data.objects.remove(head, do_unlink=True)
    bpy.context.view_layer.update()
    bake(SimpleNamespace(source=obj.name, target=target.name, uv='GNM Region',
                         out=out / 'scan-raw.png', size=size, cage=.035, distance=.115, margin_type='EXTEND'))


def compose(template, fallback, out, size):
    import cv2
    from PIL import Image
    from scipy.ndimage import distance_transform_edt
    from gnm_surface_maps import smooth
    scan = np.asarray(Image.open(out / 'scan-raw.png').convert('RGB'), dtype=np.float32)
    base = np.asarray(Image.open(fallback).convert('RGB'), dtype=np.float32)
    if base.shape != scan.shape:
        raise ValueError('Fallback must be a raw projection at the same resolution')
    with np.load(template) as data:
        uv = data['legacy'][data['tiles'] == 1001]
    coordinates = np.rint(uv * (size - 1, -(size - 1)) + (0, size - 1)).astype(np.int32)
    mask = np.zeros((size, size), dtype=np.uint8)
    for quad in coordinates:
        cv2.fillConvexPoly(mask, quad, 1)
    hit, base_hit = scan.max(-1) > 5, base.max(-1) > 5
    distance, nearest = distance_transform_edt(~hit, return_indices=True)
    near_scan, near_base = scan[tuple(nearest)], base[tuple(nearest)]
    gain = np.clip(near_scan / np.maximum(near_base, 10), .5, 2)
    blend = smooth(distance / (32 * size / 2048)) * base_hit
    composite = near_scan * (1 - blend[..., None]) + base * gain * blend[..., None]
    composite[hit] = scan[hit]
    Image.fromarray(np.clip(np.rint(composite), 0, 255).astype(np.uint8)).save(out / 'color.1001.png')
    missing = mask.astype(bool) & ~(hit | base_hit)
    coverage = {'expected_texels': int(mask.sum()), 'filled_texels': int(missing.sum()),
                'projection_coverage': 1 - float(missing.sum() / mask.sum()),
                'scan_projection_coverage': float(np.count_nonzero(hit & mask.astype(bool)) / mask.sum()),
                'fallback_texels': int(np.count_nonzero(mask.astype(bool) & ~hit & base_hit)),
                'max_fill_distance_px': float(distance[missing].max()) if missing.any() else 0.,
                'method': 'Raw scan projection plus attributed CC0 projection fallback; local color matching and feathered boundary',
                'raw_scan_sha256': digest(out / 'scan-raw.png'), 'raw_fallback_sha256': digest(fallback)}
    if coverage['projection_coverage'] < .995:
        raise ValueError('Combined raw projection fails the unchanged coverage gate')
    (out / 'color.1001.json').write_text(json.dumps(coverage, indent=2) + '\n', encoding='utf-8')
    return coverage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'assets/gnm-scan')
    parser.add_argument('--template', type=Path, required=True, help='Directory with template.npz and neutral.blend')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--blender', type=Path)
    parser.add_argument('--fallback', type=Path, help='Unfilled direct CC0 emission bake at the same size')
    parser.add_argument('--size', type=int, choices=(2048, 4096), default=4096)
    parser.add_argument('--worker', choices=('export', 'bake'))
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None
    args = parser.parse_args(argv)
    if args.worker:
        if args.worker == 'export':
            export_mesh(args.source, args.out)
        else:
            bake_scan(args.source, args.out, args.size)
        return
    if not args.blender or not args.fallback:
        parser.error('Build requires --blender and --fallback')
    source = json.loads((args.source / 'source.json').read_text())
    for name, spec in source['files'].items():
        if digest(args.source / name) != spec['sha256']:
            raise ValueError(f'Pinned scan asset mismatch: {name}')
    args.out.mkdir(parents=True, exist_ok=False)
    def worker(stage):
        subprocess.run([str(args.blender.resolve()), '--offline-mode', '-b', '--factory-startup',
                        str((args.template / 'neutral.blend').resolve()), '--python-exit-code', '1',
                        '-P', str(Path(__file__).resolve()), '--', '--worker', stage,
                        '--source', str(args.source.resolve()), '--template', str(args.template.resolve()),
                        '--out', str(args.out.resolve()), '--size', str(args.size)], check=True)
    worker('export')
    fit = align(args.template / 'template.npz', args.out)
    worker('bake')
    coverage = compose(args.template / 'template.npz', args.fallback, args.out, args.size)
    receipt = {'source': source, 'fit': fit, 'coverage': coverage,
               'template_sha256': digest(args.template / 'template.npz'),
               'output_sha256': digest(args.out / 'color.1001.png')}
    (args.out / 'scan-transfer.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
