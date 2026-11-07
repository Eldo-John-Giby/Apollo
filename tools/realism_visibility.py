"""Render an 81-point square grid plus 32 seeded random poses, then real masks.

Independent visual stress manifest; does not change the official/dataset protocol.
Supports source-bound, image-hash-checked checkpoint resume.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import shutil
import sys


def poses():
    anchors=[(h,v) for h in [-1.,0.,1.] for v in [-1.,0.,1.]]
    grid=anchors+[(i/4,j/4) for i in range(-4,5) for j in range(-4,5) if (i/4,j/4) not in anchors]
    rng=random.Random(0)
    return grid+[(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(32)]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(folder, mask_folder, limit=113, cache=None):
    import bpy
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'wrapper'));sys.path.insert(0,str(root/'tools'))
    import eyes
    from dataset_protocol import atomic_json
    from visibility_audit import run as masks
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=True)
    run={'schema_version':'apollo.realism-visibility/1','scene_sha256':digest(bpy.data.filepath),
         'wrapper_sha256':digest(root/'wrapper/eyes.py'),'worker_sha256':digest(__file__),
         'blender':bpy.app.version_string,'samples':bpy.context.scene.cycles.samples,'poses':113}
    progress=folder/'progress.json';records=[]
    if progress.exists():
        old=json.loads(progress.read_text());assert old['run']==run,'Changed stress-test inputs'
        records=old['frames'];assert len(records)<=113
        for i,r in enumerate(records):
            h,v=poses()[i]
            assert r['frame']==i and r['input']=={'h':h,'v':v}
            assert r['extra']['image']==f'renders/frame_{i:06d}.png'
            assert digest(folder/r['extra']['image'])==r['extra']['image_sha256']
    elif any(folder.iterdir()):raise ValueError('Nonempty output without matching checkpoint')
    cached={}
    if cache is not None:
        cache=Path(cache).resolve();manifest=json.loads((cache/'dataset.json').read_text())
        for key in ['scene_sha256','wrapper_sha256','blender','samples']:
            assert manifest['run'][key]==run[key],'Cache signature mismatch: '+key
        for r in manifest['frames']:cached[(r['input']['h'],r['input']['v'])]=r
    if len(records)>limit:raise ValueError('Preflight limit is below existing completed count')
    for i,(h,v) in enumerate(poses()[len(records):limit],start=len(records)):
        eyes.move(h,v);image=folder/f'renders/frame_{i:06d}.png'
        if (h,v) in cached:
            record=json.loads(json.dumps(cached[(h,v)]))
            old=cache/record['extra']['image'];assert digest(old)==record['extra']['image_sha256']
            image.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,image)
        else:record=eyes.render(image)['record']
        record.pop('theta',None);record['frame']=i
        record['extra']['image']=f'renders/{image.name}';record['extra']['image_sha256']=digest(image)
        records.append(record);atomic_json(progress,{'run':run,'frames':records})
        print('Realism visibility RGB',i+1,'/113',flush=True)
    if limit==113:atomic_json(folder/'dataset.json',{'run':run,'frames':records})
    masks(folder,Path(mask_folder).resolve(),limit,limit!=113)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True);p.add_argument('--masks',type=Path,required=True)
    p.add_argument('--limit',type=int,choices=[9,113],default=113)
    p.add_argument('--cache',type=Path)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(args.folder,args.masks,args.limit,args.cache)
