"""Export a looping sweep GIF and a concise presentation outline."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw
from validate_metadata import validate_artifacts


def export(folder):
    folder=Path(folder)
    records=validate_artifacts(folder)
    frames=[]
    for k,record in enumerate(records):
        with Image.open(folder/'renders'/f'frame_{k:02d}.png') as image:
            frame=image.convert('RGB').resize((768,768))
        draw=ImageDraw.Draw(frame)
        draw.rectangle((0,0,768,36),fill='black')
        fixture=record.get('extra',{}).get('fixture',True)
        draw.text((12,10),('DEVELOPMENT FIXTURE | ' if fixture else '')+f'Apollo frame {k:02d} h={record["input"]["h"]:+.3f} v={record["input"]["v"]:+.3f}',fill='white')
        frames.append(frame)
    output=folder/'sweep.gif'
    frames[0].save(output,save_all=True,append_images=frames[1:],duration=180,loop=0)
    (folder/'PRESENTATION.md').write_text('''# Apollo presentation outline

1. Theme 01; registered team and members (fill before submission).
2. Synthetic gaze data gap and why spherical eye rotation matters.
3. Pipeline: character → calibrated scene → absolute gaze API → renders/metadata → verifier.
4. Geometry: camera 40 cm; shared target 35 cm; ±5 cm bounds; binocular fixation.
5. Ten-frame contact sheet and measured direction shifts.
6. Verification report: include measured residuals, timings, versions, and failures honestly.
7. Tools: Blender Cycles CPU, Python/NumPy, OpenCV, JSON Schema.
8. Limitations: static identity/light, fixed pupil size, non-refractive eye surface.

## 100–110 second recording storyboard

0–10 s: problem/title. 10–35 s: calibrated rig and pivots.
35–65 s: sweep/contact sheet and metadata. 65–85 s: actual verifier report.
85–105 s: demonstrate move/reset and explain limitations.

The GIF is visual source material, not the required narrated final video.
Record/export the final video and confirm its duration and accessible upload link.
''',encoding='utf-8')
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path)
    print(export(p.parse_args().folder))
