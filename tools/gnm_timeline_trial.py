"""Install upstream-evaluated GNM gaze frames as packed Blender shape keys."""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def verify_blink(head, poses, sequence):
    skin = [list(p.vertices) for p in head.data.polygons if p.material_index == 0]
    inverse = head.matrix_world.inverted()
    camera = inverse @ Vector((0, -.58, .015))
    groups = {name: head.vertex_groups[name].index for name in ('pupils', 'left_eye', 'right_eye')}
    pupils = {side: [] for side in ('left_eye', 'right_eye')}
    for vertex in head.data.vertices:
        memberships = {group.group for group in vertex.groups}
        if groups['pupils'] in memberships:
            for side in pupils:
                if groups[side] in memberships:
                    pupils[side].append(vertex.index)
    for frame in (93, 106, 107, 112):
        vertices = poses[sequence[frame - 1]]
        tree = BVHTree.FromPolygons(vertices.tolist(), skin)
        for side, indices in pupils.items():
            visible = 0
            for point in vertices[indices]:
                ray = Vector(point) - camera
                visible += tree.ray_cast(camera, ray, ray.length)[0] is None
            if (frame in (106, 107) and visible != 0) or (frame in (93, 112) and visible == 0):
                raise ValueError(f'{side} failed pupil visibility at frame {frame}: {visible}')
            print(f'Frame {frame}: {side} {visible}/{len(indices)} visible pupil vertices')


def install(clip, out):
    if out.exists():
        raise FileExistsError(out)
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    if head.data.shape_keys:
        raise ValueError('Start from the neutral template')
    head.shape_key_add(name='Basis')
    with np.load(clip, allow_pickle=False) as data:
        poses, sequence = data['poses'], data['sequence']
        if poses.shape[1:] != (len(head.data.vertices), 3) or len(sequence) != 192:
            raise ValueError('Clip does not match the GNM template')
        for index, pose in enumerate(poses):
            key = head.shape_key_add(name=f'GNM pose {index:03d}')
            key.data.foreach_set('co', pose.ravel())
            active = sequence == index
            for frame in range(len(sequence)):
                if frame == 0 or frame == len(sequence)-1 or active[frame] != active[frame-1]:
                    if frame and active[frame] != active[frame-1]:
                        key.value = float(active[frame-1])
                        key.keyframe_insert('value', frame=frame)
                    key.value = float(active[frame])
                    key.keyframe_insert('value', frame=frame+1)
        mode = str(data['mode'])
        if mode == 'generate-motion':
            verify_blink(head, poses, sequence)
        scene['apollo_gnm_trial_mode'] = mode
        scene.frame_start, scene.frame_end = 1, len(sequence)
        scene.render.fps = 24
        curve = head.data.shape_keys.animation_data.action
        for channel in curve.fcurves:
            for point in channel.keyframe_points:
                point.interpolation = 'LINEAR'
        for frame in (1, 23, 26, 106, 107, 112, 192):
            scene.frame_set(frame)
            evaluated = head.evaluated_get(bpy.context.evaluated_depsgraph_get())
            vertices = np.empty(poses.shape[1] * 3, dtype=np.float32)
            evaluated.data.vertices.foreach_get('co', vertices)
            np.testing.assert_allclose(vertices.reshape(-1, 3), poses[sequence[frame-1]],
                                       atol=1e-6, rtol=0)
    scene.frame_set(1)
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out.resolve()), compress=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clip', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    install(args.clip, args.out)
