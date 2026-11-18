"""Image-only pupil checks for the fixed frontal v22 motion-camera framing."""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np


def pupils(path):
    image=cv2.imread(str(path),cv2.IMREAD_GRAYSCALE)
    if image is None:raise ValueError('Unreadable image '+str(path))
    height,width=image.shape
    result={}
    # Fixed judging-image regions, independent of scene metadata or projected
    # pupil predictions. Portrait/side-camera images are deliberately excluded.
    for side,lo,hi in [('screen-left',.20,.43),('screen-right',.57,.80)]:
        x0,x1=int(width*lo),int(width*hi)
        y0,y1=int(height*.37),int(height*.51)
        eye=image[y0:y1,x0:x1]
        threshold=min(60,max(12,float(np.percentile(eye,2))+6))
        mask=(eye<threshold).astype(np.uint8)
        radius=max(1,round(width/320))
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*radius+1,2*radius+1))
        mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
        count,labels,stats,centers=cv2.connectedComponentsWithStats(mask)
        candidates=[]
        for i in range(1,count):
            x,y,w,h,area=stats[i]
            if not (.00005*width*height<area<.002*width*height and .5<w/max(h,1)<1.9):continue
            contours,_=cv2.findContours((labels==i).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            if not contours or len(contours[0])<5:continue
            (cx,cy),axes,_=cv2.fitEllipse(contours[0])
            if min(axes)/max(axes)<.45:continue
            candidates.append((area,[cx+x0+.5,cy+y0+.5]))
        result[side]=max(candidates,key=lambda x:x[0])[1] if candidates else None
    return result


def main(a):
    neutral=pupils(a.neutral)
    if any(v is None for v in neutral.values()):raise ValueError('Neutral pupil not detected')
    reference=cv2.imread(str(a.neutral),cv2.IMREAD_GRAYSCALE)
    patch_size=2*round(reference.shape[1]/32)+1
    report=dict(recipe_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                images={},neutral=neutral,checks={},minimum_reference_correlation=.8,
                qualification='Image checks for fixed motion framing only; human direction review is separate.')
    inputs={'neutral':a.neutral,'left':a.left,'right':a.right,'closed':a.closed,'reopened':a.reopened}
    errors=[]
    for role,path in inputs.items():
        if path is None:continue
        report['images'][role]=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        candidates=pupils(path);found=dict(candidates);scores={}
        current=cv2.imread(str(path),cv2.IMREAD_GRAYSCALE)
        if current.shape!=reference.shape:raise ValueError('Image comparison dimensions differ')
        for side,point in candidates.items():
            if point is None:continue
            target=cv2.getRectSubPix(current,(patch_size,patch_size),tuple(v-.5 for v in point))
            baseline=cv2.getRectSubPix(reference,(patch_size,patch_size),tuple(v-.5 for v in neutral[side]))
            score=float(cv2.matchTemplate(target,baseline,cv2.TM_CCOEFF_NORMED)[0,0])
            scores[side]=score
            # A dark eyelash clump can be round after erosion. Require the
            # surrounding pupil/iris pattern to agree with the neutral image.
            if not np.isfinite(score) or score<.8:found[side]=None
        report['checks'][role]=dict(pupils=found,dark_candidates=candidates,reference_correlation=scores)
        for side,point in found.items():
            if role=='closed':
                if point is not None:errors.append(f'{side}: round dark pupil candidate remains at closure')
            elif point is None:
                errors.append(f'{side}: pupil not detected in {role}')
            elif role in ('left','right'):
                displacement=point[0]-neutral[side][0]
                report['checks'][role].setdefault('horizontal_shift_px',{})[side]=displacement
                if displacement*(-1 if role=='left' else 1)<1:
                    errors.append(f'{side}: {role} displacement is wrong or below one pixel')
    report['errors']=errors;report['passed']=not errors
    a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(report),flush=True)
    if errors:raise ValueError('; '.join(errors))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--neutral',type=Path,required=True)
    for role in ('left','right','closed','reopened'):p.add_argument('--'+role,type=Path)
    p.add_argument('--out',type=Path,required=True)
    main(p.parse_args())
