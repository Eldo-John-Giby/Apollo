import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import gnm_v22_stage as stage


def save(path,value):path.write_text(json.dumps(value))


def test_staging_rejects_changed_scenes_and_narrow_verification(tmp_path):
    scene=tmp_path/'expression.blend';scene.write_bytes(b'PACKAGING TEST')
    digest=stage.sha(scene)
    save(scene.with_suffix('.prepare.json'),dict(scene_sha256=digest,maps_manifest_sha256='maps',
         samples=512,geometry_and_uv_unchanged=True))
    checked=dict(scene_sha256=digest,status='passed_geometry_and_resources',frames=[1+i*.5 for i in range(383)],
                 verifier_sha256=stage.sha(stage.ROOT/'tools/gnm_v22_verify.py'),
                 portable_binding=dict(manifest_sha256='maps'))
    save(tmp_path/'half-frame-check.json',checked)
    save(tmp_path/'appearance-check.json',dict(scene_sha256=digest,objects=dict.fromkeys(map(str,range(18))),
         recipe_sha256=stage.sha(stage.ROOT/'tools/gnm_v22_appearance_check.py'),passed=True,
         portable_binding=dict(manifest_sha256='maps')))
    assert stage.timeline(tmp_path,'maps')[0]==scene
    checked['frames']=[1,107,112];save(tmp_path/'half-frame-check.json',checked)
    with pytest.raises(ValueError,match='integer and half'):stage.timeline(tmp_path,'maps')
    scene.write_bytes(b'CHANGED')
    with pytest.raises(ValueError,match='Stale packed'):stage.timeline(tmp_path,'maps')


def test_staged_public_cli_imports_from_outside_project_without_authoring_modules(tmp_path):
    # Invoke the copied host CLI with isolated Python path handling, from
    # outside the project; no authoring checkout is added to sys.path.
    import shutil
    for name in stage.RUNTIME:
        target=tmp_path/'runtime'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(stage.ROOT/name,target)
    result=subprocess.run([sys.executable,'-I',str(tmp_path/'runtime/tools/gnm_run.py'),'--help'],
                          cwd=tmp_path,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert 'generate-motion' in result.stdout and 'golden-hazel' in result.stdout
