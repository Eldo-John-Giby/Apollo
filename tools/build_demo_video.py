"""Build a 105-second technical demo from actual render/evidence artifacts.

Windows SAPI narration is synthesized locally; no external voice service.
The output is a demonstration edit, not a real-time render-speed recording.
"""
import argparse
import json
from pathlib import Path
import subprocess
import wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg

CHAPTERS=[
    (10,'Apollo: calibrated synthetic gaze',
     'Apollo implements Track One: Synthetic Eye Movement and Virtual Camera Rendering. It generates binocular poses, images and gaze labels in Blender.'),
    (14,'Physical eye centers. Shared fixation.',
     'Each eye rotates in three dimensions around its own center. Both aim at one fixation target, thirty five centimeters forward. The camera stays forty centimeters away. Horizontal and vertical target motion is bounded to five centimeters.'),
    (25,'Left / Right / Up / Down / Reset',
     'These are actual rendered outputs from the same scene and wrapper. Left and right shift both pupils horizontally. Up and down shift them vertically. Reset returns to the central convergent pose. Independent geometry and image measurements verify the direction, position and visibility of both pupils.'),
    (15,'Ten poses, clockwise from the top',
     'The required sequence has ten equally spaced clockwise poses, starting at the top. Every output is a one thousand and twenty four pixel square PNG, paired with inputs, world rotations, pupil projections and camera calibration.'),
    (18,'A separate, seeded research dataset',
     'The research dataset contains two hundred and fifty six rendered poses: nine anchors and seeded random inputs. Per-image hashes and atomic checkpoints support safe resume. This is geometric and image validation for one synthetic identity, not a machine learning accuracy benchmark.'),
    (13,'Optional Blender controls, same public API',
     'The optional Blender sidebar invokes the same public wrapper for movement, reset, pose rendering and the official sweep. Evaluators can run the standalone wrapper directly, without installing the panel or the character building addon.'),
    (10,'Evidence-bound release',
     'Geometry, injected defects and reproducibility tests support the release. Simplified eyes and static lighting remain limitations. No official score is claimed.'),
]


def narration(folder):
    folder.mkdir(parents=True,exist_ok=True)
    for i,(_,_,words) in enumerate(CHAPTERS):
        wav=folder/f'voice-{i}.wav'
        script="$ErrorActionPreference='Stop'; $v=New-Object -ComObject SAPI.SpVoice; $s=New-Object -ComObject SAPI.SpFileStream; $s.Open('"+str(wav).replace("'","''")+"',3,$false); $v.AudioOutputStream=$s; $v.Rate=2; $null=$v.Speak('"+words.replace("'","''")+"'); $s.Close()"
        subprocess.run(['powershell','-NoProfile','-Command',script],check=True,capture_output=True)
        with wave.open(str(wav)) as audio:
            duration=audio.getnframes()/audio.getframerate()
        if duration>CHAPTERS[i][0]-.3:raise ValueError(f'Narration {i} too long: {duration}')


def build(upgrade,output):
    upgrade=Path(upgrade).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    q=json.loads((upgrade/'candidate/verification_report.json').read_text())
    a=json.loads((upgrade/'dataset-256/analysis.json').read_text())
    v=json.loads((upgrade/'dataset-visibility/report.json').read_text())
    assert q['passed'] and a['passed'] and a['frames']==256 and v['passed'],'Final demo requires completed passing evidence'
    narration(output)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    slides=upgrade/('presentation-final' if (upgrade/'presentation-final').is_dir() else 'presentation')
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',28)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    segments=[]
    directions=['left','right','up','down','reset']
    frames=json.loads((upgrade/'dataset-256/dataset.json').read_text())['frames']
    for i,(seconds,title,_) in enumerate(CHAPTERS):
        raw=output/f'chapter-{i}.mp4';segments.append(raw)
        command=[ffmpeg,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','pipe:0','-i',str(output/f'voice-{i}.wav'),'-af','apad','-t',str(seconds),'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(raw)]
        with (output/f'chapter-{i}.log').open('w') as log:
            proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=log)
            for n in range(seconds*24):
                stamp=n/24
                if i==0:source=slides/'slide-01.png'
                elif i==1:source=slides/'slide-04.png'
                elif i==2:source=upgrade/f'candidate/verification/{directions[min(4,int(stamp//5))]}.png'
                elif i==3:source=upgrade/f'candidate/renders/frame_{int(stamp/1.5)%10:02d}.png'
                elif i==4:source=upgrade/'dataset-256'/frames[min(255,int(stamp/18*256))]['extra']['image']
                elif i==5:source=upgrade/'ui/sidebar.jpg'
                else:source=slides/'slide-10.png'
                with Image.open(source) as image:
                    image=image.convert('RGB')
                    if i in [2,3,4]:image=image.crop((0,300,1024,720))
                    if i==5:image=image.crop((990,97,1251,436))
                    scale=min(1216/image.width,556/image.height)
                    image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
                    canvas=Image.new('RGB',(1280,720),'#F4F6F5');canvas.paste(image,((1280-image.width)//2,105+(556-image.height)//2))
                draw=ImageDraw.Draw(canvas);draw.text((32,28),title,font=font,fill='#142B3B')
                if i==2:draw.text((32,75),directions[min(4,int(stamp//5))].upper(),font=font,fill='#087F8C')
                if i==4:draw.text((32,75),f"Dataset frame {min(255,int(stamp/18*256))+1}/256 · seeded order",font=small,fill='#087F8C')
                draw.text((32,686),'APOLLO / Track 01 · Actual artifacts · Edited demonstration · Local synthesized narration',font=small,fill='#526571')
                proc.stdin.write(np.asarray(canvas,dtype=np.uint8).tobytes())
            proc.stdin.close()
            if proc.wait()!=0:raise RuntimeError(f'FFmpeg failed: {raw}')
    concat=output/'chapters.txt';concat.write_text(''.join("file '"+p.as_posix().replace("'","'\\''")+"'\n" for p in segments),encoding='utf-8')
    final=output/'apollo-demo.mp4'
    subprocess.run([ffmpeg,'-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(final)],check=True,stdout=subprocess.DEVNULL,stderr=(output/'concat.log').open('w'))
    (output/'narration.txt').write_text('\n\n'.join(f'{title}\n{words}' for _,title,words in CHAPTERS),encoding='utf-8')
    (output/'video-receipt.json').write_text(json.dumps({'duration_seconds':105,'width':1280,'height':720,'fps':24,'audio':'Local Windows SAPI synthesized narration','source':'Actual Blender renders, measured reports and observed UI screenshot','limitations':'Edited pose sequence; not a real-time rendering-speed recording'},indent=2)+'\n',encoding='utf-8')
    return final


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('upgrade',type=Path);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();print(build(args.upgrade,args.out))
