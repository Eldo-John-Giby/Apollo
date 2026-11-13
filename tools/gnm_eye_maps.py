"""Remap the CC0 stock eye atlas to native GNM interior tiles."""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--variant', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
root = args.out
root.mkdir(parents=True, exist_ok=True)
y,x=np.mgrid[:1024,:1024]
dx=(x+.5)/1024-.5
dy=(y+.5)/1024-.5
r=np.hypot(dx,dy)
for side,tile in [('left',1002),('right',1004)]:
 p = args.variant / f'iris_{side}.png'
 image=Image.open(p).convert('RGB')
 # Fit native concentric pupil and iris boundaries to the licensed atlas.
 atlas_r=np.interp(r,[0,.04985,.184924,.46,.72],[0,.037,.112,.265,.38])
 scale=atlas_r/np.maximum(r,1e-10)
 u=np.clip(np.rint((.708+dx*scale)*image.width),0,image.width-1).astype(int)
 v=np.clip(np.rint((.292+dy*scale)*image.height),0,image.height-1).astype(int)
 Image.fromarray(np.asarray(image)[v,u]).save(root/f'color.{tile}.png')
