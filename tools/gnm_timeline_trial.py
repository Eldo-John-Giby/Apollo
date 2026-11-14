"""Install upstream-evaluated GNM gaze frames as packed Blender shape keys."""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np


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
        scene['apollo_gnm_trial_mode'] = str(data['mode'])
        scene.frame_start, scene.frame_end = 1, len(sequence)
        scene.render.fps = 24
        curve = head.data.shape_keys.animation_data.action
        for channel in curve.fcurves:
            for point in channel.keyframe_points:
                point.interpolation = 'LINEAR'
        for frame in (1, 23, 26, 192):
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
