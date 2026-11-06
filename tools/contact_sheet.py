"""Build an annotated development or production contact sheet."""
from pathlib import Path
import argparse
import math
from PIL import Image, ImageDraw
from validate_metadata import validate_artifacts
from apollo_core.core import Config, eye_state


def create(folder):
    folder = Path(folder)
    records = validate_artifacts(folder)
    cfg = Config(**records[0].get('extra',{}).get('calibration',{}))
    reset,_ = eye_state(0,0,cfg)
    sheet = Image.new('RGB',(2560,1160),'#151b24')
    draw = ImageDraw.Draw(sheet)
    for k,r in enumerate(records):
        x,y = (k%5)*512,(k//5)*560
        with Image.open(folder/'renders'/f'frame_{k:02d}.png') as source:
            sheet.paste(source.convert('RGB').resize((512,512)),(x,y))
        for side in 'LR':
            rx,ry = reset[side]['pupil2d']
            rx,ry = x+rx/2,y+ry/2
            draw.ellipse((rx-7,ry-7,rx+7,ry+7),outline='#aaaaaa')
            px,py = r['pupil_center_2D_'+side]
            px,py = x+px/2,y+py/2
            draw.line((px-5,py,px+5,py),fill='cyan')
            draw.line((px,py-5,px,py+5),fill='cyan')
        draw.text((x+10,y+518),f"{k:02d} theta={math.degrees(r['theta']):.0f} h={r['input']['h']:+.3f} v={r['input']['v']:+.3f}",fill='white')
        cx,cy=x+483,y+535
        draw.ellipse((cx-14,cy-14,cx+14,cy+14),outline='white')
        draw.line((cx,cy,cx+12*r['input']['h'],cy-12*r['input']['v']),fill='cyan',width=2)
    fixture = any(r.get('extra',{}).get('fixture',False) for r in records)
    draw.text((12,1130),('DEVELOPMENT FIXTURE | ' if fixture else '')+'Anatomical L = image right; +h image right; +v up; pixels top-left.',fill='white')
    path = folder/'contact_sheet.png'
    sheet.save(path)
    return path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder',type=Path)
    print(create(parser.parse_args().folder))
