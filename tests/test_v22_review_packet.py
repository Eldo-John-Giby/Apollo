import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from zipfile import ZipFile

from PIL import Image
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from gnm_v22_review_packet import authenticated,validate,main,sha,VARIANTS,MODES,DIRECTIONS


def fixture(tmp_path):
    image=tmp_path/'source.png';Image.new('RGB',(16,16),'gray').save(image)
    scene=tmp_path/'motion.blend';scene.write_bytes(b'PACKAGING TEST ONLY')
    picture=dict(file=image.name,sha256=sha(image));packed=dict(file=scene.name,sha256=sha(scene))
    return dict(appearance=[dict(candidate=True,variant=v,output=o,images=[picture])
                          for v in VARIANTS for o in ('full','texture_only')]+
                          [dict(candidate=False,reference=r,images=[picture]) for r in ('rc5','v22')],
                directions=[dict(expected=d,neutral=picture,judgment=picture) for d in DIRECTIONS],
                motion=[dict(candidate=True,mode=m,scene=packed) for m in MODES])


def test_packet_separates_answers_and_keeps_responses_blank(tmp_path):
    spec=tmp_path/'spec.json';spec.write_text(json.dumps(fixture(tmp_path)))
    out=tmp_path/'packet';main(SimpleNamespace(spec=spec,out=out,seed=17))
    key=json.loads((out/'assessor-key.json').read_text())
    with ZipFile(out/'apollo-v22-independent-review.zip') as archive:
        assert 'assessor-key.json' not in archive.namelist()
        response=json.loads(archive.read('responses.json'))
        assert response['key_sha256']==sha(out/'assessor-key.json')
        assert response['independent_first_pass'] is None and response['severe_defects'] is None
        assert all(value is None for value in response['directions'].values())
        assert len([n for n in archive.namelist() if n.endswith('.blend')])==3
        for name,digest in key['packet_files'].items():
            import hashlib
            assert hashlib.sha256(archive.read(name)).hexdigest()==digest


def test_missing_scope_and_changed_payload_cannot_make_packet(tmp_path):
    spec=fixture(tmp_path);bad=copy.deepcopy(spec);bad['appearance'].pop(0)
    with pytest.raises(ValueError,match='all five'):validate(bad)
    entry=spec['appearance'][0]['images'][0]
    (tmp_path/entry['file']).write_bytes(b'changed')
    with pytest.raises(ValueError,match='changed review input'):authenticated(tmp_path,entry,'.png')
