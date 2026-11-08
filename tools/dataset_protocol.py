"""Dataset protocol is separate from the canonical ten-frame sweep."""
import hashlib
import json
from pathlib import Path
import random


def inputs(count,seed):
    if type(count)is not int or count<9:raise ValueError('Dataset needs at least nine anchor poses')
    if type(seed)is not int:raise ValueError('Seed must be an integer')
    rng=random.Random(seed)
    return [(h,v) for h in [-1.,0.,1.] for v in [-1.,0.,1.]]+[(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(count-9)]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path,value):
    path=Path(path);temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8');temporary.replace(path)


def signature(scene,wrapper,count,seed,samples,version):
    return {'schema_version':'apollo.dataset/1','scene_sha256':digest(scene),'wrapper_sha256':digest(wrapper),'generator_sha256':digest(Path(__file__).with_name('generate_dataset.py')),'protocol_sha256':digest(__file__),'reference_sha256':digest(Path(__file__).with_name('reference_geometry.py')),'count':count,'seed':seed,'samples':samples,'blender':version}


def resume(folder,run):
    folder=Path(folder)
    progress=folder/'progress.json'
    if not progress.exists():
        if any(folder.iterdir()):raise ValueError('Nonempty dataset folder without matching progress')
        return []
    previous=json.loads(progress.read_text(encoding='utf-8'))
    if previous['run']!=run:raise ValueError('Dataset inputs/configuration changed; choose a new output folder')
    records=previous['frames']
    expected=inputs(run['count'],run['seed'])
    if len(records)>len(expected):raise ValueError('Too many dataset records')
    for i,frame in enumerate(records):
        if frame['frame']!=i or frame['input']!={'h':expected[i][0],'v':expected[i][1]}:raise ValueError('Dataset sequence mismatch')
        image=frame['extra']['image']
        if image!=f'renders/frame_{i:06d}.png':raise ValueError('Invalid dataset image path')
        if digest(folder/image)!=frame['extra']['image_sha256']:raise ValueError('Completed dataset image changed')
    return records
