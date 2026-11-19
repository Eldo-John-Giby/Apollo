import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import gnm_v22_still_convergence as check


def fixture(tmp_path):
    paths=[]
    for samples in (512,1024):
        path=tmp_path/f'samples-{samples}.png'
        rng=np.random.default_rng(18)
        image=rng.integers(40,180,size=(1024,1024,3),dtype=np.uint8)
        Image.fromarray(image).save(path)
        record=dict(samples=samples,resolution=[1024,1024],output_sha256=check.sha(path),
            scene_sha256='a'*64,maps={'manifest':'b'*64},recipe_sha256='c'*64,
            blender_build='test-build',camera_matrix=[[1,0],[0,1]],angle=False,side_light=False)
        path.with_suffix('.render.json').write_text(json.dumps(record));paths.append(path)
    return paths


def test_matching_stills_measure_native_crops(tmp_path):
    low,high=fixture(tmp_path)
    result=check.compare(low,high,'full',tmp_path/'analysis')
    assert result['numerically_stable'] is True
    assert set(result['regions'])=={'eyes','skin','lips','ear','hair'}
    assert result['regions']['eyes']['mean_absolute_rgb']==0


def test_changed_camera_cannot_pass_with_identical_pixels(tmp_path):
    low,high=fixture(tmp_path);receipt=high.with_suffix('.render.json')
    record=json.loads(receipt.read_text());record['camera_matrix']=[[0,1],[1,0]]
    receipt.write_text(json.dumps(record))
    with pytest.raises(ValueError,match='policy differ'):check.compare(low,high,'full',tmp_path/'analysis')


def test_changed_image_is_rejected_before_analysis(tmp_path):
    low,high=fixture(tmp_path);Image.new('RGB',(1024,1024),'red').save(high)
    with pytest.raises(ValueError,match='differs from'):check.compare(low,high,'full',tmp_path/'analysis')


def test_large_render_change_fails_existing_limits(tmp_path):
    low,high=fixture(tmp_path)
    image=np.asarray(Image.open(low)).copy();image=np.clip(image.astype(int)+20,0,255).astype(np.uint8)
    Image.fromarray(image).save(low)
    receipt=low.with_suffix('.render.json');record=json.loads(receipt.read_text())
    record['output_sha256']=check.sha(low);receipt.write_text(json.dumps(record))
    assert check.compare(low,high,'full',tmp_path/'analysis')['numerically_stable'] is False


def test_reference_needs_a_higher_sample_count(tmp_path):
    low,high=fixture(tmp_path)
    with pytest.raises(ValueError,match='more samples'):check.compare(high,low,'full',tmp_path/'analysis')


def test_fixed_front_regions_cannot_be_used_for_matching_angle_views(tmp_path):
    low,high=fixture(tmp_path)
    for path in (low,high):
        receipt=path.with_suffix('.render.json');record=json.loads(receipt.read_text())
        record['angle']=True;receipt.write_text(json.dumps(record))
    with pytest.raises(ValueError,match='neutral front view'):check.compare(low,high,'full',tmp_path/'analysis')


def native_fixture(tmp_path):
    sources=fixture(tmp_path);paths=[]
    for samples,source in zip((512,1024),sources):
        path=tmp_path/str(samples)/'fresh-texture-only.png';path.parent.mkdir()
        path.write_bytes(source.read_bytes())
        record=dict(samples=samples,size=1024,images={path.name:check.sha(path)},source_sha256='a'*64,
            target_sha256='b'*64,template_sha256='c'*64,maps_manifest_sha256='d'*64,
            recipe_sha256={'worker':'e'*64},blender_build='test-build',camera_matrix=[[1,0],[0,1]],
            judging_policy={'seed':18},angle=False,oblique=False,fresh_only=True)
        (path.parent/'comparison.json').write_text(json.dumps(record));paths.append(path)
    return paths


def test_fresh_native_pair_uses_native_regions(tmp_path):
    low,high=native_fixture(tmp_path)
    result=check.compare(low,high,'native',tmp_path/'analysis')
    assert result['numerically_stable'] is True
    assert set(result['regions'])=={'eyes','skin','lips','ear'}


def test_native_target_mismatch_is_not_hidden_by_same_pixels(tmp_path):
    low,high=native_fixture(tmp_path);receipt=high.parent/'comparison.json'
    record=json.loads(receipt.read_text());record['target_sha256']='f'*64
    receipt.write_text(json.dumps(record))
    with pytest.raises(ValueError,match='policy differ'):check.compare(low,high,'native',tmp_path/'analysis')
