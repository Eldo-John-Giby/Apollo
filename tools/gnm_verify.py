"""Verify saved GNM topology, UVs, packed maps and every timeline frame on reopen."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def check_camera(scene, head, source, poses, sequence, mode):
    """Check the packed scene's actual camera against evaluated pupil geometry."""
    inverse = head.matrix_world.inverted()
    camera = inverse @ scene.camera.matrix_world.translation
    skin = source['quads'][source['tiles'] == 1001].tolist()
    masks = {side: source['pupils'] & source[f'{side}_eye']
             for side in ('left', 'right')}
    if any(not mask.any() for mask in masks.values()):
        raise ValueError('Template is missing a pupil group')
    peak = 106 if mode == 'generate-motion' else 102
    before, after = peak - 3, peak + 10
    frames = (1, 25, 58, before, peak, peak + 1, after) if mode == 'generate-motion' else (
        1, 26, before, peak, peak + 1, after)
    report = {}
    for frame in frames:
        vertices = poses[sequence[frame - 1]]
        tree = BVHTree.FromPolygons(vertices.tolist(), skin)
        report[frame] = {}
        for side, mask in masks.items():
            points = vertices[mask]
            visible = 0
            for point in points:
                ray = Vector(point) - camera
                visible += tree.ray_cast(camera, ray, ray.length)[0] is None
            center = head.matrix_world @ Vector(points.mean(axis=0))
            image_x = world_to_camera_view(scene, scene.camera, center).x
            report[frame][side] = {'visible_pupil_vertices': visible, 'image_x': image_x}
    for side in masks:
        if any(report[f][side]['visible_pupil_vertices'] for f in (peak, peak + 1)):
            raise ValueError(f'{mode}: {side} pupil exposed at peak closure')
        if not all(report[f][side]['visible_pupil_vertices'] for f in frames
                   if f not in (peak, peak + 1)):
            raise ValueError(f'{mode}: {side} pupil hidden outside the blink')
        neutral = report[1][side]['image_x']
        if mode == 'generate-motion':
            shifts = [(neutral - report[25][side]['image_x']),
                      (report[58][side]['image_x'] - neutral)]
        else:
            sign = -1 if mode == 'left' else 1
            shifts = [sign * (report[26][side]['image_x'] - neutral)]
        if min(shifts) <= .005:
            raise ValueError(f'{mode}: {side} screen direction is wrong or too small')
    return report


def verify(template, clip, maps):
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    mesh = head.data
    with np.load(template, allow_pickle=False) as source, np.load(clip, allow_pickle=False) as motion:
        indices = np.empty(len(mesh.loops), dtype=np.int32)
        mesh.loops.foreach_get('vertex_index', indices)
        np.testing.assert_array_equal(indices, source['quads'].ravel())
        for layer, name in [('GNM UDIM', 'udim'), ('GNM Region', 'legacy')]:
            uv = np.empty(len(mesh.loops) * 2, dtype=np.float32)
            mesh.uv_layers[layer].uv.foreach_get('vector', uv)
            np.testing.assert_array_equal(uv, source[name].astype(np.float32).ravel())
        if (scene.frame_start, scene.frame_end, scene.render.fps,
            scene['apollo_submission_mode']) != (1, 192, 24, str(motion['mode'])):
            raise ValueError('Saved timeline settings do not match the clip')
        packed = {}
        for tile in (1001, 1002, 1004):
            material = mesh.materials[tile - 1001]
            image = next(n.image for n in material.node_tree.nodes if n.type == 'TEX_IMAGE')
            expected = hashlib.sha256((maps / f'color.{tile}.png').read_bytes()).hexdigest()
            if not image.packed_file or hashlib.sha256(image.packed_file.data).hexdigest() != expected:
                raise ValueError(f'Incorrect packed texture {tile}')
            packed[str(tile)] = expected
        vertices = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        poses, sequence = motion['poses'], motion['sequence']
        np.testing.assert_array_equal(list(scene['apollo_gnm_pose_sequence']), sequence)
        polygon_regions = np.empty(len(mesh.polygons), dtype=np.int32)
        mesh.polygons.foreach_get('material_index', polygon_regions)
        np.testing.assert_array_equal(polygon_regions + 1001, source['tiles'])
        camera_report = check_camera(scene, head, source, poses, sequence, str(motion['mode']))
        error = 0.
        for frame, pose in enumerate(sequence, 1):
            scene.frame_set(frame)
            head.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices.foreach_get('co', vertices)
            error = max(error, float(np.max(np.abs(vertices.reshape(-1, 3) - poses[pose]))))
        if error > 1e-6:
            raise ValueError(f'Reopened timeline deviates from GNM by {error} meters')
    return {'scene_sha256': hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
            'frames_checked': len(sequence), 'max_position_error_m': error, 'maps': packed, 'camera_checks': camera_report}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('template', 'clip', 'maps', 'out'):
        parser.add_argument(f'--{name}', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.out.write_text(json.dumps(verify(args.template, args.clip, args.maps), indent=2) + '\n',
                        encoding='utf-8')
