import sys
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from grader_sim import centroid,detect,template_shift
from verify import verify


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


def test_weighted_centroid_pixel_convention():
    mask=np.zeros((1024,1024))
    mask[510:514,288:290]=1
    mask[510:514,734:736]=1
    points=centroid(mask)
    assert np.allclose(points['R'],[289,512])
    assert np.allclose(points['L'],[735,512])


def test_empty_mask_fails():
    with pytest.raises(ValueError): centroid(np.zeros((1024,1024)))


def test_missing_blender_never_passes(tmp_path,monkeypatch):
    monkeypatch.delenv('BLENDER_BIN',raising=False)
    monkeypatch.setattr('verify.shutil.which',lambda name:None)
    report=verify(tmp_path)
    assert report['passed'] is False and report['production'] is False
    assert report['checks']['V1']['status']=='NOT RUN'
    assert report['checks']['V13']['status']=='FAIL'
    assert (tmp_path/'verification_report.md').exists()
