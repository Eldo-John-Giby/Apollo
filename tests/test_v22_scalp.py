from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from gnm_v22_scalp import calibrated_restore


def test_forehead_calibration_preserves_unmasked_skin_and_matches_each_palette():
    bare=np.full((4,4,3),.6,dtype=np.float32)
    mask=np.zeros((4,4),dtype=np.float32);mask[0]=1
    donors=np.zeros((4,4),dtype=bool);donors[3]=True
    for pigment in ((.5,.4,.3),(.2,.12,.08)):
        base=np.broadcast_to(np.array(pigment,dtype=np.float32),(4,4,3)).copy()
        color=base.copy();color[0]=.05
        restored,gain=calibrated_restore(color,base,bare,mask,donors)
        np.testing.assert_array_equal(restored[1:],color[1:])
        np.testing.assert_allclose(restored[0],base[0],atol=1e-6)
        assert np.isfinite(gain).all()


def test_invalid_calibration_data_is_rejected():
    image=np.ones((4,4,3),dtype=np.float32)*.5
    mask=np.ones((4,4),dtype=np.float32);donors=np.zeros((4,4),dtype=bool)
    with pytest.raises(ValueError,match='No forehead'):calibrated_restore(image,image,image,mask,donors)
    donors[:]=True
    with pytest.raises(ValueError,match='dimensions'):calibrated_restore(image[:2],image,image,mask,donors)
