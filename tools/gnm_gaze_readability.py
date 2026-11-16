"""Evaluate native horizontal-gaze alternatives for a small review experiment."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from gnm_gaze_trial import evaluator


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    evaluate=evaluator(args.model);poses={};details={}
    poses['center'],details['center']=evaluate(0,0)
    for gain in [1.,1.5,2.]:
        for side,sign in [('left',-1),('right',1)]:
            name=f'{side}-{gain:g}'
            poses[name],details[name]=evaluate(sign*.88*gain,0)
    np.savez_compressed(args.out/'poses.npz',**poses)
    report={'status':'unqualified_gaze_readability_experiment','native_model_sha256':hashlib.sha256(args.model.read_bytes()).hexdigest(),'poses_sha256':hashlib.sha256((args.out/'poses.npz').read_bytes()).hexdigest(),'method':'Same upstream native eye joints and shared 0.35 m fixation plane; horizontal target amplitude only; no sideways face deformation','poses':details}
    (args.out/'poses.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
