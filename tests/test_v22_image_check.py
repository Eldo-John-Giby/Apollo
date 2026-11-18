"""Adversarial image fixtures distinguish pupils, nostrils and closed lash lines."""
from pathlib import Path
import sys
import json
from types import SimpleNamespace

import cv2
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from gnm_v22_image_check import pupils,main


def fixture(path,shift=0,closed=False):
    canvas=np.full((640,640),190,dtype=np.uint8)
    # Larger nose/brow components are deliberately more tempting than pupils.
    for x in (282,362):cv2.ellipse(canvas,(x,440),(13,7),0,0,360,8,-1)
    for x in (210,430):
        cv2.line(canvas,(x-28,215),(x+28,215),12,7)
        if closed:
            cv2.line(canvas,(x-25,280),(x+25,280),12,3)
        else:
            cv2.ellipse(canvas,(x+shift,280),(10,11),0,0,360,12,-1)
            cv2.circle(canvas,(x+shift-3,276),2,240,-1)
    assert cv2.imwrite(str(path),canvas)


def test_eye_detection_rejects_nostril_distractors_and_tracks_direction(tmp_path):
    a,b,c=(tmp_path/name for name in ('neutral.png','left.png','right.png'))
    fixture(a);fixture(b,-5);fixture(c,5)
    neutral,left,right=map(pupils,(a,b,c))
    for side in neutral:
        assert abs(neutral[side][1]-280)<1
        assert abs((left[side][0]-neutral[side][0])+5)<.1
        assert abs((right[side][0]-neutral[side][0])-5)<.1


def test_closed_lash_lines_are_not_visible_pupils(tmp_path):
    path=tmp_path/'closed.png';fixture(path,closed=True)
    assert all(point is None for point in pupils(path).values())


def test_blink_gate_rejects_a_pupil_exposed_in_only_one_closed_eye(tmp_path):
    neutral,closed,reopened=(tmp_path/name for name in ('neutral.png','closed.png','reopened.png'))
    fixture(neutral);fixture(closed,closed=True);fixture(reopened,shift=2)
    args=SimpleNamespace(neutral=neutral,left=None,right=None,closed=closed,reopened=reopened,
                         out=tmp_path/'audit.json')
    main(args)
    assert json.loads(args.out.read_text())['passed']
    image=cv2.imread(str(closed),cv2.IMREAD_GRAYSCALE)
    source=cv2.imread(str(neutral),cv2.IMREAD_GRAYSCALE)
    image[250:311,180:241]=source[250:311,180:241]
    cv2.imwrite(str(closed),image)
    with pytest.raises(ValueError,match='pupil candidate remains'):
        main(args)
    assert not json.loads(args.out.read_text())['passed']
