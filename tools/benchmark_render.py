"""Blender-side isolated sample-count benchmark; never saves over the source scene."""
import argparse
import json
from pathlib import Path
import sys
import time
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wrapper'))
import eyes


def run(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    scene=bpy.context.scene; original=scene.cycles.samples
    report={'blender':bpy.app.version_string,'source':bpy.data.filepath,'profiles':{}}
    try:
        for samples in [8,16]:
            scene.cycles.samples=samples
            profile={'samples':samples,'poses':{}}
            for name,h,v in [('center',0,0),('up',0,1),('down',0,-1)]:
                eyes.move(h,v); start=time.monotonic()
                output=eyes.render(folder/str(samples)/(name+'.png'))
                profile['poses'][name]={'seconds':time.monotonic()-start,'record':output['record']}
                print('Benchmark:',samples,name,profile['poses'][name]['seconds'],flush=True)
            report['profiles'][str(samples)]=profile
            (folder/'benchmark.json').write_text(json.dumps(report,indent=2)+'\n')
    finally:
        scene.cycles.samples=original;eyes.reset()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(args.folder)
