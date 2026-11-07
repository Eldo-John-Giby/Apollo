"""Stress poses must include boundaries and reproducible off-grid inputs."""
from tools.realism_visibility import poses


def test_grid_and_random_coverage():
    a=poses()
    assert len(a)==113 and len(set(a))==113
    assert set(a[:9])=={(h,v) for h in [-1.,0.,1.] for v in [-1.,0.,1.]}
    assert set(a[:81])=={(i/4,j/4) for i in range(-4,5) for j in range(-4,5)}
    assert a==poses()
    assert all(-1<=h<=1 and -1<=v<=1 for h,v in a)
