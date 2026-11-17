"""Design a paired branching vessel mask for the visible scleral wedges."""
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

folder=Path(sys.argv[1])
folder.mkdir(parents=True,exist_ok=True)
size=(1536,512)
rng=np.random.default_rng(624)
mask=Image.new('L',size)
draw=ImageDraw.Draw(mask)


def pixel(x,y):
    return ((x+.055)/.110*size[0],(1-(y-.284)/.037)*size[1])


for sign in (-1,1):
    for medial in (False,True):
        for j in range(10):
            start_x=rng.uniform(.0144,.0197) if medial else rng.uniform(.044,.050)
            end_x=rng.uniform(.0217,.0271) if medial else rng.uniform(.0357,.0414)
            y0=rng.uniform(.2932,.3081)
            y1=rng.uniform(.2973,.3052)
            phase=rng.uniform(0,6.28)
            ts=np.linspace(0,1,55)
            xs=start_x+(end_x-start_x)*ts
            ys=y0+(y1-y0)*ts+.00038*np.sin(ts*7+phase)*np.sin(np.pi*ts)
            opacity=rng.uniform(60,138)
            for i in range(len(ts)-1):
                draw.line((pixel(sign*xs[i],ys[i]),pixel(sign*xs[i+1],ys[i+1])),
                          fill=int(opacity*(1-.64*ts[i])),width=3 if i<25 else 2)
            i=int(rng.integers(16,35))
            bend=rng.choice([-1,1])*rng.uniform(.001,.0024)
            branch=[pixel(sign*(xs[i]+(end_x-xs[i])*.72*t),ys[i]+bend*t+.00020*np.sin(t*6))
                    for t in np.linspace(0,1,16)]
            draw.line(branch,fill=int(opacity*.48),width=2)
mask.filter(ImageFilter.GaussianBlur(.70)).save(folder/'sclera-vessels.png')
