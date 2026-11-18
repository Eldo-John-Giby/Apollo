"""Surface-local identity transport, independent of Blender and the GNM evaluator."""
import numpy as np


def edges_from_faces(faces):
    faces = np.asarray(faces, dtype=np.int32)
    pairs = np.concatenate([faces[:, [i, (i+1) % faces.shape[1]]]
                            for i in range(faces.shape[1])])
    return np.unique(np.sort(pairs, axis=1), axis=0)


def transport_identity(reference, posed, delta, faces, protected):
    """Rotate each identity offset with the best-fit native one-ring rotation.

    Edge lengths weight the fit naturally. Offsets retain physical size, rather
    than stretching with a blink. Protected native components receive no offset.
    This is an appearance layer, not a replacement native-motion oracle.
    """
    reference, posed, delta = [np.asarray(a, dtype=np.float64) for a in (reference, posed, delta)]
    if reference.shape != posed.shape or delta.shape != posed.shape or posed.ndim != 2 or posed.shape[1] != 3:
        raise ValueError('Expected matching N by 3 surfaces and offsets')
    if not all(np.isfinite(a).all() for a in (reference, posed, delta)):
        raise ValueError('Nonfinite surface')
    protected = np.asarray(protected, dtype=np.int32)
    if np.any(delta[protected] != 0):
        raise ValueError('Identity offsets must not alter protected native components')
    if np.array_equal(reference, posed):
        return (posed + delta).astype(np.float32)
    edges = edges_from_faces(faces)
    a, b = edges.T
    rest = reference[b] - reference[a]
    moved = posed[b] - posed[a]
    covariance = np.zeros((len(reference), 3, 3))
    outer = moved[:, :, None] * rest[:, None, :]
    np.add.at(covariance, a, outer)
    np.add.at(covariance, b, outer)
    u, _, vh = np.linalg.svd(covariance)
    sign = np.linalg.det(u @ vh)
    u[:, :, -1] *= sign[:, None]
    rotation = u @ vh
    result = posed + np.einsum('nij,nj->ni', rotation, delta)
    result[protected] = posed[protected]
    return result.astype(np.float32)


def triangle_frames(vertices, triangles):
    """Orthonormal tangent/bitangent/normal frames; reject collapsed anchors."""
    points = np.asarray(vertices)[np.asarray(triangles)]
    tangent = points[:, 1] - points[:, 0]
    normal = np.cross(tangent, points[:, 2] - points[:, 0])
    lengths = np.linalg.norm(tangent, axis=1)
    areas = np.linalg.norm(normal, axis=1)
    if np.any(lengths < 1e-10) or np.any(areas < 1e-14):
        raise ValueError('Collapsed attachment triangle')
    tangent /= lengths[:, None]
    normal /= areas[:, None]
    return np.stack((tangent, np.cross(normal, tangent), normal), axis=2)


def barycentric(points, triangles):
    """Barycentric coordinates of points in triangle planes."""
    a = triangles[:, 1] - triangles[:, 0]
    b = triangles[:, 2] - triangles[:, 0]
    p = points - triangles[:, 0]
    aa = np.einsum('ij,ij->i', a, a)
    ab = np.einsum('ij,ij->i', a, b)
    bb = np.einsum('ij,ij->i', b, b)
    pa = np.einsum('ij,ij->i', p, a)
    pb = np.einsum('ij,ij->i', p, b)
    det = aa*bb-ab*ab
    if np.any(det < 1e-25):
        raise ValueError('Collapsed attachment triangle')
    v = (bb*pa-ab*pb)/det
    w = (aa*pb-ab*pa)/det
    return np.stack((1-v-w, v, w), axis=1)
