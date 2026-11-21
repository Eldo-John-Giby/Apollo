"""Acceptance requirements for the additional four seconds of gaze animation."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from gnm_v22_extend import source_time
from apollo_core.submission_timing import expression


@pytest.mark.parametrize('mode', ['left', 'right', 'generate-motion'])
def test_original_eight_seconds_remain_unretimed(mode):
    assert [source_time(mode, f) for f in range(1, 193)] == list(range(1, 193))


@pytest.mark.parametrize('mode,sign', [('left', -1), ('right', 1)])
def test_side_extension_returns_then_refocuses_without_wrong_direction(mode, sign):
    gaze = [expression(mode, source_time(mode, f)) for f in range(193, 289)]
    assert all(h*sign >= 0 for h, _, _ in gaze)
    assert abs(gaze[12][0]) < .01  # A real return, rather than a side hold.
    assert gaze[-1][0]*sign > .8
    assert max(blink for _, _, blink in gaze) == 1
    assert gaze[-1][2] == 0
    assert len({round(h, 4) for h, _, _ in gaze}) >= 5


def test_generated_extension_moves_both_axes_closes_reopens_and_resets():
    gaze = [expression('generate-motion', source_time('generate-motion', f))
            for f in range(193, 289)]
    assert min(h for h, _, _ in gaze) < -.6
    assert max(h for h, _, _ in gaze) > .6
    assert min(v for _, v, _ in gaze) < -.4
    assert max(v for _, v, _ in gaze) > .7
    assert max(blink for _, _, blink in gaze) == 1
    assert gaze[-1] == (0, 0, 0)
    blinking = [blink > .001 for _, _, blink in gaze]
    assert sum(now and not before for before, now in zip([False]+blinking, blinking)) == 1


def test_outside_delivery_range_is_rejected():
    with pytest.raises(ValueError):
        source_time('left', 289)
