"""Geometry-guided dark-surface check, independent of both OpenCV detectors.

This is not blind detection or a substitute for the occlusion-mask suite.
"""
import numpy as np


def measure(image,expected,radius):
    image=np.asarray(image,dtype=float)
    x,y=(int(v) for v in expected)
    if not (32<=x<image.shape[1]-32 and 32<=y<image.shape[0]-32):raise ValueError('Pupil ROI outside image')
    crop=image[y-32:y+33,x-32:x+33]
    dark=crop<20
    if not dark[32,32]:raise ValueError('Expected pupil is not dark')
    queue=[(32,32)];seen={(32,32)}
    for yy,xx in queue:
        for ny,nx in [(yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)]:
            if 0<=ny<65 and 0<=nx<65 and dark[ny,nx] and (ny,nx) not in seen:
                seen.add((ny,nx));queue.append((ny,nx))
    area=len(queue);ideal=np.pi*radius*radius
    if not .8*ideal<=area<=1.2*ideal:raise ValueError('Pupil area inconsistent with geometry')
    center=np.array([np.mean([xx+x-32+.5 for yy,xx in queue]),np.mean([yy+y-32+.5 for yy,xx in queue])])
    error=float(np.linalg.norm(center-expected))
    if error>=1:raise ValueError(f'Pupil displacement error {error}')
    return {'center':center.tolist(),'error_px':error,'dark_area_px':area}
