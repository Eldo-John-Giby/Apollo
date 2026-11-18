import numpy as np
import pytest

from apollo_core.identity import barycentric, transport_identity, triangle_frames


def test_identity_follows_rigid_motion_without_moving_protected_eye():
    rest = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
    faces = np.array([[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]])
    delta = np.array([[0., .02, .01], [.01, 0., 0.], [0., 0., .03], [0., 0., 0.]])
    rotation = np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]])
    posed = rest @ rotation.T + [.4, -.2, .3]
    actual = transport_identity(rest, posed, delta, faces, [3])
    np.testing.assert_allclose(actual, (rest+delta) @ rotation.T + [.4, -.2, .3], atol=3e-8)
    np.testing.assert_array_equal(actual[3], posed[3].astype(np.float32))
    np.testing.assert_array_equal(transport_identity(rest, rest, delta, faces, [3]),
                                  (rest+delta).astype(np.float32))
    delta[3, 0] = .001
    with pytest.raises(ValueError, match='protected'):
        transport_identity(rest, posed, delta, faces, [3])


def test_surface_anchor_reconstructs_root_and_direction_after_rotation():
    vertices = np.array([[0., 0., 0.], [2., 0., 0.], [0., 3., 0.]])
    ids = np.array([[0, 1, 2]])
    root = np.array([[.5, .75, 0.]])
    weights = barycentric(root, vertices[ids])
    np.testing.assert_allclose(weights, [[.5, .25, .25]])
    frame = triangle_frames(vertices, ids)
    offset = np.array([[.1, .2, .3]])
    local = np.einsum('nji,nj->ni', frame, offset)
    rotation = np.array([[1., 0., 0.], [0., 0., -1.], [0., 1., 0.]])
    moved = vertices @ rotation.T + [2., 1., .5]
    reconstructed = np.einsum('ni,nij->nj', weights, moved[ids]) + np.einsum(
        'nij,nj->ni', triangle_frames(moved, ids), local)
    np.testing.assert_allclose(reconstructed, (root+offset) @ rotation.T + [2., 1., .5])
    with pytest.raises(ValueError, match='Collapsed'):
        triangle_frames(np.zeros((3, 3)), ids)
