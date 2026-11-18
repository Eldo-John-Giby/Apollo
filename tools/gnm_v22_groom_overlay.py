"""Rasterize authored strand pigment for a separate texture-only wrapping trial."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from gnm_v22_variants import sha,linear,encode,verify_selected


def main(a):
    if a.out.exists():raise FileExistsError(a.out)
    receipt=json.loads(a.projection.with_suffix('.json').read_text(encoding='utf-8'))
    selected=verify_selected(receipt['source_sha256'])
    if sha(a.projection)!=receipt['projection_sha256']:raise ValueError('Groom projection checksum mismatch')
    with np.load(a.projection,allow_pickle=False) as data:
        segments,radius,brow=data['segments'],data['radii'],data['brow']
        strand_ids=data['strand_ids']
    size=a.size
    colors=np.zeros((size,size,3),dtype=np.float32)
    alpha=np.zeros((size,size),dtype=np.float32)
    rng=np.random.default_rng(20261119)
    variations=rng.uniform(.7,1.25,int(strand_ids.max())+1)[strand_ids]
    for index,(line,width,is_brow) in enumerate(zip(segments,radius,brow)):
        points=line*np.array((size,-size))+np.array((-.5,size-.5))
        widths=np.clip(width*size,.015,2.5)
        lo=np.maximum(0,np.floor(points.min(0)-widths.max()-1).astype(int))
        hi=np.minimum(size-1,np.ceil(points.max(0)+widths.max()+1).astype(int))
        if np.any(hi<lo):continue
        yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
        pixel=np.stack((xx,yy),axis=-1)
        direction=points[1]-points[0];length2=float(direction@direction)
        if length2<1e-10:continue
        t=np.clip(((pixel-points[0])*direction).sum(-1)/length2,0,1)
        distance=np.linalg.norm(pixel-(points[0]+t[:,:,None]*direction),axis=-1)
        r=widths[0]*(1-t)+widths[1]*t
        # Analytic subpixel coverage, retaining fine tapered strand ends.
        coverage=np.minimum(np.maximum(r+.5-distance,0),np.minimum(2*r,1))*(.90 if is_brow else .75)
        pigment=linear(np.array((.16,.095,.055) if is_brow else (.21,.125,.065),dtype=np.float32))*variations[index]
        region=np.s_[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
        old=alpha[region];new=coverage+old*(1-coverage)
        colors[region]=(pigment*coverage[:,:,None]+colors[region]*old[:,:,None]*(1-coverage[:,:,None]))/np.maximum(new[:,:,None],1e-8)
        alpha[region]=new
    a.out.parent.mkdir(parents=True,exist_ok=True)
    rgba=np.dstack((encode(colors),alpha))
    encoded=np.rint(np.clip(rgba,0,1)*65535).astype(np.uint16)[:,:,[2,1,0,3]]
    if not cv2.imwrite(str(a.out),encoded):raise OSError(a.out)
    report=dict(source_sha256=receipt['source_sha256'],projection_sha256=receipt['projection_sha256'],
                overlay_sha256=sha(a.out),recipe_sha256=sha(__file__),size=size,
                covered_pixels=int((alpha>.01).sum()),
                qualification='Authored pigment only; full character materials remain separate. Review scalp/brow projection and UV seams before use.')
    a.out.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if sha(selected)!=receipt['source_sha256']:raise ValueError('Selected identity changed')
    print('RESULT '+json.dumps(report),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--projection',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--size',type=int,default=4096)
    main(p.parse_args())
