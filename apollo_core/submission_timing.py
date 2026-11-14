"""Deterministic timing for the three submission expression modes."""

def smooth(value):
    value = max(0., min(1., value))
    return value * value * (3 - 2 * value)


def track(frame, keys):
    for (start, a), (end, b) in zip(keys, keys[1:]):
        if frame <= end:
            t = smooth((frame - start) / (end - start))
            return tuple(x + (y - x) * t for x, y in zip(a, b))
    return keys[-1][1]


def expression(mode, frame):
    center = (0., 0.)
    if mode in ('left', 'right'):
        side = -0.88 if mode == 'left' else 0.88
        gaze = ((1, center), (21, center), (26, (side, 0.)), (192, (side, 0.)))
    else:
        gaze = ((1, center), (20, center), (25, (-.7, .14)), (53, (-.7, .14)),
                (58, (.65, -.12)), (87, (.65, -.12)), (93, (.23, .72)),
                (124, (.23, .72)), (130, (-.33, -.45)), (159, (-.33, -.45)),
                (164, center), (192, center))
    blink_start = 103 if mode == 'generate-motion' else 99
    blink = ((1, (0.,)), (blink_start, (0.,)), (blink_start + 3, (1.,)),
             (blink_start + 4, (1.,)), (blink_start + 9, (0.,)), (192, (0.,)))
    return (*track(frame, gaze), track(frame, blink)[0])
