"""Measure persistent-data off against an existing matching three-pose benchmark."""
import argparse,hashlib,json,sys,time
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'wrapper'))
import eyes

def run(reference,folder):
    reference=Path(reference);folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    scene=bpy.context.scene;source=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    benchmark=json.loads((reference/'benchmark.json').read_text(encoding='utf-8'))
    assert benchmark['completed'] and benchmark['scene_sha256']==sha(source)
    original=scene.render.use_persistent_data;scene.render.use_persistent_data=False;rows=[]
    try:
        for name,h,v in [('center',0,0),('up',0,1)]:
            eyes.move(h,v);start=time.monotonic();eyes.render(folder/(name+'.png'));elapsed=time.monotonic()-start
            assert sha(folder/(name+'.png'))==sha(reference/'32'/(name+'.png')),'Persistence toggle changed render bytes'
            rows.append({'pose':name,'persistent_off_seconds':elapsed,'reference_seconds':benchmark['profiles']['32']['poses'][name]['seconds'],'png_identical':True})
    finally:scene.render.use_persistent_data=original
    (folder/'comparison.json').write_text(json.dumps({'passed':True,'scene_sha256':sha(source),'reference_persistent_data':original,'measurements':rows,'scope':'Single serial local trials; timing variation is not a statistical performance claim. No source scene save.'},indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reference',required=True,type=Path);p.add_argument('--folder',required=True,type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(a.reference,a.folder)
