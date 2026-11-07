import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from analyze_visibility import coverage


def test_mask_detects_half_occlusion_and_bright_pupil():
    mask=np.zeros((100,100));mask[30:70,30:70]=255
    assert coverage(mask,mask,np.zeros_like(mask))==1
    half=mask.copy();half[:,50:]=0
    assert coverage(mask,half)==.5
    assert coverage(mask,mask,np.full_like(mask,100))==0


def test_empty_visibility_mask_rejected():
    with pytest.raises(ValueError,match='Empty'):
        coverage(np.zeros((10,10)),np.zeros((10,10)))
