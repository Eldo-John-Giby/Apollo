"""Run targeted v2 development checks, without full verification or publishing."""
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(scene,out,blender):
    scene=scene.resolve();out=out.resolve()
    if out.exists():raise ValueError('Use a new check output directory')
    out.mkdir(parents=True);source_sha=hashlib.sha256(scene.read_bytes()).hexdigest();peaks=[]
    def status(stage,**fields):
        p=out/'status.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps({'stage':stage,**fields},indent=2)+'\n',encoding='utf-8');tmp.replace(p);print(stage,flush=True)
    def command(stage,args):
        status(stage);start=time.monotonic()
        with (out/(stage+'.log')).open('wb') as log:
            child=subprocess.Popen([str(x) for x in args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            peak=0
            if sys.platform=='win32':
                import ctypes
                from ctypes import wintypes
                class Counters(ctypes.Structure):
                    _fields_=[('cb',wintypes.DWORD),('faults',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ['peak','working','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile']]
                kernel=ctypes.windll.kernel32;kernel.OpenProcess.restype=wintypes.HANDLE;kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.CloseHandle.argtypes=[wintypes.HANDLE]
                handle=kernel.OpenProcess(0x410,False,child.pid);info=Counters();info.cb=ctypes.sizeof(info)
                get=ctypes.windll.psapi.GetProcessMemoryInfo;get.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
                while child.poll() is None:
                    if handle and get(handle,ctypes.byref(info),info.cb):peak=max(peak,info.peak)
                    time.sleep(.5)
                if handle:kernel.CloseHandle(handle)
            else:
                child.wait()
                import resource
                peak=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*(1 if sys.platform=='darwin' else 1024)
            if child.returncode:raise RuntimeError(stage+' failed; inspect its log')
            peaks.append({'stage':stage,'elapsed_seconds':time.monotonic()-start,'peak_process_rss_bytes':peak})
        assert hashlib.sha256(scene.read_bytes()).hexdigest()==source_sha,'Source scene changed'
    def worker(script,*args):return [blender,'-b','--factory-startup',scene,'--python-exit-code','1','-P',ROOT/script,'--',*args]
    py=sys.executable
    try:
        command('preflight',worker('tools/scene_preflight.py','--out',out/'scene-preflight.json'))
        command('geometry',worker('tools/independent_audit.py','--out',out/'geometry.json','--random','1000'))
        command('benchmark',worker('tools/benchmark_render.py','--folder',out/'performance','--samples','32','--corner'))
        bench=json.loads((out/'performance/benchmark.json').read_text(encoding='utf-8'));assert bench['completed']
        # Check actual benchmark pixels before paying for the full pose set.
        import numpy as np
        from grader_sim import gray,detect
        from reference_geometry import reference
        for pose,item in bench['profiles']['32']['poses'].items():
            record=item['record'];found=detect(gray(out/'performance/32'/f'{pose}.png'))
            for side in 'LR':assert np.linalg.norm(found[side]-reference(side,record['input']['h'],record['input']['v'],ipd=record['extra']['calibration']['ipd'])['pixel'])<1,'Benchmark pupil check failed'
        assert max(x['seconds'] for x in bench['profiles']['32']['poses'].values())<=120,'CPU frame budget exceeded; optimize first'
        command('anchors',worker('tools/realism_visibility.py','--folder',out/'poses','--masks',out/'masks','--limit','9'))
        command('anchor-images',[py,ROOT/'tools/early_image_gate.py',out/'poses','--baseline',out/'performance/32/center.png','--progress'])
        command('mask-analysis',[py,ROOT/'tools/analyze_visibility.py',out/'masks'])
        command('directions',worker('tools/direction_smoke.py','--folder',out/'directions'))
        command('direction-report',[py,ROOT/'tools/direction_report.py',out/'directions'])
        official=out/'official';official.mkdir();shutil.copy2(scene,official/'scene.blend')
        command('official-sweep',worker('wrapper/eyes.py','--out',official))
        command('official-validation',[py,ROOT/'tools/validate_metadata.py',official])
        command('official-images',[py,ROOT/'tools/early_image_gate.py',official,'--baseline',out/'performance/32/center.png'])
        command('sheet',[py,ROOT/'tasks.py','sheet','--folder',official])
        command('portraits',worker('tools/realism_hero.py','--folder',out/'portraits'))
        command('diagnostics',worker('tools/photorealism_diagnostics.py','--folder',out/'diagnostics'))
        command('comparisons',[py,ROOT/'tools/realism_comparison.py','--before',ROOT/'out/photorealism-v2/baseline-poses','--after',out/'poses','--out',out/'comparisons'])
        peak=max(p['peak_process_rss_bytes'] for p in peaks);assert 0<peak<=4*1024**3,'Memory budget failed/unmeasured'
        (out/'resources.json').write_text(json.dumps({'peak_process_rss_bytes':peak,'stages':peaks},indent=2)+'\n',encoding='utf-8')
        status('targeted-checks-complete-awaiting-visual-review',scene_sha256=source_sha,qualified=False)
    except Exception as exc:
        (out/'resources.json').write_text(json.dumps({'stages':peaks},indent=2)+'\n',encoding='utf-8');status('failed',error=str(exc));raise
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scene',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--blender',default=os.environ.get('BLENDER_BIN') or shutil.which('blender'));a=p.parse_args();assert a.blender,'Set BLENDER_BIN';run(a.scene,a.out,a.blender)
