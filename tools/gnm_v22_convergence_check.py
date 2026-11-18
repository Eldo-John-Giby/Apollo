"""Compare authenticated render samples in native eye, lip, skin and hair crops."""
import argparse
import json
from pathlib import Path
import hashlib

import cv2
import numpy as np
from PIL import Image,ImageDraw

REGIONS={'eyes':(.20,.34,.80,.52),'lips':(.39,.79,.64,.91),
         'skin':(.18,.52,.37,.70),'hair':(.15,0,.85,.22)}
LIMITS=dict(mean_absolute_rgb=1.,p95_absolute_rgb=3.,detail_ratio_min=.90,detail_ratio_max=1.10)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def detail(image):
    gray=cv2.cvtColor(image.astype(np.float32),cv2.COLOR_RGB2GRAY)
    return float(np.std(gray-cv2.GaussianBlur(gray,(0,0),1.)))


def main(a):
    receipt=json.loads((a.source/'convergence.json').read_text(encoding='utf-8'))
    if not receipt['complete']:raise ValueError('Convergence rendering is incomplete')
    if a.out.exists():raise FileExistsError(a.out)
    a.out.mkdir(parents=True)
    images={};receipts={}
    policy={k:v for k,v in receipt.items() if k not in ('profiles','complete')}
    for folder in [a.source]+a.additional_source:
        checked=json.loads((folder/'convergence.json').read_text(encoding='utf-8'))
        if not checked['complete'] or {k:v for k,v in checked.items() if k not in ('profiles','complete')}!=policy:
            raise ValueError('Sample comparisons must use identical source, worker, camera and render policy')
        receipts[str(folder)]=sha(folder/'convergence.json')
        for samples,profile in checked['profiles'].items():
            path=folder/profile['file']
            if path.name!=profile['file'] or sha(path)!=profile['sha256']:raise ValueError('Stale convergence image')
            image=np.asarray(Image.open(path).convert('RGB'))
            if image.shape[:2]!=(receipt['size'],receipt['size']):raise ValueError('Render dimensions differ')
            if int(samples) in images and not np.array_equal(images[int(samples)],image):
                raise ValueError('Conflicting copies of a sample profile')
            images[int(samples)]=image
    reference=max(images);candidates=sorted(n for n in images if n!=reference)
    if not candidates:raise ValueError('Need at least two sample profiles')
    size=receipt['size'];results={}
    for samples in candidates:
        rows={};board=Image.new('RGB',(1536,4*256),'#20262b');draw=ImageDraw.Draw(board)
        for row,(name,bounds) in enumerate(REGIONS.items()):
            x0,y0,x1,y1=[round(v*size) for v in bounds]
            low=images[samples][y0:y1,x0:x1];high=images[reference][y0:y1,x0:x1]
            delta=np.abs(low.astype(float)-high.astype(float))
            energy=detail(high);ratio=detail(low)/energy if energy>1e-8 else 1.
            metrics=dict(mean_absolute_rgb=float(delta.mean()),p95_absolute_rgb=float(np.percentile(delta,95)),
                         detail_ratio=ratio,native_crop=[x0,y0,x1,y1])
            metrics['numerically_stable']=(metrics['mean_absolute_rgb']<=LIMITS['mean_absolute_rgb'] and
                metrics['p95_absolute_rgb']<=LIMITS['p95_absolute_rgb'] and
                LIMITS['detail_ratio_min']<=ratio<=LIMITS['detail_ratio_max'])
            rows[name]=metrics
            for col,(crop,label) in enumerate(((low,f'{samples} samples'),(high,f'{reference} samples'),
                    (np.clip(delta*8,0,255).astype(np.uint8),'absolute RGB difference x8'))):
                tile=Image.fromarray(crop)
                tile.thumbnail((496,216),Image.Resampling.LANCZOS)
                board.paste(tile,(col*512+(512-tile.width)//2,row*256+32))
                draw.text((col*512+12,row*256+10),f'{name}: {label}',fill='white')
        output=a.out/f'{samples}-vs-{reference}.png';board.save(output)
        results[str(samples)]=dict(regions=rows,numerically_stable=all(m['numerically_stable'] for m in rows.values()),
                                  sheet=output.name,sheet_sha256=sha(output))
    passing=[int(n) for n,r in results.items() if r['numerically_stable']]
    report=dict(source_receipts=receipts,recipe_sha256=sha(__file__),
                reference_samples=reference,limits=LIMITS,comparisons=results,
                lowest_numerically_stable_samples=min(passing) if passing else None,
                qualification='Internal convergence evidence only; sheets still require visual inspection and other motion frames need separate checks.')
    (a.out/'analysis.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(report),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--additional-source',type=Path,action='append',default=[])
    main(p.parse_args())
