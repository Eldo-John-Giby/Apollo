"""Build an isolated, review-driven naturalness trial from the rc.5 maps."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import map_coordinates, distance_transform_edt
from scipy.spatial import cKDTree

from gnm_skin_detail import surface_positions
from gnm_surface_maps import smooth, noise


def scalp_density(p):
    x, y, z = p.T
    front = smooth((z + .10) / .07)
    side = smooth((abs(x) - .047) / .035)
    line = -.025 + front * (.095 - .055 * side)
    return smooth((y - line) / .007)


def short_brows():
    bounds = (-.075, .075, .002, .045)
    image = Image.new('L', (4096, 1174))
    d = ImageDraw.Draw(image)
    rng = np.random.default_rng(20261116)
    def pixel(x, y):
        return ((x-bounds[0])/.15*4095, (bounds[3]-y)/.043*1173)
    for side in (-1, 1):
        for _ in range(620):
            t = rng.beta(1.3, 1.5)
            x = side * (.014 + .044*t)
            center = .017 + .0045*np.sin(np.pi*t) - .0035*t*t
            y = center + rng.normal(0, .00075) * (1-.72*t)
            length = rng.uniform(.00065, .0019)*(1-.35*t)
            dx, dy = side*length*(.20+.70*t), length*(.85-1.05*t)
            opacity = int(rng.uniform(60, 180))
            d.line([pixel(x,y),pixel(x+.55*dx,y+.6*dy)],fill=opacity,width=2)
            d.line([pixel(x+.55*dx,y+.6*dy),pixel(x+dx,y+dy)],fill=int(opacity*.6),width=1)
    return np.asarray(image.filter(ImageFilter.GaussianBlur(.35)),dtype=np.float32)/255,bounds


def build(template, source, eye_source, out, size=4096):
    out.mkdir(parents=True, exist_ok=False)
    fields = surface_positions(template, size)
    valid = np.isfinite(fields[...,0]);p=fields[valid];x,y,z=p.T
    color=np.asarray(Image.open(source/'color.1001.png').convert('RGB'),dtype=np.float32)[valid]/255
    front=smooth((z+.008)/.015)
    remove=(smooth((abs(x)-.007)/.006)*smooth((.078-abs(x))/.009)
            *smooth((y-.005)/.005)*smooth((.044-y)/.008)*front)
    donors=(abs(x)<.085)&(y>.045)&(y<.065)&(z>-.005)
    selected=remove>.001
    if not donors.any():raise ValueError('No clean forehead donor skin')
    tree=cKDTree(p[donors]);indices=tree.query(p[selected],k=8)[1]
    replacement=color[donors][indices].mean(axis=1)
    darkness=smooth((replacement.mean(axis=1)-color[selected].mean(axis=1)-.008)/.11)
    weight=remove[selected]*darkness
    color[selected]=color[selected]*(1-weight[:,None])+replacement*weight[:,None]
    brow,bounds=short_brows()
    opacity=map_coordinates(brow,((bounds[3]-y)/.043*(brow.shape[0]-1),(x-bounds[0])/.15*(brow.shape[1]-1)),order=1,mode='constant',cval=0)*front
    color=color*(1-opacity[:,None])+np.array((.17,.115,.085))*opacity[:,None]
    color*=np.array((.82,.79,.75))
    density=scalp_density(p)
    # Portable scalp root pigment accompanies the separate silhouette strands.
    for start in range(0,len(p),160000):
        sl=slice(start,start+160000);detail=noise(p[sl],4500,1611)
        root=np.array((.055,.032,.020))*(.75+.5*detail[:,None])
        a=density[sl]*.94;color[sl]=color[sl]*(1-a[:,None])+root*a[:,None]
    atlas=np.zeros((size,size,3),dtype=np.float32);atlas[valid]=color
    nearest=distance_transform_edt(~valid,return_distances=False,return_indices=True)
    atlas=atlas[tuple(nearest)]
    Image.fromarray(np.rint(np.clip(atlas,0,1)*255).astype(np.uint8)).save(out/'color.1001.png')
    rough=np.asarray(Image.open(source/'roughness.1001.png'),dtype=np.float32)/255
    Image.fromarray(np.rint(np.clip(rough+.065,.38,.78)*255).astype(np.uint8)).save(out/'roughness.1001.png')
    shutil.copy2(source/'height.1001.png',out/'height.1001.png')
    # Bilinear licensed stock detail replaces the high-contrast periodic weave.
    stock=np.asarray(Image.open(eye_source).convert('RGB'),dtype=np.float32)/255
    yy,xx=np.mgrid[:1024,:1024].astype(np.float32);dx=(xx+.5)/1024-.5;dy=(yy+.5)/1024-.5
    radius=np.hypot(dx,dy);r=np.clip((radius-.04985)/(.184924-.04985),0,1)
    atlas_r=np.interp(radius,[0,.04985,.184924],[0,.037,.112])
    scale=atlas_r/np.maximum(radius,1e-8)
    for tile,center in [(1002,(.708,.292)),(1004,(.292,.708))]:
        sampled=np.stack([map_coordinates(stock[...,c],((center[1]+dy*scale)*1023,(center[0]+dx*scale)*1023),order=1,mode='nearest') for c in range(3)],-1)
        lum=sampled@np.array((.3,.59,.11));annulus=(r>.1)&(r<.85)&(radius<.1849)
        detail=np.clip(lum/np.median(lum[annulus]),.45,1.5)
        center_weight=np.exp(-((r-.18)/.22)**2)
        base=np.array((.27,.315,.33))*(1-center_weight[...,None])+np.array((.34,.295,.20))*center_weight[...,None]
        iris=base*(.83+.34*(detail-1))[...,None]
        iris*= (1-.22*smooth((r-.9)/.1))[...,None]
        original=np.asarray(Image.open(source/f'color.{tile}.png').convert('RGB'),dtype=np.float32)/255*.90
        boundary=smooth((radius-.1825)/.0045)
        result=iris*(1-boundary[...,None])+original*boundary[...,None]
        pupil=smooth((radius-.0486)/.0015)
        result=result*pupil[...,None]+np.array((.005,.004,.003))*(1-pupil[...,None])
        Image.fromarray(np.rint(np.clip(result,0,1)*255).astype(np.uint8)).save(out/f'color.{tile}.png')
    report={'status':'unqualified_appearance_trial','feedback_case':'A01','source':'rc.5 cool-grey maps','template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'recipe_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_maps':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in source.glob('*.png') if f.name.startswith(('color.','roughness.','height.'))},'stock_eye_source_sha256':hashlib.sha256(eye_source.read_bytes()).hexdigest(),'eye_source_license':'Existing MakeHuman CC0 stock atlas; no new photographic resolution claimed','skin_license':'Existing CC-BY-3.0 scan derivative with CC0 fallback; original attribution remains applicable','skin_gain':[.82,.79,.75],'head_topology_and_uvs':'unchanged','changes':['remove long scanned brow fibers; author shorter directional brows','reduce pale gain and glossy skin response','replace periodic iris weave with restrained bilinear stock detail','portable scalp root pigment; separate optional rendered hair strands'],'maps':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.glob('*.png')}}
    (out/'trial.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['template','source','eye-source','out']:parser.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args();build(a.template,a.source,a.eye_source,a.out)
