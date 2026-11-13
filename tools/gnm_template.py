"""Export the pinned Google GNM Head model for Blender, preserving corner UVs."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlretrieve

import numpy as np

REVISION = 'c01e90d298d82301f9fd18f54806be751775cb7c'
SOURCE = 'f84cdbdc86a34f55627526f137495f864e687679'
MODEL_SHA256 = '61d78bbfb4ad8e0b38495804a4caef3214d3df00f8c3f68761e63b41ce3747eb'
URL = f'https://huggingface.co/google/gnm-v3/resolve/{REVISION}/v3_0/gnm_head.npz'


def array_hash(data, dtype):
    return hashlib.sha256(np.asarray(data, dtype=dtype).tobytes()).hexdigest()


def export(model_path, out):
    if not model_path.exists():
        model_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = model_path.with_suffix('.download')
        urlretrieve(URL, temporary)
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != MODEL_SHA256:
            raise ValueError('Downloaded GNM model checksum mismatch')
        temporary.replace(model_path)
    if hashlib.sha256(model_path.read_bytes()).hexdigest() != MODEL_SHA256:
        raise ValueError('GNM model checksum mismatch')
    from gnm.shape import gnm_numpy

    model = gnm_numpy.GNM.from_custom_file(str(model_path))
    vertices = model.template_vertex_positions
    neutral = model(np.zeros(model.identity_dim), np.zeros(model.expression_dim),
                    np.zeros((model.num_joints, 3)), np.zeros(3))
    np.testing.assert_allclose(neutral, vertices, atol=1e-6, rtol=0)
    faces = model.quads
    legacy = model.quad_uvs
    udim = model.quad_uvs_udim
    tiles = model.quad_udim_tiles
    offsets = np.stack((tiles - 1001, np.zeros_like(tiles)), axis=-1)
    np.testing.assert_allclose(udim, legacy + offsets[:, None], atol=1e-6, rtol=0)
    groups = {str(name): model.vertex_group_mask(str(name))
              for name in model.vertex_group_names}
    for side, tile in [('left', 1002), ('right', 1004)]:
        expected = groups[f'{side}_eye'] & groups['eye_interiors']
        np.testing.assert_array_equal(tiles == tile, np.all(expected[faces], axis=1))
    out.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(out / 'template.npz', vertices=vertices, quads=faces,
                        legacy=legacy, udim=udim, tiles=tiles,
                        joints=model.template_joint_positions,
                        joint_names=model.joint_names, **groups)
    receipt = {
        'source_commit': SOURCE, 'model_revision': REVISION,
        'model_sha256': MODEL_SHA256, 'model_url': URL,
        'vertices': len(vertices), 'quads': len(faces),
        'connectivity_sha256': array_hash(faces, '<i4'),
        'legacy_uv_sha256': array_hash(legacy, '<f4'),
        'udim_uv_sha256': array_hash(udim, '<f4'),
        'joints': dict(zip(model.joint_names, model.template_joint_positions.tolist())),
        'regions': {int(tile): {'quads': int(np.count_nonzero(tiles == tile)),
                                'legacy_uv_sha256': array_hash(legacy[tiles == tile], '<f4'),
                                'udim_uv_sha256': array_hash(udim[tiles == tile], '<f4')}
                    for tile in np.unique(tiles)},
    }
    (out / 'template-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n',
                                              encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    export(args.model, args.out)
