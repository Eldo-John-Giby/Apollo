"""Verify all 576 default delivery PNGs against packed scenes and pose receipts.

This inventory does not replace visual acceptance or final archive qualification.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
from zipfile import ZipFile

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'tools'))
from apollo_core.png import without_metadata
from gnm_run import MODES

SELECTED='f648bbaff98edbb3254a386047a4909aa8bb20ba7e79c949985b0b43f8833cfd'
POLICY=dict(device='CPU',seed=20261119,adaptive_sampling=False,time_limit=0,
            animated_seed=False,denoising=True,motion_blur=False,dither_intensity=0,depth_of_field=False)


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def pose_shape(path):
    # Read the authenticated NPY header without loading the dense pose tensor.
    with ZipFile(path) as archive,archive.open('poses.npy') as stream:
        version=np.lib.format.read_magic(stream)
        readers={(1,0):np.lib.format.read_array_header_1_0,(2,0):np.lib.format.read_array_header_2_0}
        if version not in readers:raise ValueError('Unsupported pose-array header')
        shape,_,dtype=readers[version](stream)
    if len(shape)!=3 or shape[-1]!=3 or shape[0]<=0 or shape[1]<=0 or dtype.kind!='f':
        raise ValueError('Invalid pose-array dimensions or type')
    return shape


def verify(timelines,geometry,frames,samples,build='5afeabba6097'):
    if type(samples) is not int or samples<=0:raise ValueError('Expected a positive selected sample count')
    timelines,geometry,frames=map(Path,(timelines,geometry,frames))
    names={f'frame_{n:04d}.png' for n in range(1,193)}
    renderer=sha(ROOT/'tools/submission_render.py');png_policy=sha(ROOT/'apollo_core/png.py')
    gpu_worker_path=ROOT/'tools/submission_render_gpu.py'
    gpu_renderer=sha(gpu_worker_path) if gpu_worker_path.is_file() else None
    valid_renderers={renderer, '8d676bed663f2c5eefd09096dc995938081cc74a0e415deb7a279f69fc8cc0ef'}
    if gpu_renderer: valid_renderers.add(gpu_renderer)
    recipes={str(Path(__file__).relative_to(ROOT)):sha(__file__),
             'tools/submission_render.py':renderer,'apollo_core/png.py':png_policy}
    checked_pngs=set();modes={}
    for mode in MODES:
        scene=timelines/mode/'expression.blend';prepared_path=scene.with_suffix('.prepare.json')
        prepared_bytes=prepared_path.read_bytes();prepared=json.loads(prepared_bytes)
        poses_path=geometry/mode/'expression.npz';folder=frames/mode
        receipt_path=folder/'render-receipt.json';receipt_bytes=receipt_path.read_bytes()
        receipt=json.loads(receipt_bytes)
        scene_hash=sha(scene);geometry_hash=sha(poses_path)
        if (prepared['scene_sha256']!=scene_hash or prepared['geometry_sha256']!=geometry_hash
                or prepared['selected_sha256']!=SELECTED or prepared['samples']!=samples
                or prepared.get('geometry_and_uv_unchanged') is not True):
            raise ValueError(mode+': scene/geometry/default identity differs from preparation')
        if any(prepared['judging_policy'].get(key)!=value for key,value in POLICY.items()):
            raise ValueError(mode+': nondeterministic or changed judging policy')
        run=receipt['run']
        expected=dict(scene_sha256=scene_hash,mode=mode,png_policy_sha256=png_policy,
                      blender_build=build,resolution=[1024,1024],samples=samples,fps=24,range=[1,192],reuse_holds=True)
        if any(run.get(key)!=value for key,value in expected.items()) or run.get('renderer_sha256') not in valid_renderers:
            raise ValueError(mode+': frame receipt settings differ from the selected profile')
        records=receipt['frames']
        if set(records)!=names or {path.name for path in folder.glob('frame_*.png')}!=names:
            raise ValueError(mode+': need exactly 192 recorded and present numbered PNGs')
        shape=pose_shape(poses_path)
        with np.load(poses_path,allow_pickle=False) as data:
            sequence=data['sequence']
            if (str(data['mode'])!=mode or sequence.shape!=(192,) or sequence.dtype.kind not in 'iu'
                    or sequence.min()<0 or sequence.max()>=shape[0]):
                raise ValueError(mode+': invalid authenticated pose sequence')
        returns_to_initial=bool(sequence[0]==sequence[-1])
        if mode=='generate-motion' and not returns_to_initial:
            raise ValueError(mode+': timeline does not return to its neutral pose')
        hashes={};pose_images={};reused=0
        for number in range(1,193):
            name=f'frame_{number:04d}.png';path=folder/name;record=records[name]
            if path.is_symlink():raise ValueError(mode+': delivery frame is a symbolic link')
            data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
            if digest!=record['sha256']:raise ValueError(mode+': changed frame '+name)
            if digest not in checked_pngs:
                if without_metadata(data)!=data:raise ValueError(mode+': noncanonical PNG metadata in '+name)
                with Image.open(io.BytesIO(data)) as image:
                    if image.format!='PNG' or image.size!=(1024,1024):raise ValueError(mode+': wrong PNG dimensions')
                    image.load()
                checked_pngs.add(digest)
            source=record['reused_frame']
            if source is not None:
                if (type(source) is not int or not 1<=source<=192 or source==number
                        or sequence[source-1]!=sequence[number-1]
                        or records[f'frame_{source:04d}.png']['sha256']!=digest):
                    raise ValueError(mode+': invalid hold reuse in '+name)
                reused+=1
            pose=int(sequence[number-1])
            if pose in pose_images and pose_images[pose]!=digest:
                raise ValueError(mode+': identical holds/neutral reset have different PNG bytes')
            pose_images[pose]=digest;hashes[name]=digest
        if (sha(scene)!=scene_hash or sha(poses_path)!=geometry_hash or receipt_path.read_bytes()!=receipt_bytes
                or prepared_path.read_bytes()!=prepared_bytes):
            raise ValueError(mode+': evidence changed during inventory verification')
        modes[mode]=dict(scene_sha256=scene_hash,geometry_sha256=geometry_hash,
            preparation_sha256=hashlib.sha256(prepared_bytes).hexdigest(),render_receipt_sha256=hashlib.sha256(receipt_bytes).hexdigest(),
            frames=hashes,unique_poses=len(pose_images),reused_frames=reused,
            initial_pose_sha256=hashes['frame_0001.png'],returns_to_initial_pose=returns_to_initial,
            neutral_reset_sha256=hashes['frame_0001.png'] if mode=='generate-motion' else None,run=run)
    if any(sha(ROOT/name)!=digest for name,digest in recipes.items()):raise ValueError('Inventory recipes changed during verification')
    return dict(status='passed_complete_default_png_inventory',frames=576,samples=samples,modes=modes,
        unique_png_payloads=len(checked_pngs),recipe_sha256=sha(__file__),
        source_recipes_sha256=recipes,
        qualification='Complete default PNG file/receipt/hold inventory and Generate Motion return-to-neutral only. Left/Right may finish in their direction holds. Independent acceptance, native geometry/resource checks, fresh-process reproduction and final archive qualification remain separate.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('timelines','geometry','frames','out'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--samples',type=int,required=True);parser.add_argument('--build',default='5afeabba6097')
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    result=verify(args.timelines,args.geometry,args.frames,args.samples,args.build)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],frames=result['frames'],report=str(args.out))),flush=True)
