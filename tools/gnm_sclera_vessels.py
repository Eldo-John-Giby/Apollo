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
portrait='--portrait-scale' in sys.argv
strong='--readable' in sys.argv or portrait


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
            primary=strong and j%3==0
            if strong:
                opacity*=1.72 if primary else 1.19
            for i in range(len(ts)-1):
                draw.line((pixel(sign*xs[i],ys[i]),pixel(sign*xs[i+1],ys[i+1])),
                          fill=int(opacity*(1-.64*ts[i])),
                          width=(6 if i<28 else 4) if primary else (3 if i<25 else 2))
            i=int(rng.integers(16,35))
            bend=rng.choice([-1,1])*rng.uniform(.001,.0024)
            branch=[pixel(sign*(xs[i]+(end_x-xs[i])*.72*t),ys[i]+bend*t+.00020*np.sin(t*6))
                    for t in np.linspace(0,1,16)]
            draw.line(branch,fill=int(opacity*.55),width=3 if primary else 2)

if portrait:
    for sign in (-1,1):
        offset=.00045*sign
        # Place the strongest tapered branches in the exposed wedges.
        for points,width,color in (
            ([(.047,.2994),(.044,.2996),(.042,.3007),(.0405,.3011),(.038,.3008)],9,226),
            ([(.042,.3007),(.0411,.3020),(.0395,.3031),(.0386,.3033)],6,187),
            ([(.046,.3047),(.0437,.3044),(.0417,.3053),(.0395,.3054)],7,198),
            ([(.016,.3000),(.019,.3002),(.0206,.3013),(.0238,.3016),(.0254,.3023)],8,215),
            ([(.0206,.3013),(.0220,.2998),(.0245,.2993)],5,171),
        ):
            locations=[pixel(sign*x,y+offset) for x,y in points]
            for i,(a,b) in enumerate(zip(locations,locations[1:])):
                fade=1-i/len(points)*.6
                draw.line((a,b),fill=int(color*fade),width=max(2,round(width*fade)))
mask.filter(ImageFilter.GaussianBlur(.70)).save(folder/'sclera-vessels.png')
