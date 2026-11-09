import copy
import json
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


@pytest.mark.parametrize('blocked_attempts', [2, 6])
def test_checkpoint_replace_retries_preserving_previous_data(tmp_path, monkeypatch, blocked_attempts):
    checkpoint = tmp_path/'progress.json'
    atomic_json(checkpoint, {'frame': 1})
    original_replace = Path.replace
    attempts = []

    def replace_with_reader_lock(temporary, target):
        attempts.append(target)
        if len(attempts) <= blocked_attempts:
            assert json.loads(checkpoint.read_text()) == {'frame': 1}
            raise PermissionError('Checkpoint reader holds a Windows handle')
        return original_replace(temporary, target)

    monkeypatch.setattr(Path, 'replace', replace_with_reader_lock)
    monkeypatch.setattr('dataset_protocol.time.sleep', lambda seconds: None)
    if blocked_attempts == 6:
        with pytest.raises(PermissionError):
            atomic_json(checkpoint, {'frame': 2})
        assert json.loads(checkpoint.read_text()) == {'frame': 1}
        assert json.loads(checkpoint.with_suffix('.json.tmp').read_text()) == {'frame': 2}
    else:
        atomic_json(checkpoint, {'frame': 2})
        assert len(attempts) == 3
        assert json.loads(checkpoint.read_text()) == {'frame': 2}
