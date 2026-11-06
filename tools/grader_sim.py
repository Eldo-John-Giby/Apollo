"""Image-only pupil detectors; never consume metadata predictions."""
import cv2
import numpy as np
from PIL import Image


def gray(path):
    return np.asarray(Image.open(path).convert('L'),dtype=np.float32)


def detect(image):
    image = np.asarray(image,dtype=np.float32)
    height,width = image.shape
    band = image[int(height*.3):int(height*.7)]
    threshold = min(60.,max(8.,float(np.percentile(band,1))+8.))
    mask = (band < threshold).astype(np.uint8)
    count,labels,stats,_ = cv2.connectedComponentsWithStats(mask)
    candidates=[]
    for i in range(1,count):
        x,y,w,h,area = stats[i]
        if not (40 < area < 3500 and .45 < w/max(h,1) < 2.2): continue
        contour,_ = cv2.findContours((labels==i).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        if not contour or len(contour[0])<5: continue
        (cx,cy),axes,_ = cv2.fitEllipse(contour[0])
        candidates.append((abs(area-650),np.array([cx+.5,cy+int(height*.3)+.5])))
    result={}
    for side,condition in [('L',lambda x:x>=width/2),('R',lambda x:x<width/2)]:
        points=[(score,p) for score,p in candidates if condition(p[0])]
        if not points: raise ValueError(f'Blind detector found no pupil for {side}')
        result[side]=min(points,key=lambda item:item[0])[1]
    return result


def centroid(image):
    image=np.asarray(image,dtype=float)
    height,width=image.shape
    result={}
    for side,start,end in [('R',0,width//2),('L',width//2,width)]:
        weights=image[:,start:end]
        total=weights.sum()
        if total<=0: raise ValueError('Empty pupil mask')
        yy,xx=np.indices(weights.shape)
        result[side]=np.array([float(((xx+start+.5)*weights).sum()/total),float(((yy+.5)*weights).sum()/total)])
    return result


def template_shift(reference,current):
    centers=detect(reference)
    # Track the pupil and a small iris border. A whole-eye template can lock
    # onto stationary lids/lashes while the pupil moves underneath them.
    _,labels,stats,_=cv2.connectedComponentsWithStats((reference<60).astype(np.uint8))
    shifts={}
    for side,p in centers.items():
        x,y=np.floor(p).astype(int)
        label=labels[y,x]
        if label==0: raise ValueError('Reference pupil center is not dark')
        _,_,w,h,_=stats[label]
        radius,margin=int(np.ceil(max(w,h)/2))+2,24
        if radius>32: raise ValueError('Reference pupil is connected to a large dark region')
        template=reference[y-radius:y+radius,x-radius:x+radius]
        region=current[y-radius-margin:y+radius+margin,x-radius-margin:x+radius+margin]
        if template.shape != (2*radius,2*radius) or region.shape != (2*(radius+margin),2*(radius+margin)):
            raise ValueError('Template crop outside image')
        yy,xx=np.indices(template.shape)
        pupil_mask=(((xx+.5-radius-(p[0]-x))**2+
                     (yy+.5-radius-(p[1]-y))**2)<(radius-1)**2).astype(np.float32)
        scores=cv2.matchTemplate(region.astype(np.float32),template.astype(np.float32),
                                cv2.TM_CCOEFF_NORMED,mask=pupil_mask)
        scores[~np.isfinite(scores)]=-1.
        _,_,_,(px,py)=cv2.minMaxLoc(scores)
        delta=[]
        for axis,index in [(1,px),(0,py)]:
            if index<=0 or index>=scores.shape[axis]-1: raise ValueError('Template peak at search boundary')
            a,b,c=(scores[py,px-1:px+2] if axis==1 else scores[py-1:py+2,px])
            divisor=float(a-2*b+c)
            delta.append(0. if abs(divisor)<1e-9 else .5*float(a-c)/divisor)
        shifts[side]=np.array([px-margin+delta[0],py-margin+delta[1]])
    return shifts
