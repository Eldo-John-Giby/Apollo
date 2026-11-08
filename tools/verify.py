"""End-to-end verifier. Missing evidence is NOT RUN, never PASS."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from apollo_core.core import Config,make_record,eye_state,angle_from_primary,MAX_ECCENTRICITY
from apollo_core.metadata import load
from validate_metadata import validate_artifacts
from grader_sim import gray,detect,centroid,template_shift


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verifier_sources():
    names=['tools/verify.py','tools/blender_verify.py','tools/grader_sim.py','apollo_core/core.py','apollo_core/metadata.py','metadata.schema.json','tools/independent_audit.py','tools/reference_geometry.py']
    return {name:digest(ROOT/name) for name in names}


def evidence_hashes(folder):
    folder=Path(folder);ev=folder/'verification'
    files=[ev/'blender_evidence.json',ev/'independent_geometry.json',ev/'baseline.png']
    files += [ev/(name+'.png') for name in ['left','right','up','down','reset']]
    for sub in ['masks','repeat_a','repeat_b','secondary_reference']:
        if (ev/sub).exists():files+=list((ev/sub).rglob('*.png'))+list((ev/sub).rglob('metadata.json'))
    return {str(p.relative_to(folder)).replace('\\','/'):digest(p) for p in sorted(set(files)) if p.is_file()}


def hashes(folder):
    folder=Path(folder)
    paths=[folder/'scene.blend',folder/'metadata.json',ROOT/'wrapper/eyes.py']+sorted((folder/'renders').glob('*.png'))
    return {('wrapper/eyes.py' if p==ROOT/'wrapper/eyes.py' else str(p.relative_to(folder)).replace('\\','/')):digest(p) for p in paths if p.is_file()}


def write_report(folder,report):
    folder=Path(folder); folder.mkdir(parents=True,exist_ok=True)
    current={'artifacts':hashes(folder),'verifier':verifier_sources()}
    if 'run_start' in report and report['run_start']!=current:
        report['checks']['V13']={'status':'FAIL','detail':'Inputs or verifier changed during qualification'}
    report['verifier_sha256']=current['verifier']
    report['evidence_sha256']=evidence_hashes(folder)
    report['passed']=all(report['checks'][f'V{i}']['status']=='PASS' for i in range(1,18))
    report['artifact_hashes']=hashes(folder)
    (folder/'verification_report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    lines=['# Apollo verification','',f"Production asset: {report['production']}",f"All checks passed: {report['passed']}",'','| Check | Status | Evidence |','| --- | --- | --- |']
    for name,item in report['checks'].items():
        detail=str(item.get('measurement',item.get('detail',''))).replace('|','/').replace('\n',' ')
        lines.append(f"| {name} | {item['status']} | {detail} |")
    (folder/'verification_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return report


def verify(folder,blender=None,secondary=None,reuse_evidence=False):
    folder=Path(folder).resolve()
    report={'production':False,'environment':{'python':sys.version,'platform':platform.platform()},'checks':{f'V{i}':{'status':'NOT RUN','detail':'Evidence unavailable'} for i in range(1,18)}}
    report['run_start']={'artifacts':hashes(folder),'verifier':verifier_sources()}
    def check(name,fn):
        try: report['checks'][name]={'status':'PASS','measurement':fn()}
        except Exception as exc: report['checks'][name]={'status':'FAIL','detail':str(exc)}
    def schema():
        records=validate_artifacts(folder)
        report['production']=all(r.get('extra',{}).get('fixture') is False for r in records)
        return 'schema, sequence, image dimensions and finite annotations valid'
    check('V13',schema)
    blender=blender or os.environ.get('BLENDER_BIN') or shutil.which('blender')
    if not blender:
        for i in [1,2,3,4,5,6,7,8,9,10,11,12,14,15,16,17]:
            report['checks'][f'V{i}']['detail']='Blender unavailable; set BLENDER_BIN'
        return write_report(folder,report)
    command=[str(blender),'-b','--factory-startup',str(folder/'scene.blend'),'--python-exit-code','1','-P',str(ROOT/'tools/blender_verify.py'),'--','--folder',str(folder)]
    evidence_path=folder/'verification/blender_evidence.json'
    if reuse_evidence:
        prior=json.loads((folder/'verification_report.json').read_text())
        if prior['artifact_hashes']!=hashes(folder):
            raise ValueError('Inputs changed; cannot reuse verification evidence')
        if prior.get('verifier_sha256')!=verifier_sources() or prior.get('evidence_sha256')!=evidence_hashes(folder):
            raise ValueError('Verifier/evidence changed or legacy provenance missing; full verification required')
    elif evidence_path.exists(): evidence_path.unlink()
    try:
        if not reuse_evidence: subprocess.run(command,check=True)
        evidence=json.loads(evidence_path.read_text(encoding='utf-8'))
        report['environment']['blender']=evidence['blender']
        report['production']=not evidence['fixture']
        for name,item in evidence['checks'].items():
            if name.startswith('V'): report['checks'][name]=item
        assert evidence['checks'].get('independent_geometry',{}).get('status')=='PASS','Independent deformed-geometry audit failed or missing'
        cfg=Config(**evidence['config'])
        records=load(folder/'metadata.json',cfg)
        assert all(r.get('extra',{}).get('fixture')==evidence['fixture'] for r in records),'Scene/metadata fixture classification mismatch'
        report['checks']['V13']={'status':'PASS','measurement':'JSON Schema, images, sequence and calibrated analytic annotations agree'}
    except Exception as exc:
        for name,item in report['checks'].items():
            if item['status']=='NOT RUN': item.update(status='FAIL',detail=f'Blender evidence collection failed: {exc}')
        return write_report(folder,report)
    ev=folder/'verification'
    def pixels():
        residuals=[]
        for k,r in enumerate(records):
            centers=centroid(gray(ev/'masks/unoccluded'/f'frame_{k:02d}.png'))
            residuals.extend(float(np.linalg.norm(centers[s]-r['pupil_center_2D_'+s])) for s in 'LR')
        maximum=max(residuals)
        assert maximum<.5,f'Max pixel centroid residual {maximum:.6f} px'
        return {'max_residual_px':maximum}
    check('V7',pixels)
    def blind():
        maximum=0.
        for k,r in enumerate(records):
            measured=detect(gray(folder/'renders'/f'frame_{k:02d}.png'))
            maximum=max(maximum,*(float(np.linalg.norm(measured[s]-r['pupil_center_2D_'+s])) for s in 'LR'))
        assert maximum<1.,f'Blind ellipse residual {maximum:.6f} px'
        return {'max_residual_px':maximum}
    check('V8',blind)
    baseline=gray(ev/'baseline.png')
    def templates():
        centers=detect(baseline); maximum=0.
        for name,r in evidence['directions'].items():
            measured=template_shift(baseline,gray(ev/(name+'.png')))
            for side in 'LR':
                expected=np.array(r['pupil_center_2D_'+side])-eyes_center(cfg,side)
                maximum=max(maximum,float(np.linalg.norm(measured[side]-expected)))
        assert maximum<1.5,f'Template displacement error {maximum:.6f} px'
        return {'max_displacement_error_px':maximum}
    check('V9',templates)
    def directions():
        center=detect(baseline)
        for name,axis,sign in [('left',0,-1),('right',0,1),('up',1,-1),('down',1,1)]:
            image=gray(ev/(name+'.png'))
            found=detect(image); shifts=template_shift(baseline,image)
            for side in 'LR':
                for delta in [found[side]-center[side],shifts[side]]:
                    assert delta[axis]*sign>=8.,f'{name}/{side}: insufficient/counterdirectional displacement {delta}'
                    assert abs(delta[1-axis])<.5,f'{name}/{side}: cross-talk {delta}'
        assert evidence['reset_identical'],'Reset PNG differs from baseline'
        return 'both blind detectors passed all directions; reset byte-identical'
    check('V10',directions)
    def visibility():
        minimum=1.
        poses=[(f'frame_{k:02d}',folder/'renders'/f'frame_{k:02d}.png') for k in range(10)]
        poses += [(name,ev/(name+'.png')) for name in evidence['directions']]
        for name,path in poses:
            expected_mask=gray(ev/'masks/unoccluded'/(name+'.png'))/255.
            visible_mask=gray(ev/'masks/occluded'/(name+'.png'))/255.
            # Compare full-coverage interiors, and separately audit total
            # coverage. Partial edge pixels are blended with the bright iris.
            truth=expected_mask>=.99
            visible=visible_mask>=.99
            decode=lambda x: np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
            expected_coverage=decode(expected_mask)
            visible_coverage=decode(visible_mask)
            final=gray(path)
            for left,right in [(0,512),(512,1024)]:
                expected=truth[:,left:right]
                assert expected.sum()>0,'Empty expected pupil'
                fraction=float((expected & visible[:,left:right] & (final[:,left:right]<60)).sum()/expected.sum())
                coverage=float(visible_coverage[:,left:right].sum()/expected_coverage[:,left:right].sum())
                minimum=min(minimum,fraction,coverage)
        assert minimum>=.98,f'Pupil visible/dark fraction {minimum:.6f}'
        return {'minimum_visible_dark_fraction':minimum}
    check('V14',visibility)
    def annotations():
        max_offset=0.
        for r in records:
            states,_=eye_state(r['input']['h'],r['input']['v'],cfg)
            expected=make_record(r['frame'],r['theta'],r['input']['h'],r['input']['v'],cfg,r['extra']['image'])
            for side in 'LR':
                assert angle_from_primary(states[side]['quat'])<MAX_ECCENTRICITY
                ellipse=r['extra']['pupil_ellipse_2D_'+side]
                offset=float(np.linalg.norm(np.array(ellipse['center'])-r['pupil_center_2D_'+side]))
                max_offset=max(max_offset,offset)
                assert 0<ellipse['semi_axes'][1]<=ellipse['semi_axes'][0]<100
                assert np.allclose(r['extra']['gaze_pitch_yaw_'+side],expected['extra']['gaze_pitch_yaw_'+side],atol=1e-10)
        assert max_offset<.02,f'Ellipse center offset {max_offset} px'
        return {'max_ellipse_center_offset_px':max_offset}
    check('V17',annotations)
    def cleanroom():
        assert evidence['checks']['resources']['status']=='PASS','Packed resource audit failed'
        with tempfile.TemporaryDirectory(dir=folder.parent) as temp:
            temp=Path(temp); stage=temp/'bundle'; stage.mkdir()
            shutil.copy2(folder/'scene.blend',stage/'scene.blend')
            (stage/'wrapper').mkdir()
            shutil.copy2(ROOT/'wrapper/eyes.py',stage/'wrapper/eyes.py')
            work=temp/'different_cwd'; work.mkdir()
            env=os.environ.copy()
            for key in ['BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','BLENDER_USER_DATAFILES']:
                path=temp/key; path.mkdir(); env[key]=str(path)
            # Regenerate the actual stored scene settings, including 64-sample
            # candidates; a draft/final override silently changed those to 32.
            subprocess.run([str(blender),'-b','--factory-startup','--python-exit-code','1','-P',str(stage/'wrapper/eyes.py')],cwd=work,env=env,check=True)
            names=['metadata.json']+[f'renders/frame_{k:02d}.png' for k in range(10)]
            assert all(digest(stage/name)==digest(folder/name) for name in names),'Clean-room hashes differ'
        return 'packed resources; standalone extracted layout regenerated byte-identical from different cwd'
    if reuse_evidence and prior.get('checks',{}).get('V15',{}).get('status')=='PASS':
        report['checks']['V15']=prior['checks']['V15']
    else:
        check('V15',cleanroom)
    if secondary:
        def cross_version():
            with tempfile.TemporaryDirectory(dir=folder.parent) as temp:
                stage=Path(temp)/'secondary'; stage.mkdir()
                shutil.copy2(folder/'scene.blend',stage/'scene.blend')
                # Produce version-specific reference frames, then validate all geometric/pixel checks.
                subprocess.run([str(secondary),'-b','--factory-startup',str(stage/'scene.blend'),'--python-exit-code','1','-P',str(ROOT/'wrapper/eyes.py'),'--','--out',str(stage)],check=True)
                secondary_report=verify(stage,secondary)
                for name in [f'V{i}' for i in range(1,18) if i!=16]:
                    assert secondary_report['checks'][name]['status']=='PASS',f'Secondary {name} failed'
                assert evidence['blender'].startswith('4.5.'),'Primary qualification requires Blender 4.5 LTS'
                assert secondary_report['environment']['blender'].startswith('5.2.'),'Secondary qualification requires Blender 5.2 LTS'
                shutil.copy2(stage/'verification_report.json',ev/'secondary_report.json')
                shutil.copy2(stage/'verification_report.md',ev/'secondary_report.md')
                reference=ev/'secondary_reference'; reference.mkdir(exist_ok=True)
                shutil.copytree(stage/'renders',reference/'renders',dirs_exist_ok=True)
                shutil.copy2(stage/'metadata.json',reference/'metadata.json')
                shutil.copytree(stage/'verification/masks',reference/'masks',dirs_exist_ok=True)
                return secondary_report['environment']['blender']
        check('V16',cross_version)
    else:
        report['checks']['V16']={'status':'NOT RUN','detail':'Set BLENDER_SECONDARY_BIN for cross-version verification'}
    return write_report(folder,report)


def eyes_center(cfg,side): return np.array(eye_state(0,0,cfg)[0][side]['pupil2d'])

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('folder',type=Path)
    parser.add_argument('--blender')
    parser.add_argument('--secondary',default=os.environ.get('BLENDER_SECONDARY_BIN'))
    parser.add_argument('--reuse-evidence',action='store_true')
    args=parser.parse_args()
    report=verify(args.folder,args.blender,args.secondary,args.reuse_evidence)
    print('PASS' if report['passed'] else 'INCOMPLETE / FAILED',args.folder/'verification_report.md')
    raise SystemExit(0 if report['passed'] else 1)
