"""Fit bilateral closure, vertical lid follow and brow response in native GNM."""
from collections import Counter

import numpy as np
from scipy.optimize import lsq_linear


def eyelid_rims(model):
    faces = model.quads
    exterior = model.vertex_group_mask('skin_exterior')
    faces = faces[np.all(exterior[faces], axis=1)]
    counts = Counter(tuple(sorted(edge)) for face in faces
                     for edge in zip(face, np.roll(face, -1)))
    boundary = np.array(sorted({i for e, count in counts.items() if count == 1 for i in e}))
    for side in ('left', 'right'):
        index = list(model.joint_names).index(f'{side}_eye')
        pivot = model.template_joint_positions[index]
        delta = model.template_vertex_positions[boundary] - pivot
        rim = boundary[(abs(delta[:, 0]) < .019) & (abs(delta[:, 1]) < .012)
                       & (delta[:, 2] > .005)]
        if len(rim) < 20:
            raise ValueError(f'Could not locate the {side} eyelid rim')
        yield side, rim


def fit_blink(model, basis):
    """Fit a low, slightly curved contact line while suppressing unrelated motion."""
    positions = model.template_vertex_positions
    solutions = []
    for side, rim in eyelid_rims(model):
        active = np.flatnonzero(np.char.startswith(model.expression_names, f'{side}_eye_region_'))
        rim_xyz = positions[rim]
        low, high = rim_xyz[np.argmin(rim_xyz[:, 0])], rim_xyz[np.argmax(rim_xyz[:, 0])]
        t = (rim_xyz[:, 0] - low[0]) / (high[0] - low[0])
        contact = low[1] * (1 - t) + high[1] * t - .0022 * np.sin(np.pi * t)
        desired = np.zeros_like(rim_xyz)
        desired[:, 1] = contact - rim_xyz[:, 1]
        # Keep the contact line just anterior to the neutral globe. Free depth
        # in the first fit allowed sharp folds and locally exposed cornea.
        eye = model.template_joint_positions[list(model.joint_names).index(f'{side}_eye')]
        desired[:, 2] = np.maximum(rim_xyz[:, 2], eye[2] + .0148) - rim_xyz[:, 2]
        weight = np.array([.4, 1., .6])
        constraint = (basis[active][:, rim] * weight).reshape(len(active), -1).T
        # Penalize displacement jumps along adjacent orbital vertices.
        local = model.vertex_group_mask(f'{side}_orbital_region')
        edges = {tuple(sorted((int(a), int(b)))) for face in model.quads
                 for a, b in zip(face, np.roll(face, -1)) if local[a] and local[b]}
        adjacent = np.array(sorted(edges))
        smoothness = (basis[active][:, adjacent[:, 0]]
                      - basis[active][:, adjacent[:, 1]]).reshape(len(active), -1).T
        regularizer = np.vstack((.5 * smoothness, .00035 * np.eye(len(active))))
        fit_result = lsq_linear(
            np.vstack((constraint, regularizer)),
            np.concatenate(((desired * weight).ravel(), np.zeros(len(regularizer)))),
            bounds=(-3., 3.), tol=1e-10)
        if not fit_result.success:
            raise ValueError(f'{side} eyelid fit did not converge: {fit_result.message}')
        fit = fit_result.x
        result = np.zeros(model.expression_dim)
        result[active] = fit
        solutions.append(result)
    return solutions


def fit_lid_follow(model, basis):
    """Fit small vertical lid-follow and brow responses for the upward glance."""
    positions = model.template_vertex_positions
    result = np.zeros(model.expression_dim)
    for side, rim in eyelid_rims(model):
        active = np.flatnonzero(
            np.char.startswith(model.expression_names, f'{side}_eye_region_')
            | np.char.startswith(model.expression_names, f'{side}_brow_region_'))
        brow = np.flatnonzero(model.vertex_group_mask(f'{side}_brow_region'))
        selected = np.concatenate((rim, brow))
        desired = np.zeros((len(selected), 3))
        y = positions[rim, 1]
        desired[:len(rim), 1] = .0005 + .001 * (y - y.min()) / np.ptp(y)
        desired[len(rim):, 1] = .0003
        constraint = basis[active][:, selected].reshape(len(active), -1).T
        regularizer = .00075 * np.eye(len(active))
        fitted = lsq_linear(np.vstack((constraint, regularizer)),
                            np.concatenate((desired.ravel(), np.zeros(len(active)))),
                            bounds=(-.75, .75), tol=1e-10)
        if not fitted.success:
            raise ValueError(f'{side} lid-follow fit did not converge')
        result[active] = fitted.x
    return result
