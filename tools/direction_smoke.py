"""Render the real cardinal/reset gate before starting expensive qualification."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
import sys
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wrapper'))
import eyes


def run(folder,reuse_poses=None):
    folder=Path(folder).resolve();evidence=folder/'verification';evidence.mkdir(parents=True,exist_ok=True)
    digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    cached={}
    if reuse_poses:
        reuse_poses=Path(reuse_poses).resolve()
        progress=json.loads((reuse_poses/'progress.json').read_text(encoding='utf-8'))
        run=progress['run']
        assert run['scene_sha256']==digest(bpy.data.filepath),'Cached scene mismatch'
        assert run['wrapper_sha256']==digest(ROOT/'wrapper/eyes.py'),'Cached wrapper mismatch'
        assert run['worker_sha256']==digest(ROOT/'tools/realism_visibility.py'),'Cached worker mismatch'
        assert run['blender']==bpy.app.version_string and run['samples']==bpy.context.scene.cycles.samples,'Cached runtime mismatch'
        for record in progress['frames']:
            image=reuse_poses/record['extra']['image']
            assert digest(image)==record['extra']['image_sha256'],'Cached image mismatch'
            assert record['extra']['calibration']==eyes.calibration(),'Cached calibration mismatch'
            cached[(record['input']['h'],record['input']['v'])]=(image,record)
    def render(name,h,v):
        if cached:
            source,record=cached[(h,v)];shutil.copy2(source,evidence/(name+'.png'));return record
        return eyes.render(evidence/(name+'.png'))['record']
    eyes.reset();render('baseline',0,0);directions={}
    for name,h,v in [('left',-1,0),('right',1,0),('up',0,1),('down',0,-1),('reset',0,0)]:
        if name=='reset':
            eyes.move(1,1);eyes.reset()
            directions[name]=eyes.render(evidence/(name+'.png'))['record']
        else:
            eyes.move(h,v);directions[name]=render(name,h,v)
    result={'config':eyes.calibration(),'directions':directions,'reset_identical':digest(evidence/'baseline.png')==digest(evidence/'reset.png'),
            'scene_sha256':digest(Path(bpy.data.filepath)),'blender':bpy.app.version_string,
            'cardinal_rgb_source':'hash-checked matching pose renders' if cached else 'fresh renders',
            'reset_source':'fresh actual eyes.reset() render after corner pose'}
    (evidence/'progress.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    eyes.reset()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True)
    p.add_argument('--reuse-poses',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(a.folder,a.reuse_poses)
