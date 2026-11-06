import sys
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from grader_sim import centroid,detect,template_shift
from verify import verify
from direction_report import measure


def image(dx=0.,dy=0.):
    yy,xx=np.indices((1024,1024),dtype=float)
    xx+=.5; yy+=.5
    image=np.full((1024,1024),160.)
    for x in [289.,735.]:
        distance=np.sqrt((xx-x-dx)**2+(yy-512-dy)**2)
        image=np.where(distance<42.,120.,image)
        edge=np.clip(14.5-distance,0,1)
        image=image*(1-edge)+2*edge
    return image.astype(np.float32)


def test_blind_detector_subpixel():
    measured=detect(image(.35,-.2))
    for side,x in [('L',735.),('R',289.)]:
        assert np.linalg.norm(measured[side]-[x+.35,511.8])<.3

@pytest.mark.parametrize('dx,dy',[(10.3,0),(-10.3,0),(0,10.3),(0,-10.3)])
def test_template_directions(dx,dy):
    shifts=template_shift(image(),image(dx,dy))
    for value in shifts.values():
        assert np.linalg.norm(value-[dx,dy])<.3


@pytest.mark.parametrize('dy',[-10.3,10.3])
def test_template_ignores_stationary_eyelids(dy):
    reference=image()
    current=image(0,dy)
    # Strong stationary bands near the eyes mimic lashes/lids. A whole-eye
    # template locks onto these instead of measuring the moving pupil.
    for pixels in [reference,current]:
        for x in [289,735]:
            pixels[477:487,x-65:x+65]=8
            pixels[541:548,x-65:x+65]=8
    shifts=template_shift(reference,current)
    for value in shifts.values():
        assert np.linalg.norm(value-[0,dy])<.3


def test_weighted_centroid_pixel_convention():
    mask=np.zeros((1024,1024))
    mask[510:514,288:290]=1
    mask[510:514,734:736]=1
    points=centroid(mask)
    assert np.allclose(points['R'],[289,512])
    assert np.allclose(points['L'],[735,512])


def test_empty_mask_fails():
    with pytest.raises(ValueError): centroid(np.zeros((1024,1024)))


@pytest.mark.parametrize('defect',[None,'reversed','stationary','cross_axis','reset'])
def test_direction_suite_detects_behavior_failures(defect):
    commands={'left':(-10.3,0),'right':(10.3,0),'up':(0,-10.3),
              'down':(0,10.3),'reset':(0,0)}
    if defect=='reversed': commands['left']=(10.3,0)
    if defect=='stationary': commands['right']=(0,0)
    if defect=='cross_axis': commands['up']=(2,-10.3)
    images={name:image(*delta) for name,delta in commands.items()}
    result=measure(image(),images,reset_identical=defect!='reset')
    assert result['passed'] is (defect is None)


def test_missing_blender_never_passes(tmp_path,monkeypatch):
    monkeypatch.delenv('BLENDER_BIN',raising=False)
    monkeypatch.setattr('verify.shutil.which',lambda name:None)
    report=verify(tmp_path)
    assert report['passed'] is False and report['production'] is False
    assert report['checks']['V1']['status']=='NOT RUN'
    assert report['checks']['V13']['status']=='FAIL'
    assert (tmp_path/'verification_report.md').exists()
