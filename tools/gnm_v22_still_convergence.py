"""Compare native-pixel judging-still detail under matching authenticated receipts."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from gnm_v22_convergence_check import LIMITS, detail, sha

REGIONS = {'eyes':(.29,.38,.72,.49), 'skin':(.33,.47,.43,.59),
           'lips':(.42,.60,.59,.69), 'ear':(.24,.43,.32,.59)}


def authenticated_image(path, kind):
    path=Path(path)
    receipt=path.with_suffix('.render.json') if kind=='full' else path.parent/'comparison.json'
    record=json.loads(receipt.read_text(encoding='utf-8'))
    if kind=='full':
        expected=record['output_sha256'];dimensions=record['resolution']
        policy={k:v for k,v in record.items() if k not in ('samples','output_sha256')}
        required=('scene_sha256','maps','recipe_sha256','blender_build','camera_matrix','angle','side_light')
        if record.get('angle') is not False or record.get('side_light') is not False:
            raise ValueError('Fixed front-still crops require a neutral front view')
    elif kind=='native':
        if set(record['images'])!={path.name}:raise ValueError('Need one fresh-only native still')
        expected=record['images'][path.name];dimensions=[record['size']]*2
        policy={k:v for k,v in record.items() if k not in ('samples','images')}
        required=('source_sha256','target_sha256','template_sha256','maps_manifest_sha256',
                  'recipe_sha256','blender_build','camera_matrix','judging_policy','angle','oblique','fresh_only')
        if record.get('fresh_only') is not True:raise ValueError('Need a fresh native target')
        if record.get('angle') is not False or record.get('oblique') is not False:
            raise ValueError('Fixed front-still crops require a neutral front view')
    else:raise ValueError('Unknown still kind')
    if any(key not in record for key in required):raise ValueError('Incomplete render receipt')
    if sha(path)!=expected:raise ValueError('Still differs from its receipt')
    if dimensions!=[1024,1024]:raise ValueError('Expected native 1024px judging image')
    samples=record['samples']
    if type(samples) is not int or samples<=0:raise ValueError('Invalid sample count')
    image=np.asarray(Image.open(path).convert('RGB'))
    if image.shape!=(1024,1024,3):raise ValueError('Image dimensions differ from receipt')
    return image,policy,samples,sha(receipt)


def compare(low_path,high_path,kind,out):
    low,lp,ls,lr=authenticated_image(low_path,kind)
    high,hp,hs,hr=authenticated_image(high_path,kind)
    if lp!=hp:raise ValueError('Source, maps, worker, camera or render policy differ')
    if hs<=ls:raise ValueError('Reference must have more samples than candidate')
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    regions=dict(REGIONS)
    if kind=='full':regions['hair']=(.30,.10,.70,.27)
    board=Image.new('RGB',(1536,len(regions)*256),'#20262b');draw=ImageDraw.Draw(board)
    metrics={}
    for row,(name,bounds) in enumerate(regions.items()):
        x0,y0,x1,y1=[round(v*1024) for v in bounds]
        a=low[y0:y1,x0:x1];b=high[y0:y1,x0:x1]
        delta=np.abs(a.astype(float)-b.astype(float))
        energy=detail(b);candidate_energy=detail(a)
        ratio=candidate_energy/energy if energy>1e-8 else (1. if candidate_energy<=1e-8 else None)
        mean=float(delta.mean());p95=float(np.percentile(delta,95))
        stable=(mean<=LIMITS['mean_absolute_rgb'] and p95<=LIMITS['p95_absolute_rgb']
                and ratio is not None and LIMITS['detail_ratio_min']<=ratio<=LIMITS['detail_ratio_max'])
        metrics[name]=dict(mean_absolute_rgb=mean,p95_absolute_rgb=p95,detail_ratio=ratio,
                           native_crop=[x0,y0,x1,y1],numerically_stable=stable)
        for col,(crop,label) in enumerate(((a,f'{ls} samples'),(b,f'{hs} samples'),
                (np.clip(delta*8,0,255).astype(np.uint8),'absolute RGB difference x8'))):
            tile=Image.fromarray(crop);tile.thumbnail((496,216),Image.Resampling.LANCZOS)
            board.paste(tile,(col*512+(512-tile.width)//2,row*256+32))
            draw.text((col*512+12,row*256+10),f'{name}: {label}',fill='white')
    sheet=out/'comparison.png';board.save(sheet)
    report=dict(status='completed_still_convergence_measurement',kind=kind,
        candidate_samples=ls,reference_samples=hs,source_receipts=dict(candidate=lr,reference=hr),
        input_images=dict(candidate=sha(low_path),reference=sha(high_path)),
        limits=LIMITS,regions=metrics,numerically_stable=all(v['numerically_stable'] for v in metrics.values()),
        source_policy=lp,sheet_sha256=sha(sheet),recipe_sha256=sha(__file__),
        metric_recipe_sha256=sha(Path(__file__).with_name('gnm_v22_convergence_check.py')),
        qualification='Front judging-still convergence only, display RGB at native pixel scale. Visual inspection, other views/motion, independent acceptance and final frozen rebuild remain separate.')
    (out/'analysis.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--low',type=Path,required=True);parser.add_argument('--high',type=Path,required=True)
    parser.add_argument('--kind',choices=('full','native'),required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(compare(args.low,args.high,args.kind,args.out)),flush=True)
