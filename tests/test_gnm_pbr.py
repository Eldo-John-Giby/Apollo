import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import gnm_run
from gnm_pbr_manifest import load_manifest


def setup_maps(root):
    receipt=dict(source_sha256='a'*64,maps={},
                 material_defaults={str(t):{} for t in (1001,1002,1004)},
                 material_settings={str(t):{} for t in (1001,1002,1004)},
                 corneas={'2':{},'4':{}})
    for role in ('color','roughness','specular','normal'):
        for tile in (1001,1002,1004):
            name=f'{role}.{tile}.png';payload=name.encode()
            (root/name).write_bytes(payload)
            receipt['maps'][name]={'sha256':hashlib.sha256(payload).hexdigest()}
    (root/'manifest.json').write_text(json.dumps(receipt))
    return receipt


def test_complete_pbr_set_rejects_missing_and_corrupt_eyes(tmp_path):
    receipt=setup_maps(tmp_path)
    assert len(gnm_run.surface_files(tmp_path))==13
    (tmp_path/'normal.1004.png').write_bytes(b'corrupt')
    with pytest.raises(ValueError,match='checksum'):
        gnm_run.surface_files(tmp_path)
    (tmp_path/'normal.1004.png').unlink()
    with pytest.raises(ValueError,match='Missing'):
        load_manifest(tmp_path)
    receipt['maps'].pop('normal.1004.png')
    (tmp_path/'manifest.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError,match='Incomplete'):
        load_manifest(tmp_path)


def test_missing_skin_normal_does_not_fall_back_to_legacy_height_mode(tmp_path):
    setup_maps(tmp_path)
    (tmp_path/'normal.1001.png').unlink()
    with pytest.raises(ValueError,match='Missing PBR map normal.1001'):
        gnm_run.surface_files(tmp_path)


def test_unfinished_bake_is_rejected_even_after_all_map_files_exist(tmp_path):
    receipt=setup_maps(tmp_path);receipt['complete']=False
    (tmp_path/'manifest.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError,match='final source checks'):
        load_manifest(tmp_path)


@pytest.mark.parametrize('builder',['variants','texture_only'])
def test_derivatives_reject_unfinished_master_before_creating_outputs(tmp_path,builder):
    import gnm_v22_variants
    import gnm_v22_texture_only
    master=tmp_path/'master';master.mkdir()
    receipt=setup_maps(master);receipt['complete']=False
    (master/'manifest.json').write_text(json.dumps(receipt))
    out=tmp_path/'derived'
    args=SimpleNamespace(master=master,out=out)
    build=gnm_v22_variants.build if builder=='variants' else gnm_v22_texture_only.main
    with pytest.raises(ValueError,match='final source checks'):
        build(args)
    assert not out.exists()


def test_variant_cache_covers_cornea_recipe_and_shader_code(tmp_path,monkeypatch):
    receipt=setup_maps(tmp_path)
    monkeypatch.setattr(gnm_run,'ROOT',tmp_path)
    (tmp_path/'tools').mkdir()
    recipes=('gnm_materials.py','gnm_motion_variant.py','gnm_portable.py',
             'gnm_v22_materials.py','gnm_pbr_manifest.py','gnm_v22_audit.py')
    for name in recipes:(tmp_path/'tools'/name).write_text('recipe')
    scene=tmp_path/'scene.blend';scene.write_bytes(b'packed scene')
    initial=gnm_run.variant_identity(scene,tmp_path,'udim')
    receipt['corneas']['2']['nodes']=[{'test':'changed corneal film'}]
    (tmp_path/'manifest.json').write_text(json.dumps(receipt))
    changed=gnm_run.variant_identity(scene,tmp_path,'udim')
    assert changed!=initial
    (tmp_path/'tools/gnm_v22_materials.py').write_text('changed shader binding')
    assert changed!=gnm_run.variant_identity(scene,tmp_path,'udim')


def test_manifest_does_not_accept_maps_outside_texture_directory(tmp_path):
    receipt=setup_maps(tmp_path)
    receipt['maps']['../outside.png']={'sha256':'0'*64}
    (tmp_path/'manifest.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError,match='filename'):
        load_manifest(tmp_path)


@pytest.mark.parametrize('full_character',[False,True])
def test_existing_still_command_selects_full_character_when_supplied(tmp_path,monkeypatch,full_character):
    monkeypatch.setattr(gnm_run,'ROOT',tmp_path)
    model=tmp_path/'model';model.mkdir()
    (model/'neutral.blend').write_bytes(b'legacy native target')
    if full_character:(model/'character.blend').write_bytes(b'approved full character')
    monkeypatch.setattr(sys,'argv',['gnm_run.py','still','--blender',str(tmp_path/'blender.exe'),
                                    '--out',str(tmp_path/'render.png')])
    calls=[]
    def run(command,**kwargs):
        calls.append(command);return SimpleNamespace(returncode=0)
    monkeypatch.setattr(gnm_run.subprocess,'run',run)
    assert gnm_run.main()==0
    expected=model/('character.blend' if full_character else 'neutral.blend')
    assert str(expected) in calls[0]
    if full_character:
        assert '--scene-samples' in calls[0]
        assert '--samples' not in calls[0]
    else:
        assert calls[0][calls[0].index('--samples')+1]=='32'
        assert '--scene-samples' not in calls[0]
