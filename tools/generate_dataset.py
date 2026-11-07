"""Seeded, resumable, fixed-light gaze dataset generator inside Blender."""
import argparse
from pathlib import Path
import sys
import time
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'wrapper'))
from dataset_protocol import inputs,digest,atomic_json,signature,resume
from reference_geometry import reference
import eyes


def run(folder,count,seed,samples):
    poses=inputs(count,seed)
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=True)
    source=Path(bpy.data.filepath).resolve()
    if folder==source.parent:raise ValueError('Dataset output must be separate from source scene')
    run_info=signature(source,ROOT/'wrapper/eyes.py',count,seed,samples,bpy.app.version_string)
    frames=resume(folder,run_info);scene=bpy.context.scene;scene.cycles.samples=samples
    lighting=None
    if frames:lighting=frames[0]['extra']['lighting_sha256']
    atomic_json(folder/'progress.json',{'run':run_info,'frames':frames})
    start=time.monotonic();initial=len(frames)
    try:
        for i,(h,v) in enumerate(poses):
            if i<len(frames):continue
            eyes.move(h,v)
            name=f'renders/frame_{i:06d}.png'
            record=eyes.render(folder/name)['record'];record.pop('theta')
            record['frame']=i;record['extra']['image']=name
            record['extra']['image_sha256']=digest(folder/name)
            if lighting is None:lighting=record['extra']['lighting_sha256']
            if record['extra']['lighting_sha256']!=lighting:raise ValueError('Dataset lighting changed')
            cfg=eyes.calibration()
            for side in 'LR':
                expected=reference(side,h,v,ipd=cfg['ipd'],lens=cfg['focal_mm'],sensor=cfg['sensor_mm'],resolution=cfg['res'])
                if np.linalg.norm(expected['pixel']-record['pupil_center_2D_'+side])>=.001:raise ValueError('Independent annotation check failed')
            frames.append(record)
            atomic_json(folder/'progress.json',{'run':run_info,'frames':frames})
            print(f'Dataset {i+1}/{count}',flush=True)
        atomic_json(folder/'dataset.json',{'run':run_info,'annotation_definition':'Analytic projection of the physical pupil-plane center; not a refracted image centroid.','frames':frames})
        atomic_json(folder/'timing.json',{'new_frames':len(frames)-initial,'seconds':time.monotonic()-start})
    finally:eyes.reset()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True);p.add_argument('--count',type=int,default=256);p.add_argument('--seed',type=int,default=0);p.add_argument('--samples',type=int,choices=[8,32,64,128],default=32)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(args.folder,args.count,args.seed,args.samples)
