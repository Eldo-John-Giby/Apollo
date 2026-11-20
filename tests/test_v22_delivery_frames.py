from contextlib import contextmanager
import io
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, PngImagePlugin
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import gnm_v22_delivery_frames as check


def save(path,value):path.write_text(json.dumps(value),encoding='utf-8')


@pytest.fixture(scope='module')
def delivery(tmp_path_factory):
    root=tmp_path_factory.mktemp('delivery inventory')
    scenes=root/'timelines';geometry=root/'geometry';frames=root/'frames'
    images=[]
    for color in ('#203040','#304050'):
        stream=io.BytesIO();Image.new('RGB',(1024,1024),color).save(stream,format='PNG');images.append(stream.getvalue())
    import hashlib
    digests=[hashlib.sha256(data).hexdigest() for data in images]
    for mode in check.MODES:
        for directory in (scenes/mode,geometry/mode,frames/mode):directory.mkdir(parents=True)
        scene=scenes/mode/'expression.blend';scene.write_bytes(b'SCENE FIXTURE '+mode.encode())
        sequence=np.zeros(192,dtype=np.int64);sequence[25]=sequence[107]=1
        if mode!='generate-motion':sequence[-1]=1
        pose=geometry/mode/'expression.npz'
        np.savez_compressed(pose,mode=mode,sequence=sequence,poses=np.zeros((2,3,3)))
        save(scene.with_suffix('.prepare.json'),dict(scene_sha256=check.sha(scene),geometry_sha256=check.sha(pose),
            selected_sha256=check.SELECTED,samples=512,geometry_and_uv_unchanged=True,judging_policy=check.POLICY))
        run=dict(scene_sha256=check.sha(scene),mode=mode,renderer_sha256=check.sha(check.ROOT/'tools/submission_render.py'),
            png_policy_sha256=check.sha(check.ROOT/'apollo_core/png.py'),blender_build='5afeabba6097',
            resolution=[1024,1024],samples=512,fps=24.0,range=[1,192],reuse_holds=True)
        records={}
        for number in range(1,193):
            index=int(sequence[number-1]);name=f'frame_{number:04d}.png'
            (frames/mode/name).write_bytes(images[index])
            source=None if number in (1,26) else (26 if index else 1)
            records[name]=dict(sha256=digests[index],reused_frame=source)
        save(frames/mode/'render-receipt.json',dict(run=run,frames=records))
    return scenes,geometry,frames


@contextmanager
def replace(path,data):
    before=path.read_bytes();path.write_bytes(data)
    try:yield
    finally:path.write_bytes(before)


def test_full_inventory_and_exact_neutral_reset(delivery):
    result=check.verify(*delivery,512)
    assert result['frames']==576
    assert result['unique_png_payloads']==2
    assert all(mode['unique_poses']==2 for mode in result['modes'].values())
    assert all(mode['reused_frames']==190 for mode in result['modes'].values())
    assert result['modes']['generate-motion']['returns_to_initial_pose'] is True
    assert result['modes']['left']['returns_to_initial_pose'] is False
    assert result['modes']['right']['neutral_reset_sha256'] is None


def test_missing_frame_cannot_count_as_complete(delivery):
    path=delivery[2]/'left/frame_0192.png';before=path.read_bytes();path.unlink()
    try:
        with pytest.raises(ValueError,match='exactly 192'):check.verify(*delivery,512)
    finally:path.write_bytes(before)


def test_changed_frame_is_detected(delivery):
    with replace(delivery[2]/'left/frame_0002.png',b'broken'):
        with pytest.raises(ValueError,match='changed frame'):check.verify(*delivery,512)


def test_stale_settings_are_rejected(delivery):
    path=delivery[2]/'left/render-receipt.json';record=json.loads(path.read_text());record['run']['samples']=32
    with replace(path,json.dumps(record).encode()):
        with pytest.raises(ValueError,match='settings differ'):check.verify(*delivery,512)


def test_same_image_hash_cannot_justify_reuse_across_poses(delivery):
    path=delivery[2]/'left/render-receipt.json';record=json.loads(path.read_text())
    # Point to the other pose and forge only its receipt hash. The independent
    # authenticated sequence rejects this before that target frame is read.
    record['frames']['frame_0002.png']['reused_frame']=26
    record['frames']['frame_0026.png']['sha256']=record['frames']['frame_0002.png']['sha256']
    with replace(path,json.dumps(record).encode()):
        with pytest.raises(ValueError,match='invalid hold reuse'):check.verify(*delivery,512)


def test_private_png_metadata_is_rejected_even_with_matching_hash(delivery):
    import hashlib
    path=delivery[2]/'left/frame_0001.png';receipt=path.parent/'render-receipt.json'
    info=PngImagePlugin.PngInfo();info.add_text('Comment','author-machine path fixture')
    stream=io.BytesIO();Image.new('RGB',(1024,1024),'#203040').save(stream,format='PNG',pnginfo=info)
    data=stream.getvalue();record=json.loads(receipt.read_text())
    record['frames'][path.name]['sha256']=hashlib.sha256(data).hexdigest()
    with replace(path,data),replace(receipt,json.dumps(record).encode()):
        with pytest.raises(ValueError,match='noncanonical'):check.verify(*delivery,512)


def test_changed_geometry_cannot_reuse_the_inventory(delivery):
    with replace(delivery[1]/'left/expression.npz',b'changed'):
        with pytest.raises(ValueError,match='differs from preparation'):check.verify(*delivery,512)


def test_inventory_cli_imports_from_outside_the_checkout(tmp_path):
    import subprocess
    result=subprocess.run([sys.executable,'-I',str(check.ROOT/'tools/gnm_v22_delivery_frames.py'),'--help'],
        cwd=tmp_path,text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    assert '--timelines' in result.stdout and '--geometry' in result.stdout


def test_generate_motion_must_return_to_neutral(delivery):
    path=delivery[1]/'generate-motion/expression.npz'
    prepared=delivery[0]/'generate-motion/expression.prepare.json'
    sequence=np.zeros(192,dtype=np.int64);sequence[25]=sequence[107]=sequence[-1]=1
    stream=io.BytesIO();np.savez_compressed(stream,mode='generate-motion',sequence=sequence,poses=np.zeros((2,3,3)))
    data=stream.getvalue();record=json.loads(prepared.read_text())
    import hashlib
    record['geometry_sha256']=hashlib.sha256(data).hexdigest()
    with replace(path,data),replace(prepared,json.dumps(record).encode()):
        with pytest.raises(ValueError,match='does not return'):check.verify(*delivery,512)
