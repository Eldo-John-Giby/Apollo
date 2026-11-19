from pathlib import Path
import sys

import cv2
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from gnm_v22_texture_check import check_map


def test_overlay_requires_actual_16_bit_alpha_channel(tmp_path):
    path=tmp_path/'overlay.png'
    image=np.full((8,8,4),32000,dtype=np.uint16)
    cv2.imwrite(str(path),image)
    assert check_map(path,8,'overlay',4)['bit_depth']==16
    cv2.imwrite(str(path),image[:,:,:3])
    with pytest.raises(ValueError,match='RGBA'):
        check_map(path,8,'overlay',4)


def test_decoder_rejects_actual_low_precision_and_wrong_dimensions(tmp_path):
    path=tmp_path/'color.png'
    cv2.imwrite(str(path),np.full((8,8,3),128,dtype=np.uint8))
    with pytest.raises(ValueError,match='16-bit'):
        check_map(path,8,'color')
    cv2.imwrite(str(path),np.full((8,8,3),32000,dtype=np.uint16))
    with pytest.raises(ValueError,match='dimensions'):
        check_map(path,16,'color')


def test_normal_validation_distinguishes_padding_from_inverted_or_short_vectors(tmp_path):
    path=tmp_path/'normal.png'
    image=np.zeros((8,8,3),dtype=np.uint16)
    image[2:6,2:6]=[65535,32768,32768]  # OpenCV BGR: tangent +Z.
    cv2.imwrite(str(path),image)
    checked=check_map(path,8,'normal')
    assert checked['covered_pixels']==16
    assert checked['negative_z_pixels']==0
    image[2:6,2:6]=[0,32768,32768]
    cv2.imwrite(str(path),image)
    with pytest.raises(ValueError,match='normal vectors'):
        check_map(path,8,'normal')
    image[2:6,2:6]=[32768,32768,32768]
    cv2.imwrite(str(path),image)
    with pytest.raises(ValueError,match='normal vectors'):
        check_map(path,8,'normal')
