"""Height-map precision must survive authoring rather than clip to white."""
from pathlib import Path
import sys

import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from gnm_portrait_maps import read_data_image


def test_sixteen_bit_height_preserves_real_relief(tmp_path):
    values=np.array([[19390,26188],[32585,34046]],dtype=np.uint16)
    path=tmp_path/'height.png';Image.fromarray(values).save(path)
    result=read_data_image(path)
    np.testing.assert_allclose(result,values.astype(float)/65535,rtol=1e-7)
    assert np.ptp(result)>.2
    assert result.max()<.53


def test_eight_bit_roughness_uses_its_own_precision(tmp_path):
    values=np.array([[0,106],[165,255]],dtype=np.uint8)
    path=tmp_path/'roughness.png';Image.fromarray(values).save(path)
    np.testing.assert_allclose(read_data_image(path),values.astype(float)/255,rtol=1e-7)
