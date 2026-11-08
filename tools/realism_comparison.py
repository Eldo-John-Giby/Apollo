"""Matched, image-hash-checked baseline/candidate sheets; never awards ratings."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(folder):
    folder=Path(folder);manifest=folder/('dataset.json' if (folder/'dataset.json').exists() else 'progress.json')
    data=json.loads(manifest.read_text(encoding='utf-8'));records={}
    for frame in data['frames']:
        key=(frame['input']['h'],frame['input']['v'])
        if key[0] not in (-1,0,1) or key[1] not in (-1,0,1):continue
        path=folder/frame['extra']['image']
        assert digest(path)==frame['extra']['image_sha256'],'Comparison image changed'
        with Image.open(path) as im:assert im.size==(1024,1024)
        records[key]=(path,frame)
    assert len(records)==9,'Comparison requires all nine anchors'
    return data,records


def create(before,after,output):
    output=Path(output)
    if output.exists():raise ValueError('Use a new comparison folder')
    b,old=load(before);a,new=load(after)
    for pose in old:
        assert old[pose][1]['extra']['calibration']==new[pose][1]['extra']['calibration'],'Unmatched calibration'
    output.mkdir(parents=True)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20) if Path('C:/Windows/Fonts/arial.ttf').exists() else ImageFont.load_default()
    poses=[(-1,1),(0,1),(1,1),(-1,0),(0,0),(1,0),(-1,-1),(0,-1),(1,-1)]
    sheet=Image.new('RGB',(1536,864),'#e9ecec');draw=ImageDraw.Draw(sheet)
    details=Image.new('RGB',(1490,9*232),'#e9ecec');detaildraw=ImageDraw.Draw(details)
    for i,pose in enumerate(poses):
        x=(i%3)*512;y=(i//3)*288
        draw.text((x+8,y+5),f'h={pose[0]:+} v={pose[1]:+}     Before | Candidate',fill='#142b3b',font=font)
        detaildraw.text((8,i*232+4),f'h={pose[0]:+} v={pose[1]:+} - Before / Candidate; native pixel crops',fill='#142b3b',font=font)
        for column,records in enumerate([old,new]):
            with Image.open(records[pose][0]) as im:
                image=im.convert('RGB');sheet.paste(image.resize((256,256)),(x+256*column,y+32))
                details.paste(image.crop((140,390,885,590)),(745*column,i*232+32))
    sheet.save(output/'pose-comparison.png');details.save(output/'eye-details.png')
    center=Image.new('RGB',(2048,1060),'#e9ecec');d=ImageDraw.Draw(center)
    for i,(label,records) in enumerate([('Baseline',old),('Realism candidate',new)]):
        d.text((1024*i+12,6),label,fill='#142b3b',font=font)
        with Image.open(records[(0,0)][0]) as im:center.paste(im.convert('RGB'),(1024*i,36))
    center.save(output/'center-comparison.png')
    report={'review_required':True,'baseline_scene_sha256':b['run']['scene_sha256'],'scene_sha256':a['run']['scene_sha256'],
            'worker_sha256':digest(__file__),
            'source_images':{str(path):digest(path) for records in [old,new] for path,_ in records.values()},
            'sheets':{p.name:digest(p) for p in output.glob('*.png')},'scope':'Matched poses/calibration; deliberate material, grooming and lighting changes. Agent review is separate.'}
    (output/'comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();create(a.before,a.after,a.out)
