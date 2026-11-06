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
    shifts={}
    for side,p in centers.items():
        x,y=np.floor(p).astype(int)
        radius,margin=48,24
        template=reference[y-radius:y+radius,x-radius:x+radius]
        region=current[y-radius-margin:y+radius+margin,x-radius-margin:x+radius+margin]
        if template.shape != (96,96) or region.shape != (144,144):
            raise ValueError('Template crop outside image')
        scores=cv2.matchTemplate(region.astype(np.float32),template.astype(np.float32),cv2.TM_CCOEFF_NORMED)
        _,_,_,(px,py)=cv2.minMaxLoc(scores)
        delta=[]
        for axis,index in [(1,px),(0,py)]:
            if index<=0 or index>=scores.shape[axis]-1: raise ValueError('Template peak at search boundary')
            a,b,c=(scores[py,px-1:px+2] if axis==1 else scores[py-1:py+2,px])
            divisor=float(a-2*b+c)
            delta.append(0. if abs(divisor)<1e-9 else .5*float(a-c)/divisor)
        shifts[side]=np.array([px-margin+delta[0],py-margin+delta[1]])
    return shifts
