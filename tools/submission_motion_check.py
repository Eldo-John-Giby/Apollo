"""Check direction and peak-blink pupil coverage on saved submission timelines."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view


def measure(scene, side):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    pupil = scene.objects[f'Pupil.{side}'].evaluated_get(depsgraph)
    points = [pupil.matrix_world @ polygon.center for polygon in pupil.data.polygons]
    if not points:
        raise ValueError(f'Pupil.{side} has no surface')
    projected_x = sum(world_to_camera_view(scene, scene.camera, p).x for p in points)
    camera = scene.camera.matrix_world.translation
    visible = 0
    for point in points:
        ray = point - camera
        hit, _, _, _, obj, _ = scene.ray_cast(depsgraph, camera, ray.normalized(),
                                               distance=ray.length + .00001)
        visible += bool(hit and obj.name == pupil.name)
    return {'screen_x': projected_x / len(points), 'pupil_surface_samples': len(points),
            'visible_samples': visible}


def packed_maps(scene, manifest):
    maps = {}
    for entry in manifest['maps']:
        obj = scene.objects[entry['object']]
        slots = obj.material_slots if entry.get('replace_on_all_slots') else [obj.material_slots[entry['slot']]]
        for slot in slots:
            images = [node.image for node in slot.material.node_tree.nodes
                      if node.type == 'TEX_IMAGE' and node.image and node.image.packed_file]
            if not any(hashlib.sha256(image.packed_file.data).hexdigest() == entry['sha256']
                       for image in images):
                raise ValueError(f"{obj.name} is missing its packed {entry['role']} map")
        maps[entry['role']] = entry['sha256']
    return maps


def check(root, variant=None):
    report = {}
    packed = {}
    manifest = json.loads(variant.read_text(encoding='utf-8')) if variant else None
    for mode in ('left', 'right', 'generate-motion'):
        path = root / mode / 'expression.blend'
        bpy.ops.wm.open_mainfile(filepath=str(path))
        scene = bpy.context.scene
        if manifest:
            packed[mode] = {'scene_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                            'maps': packed_maps(scene, manifest)}
        if (scene.frame_start, scene.frame_end, scene.render.fps, scene.render.fps_base) != (1, 192, 24, 1.):
            raise ValueError(f'{mode} must be 192 frames at 24 fps')
        frames = (1, 26, 101, 102, 103, 105, 108) if mode != 'generate-motion' else (
            1, 25, 58, 105, 106, 107, 109, 112)
        results = {}
        for frame in frames:
            scene.frame_set(frame)
            results[frame] = {side: measure(scene, side) for side in 'LR'}
        first_peak = 106 if mode == 'generate-motion' else 102
        for side in 'LR':
            def visible(frame):
                return results[frame][side]['visible_samples']

            if not visible(1) or not visible(first_peak + 6):
                raise ValueError(f'{mode} {side}: expected visible pupil before and after blink')
            if visible(first_peak) or visible(first_peak + 1):
                raise ValueError(f'{mode} {side}: pupil visible at peak blink')
            if mode != 'generate-motion':
                shift = results[26][side]['screen_x'] - results[1][side]['screen_x']
                if shift * (-1 if mode == 'left' else 1) <= .005:
                    raise ValueError(f'{mode} {side}: wrong or unreadable direction')
            elif not results[25][side]['screen_x'] < results[1][side]['screen_x'] < results[58][side]['screen_x']:
                raise ValueError(f'{mode} {side}: expected both gaze directions')
        report[mode] = results
    (root / 'motion-report.json').write_text(json.dumps(report, indent=2) + '\n',
                                            encoding='utf-8')
    if packed:
        (root / 'timeline-textures.json').write_text(json.dumps(packed, indent=2) + '\n',
                                                   encoding='utf-8')
    print('Passed direction and peak-blink checks on all three saved timelines')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--variant', type=Path, help='Also verify packed maps against this manifest')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    check(args.root.resolve(), args.variant)


if __name__ == '__main__':
    main()
