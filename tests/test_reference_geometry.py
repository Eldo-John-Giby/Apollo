import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from reference_geometry import reference,fit_sphere,surface_centroid


@pytest.mark.parametrize('side',['L','R'])
def test_independent_rotation_and_projection(side):
    for h,v in [(0,0),(-1,-1),(1,1),(-1,1),(1,-1)]:
        r=reference(side,h,v)
        assert np.allclose(r['rotation']@[0,-1,0],r['direction'])
        assert np.allclose(r['rotation'].T@r['rotation'],np.eye(3))
        assert np.linalg.det(r['rotation'])==pytest.approx(1)
        assert r['pixel'][1]<512 if v>0 else r['pixel'][1]>=512


def test_sphere_fit_and_area_centroid():
    rng=np.random.default_rng(2);unit=rng.normal(size=(100,3));unit/=np.linalg.norm(unit,axis=1)[:,None]
    center,radius=fit_sphere(unit*.012+[.0315,0,0])
    assert np.allclose(center,[.0315,0,0]);assert radius==pytest.approx(.012)
    assert np.allclose(surface_centroid([[0,0,0],[2,0,0],[0,2,0]],[[0,1,2]]),[2/3,2/3,0])
