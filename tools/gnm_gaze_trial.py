"""Evaluate native GNM gaze anchors using a shared forward fixation plane."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

from gnm_template import MODEL_SHA256


def anchors(model_path, out):
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
    poses, report = {}, {}
    for name, h, v in [('center', 0, 0), ('left', -1, 0), ('right', 1, 0),
                       ('up', 0, 1), ('down', 0, -1)]:
        target = center + np.array([.05 * h, .05 * v, .35])
        rotations = np.zeros((model.num_joints, 3))
        for index, mask in zip(indices, pupil_masks):
            axis = neutral[mask].mean(0) - joints[index]
            direction = target - joints[index]
            axis /= np.linalg.norm(axis)
            direction /= np.linalg.norm(direction)
            rotations[index] = Rotation.align_vectors(direction[None], axis[None])[0].as_rotvec()
        posed = model(rotations=rotations)
        poses[name] = posed.astype(np.float32)
        report[name] = {'fixation': target.tolist(),
                        'pupil_centers': [posed[mask].mean(0).tolist() for mask in pupil_masks]}
    for axis, low, high in [(0, 'left', 'right'), (1, 'down', 'up')]:
        mid = np.asarray(report['center']['pupil_centers'])
        assert np.all(np.asarray(report[low]['pupil_centers'])[:, axis] < mid[:, axis])
        assert np.all(np.asarray(report[high]['pupil_centers'])[:, axis] > mid[:, axis])
    out.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(out / 'anchors.npz', **poses)
    (out / 'anchors.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    anchors(args.model, args.out)
