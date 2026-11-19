from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from gnm_v22_normal_repair import repair


def test_isolated_repair_preserves_every_other_encoded_pixel():
    image=np.full((512,512,3),32768,dtype=np.uint16);image[:,:,2]=65535
    image[256,256]=[32768,32768,100]
    result,changes=repair(image)
    assert len(changes)==1
    assert changes[0]['pixel']==[256,256]
    assert result[256,256,2]==65535
    assert np.count_nonzero(np.any(result!=image,axis=2))==1
    vector=result[256,256].astype(float)*2/65535-1
    assert abs(np.linalg.norm(vector)-1)<.0001


def test_widespread_or_unsupported_normal_damage_is_not_silently_repaired():
    image=np.full((512,512,3),32768,dtype=np.uint16);image[:,:,2]=65535
    image[200:220,200:220,2]=0
    with pytest.raises(ValueError,match='Widespread'):
        repair(image)
    with pytest.raises(ValueError,match='16-bit'):
        repair(image.astype(np.uint8))
