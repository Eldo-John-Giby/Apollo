"""Validate canonical ten-frame metadata against structure and analytic geometry."""
import json
import math
from pathlib import Path
from .core import Config, make_record


def validate(records, config=None):
    if not isinstance(records, list) or len(records) != 10:
        raise ValueError('Expected exactly ten frame records')
    def number(value):
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError('Expected finite numeric value')
        return value
    def vector(value, size):
        if not isinstance(value, list) or len(value) != size:
            raise ValueError(f'Expected vector of length {size}')
        return [number(x) for x in value]
    def finite(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('Nonfinite metadata number')
        if isinstance(value, dict):
            for v in value.values(): finite(v)
        if isinstance(value, list):
            for v in value: finite(v)
    finite(records)
    required = {'frame','theta','input','eye_rotation_L','eye_rotation_R','pupil_center_2D_L','pupil_center_2D_R','camera_matrix'}
    cfg = config
    for k, r in enumerate(records):
        if not isinstance(r, dict) or not required <= r.keys() or r.keys() - (required | {'extra'}):
            raise ValueError(f'Invalid record keys at frame {k}')
        theta = 2 * math.pi * k / 10
        if type(r['frame']) is not int or r['frame'] != k or abs(number(r['theta']) - theta) > 1e-12:
            raise ValueError(f'Invalid sequence at frame {k}')
        if not isinstance(r['input'], dict) or set(r['input']) != {'h','v'}:
            raise ValueError('Expected h/v input object')
        for axis, expected in [('h', math.sin(theta)), ('v', math.cos(theta))]:
            if abs(number(r['input'][axis]) - expected) > 1e-12:
                raise ValueError(f'Invalid {axis} at frame {k}')
        for side in 'LR':
            vector(r[f'eye_rotation_{side}'], 3)
            pupil = vector(r[f'pupil_center_2D_{side}'], 2)
            if not all(0 <= p < (cfg.res if cfg else 1024) for p in pupil):
                raise ValueError(f'Pupil outside image at frame {k}')
        matrix = r['camera_matrix']
        if not isinstance(matrix, list) or len(matrix) != 3:
            raise ValueError('Expected 3x3 intrinsics')
        for row in matrix: vector(row, 3)
        if matrix[0][0] <= 0 or matrix[1][1] <= 0 or matrix[2] != [0,0,1]:
            raise ValueError('Invalid camera intrinsics')
        extra = r.get('extra', {})
        if not isinstance(extra, dict):
            raise ValueError('extra must be an object')
        if 'image' in extra and extra['image'] != f'frame_{k:02d}.png':
            raise ValueError('Unexpected frame image name')
        if cfg:
            expected = make_record(k,theta,r['input']['h'],r['input']['v'],cfg,f'frame_{k:02d}.png')
            for key in ['eye_rotation_L','eye_rotation_R','pupil_center_2D_L','pupil_center_2D_R']:
                if any(abs(a-b) > 1e-8 for a,b in zip(r[key],expected[key])):
                    raise ValueError(f'{key} disagrees with geometry at frame {k}')
            if any(abs(a-b)>1e-8 for row, exp in zip(matrix,expected['camera_matrix']) for a,b in zip(row,exp)):
                raise ValueError('Intrinsics disagree with calibration')
    return records


def load(path, config=None):
    try:
        records = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        return validate(records, config)
    except (KeyError, TypeError, OverflowError) as exc:
        raise ValueError(f'Malformed metadata: {exc}') from exc
