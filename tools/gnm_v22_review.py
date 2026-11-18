"""Render still-only full-v22 identity and blink review evidence; never saves the scene."""
import argparse
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from gnm_v22_audit import SELECTED,sha,appearance_signature
from gnm_portrait_refine import render


def main(a):
    if a.out.exists():raise FileExistsError(a.out)
    a.out.mkdir(parents=True)
    scene=bpy.context.scene;source=Path(bpy.data.filepath)
    source_hash=sha(source)
    if source_hash!=SELECTED and scene.get('apollo_identity_source_sha256')!=SELECTED:
        raise ValueError('Expected approved v22 or its authenticated derivation')
    audit=json.loads(a.audit.read_text(encoding='utf-8'))
    if audit['source_sha256']!=SELECTED or appearance_signature(scene.objects['GNM Head'])!=audit['appearance_signature']:
        raise ValueError('Full character appearance differs from approved v22')
    report=dict(scene_sha256=source_hash,approved_source_sha256=SELECTED,
                recipe_sha256=sha(__file__),renders=[],qualification='Still review only; user identity acceptance remains pending.')
    cameras={'portrait':'Portrait beauty 85mm','motion':'GNM Camera'}
    requested=a.cameras.split(',')
    if any(name not in cameras for name in requested):raise ValueError('Unknown review camera')
    for frame in [int(x) for x in a.frames.split(',')]:
        scene.frame_set(frame)
        for short in requested:
            camera=cameras[short]
            if source_hash==SELECTED and short=='motion':continue
            scene.camera=scene.objects[camera]
            name=f'{short}-{frame:03d}'
            render(scene,a.out,name,a.size,a.samples)
            report['renders'].append(dict(file=name+'.png',sha256=sha(a.out/(name+'.png')),
                frame=frame,camera=camera,matrix=[list(row) for row in scene.camera.matrix_world],
                lens=scene.camera.data.lens,samples=a.samples,size=a.size))
    if sha(source)!=source_hash:raise ValueError('Source scene changed during review')
    (a.out/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(dict(report=str(a.out/'review.json'),source_unchanged=True)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--audit',type=Path,required=True)
    p.add_argument('--frames',default='1,107,112');p.add_argument('--size',type=int,default=768)
    p.add_argument('--cameras',default='portrait,motion')
    p.add_argument('--samples',type=int,default=32)
    main(p.parse_args(sys.argv[sys.argv.index('--')+1:]))
