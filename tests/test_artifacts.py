import importlib.util
import json
from pathlib import Path
import sys
from PIL import Image
import pytest
from apollo_core.core import Config,make_record,sweep_inputs
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_metadata import validate_artifacts
from contact_sheet import create
from make_bundle import bundle
from freeze_candidate import freeze

@pytest.fixture
def artifacts(tmp_path):
    (tmp_path/'renders').mkdir()
    records=[]
    for k,t,h,v in sweep_inputs():
        name=f'frame_{k:02d}.png'
        Image.new('RGB',(1024,1024),'gray').save(tmp_path/'renders'/name)
        r=make_record(k,t,h,v,Config(),name)
        r['extra']['fixture']=True
        records.append(r)
    (tmp_path/'metadata.json').write_text(json.dumps(records))
    return tmp_path

def test_artifact_validation_and_sheet(artifacts):
    assert len(validate_artifacts(artifacts))==10
    with Image.open(create(artifacts)) as im:
        assert im.size==(2560,1160)

def test_artifact_missing_frame(artifacts):
    (artifacts/'renders/frame_09.png').unlink()
    with pytest.raises(ValueError): validate_artifacts(artifacts)

def test_artifact_wrong_size(artifacts):
    Image.new('RGB',(10,10)).save(artifacts/'renders/frame_00.png')
    with pytest.raises(ValueError): validate_artifacts(artifacts)

def test_fixture_cannot_be_packaged(artifacts):
    with pytest.raises(ValueError,match='fixtures'):
        bundle(artifacts,'College_RealTeam')

def test_placeholder_rejected(artifacts):
    with pytest.raises(ValueError,match='registered'):
        bundle(artifacts,'College_YourTeamName')

def test_demo_and_candidate_docs(artifacts):
    from demo import export
    from prepare_candidate import prepare
    prepare(artifacts)
    assert 'development fixture' in (artifacts/'README.md').read_text()
    with Image.open(export(artifacts)) as animation:
        assert animation.is_animated and animation.n_frames==10
    assert (artifacts/'PRESENTATION.md').exists()


def production_stage(artifacts):
    import json
    from verify import hashes,verifier_sources,evidence_hashes
    records=json.loads((artifacts/'metadata.json').read_text())
    for record in records: record['extra']['fixture']=False
    (artifacts/'metadata.json').write_text(json.dumps(records))
    (artifacts/'scene.blend').write_bytes(b'unit-test-scene-placeholder')
    create(artifacts)
    for name in ['README.md','ATTRIBUTION.md','verification_report.md']:
        (artifacts/name).write_text('Test-only artifact, not a real verified Blender scene.')
    report={'production':True,'passed':True,'checks':{f'V{i}':{'status':'PASS'} for i in range(1,18)},'artifact_hashes':hashes(artifacts),'verifier_sha256':verifier_sources(),'evidence_sha256':evidence_hashes(artifacts)}
    (artifacts/'verification_report.json').write_text(json.dumps(report))
    return report


def test_bundle_integrity_and_layout(artifacts):
    import zipfile
    production_stage(artifacts)
    archive=bundle(artifacts,'College_TestTeam')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert 'College_TestTeam/wrapper/eyes.py' in z.namelist()
        assert len([n for n in z.namelist() if '/renders/' in n])==10


def test_changed_scene_invalidates_report(artifacts):
    production_stage(artifacts)
    (artifacts/'scene.blend').write_bytes(b'changed-scene')
    with pytest.raises(ValueError,match='changed since verification'):
        bundle(artifacts,'College_TestTeam')


def test_development_freeze_preserves_manifest_and_rejects_stale_inputs(artifacts,tmp_path):
    import hashlib,zipfile
    production_stage(artifacts)
    output=freeze(artifacts,tmp_path/'development.zip')
    with zipfile.ZipFile(output) as archive:
        manifest=json.loads(archive.read('apollo-development/MANIFEST.json'))
        assert all(hashlib.sha256(archive.read('apollo-development/'+name)).hexdigest()==value for name,value in manifest.items())
        assert 'not an organizer submission' in archive.read('apollo-development/README.md').decode()
    (artifacts/'scene.blend').write_bytes(b'changed')
    with pytest.raises(ValueError,match='changed since verification'):freeze(artifacts,output)


def test_missing_check_invalidates_pass_flag(artifacts):
    report=production_stage(artifacts)
    report['checks']['V7']['status']='NOT RUN'
    (artifacts/'verification_report.json').write_text(json.dumps(report))
    with pytest.raises(ValueError,match='seventeen'):
        bundle(artifacts,'College_TestTeam')


def test_changed_diagnostic_invalidates_package(artifacts):
    production_stage(artifacts)
    evidence=artifacts/'verification';evidence.mkdir()
    (evidence/'baseline.png').write_bytes(b'added-after-qualification')
    with pytest.raises(ValueError,match='Verifier/evidence'):
        bundle(artifacts,'College_TestTeam')
