import datetime,hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path('C:/Users/eldoj/PycharmProjects/Apollo-full-test-20261109')
OUT=Path('C:/Users/eldoj/PycharmProjects/Samsung XR/out/full-test-20261109')
BLENDER=Path('C:/Program Files/Blender Foundation/Blender 4.5/blender.exe')
SCENE=ROOT/'milestones/photorealism-v2-candidate/scene.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[SCENE,*sorted((ROOT/'tools').glob('*.py')),*sorted((ROOT/'wrapper').glob('*.py'))]
bindings={str(p.relative_to(ROOT)):sha(p) for p in files}
receipt={'commit':'fda66c7','source_root':str(ROOT),'scene_sha256':sha(SCENE),'inputs':bindings,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'resolution':1024,'samples':32,'mode':'serial full 113 RGB + actual masks, then fresh 256 RGB and independent/blind analyses'}
(OUT/'run.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
def status(stage,**kw):
 p=OUT/'status.json';q=p.with_suffix('.tmp');q.write_text(json.dumps({'stage':stage,'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**kw},indent=2)+'\n',encoding='utf-8');q.replace(p)
def guard():
 for p in files:
  if sha(p)!=bindings[str(p.relative_to(ROOT))]:raise RuntimeError('Frozen source changed: '+str(p))
def run(stage,args):
 guard();status(stage);start=time.monotonic()
 with (OUT/(stage+'.log')).open('ab') as log:
  child=subprocess.Popen([str(x) for x in args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  status(stage,pid=child.pid)
  code=child.wait()
 if code:raise RuntimeError(stage+' failed with code '+str(code))
 guard();print(stage,'passed',round(time.monotonic()-start,2),flush=True)
def worker(script,*args):return [BLENDER,'-b','--factory-startup',SCENE,'--python-exit-code','1','-P',ROOT/script,'--',*args]
try:
 run('preflight',worker('tools/scene_preflight.py','--out',OUT/'preflight.json'))
 if not (OUT/'masks113/evidence.json').exists():
  run('visibility113',worker('tools/realism_visibility.py','--folder',OUT/'poses113','--masks',OUT/'masks113','--limit','113'))
 baseline=OUT/'poses113/renders/frame_000004.png'
 run('visibility-images',[sys.executable,ROOT/'tools/early_image_gate.py',OUT/'poses113','--baseline',baseline,'--progress'])
 run('visibility-masks',[sys.executable,ROOT/'tools/analyze_visibility.py',OUT/'masks113'])
 run('dataset256',worker('tools/generate_dataset.py','--folder',OUT/'dataset256','--count','256','--seed','0','--samples','32'))
 run('dataset-analysis',[sys.executable,ROOT/'tools/analyze_dataset.py',OUT/'dataset256'])
 run('dataset-images',[sys.executable,ROOT/'tools/early_image_gate.py',OUT/'dataset256','--baseline',OUT/'dataset256/renders/frame_000004.png','--progress'])
 guard();status('complete-awaiting-visual-review',scene_sha256=sha(SCENE));print('All automated stages passed',flush=True)
except Exception as exc:
 status('failed',error=str(exc));raise
