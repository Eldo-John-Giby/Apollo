"""Portable end-to-end Apollo task runner."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser()
    p.add_argument('task',choices=['test','doctor','sync','inspect','scene','production-scene','sweep','framing','verify','validate','sheet','prepare','demo','bundle','all','docker','dataset'])
    p.add_argument('--folder',type=Path)
    p.add_argument('--source',type=Path,default=ROOT/'assets/base_character.blend')
    p.add_argument('--mapping',type=Path)
    p.add_argument('--team')
    p.add_argument('--quality',choices=['draft','final'])
    p.add_argument('--production',action='store_true')
    p.add_argument('--look',choices=['flat','radial'],default='radial')
    p.add_argument('--scene',type=Path,default=ROOT/'out/production/scene.blend')
    p.add_argument('--count',type=int,default=256)
    p.add_argument('--seed',type=int,default=0)
    p.add_argument('--samples',type=int,choices=[8,32,64,128],default=32)
    args=p.parse_args()
    args.folder=(args.folder or ROOT/('out/dataset' if args.task=='dataset' else 'out/production' if args.production else 'out/fixture')).resolve()
    python=sys.executable
    def run(command,**kwargs):
        return subprocess.call([str(item) for item in command],**kwargs)
    if args.task=='test':
        return run([python,'-m','pytest','-q','--import-mode=importlib','-c',ROOT/'pyproject.toml','--confcutdir',ROOT,ROOT/'tests'],cwd=ROOT)
    if args.task=='sync': return run([python,ROOT/'tools/sync_core.py'])
    blender=os.environ.get('BLENDER_BIN') or shutil.which('blender')
    if not blender and os.name=='nt':
        installed=Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Blender Foundation/Blender 4.5/blender.exe'
        if installed.is_file(): blender=str(installed)
    if blender:
        os.environ['BLENDER_BIN']=blender
    secondary=os.environ.get('BLENDER_SECONDARY_BIN')
    portable=ROOT/'out/runtimes/blender-5.2.3/blender-5.2.3-windows-x64/blender.exe'
    if not secondary and portable.is_file(): secondary=str(portable)
    if secondary: os.environ['BLENDER_SECONDARY_BIN']=secondary
    if args.task=='dataset':
        if not blender or not args.scene.is_file():p.error('Dataset requires Blender and an existing --scene')
        return run([blender,'-b','--factory-startup',args.scene.resolve(),'--python-exit-code','1','-P',ROOT/'tools/generate_dataset.py','--','--folder',args.folder,'--count',args.count,'--seed',args.seed,'--samples',args.samples])
    if args.task=='doctor':
        print('Python:',sys.version)
        print('Blender:',blender or 'NOT AVAILABLE: set BLENDER_BIN')
        print('Secondary:',os.environ.get('BLENDER_SECONDARY_BIN','not configured'))
        print('Character:',args.source if args.source.is_file() else 'pending')
        return 0 if blender else 2
    if args.task=='docker': return run(['docker','build','-t','apollo',str(ROOT)])
    if args.task=='all':
        pipeline=['test','sync','production-scene' if args.production else 'scene','sweep','validate','sheet','prepare','demo','verify']
        if args.production and args.team: pipeline.append('bundle')
        for task in pipeline:
            command=[python,ROOT/'tasks.py',task,'--folder',args.folder,'--source',args.source]
            command+=['--look',args.look]
            if args.mapping: command+=['--mapping',args.mapping]
            if args.team: command+=['--team',args.team]
            if args.quality: command+=['--quality',args.quality]
            code=run(command)
            if code: return code
        return 0
    if args.task in ['scene','production-scene','inspect','sweep','framing']:
        if not blender:
            print('Blender unavailable. Set BLENDER_BIN to blender.exe.',file=sys.stderr)
            return 2
        command=[blender,'-b','--factory-startup','--python-exit-code','1']
        if args.task=='scene':
            command+=['-P',ROOT/'build/fixture_scene.py','--','--out',args.folder/'scene.blend']
        elif args.task=='inspect':
            if not args.source.is_file(): p.error('Missing character source asset')
            command+=[args.source,'-P',ROOT/'build/inspect_character.py','--','--out',args.folder/'inspect.json']
        elif args.task=='production-scene':
            if not args.source.is_file() or not args.mapping or not args.mapping.is_file():
                p.error('Production build requires --source asset and --mapping JSON')
            command+=['-P',ROOT/'build/build_scene.py','--','--source',args.source,'--mapping',args.mapping,'--out',args.folder/'scene.blend','--look',args.look]
        elif args.task=='framing':
            scene=args.folder/'scene.blend'
            if not scene.is_file(): p.error('Build the scene first')
            command+=[scene,'-P',ROOT/'tools/framing_sweep.py','--','--folder',args.folder]
        else:
            scene=args.folder/'scene.blend'
            if not scene.is_file(): p.error('Build the scene first')
            command+=[scene,'-P',ROOT/'wrapper/eyes.py','--','--out',args.folder]
            if args.quality: command+=['--quality',args.quality]
        return run(command)
    script={'validate':'validate_metadata.py','sheet':'contact_sheet.py','prepare':'prepare_candidate.py','bundle':'make_bundle.py','verify':'verify.py','demo':'demo.py'}[args.task]
    command=[python,ROOT/'tools'/script,args.folder]
    if args.task=='bundle':
        if not args.team: p.error('--team is required for bundle')
        command+=['--team',args.team]
    return run(command)

if __name__=='__main__':
    raise SystemExit(main())
