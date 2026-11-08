import copy
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from dataset_protocol import inputs,resume,atomic_json,digest


def test_seeded_inputs_cover_anchors_and_repeat():
    a=inputs(256,0)
    assert a==inputs(256,0) and a!=inputs(256,1)
    assert len(set(a[:9]))==9 and (0,0) in a[:9]
    assert all(-1<=x<=1 for pair in a for x in pair)


@pytest.mark.parametrize('count',[0,8,True,-1,9.5])
def test_invalid_count(count):
    with pytest.raises(ValueError):inputs(count,0)


def test_resume_requires_same_inputs_and_intact_images(tmp_path):
    run={'count':9,'seed':0,'scene':'hash-a'}
    (tmp_path/'renders').mkdir();image=tmp_path/'renders/frame_000000.png';image.write_bytes(b'image')
    frame={'frame':0,'input':{'h':-1.,'v':-1.},'extra':{'image':'renders/frame_000000.png','image_sha256':digest(image)}}
    atomic_json(tmp_path/'progress.json',{'run':run,'frames':[frame]})
    assert resume(tmp_path,run)==[frame]
    changed=copy.deepcopy(run);changed['scene']='hash-b'
    with pytest.raises(ValueError,match='changed'):resume(tmp_path,changed)
    image.write_bytes(b'corrupt')
    with pytest.raises(ValueError,match='image changed'):resume(tmp_path,run)


def test_nonempty_output_is_not_silently_overwritten(tmp_path):
    (tmp_path/'unrelated.txt').write_text('preserve')
    with pytest.raises(ValueError,match='Nonempty'):resume(tmp_path,{'count':9,'seed':0})
