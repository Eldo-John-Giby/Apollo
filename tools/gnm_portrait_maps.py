"""Isolated portrait atlas refinement; source maps and native UVs stay intact."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree

from gnm_skin_detail import surface_positions
from gnm_surface_maps import smooth, noise


def build(template, source, out):
    out.mkdir(parents=True, exist_ok=True)
    size = 4096
    fields = surface_positions(template, size, ('upper_lip', 'lower_lip'))
    valid = np.isfinite(fields[..., 0])
    p = fields[valid, :3]
    x, y, z = p.T
    lip = smooth(fields[valid, 3:].max(axis=1))
    color = np.asarray(Image.open(source/'color.1001.png').convert('RGB'), dtype=np.float32)[valid]/255
    front = smooth((z+.005)/.015)
    # Remove misplaced photographed fibers throughout the orbital region.
    repair = (smooth((abs(x)-.009)/.005)*smooth((.068-abs(x))/.008)
              *smooth((y+.007)/.006)*smooth((.033-y)/.008)*front)
    donors = (y>.035)&(y<.055)&(abs(x)<.070)&(z>.003)
    chosen = repair>.002
    tree = cKDTree(p[donors])
    ids = tree.query(p[chosen], k=8)[1]
    replacement = color[donors][ids].mean(axis=1)
    weight = repair[chosen]*.94
    color[chosen] = color[chosen]*(1-weight[:, None])+replacement*weight[:, None]
    # Warm medium complexion; retain the scan's broad variation and fine pigment.
    color *= np.array((.87, .83, .79), dtype=np.float32)
    rough = np.asarray(Image.open(source/'roughness.1001.png'), dtype=np.float32)[valid]/255
    height = np.asarray(Image.open(source/'height.1001.png'), dtype=np.float32)[valid]/255
    for start in range(0, len(p), 150000):
        sl = slice(start, start+150000)
        xyz=p[sl]; xx, yy, zz=xyz.T
        broad=noise(xyz, 150, 621)-.5
        fine=noise(xyz, 2800, 622)-.5
        cheek=np.exp(-((abs(xx)-.040)/.022)**2-((yy+.023)/.025)**2)*front[sl]
        nose=np.exp(-(xx/.014)**2-((yy+.028)/.029)**2)*front[sl]
        forehead=np.exp(-(xx/.045)**2-((yy-.044)/.027)**2)*front[sl]
        l=lip[sl]
        color[sl]*=1+(broad*.025)[:,None]
        color[sl]*=1+(cheek*.025)[:,None]*np.array((.4,-.6,-.45))
        # Subtle vermilion warmth, anatomical membership gives a soft natural edge.
        target=np.array((.41,.215,.19))*(1+.07*fine[:,None])
        color[sl]=color[sl]*(1-.23*l[:,None])+target*(.23*l[:,None])
        rough[sl]=np.clip(.59+.05*broad+.025*fine-.10*nose-.055*forehead-.16*l,.32,.72)
        # Keep existing physical relief; no large uniform procedural bump.
        height[sl]=np.clip(height[sl]+.012*fine,0,1)
    # A restrained follicle underpainting supports real geometry fibers.
    t=(abs(x)-.014)/.044; u=np.clip(t,0,1)
    center=.0135+.004*np.sin(np.pi*u)-.002*u*u
    thickness=.0023*(1-.72*u*u)
    brow=.24*np.exp(-((y-center)/thickness)**4)*smooth(t/.12)*smooth((1-t)/.18)*front
    color=color*(1-brow[:,None])+np.array((.075,.046,.032))*brow[:,None]
    nearest=distance_transform_edt(~valid,return_distances=False,return_indices=True)
    for name,values in [('color.1001.png',color),('roughness.1001.png',rough),('height.1001.png',height)]:
        atlas=np.zeros((size,size)+values.shape[1:],dtype=np.float32)
        atlas[valid]=values; atlas=atlas[tuple(nearest)]
        Image.fromarray(np.rint(np.clip(atlas,0,1)*255).astype(np.uint8)).save(out/name)
    report={'status':'isolated portrait appearance candidate','source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in source.glob('*.png')},'template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'recipe_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'outputs':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.glob('*.png')},'license':'Existing CC-BY-3.0 scan derivative with CC0 fallback; existing attribution applies. Added detail is authored synthesis.'}
    (out/'maps.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'maps saved','out':str(out)}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['template','source','out']:
        parser.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args(); build(a.template,a.source,a.out)
