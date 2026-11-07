"""Blender-side isolated sample-count benchmark; never saves over the source scene."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wrapper'))
import eyes


def run(folder, sample_counts=(8,16), corner=False):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    scene=bpy.context.scene; original=scene.cycles.samples
    digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    source=Path(bpy.data.filepath)
    bindings={'scene_sha256':digest(source),'worker_sha256':digest(__file__),'wrapper_sha256':digest(ROOT/'wrapper/eyes.py')}
    report={'blender':bpy.app.version_string,'source':str(source),'profiles':{},'completed':False,**bindings}
    try:
        for samples in sample_counts:
            if samples not in (8,16,32,64,128): raise ValueError('Unsupported sample profile')
            scene.cycles.samples=samples
            profile={'samples':samples,'poses':{}}
            poses=[('center',0,0),('up',0,1),('corner',1,1) if corner else ('down',0,-1)]
            for name,h,v in poses:
                eyes.move(h,v); start=time.monotonic()
                output=eyes.render(folder/str(samples)/(name+'.png'))
                profile['poses'][name]={'seconds':time.monotonic()-start,'record':output['record']}
                print('Benchmark:',samples,name,profile['poses'][name]['seconds'],flush=True)
            report['profiles'][str(samples)]=profile
            (folder/'benchmark.json').write_text(json.dumps(report,indent=2)+'\n')
        assert bindings=={'scene_sha256':digest(source),'worker_sha256':digest(__file__),'wrapper_sha256':digest(ROOT/'wrapper/eyes.py')},'Benchmark sources changed'
        report['completed']=True
        (folder/'benchmark.json').write_text(json.dumps(report,indent=2)+'\n')
    finally:
        scene.cycles.samples=original;eyes.reset()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True)
    p.add_argument('--samples',type=int,nargs='+',default=[8,16])
    p.add_argument('--corner',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(args.folder,args.samples,args.corner)
