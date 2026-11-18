"""Evaluate pinned native GNM motion at integer and intermediate transition samples."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from apollo_core.submission_timing import expression
from gnm_gaze_trial import evaluator
from gnm_template import MODEL_SHA256


def build(model,out,mode,substeps):
    if out.exists():
        raise FileExistsError(out)
    pose = evaluator(model)
    frames = np.arange(191*substeps+1,dtype=np.float64)/substeps+1
    poses,lookup,samples = [],{},[]
    for frame in frames:
        h,v,blink = expression(mode,frame)
        delayed = expression(mode,max(1,frame-1))[2] if mode=='generate-motion' else blink
        key = (h,v,blink,delayed)
        if key not in lookup:
            lookup[key] = len(poses)
            poses.append(pose(*key)[0])
        samples.append(lookup[key])
    samples = np.array(samples,dtype=np.int32)
    out.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out,poses=np.asarray(poses),sequence=samples[::substeps],
                        sample_frames=frames,sample_sequence=samples,mode=mode)
    # Check between packed samples directly against the upstream evaluator.
    worst = 0.
    for i in range(len(frames)-1):
        if samples[i]==samples[i+1]:
            continue
        frame = (frames[i]+frames[i+1])/2
        h,v,blink=expression(mode,frame)
        delayed=expression(mode,max(1,frame-1))[2] if mode=='generate-motion' else blink
        oracle=pose(h,v,blink,delayed)[0]
        interpolated=(poses[samples[i]]+poses[samples[i+1]])*.5
        worst=max(worst,float(np.max(np.abs(oracle-interpolated))))
    receipt=dict(model_sha256=MODEL_SHA256,clip_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
                 mode=mode,substeps=substeps,unique_poses=len(poses),samples=len(frames),
                 midpoint_native_interpolation_error_m=worst,
                 qualification='Native evaluation only; derived appearance and rendered motion require separate gates.')
    out.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(receipt),flush=True)
    if worst>1e-6:
        raise ValueError('Increase substeps: native midpoint error exceeds unchanged 1 micrometre tolerance')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--mode',choices=('left','right','generate-motion'),required=True)
    parser.add_argument('--substeps',type=int,choices=(2,4,8,16,32,64),default=32)
    a=parser.parse_args()
    build(a.model,a.out,a.mode,a.substeps)
