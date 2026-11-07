"""Independent numerical oracle. Never import production core or wrapper math."""
import math
import numpy as np


def reference(side,h,v,ipd=.063,lens=100.,sensor=36.,resolution=1024):
    if side not in ('L','R'):raise ValueError('Unknown anatomical eye')
    if not all(math.isfinite(x) and -1<=x<=1 for x in (h,v)):raise ValueError('Invalid normalized input')
    center=np.array([ipd/2 if side=='L' else -ipd/2,0.,0.])
    target=np.array([.05*h,-.35,.05*v])
    direction=target-center;direction/=np.linalg.norm(direction)
    axis=np.cross([0.,-1.,0.],direction)
    sine=np.linalg.norm(axis);cosine=-direction[1]
    if sine<1e-15:rotation=np.eye(3)
    else:
        x,y,z=axis/sine
        skew=np.array([[0.,-z,y],[z,0.,-x],[-y,x,0.]])
        rotation=np.eye(3)+sine*skew+(1-cosine)*(skew@skew)
    pupil=center+.01*direction
    focal=lens/sensor*resolution
    pixel=np.array([resolution/2+focal*pupil[0]/(pupil[1]+.4),resolution/2-focal*pupil[2]/(pupil[1]+.4)])
    return {'center':center,'target':target,'direction':direction,'rotation':rotation,'pupil':pupil,'pixel':pixel}


def fit_sphere(points):
    points=np.asarray(points,dtype=float)
    solution,_,rank,_=np.linalg.lstsq(np.column_stack([2*points,np.ones(len(points))]),(points*points).sum(axis=1),rcond=None)
    if rank!=4:raise ValueError('Degenerate sphere geometry')
    center=solution[:3];radius=math.sqrt(solution[3]+center@center)
    return center,radius


def surface_centroid(vertices,triangles):
    triangles=np.asarray(vertices,dtype=float)[np.asarray(triangles,dtype=int)]
    areas=np.linalg.norm(np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]),axis=1)/2
    if areas.sum()<=0:raise ValueError('Empty/degenerate pupil surface')
    return np.average(triangles.mean(axis=1),axis=0,weights=areas)
