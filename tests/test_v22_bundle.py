import hashlib
import json
from pathlib import Path
import sys
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from gnm_bundle_verify import verify, safe_name
import gnm_v22_bundle as bundle


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


def fixture(tmp_path):
    runtime=tmp_path/'runtime';licenses=tmp_path/'licenses'
    hashes={}
    for name in ['tools/gnm_run.py', *[f'timelines/{m}/expression.blend' for m in bundle.MODES],
                 *[f'textures/{v}/manifest.json' for v in bundle.VARIANTS]]:
        path=runtime/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(name);hashes[name]=bundle.sha(path)
    maps={v:hashes[f'textures/{v}/manifest.json'] for v in bundle.VARIANTS}
    save(runtime/'runtime-manifest.json',dict(status='development_runtime_staged',
         selected_sha256='identity',sha256=hashes,maps_manifest_sha256=maps))
    names=['assets/gnm/LICENSE.txt','assets/gnm/source.json','assets/gnm-scan/LICENSE.txt',
           'assets/gnm-scan/source.json','assets/gnm-eye-photo/source.json',
           'assets/v22-provenance.json','Google-GNM-LICENSE.txt','ATTRIBUTION.md']
    retained={}
    for name in names:
        path=licenses/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('retained fixture notice: '+name);retained[name]=bundle.sha(path)
    save(licenses/'attribution-receipt.json',dict(selected_sha256='identity',
         texture_manifests=maps,files=retained))
    return runtime,licenses


def test_archive_roundtrip_and_corruption_are_checked(tmp_path):
    runtime,licenses=fixture(tmp_path)
    archive=tmp_path/'bundle.zip'
    result=bundle.build(runtime,licenses,{},archive,source_revision='a'*40,source_dirty=False)
    assert result['release_ready'] is False
    extracted=tmp_path/'clean path'
    with zipfile.ZipFile(archive) as package:package.extractall(extracted)
    assert verify(extracted,True)['release_ready'] is False
    assert 'frozen regeneration' in verify(extracted)['qualification']
    changed=extracted/'timelines/left/expression.blend';changed.write_bytes(b'broken')
    with pytest.raises(ValueError,match='Changed bundle'):verify(extracted)


def test_package_rejects_changed_inputs_and_wrong_attribution(tmp_path):
    runtime,licenses=fixture(tmp_path)
    receipt=licenses/'attribution-receipt.json'
    value=json.loads(receipt.read_text());value['selected_sha256']='wrong'
    save(receipt,value)
    with pytest.raises(ValueError,match='Attribution'):bundle.collect(runtime,licenses,{})
    value['selected_sha256']='identity';save(receipt,value)
    (licenses/'Google-GNM-LICENSE.txt').write_text('changed')
    with pytest.raises(ValueError,match='Changed input'):bundle.collect(runtime,licenses,{})


@pytest.mark.parametrize('name',['../outside','/absolute','C:/path','a\\b','a//b','a/./b','a/../b','',
                                 'CON.txt','a/aux','a/b.','a/b ','a/b\x00c'])
def test_manifest_paths_cannot_escape(name):
    with pytest.raises(ValueError):safe_name(name)


def test_case_collisions_missing_files_and_extra_payloads(tmp_path):
    root=tmp_path/'bundle';root.mkdir();(root/'input.txt').write_bytes(b'ok')
    digest=hashlib.sha256(b'ok').hexdigest()
    manifest=dict(schema=1,sha256={'input.txt':digest,'INPUT.txt':digest})
    save(root/'manifest.json',manifest)
    with pytest.raises(ValueError,match='Case-colliding'):verify(root)
    manifest['sha256']={'missing.txt':digest};save(root/'manifest.json',manifest)
    with pytest.raises(ValueError,match='Missing'):verify(root)
    manifest['sha256']={'input.txt':digest};save(root/'manifest.json',manifest)
    (root/'accidental.env').write_bytes(b'not intended')
    with pytest.raises(ValueError,match='Unexpected'):verify(root,True)


def test_extras_cannot_replace_licenses_or_runtime(tmp_path):
    runtime,licenses=fixture(tmp_path)
    with pytest.raises(ValueError,match='Duplicate'):
        bundle.collect(runtime,licenses,{'TOOLS/GNM_RUN.PY':runtime/'tools/gnm_run.py'})


def test_verifier_runs_isolated_without_project_imports(tmp_path):
    import shutil
    import subprocess
    root=tmp_path/'isolated bundle';root.mkdir()
    script=root/'tools/gnm_bundle_verify.py';script.parent.mkdir()
    shutil.copyfile(bundle.ROOT/'tools/gnm_bundle_verify.py',script)
    save(root/'manifest.json',dict(schema=1,sha256={'tools/gnm_bundle_verify.py':bundle.sha(script)},
         qualification='fixture',release_ready=False))
    result=subprocess.run([sys.executable,'-I',str(script),'--reject-extra'],cwd=tmp_path,
                          text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    assert json.loads(result.stdout)['release_ready'] is False
