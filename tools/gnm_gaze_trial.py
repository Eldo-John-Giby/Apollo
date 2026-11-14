"""Evaluate native GNM gaze anchors using a shared forward fixation plane."""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

from gnm_template import MODEL_SHA256


def evaluator(model_path):
    import hashlib
    from gnm.shape import gnm_numpy

    if hashlib.sha256(model_path.read_bytes()).hexdigest() != MODEL_SHA256:
        raise ValueError('GNM model checksum mismatch')
    model = gnm_numpy.GNM.from_custom_file(str(model_path))
    neutral = model()
    joints = model.template_joint_positions
    names = list(model.joint_names)
    indices = [names.index(f'{side}_eye') for side in ('left', 'right')]
    center = joints[indices].mean(axis=0)
    pupil_masks = [model.vertex_group_mask(f'{side}_eye', '&pupils')
                   for side in ('left', 'right')]
    def pose(h, v):
        target = center + np.array([.05 * h, .05 * v, .35])
        rotations = np.zeros((model.num_joints, 3))
        for index, mask in zip(indices, pupil_masks):
            axis = neutral[mask].mean(0) - joints[index]
            direction = target - joints[index]
            axis /= np.linalg.norm(axis)
            direction /= np.linalg.norm(direction)
            rotations[index] = Rotation.align_vectors(direction[None], axis[None])[0].as_rotvec()
        posed = model(rotations=rotations)
        return posed.astype(np.float32), {
            'fixation': target.tolist(),
            'pupil_centers': [posed[mask].mean(0).tolist() for mask in pupil_masks],
        }

    return pose


def anchors(model_path, out):
    pose = evaluator(model_path)
    poses, report = {}, {}
    for name, h, v in [('center', 0, 0), ('left', -1, 0), ('right', 1, 0),
                       ('up', 0, 1), ('down', 0, -1)]:
        poses[name], report[name] = pose(h, v)
    for axis, low, high in [(0, 'left', 'right'), (1, 'down', 'up')]:
        mid = np.asarray(report['center']['pupil_centers'])
        assert np.all(np.asarray(report[low]['pupil_centers'])[:, axis] < mid[:, axis])
        assert np.all(np.asarray(report[high]['pupil_centers'])[:, axis] > mid[:, axis])
    out.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(out / 'anchors.npz', **poses)
    (out / 'anchors.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


def clip(model_path, out, mode):
    """Evaluate each unique gaze pose for a 192-frame Blender timeline."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from apollo_core.submission_timing import expression

    pose = evaluator(model_path)
    poses = []
    lookup = {}
    sequence = []
    for frame in range(1, 193):
        h, v, _ = expression(mode, frame)
        key = (h, v)
        if key not in lookup:
            lookup[key] = len(poses)
            vertices, _ = pose(h, v)
            poses.append(vertices)
        sequence.append(lookup[key])
    np.savez_compressed(out, poses=poses, sequence=sequence, mode=mode)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument("--mode", choices=("left", "right", "generate-motion"))
    args = parser.parse_args()
    if args.mode:
        clip(args.model, args.out, args.mode)
    else:
        anchors(args.model, args.out)
