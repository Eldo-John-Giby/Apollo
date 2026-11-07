import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from pixel_oracle import measure


def test_geometry_guided_pixel_check_rejects_occlusion_and_false_locations():
    yy,xx=np.indices((120,120));image=np.full((120,120),140.)
    image[(xx+.5-60)**2+(yy+.5-60)**2<14**2]=2
    assert measure(image,[60,60],14)['error_px']<.01
    hidden=image.copy();hidden[:,60:]=140
    with pytest.raises(ValueError):measure(hidden,[60,60],14)
    with pytest.raises(ValueError):measure(image,[75,60],14)
