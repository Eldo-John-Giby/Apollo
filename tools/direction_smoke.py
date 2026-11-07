"""Render the real cardinal/reset gate before starting expensive qualification."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wrapper'))
import eyes


def run(folder):
    folder=Path(folder).resolve();evidence=folder/'verification';evidence.mkdir(parents=True,exist_ok=True)
    eyes.reset();eyes.render(evidence/'baseline.png');directions={}
    for name,h,v in [('left',-1,0),('right',1,0),('up',0,1),('down',0,-1),('reset',0,0)]:
        eyes.move(h,v);directions[name]=eyes.render(evidence/(name+'.png'))['record']
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    result={'config':eyes.calibration(),'directions':directions,'reset_identical':digest(evidence/'baseline.png')==digest(evidence/'reset.png'),
            'scene_sha256':digest(Path(bpy.data.filepath)),'blender':bpy.app.version_string}
    (evidence/'progress.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    eyes.reset()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(a.folder)
