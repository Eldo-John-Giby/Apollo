from pathlib import Path
import copy
import json
import sys

import numpy as np
from PIL import Image
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from gnm_v22_wrap_check import case,compare,COMPARABLE,IMAGE,sha


def test_render_hash_and_declared_case_are_checked(tmp_path):
    image=tmp_path/IMAGE;Image.new('RGB',(8,8),'gray').save(image)
    expected=dict(layout='udim',maps_manifest_sha256='master',size=8)
    receipt=dict(expected,fresh_binding=dict(manifest_sha256='master',layout='udim',full_character=False),
                 images={IMAGE:sha(image)})
    (tmp_path/'comparison.json').write_text(json.dumps(receipt))
    case(tmp_path,expected)
    with pytest.raises(ValueError,match='mismatched'):
        case(tmp_path,dict(expected,layout='legacy'))
    Image.new('RGB',(8,8),'red').save(image)
    with pytest.raises(ValueError,match='Stale wrap image'):case(tmp_path,expected)


def test_layout_comparison_rejects_changed_lighting_or_pixel_difference():
    settings=dict.fromkeys(COMPARABLE,'same');pixels=np.zeros((4,4,3),dtype=np.uint8)
    other=copy.deepcopy(settings)
    assert compare((settings,pixels),(other,pixels+1))['max_absolute_rgb']==1
    other['lights']='different'
    with pytest.raises(ValueError,match='settings differ'):compare((settings,pixels),(other,pixels))
    with pytest.raises(ValueError,match='one RGB'):compare((settings,pixels),(settings,pixels+2))
    incomplete=copy.deepcopy(settings);del incomplete['fresh_only']
    with pytest.raises(ValueError,match='Missing UV'):compare((settings,pixels),(incomplete,pixels))
