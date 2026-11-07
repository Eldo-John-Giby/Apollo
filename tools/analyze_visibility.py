"""Evaluate full-coverage interiors and integrated linear-light mask coverage."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
from reference_geometry import reference


def gray(path):return np.asarray(Image.open(path).convert('L'),dtype=float)
def linear(a):return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)


def coverage(expected,visible,final=None):
    a=linear(expected/255);b=linear(visible/255);interior=expected>=.99*255
    if a.sum()<=0 or not interior.any():raise ValueError('Empty pupil mask')
    fraction=float(b.sum()/a.sum())
    if final is not None:fraction=min(fraction,float((interior&(visible>=.99*255)&(final<60)).sum()/interior.sum()))
    return fraction


def analyze(folder,dataset_override=None):
    folder=Path(folder);e=json.loads((folder/'evidence.json').read_text());dataset=Path(dataset_override) if dataset_override is not None else Path(e['dataset']);rows=[];residuals=[]
    for frame in e['frames']:
        i=frame['frame'];expected=gray(folder/'unoccluded'/f'frame_{i:06d}.png');visible=gray(folder/'occluded'/f'frame_{i:06d}.png');image=dataset/frame['extra']['image']
        assert hashlib.sha256(image.read_bytes()).hexdigest()==frame['extra']['image_sha256'],'Dataset image changed'
        final=gray(image)
        for side,start,end in [('R',0,512),('L',512,1024)]:
            a=expected[:,start:end];r=reference(side,frame['input']['h'],frame['input']['v'],ipd=frame['extra']['calibration']['ipd'])
            weights=linear(a/255);yy,xx=np.indices(weights.shape);center=np.array([float(((xx+start+.5)*weights).sum()/weights.sum()),float(((yy+.5)*weights).sum()/weights.sum())])
            residuals.append(float(np.linalg.norm(center-r['pixel'])))
            rows.append({'frame':i,'eye':side,'visible_dark_fraction':coverage(a,visible[:,start:end],final[:,start:end])})
    expected=gray(folder/'fault_expected.png')[:,512:];visible=gray(folder/'fault_occluded.png')[:,512:];fault=coverage(expected,visible)
    minimum=min(x['visible_dark_fraction'] for x in rows)
    report={'passed':minimum>=.98 and max(residuals)<.5 and fault<.98,'poses':len(e['frames']),'minimum_visible_dark_fraction':minimum,'maximum_mask_centroid_error_px':max(residuals),'injected_half_pupil_fraction':fault,'injected_occlusion_detected':fault<.98,'measurements':rows}
    report.update(scene_sha256=e['scene_sha256'],
                  evidence_sha256=hashlib.sha256((folder/'evidence.json').read_bytes()).hexdigest(),
                  analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  mask_sha256={str(p.relative_to(folder)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob('*.png'))})
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k!='measurements'});return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--dataset',type=Path)
    a=p.parse_args();raise SystemExit(0 if analyze(a.folder,a.dataset)['passed'] else 1)
