"""Fail early on actual candidate images, using unchanged grader thresholds."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from grader_sim import gray,detect,template_shift
from reference_geometry import reference


def run(folder,baseline,progress=False):
    folder=Path(folder);baseline=Path(baseline)
    data=json.loads((folder/('progress.json' if progress else 'metadata.json')).read_text(encoding='utf-8'))
    records=data['frames'] if isinstance(data,dict) else data
    source=gray(baseline);errors=[];shifts=[];failures=[]
    for record in records:
        name=record['extra']['image'];path=folder/name if name.startswith('renders/') else folder/'renders'/name
        image=gray(path)
        try:
            centers=detect(image);delta=template_shift(source,image)
            cfg=record['extra']['calibration']
            for side in 'LR':
                expected=reference(side,record['input']['h'],record['input']['v'],ipd=cfg['ipd'])['pixel']
                center=reference(side,0,0,ipd=cfg['ipd'])['pixel']
                errors.append(float(np.linalg.norm(centers[side]-expected)))
                shifts.append(float(np.linalg.norm(delta[side]-(expected-center))))
        except ValueError as exc:failures.append({'frame':record['frame'],'error':str(exc)})
    passed=bool(records) and not failures and max(errors,default=999)<1 and max(shifts,default=999)<1.5
    report={'passed':passed,'frames':len(records),'max_blind_error_px':max(errors,default=None),'max_template_error_px':max(shifts,default=None),'failures':failures,
            'baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'grader_sha256':hashlib.sha256(Path(__file__).with_name('grader_sim.py').read_bytes()).hexdigest()}
    if (folder/'scene.blend').is_file():report['scene_sha256']=hashlib.sha256((folder/'scene.blend').read_bytes()).hexdigest()
    else:report['scene_sha256']=data['run']['scene_sha256']
    temporary=folder/'early-image-report.json.tmp'
    temporary.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    temporary.replace(folder/'early-image-report.json')
    print(report);return passed


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--progress',action='store_true')
    a=p.parse_args();raise SystemExit(0 if run(a.folder,a.baseline,a.progress) else 1)
