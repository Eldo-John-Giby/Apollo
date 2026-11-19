"""Measure sample convergence on full-v22 stills without changing the saved scene."""
import argparse
import json
from pathlib import Path
import sys
import time

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from gnm_v22_audit import SELECTED,sha,appearance_signature
from gnm_portrait_refine import render
from gnm_v22_render_policy import apply as judging_policy


def main(a):
    if a.out.exists():raise FileExistsError(a.out)
    source=Path(bpy.data.filepath);source_hash=sha(source)
    scene=bpy.context.scene
    if scene.get('apollo_identity_source_sha256')!=SELECTED:
        raise ValueError('Expected the full v22 motion candidate')
    audit=json.loads(a.audit.read_text(encoding='utf-8'))
    if audit['source_sha256']!=SELECTED or appearance_signature(scene.objects['GNM Head'])!=audit['appearance_signature']:
        raise ValueError('Selected full-character appearance changed')
    portable=None
    if a.maps:
        from gnm_v22_materials import bind,validate
        bind(scene.objects['GNM Head'],a.maps,'udim',full_character=True)
        portable=validate(scene.objects['GNM Head'],a.maps,'udim',full_character=True,require_packed=False)
    a.out.mkdir(parents=True)
    scene.camera=scene.objects['GNM Camera']
    scene.frame_set(a.frame)
    policy=judging_policy(scene)
    report=dict(scene_sha256=source_hash,selected_sha256=SELECTED,recipe_sha256=sha(__file__),
                appearance_signature=audit['appearance_signature'],frame=a.frame,size=a.size,
                blender=bpy.app.version_string,device='CPU',adaptive_sampling=False,
                animated_seed=False,seed=20261119,denoising=True,time_limit=0,
                motion_blur=False,dither_intensity=0,judging_policy=policy,
                judging_policy_sha256=sha(Path(__file__).with_name('gnm_v22_render_policy.py')),
                camera_matrix=[list(r) for r in scene.camera.matrix_world],
                camera_lens=scene.camera.data.lens,view_transform=scene.view_settings.view_transform,
                exposure=scene.view_settings.exposure,profiles={},complete=False)
    if portable:report['portable_materials']=portable
    for samples in a.samples:
        start=time.monotonic()
        name=f'samples-{samples:03d}'
        render(scene,a.out,name,a.size,samples)
        report['profiles'][str(samples)]=dict(samples=samples,seconds=time.monotonic()-start,
                file=name+'.png',sha256=sha(a.out/(name+'.png')))
        (a.out/'convergence.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if sha(source)!=source_hash:raise ValueError('Source changed during convergence test')
    report['complete']=True
    (a.out/'convergence.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(dict(report=str(a.out/'convergence.json'),source_unchanged=True)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--audit',type=Path,required=True)
    p.add_argument('--samples',type=int,nargs='+',default=[32,64])
    p.add_argument('--size',type=int,default=1024);p.add_argument('--frame',type=int,default=1)
    p.add_argument('--maps',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if any(n not in (16,24,32,48,64,96,128,256,512,1024) for n in a.samples):p.error('Unsupported sample count')
    main(a)
