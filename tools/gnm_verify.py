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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_run import surface_files


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
    if bpy.data.libraries:
        raise ValueError('Timeline depends on an external linked Blender library')
    file_images = [image for image in bpy.data.images if image.source in ('FILE', 'TILED')]
    if any(not image.packed_file for image in file_images):
        raise ValueError('Timeline has an unpacked file image')
    if any(not image.filepath.startswith('//')
           or any(not packed.filepath.startswith('//') for packed in image.packed_files)
           for image in file_images):
        raise ValueError('Timeline retains an absolute image authoring path')
    if not scene.render.filepath.startswith('//'):
        raise ValueError('Timeline has an absolute render output path')
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
            color = material.node_tree.nodes.get('Principled BSDF').inputs['Base Color']
            if len(color.links) != 1 or color.links[0].from_node.type != 'TEX_IMAGE':
                raise ValueError(f'Unexpected base-color binding in tile {tile}')
            image = color.links[0].from_node.image
            expected = hashlib.sha256((maps / f'color.{tile}.png').read_bytes()).hexdigest()
            if (not image.packed_file or image.colorspace_settings.name != 'sRGB'
                    or hashlib.sha256(image.packed_file.data).hexdigest() != expected):
                raise ValueError(f'Incorrect packed texture {tile}')
            vector = color.links[0].from_node.inputs['Vector']
            if len(vector.links) != 1:
                raise ValueError(f'Missing explicit texture UV binding in tile {tile}')
            coordinate = vector.links[0].from_node
            if coordinate.type == 'VECT_MATH':
                if (coordinate.operation != 'SUBTRACT'
                        or tuple(coordinate.inputs[1].default_value) != (tile - 1001, 0., 0.)
                        or len(coordinate.inputs[0].links) != 1):
                    raise ValueError(f'Incorrect UDIM offset for tile {tile}')
                coordinate = coordinate.inputs[0].links[0].from_node
                expected_uv = 'GNM UDIM'
            else:
                expected_uv = 'GNM Region'
            if coordinate.type != 'UVMAP' or coordinate.uv_map != expected_uv:
                raise ValueError(f'Incorrect corner UV layout for tile {tile}')
            packed[str(tile)] = expected
        surface = {}
        shader = mesh.materials[0].node_tree.nodes.get('Principled BSDF')
        for role, path in surface_files(maps).items():
            socket = shader.inputs['Roughness' if role == 'roughness' else 'Normal']
            if len(socket.links) != 1:
                raise ValueError(f'Missing portable skin {role} binding')
            node = socket.links[0].from_node
            if role == 'height':
                if node.type != 'BUMP' or abs(node.inputs['Distance'].default_value - .00009) > 1e-9:
                    raise ValueError('Incorrect skin relief scale')
                if len(node.inputs['Height'].links) != 1:
                    raise ValueError('Missing portable skin height image')
                node = node.inputs['Height'].links[0].from_node
            expected = hashlib.sha256(path.read_bytes()).hexdigest()
            if (node.type != 'TEX_IMAGE' or not node.image or not node.image.packed_file
                    or node.image.colorspace_settings.name != 'Non-Color'
                    or hashlib.sha256(node.image.packed_file.data).hexdigest() != expected):
                raise ValueError(f'Incorrect packed skin {role} map or color space')
            skin_color = shader.inputs['Base Color'].links[0].from_node
            if (len(node.inputs['Vector'].links) != 1
                    or node.inputs['Vector'].links[0].from_socket != skin_color.inputs['Vector'].links[0].from_socket):
                raise ValueError(f'Incorrect skin {role} UV binding')
            surface[role] = expected
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
            'frames_checked': len(sequence), 'max_position_error_m': error, 'maps': packed,
            'surface_maps': surface,
            'camera_checks': camera_report,
            'resource_checks': {'linked_libraries': 0, 'unpacked_file_images': 0,
                                'absolute_image_paths': 0,
                                'packed_file_images': len(file_images),
                                'blender_online_access': bpy.app.online_access}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('template', 'clip', 'maps', 'out'):
        parser.add_argument(f'--{name}', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.out.write_text(json.dumps(verify(args.template, args.clip, args.maps), indent=2) + '\n',
                        encoding='utf-8')
