"""Render still-only full-v22 identity and blink review evidence; never saves the scene."""
import argparse
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from apollo_core.png import canonicalize
from gnm_v22_audit import SELECTED,sha,appearance_signature
from gnm_portrait_refine import render
from gnm_v22_render_policy import apply as judging_policy


def main(a):
    if a.out.exists():raise FileExistsError(a.out)
    a.out.mkdir(parents=True)
    scene=bpy.context.scene;source=Path(bpy.data.filepath)
    source_hash=sha(source)
    if source_hash!=SELECTED and scene.get('apollo_identity_source_sha256')!=SELECTED:
        raise ValueError('Expected approved v22 or its authenticated derivation')
    audit=json.loads(a.audit.read_text(encoding='utf-8'))
    audit_hash=sha(a.audit);head=scene.objects['GNM Head']
    if audit['source_sha256']!=SELECTED:
        raise ValueError('Full character appearance differs from approved v22')
    recipe_files=[Path(__file__),Path(__file__).with_name('gnm_portrait_refine.py'),
        Path(__file__).with_name('gnm_v22_audit.py'),Path(__file__).with_name('gnm_v22_render_policy.py'),
        Path(__file__).resolve().parents[1]/'apollo_core/png.py']
    maps_hash=None;binding=None
    if a.maps:
        from gnm_v22_materials import bind,validate,load_manifest
        recipe_files.extend([Path(__file__).with_name('gnm_v22_materials.py'),
                             Path(__file__).with_name('gnm_pbr_manifest.py')])
        load_manifest(a.maps);maps_hash=sha(a.maps/'manifest.json')
        if appearance_signature(head)==audit['appearance_signature']:
            bind(head,a.maps,a.layout,full_character=True)
            binding=validate(head,a.maps,a.layout,full_character=True,require_packed=False)
        else:
            binding=validate(head,a.maps,a.layout,full_character=True,require_packed=True)
    elif appearance_signature(head)!=audit['appearance_signature']:
        raise ValueError('Full character appearance differs from approved v22')
    recipes={path.name:sha(path) for path in recipe_files}
    policy=judging_policy(scene,a.samples)
    report=dict(scene_sha256=source_hash,approved_source_sha256=SELECTED,
                recipe_sha256=recipes,source_audit_sha256=audit_hash,
                maps_manifest_sha256=maps_hash,binding=binding,judging_policy=policy,
                blender=bpy.app.version_string,blender_build=bpy.app.build_hash.decode(),
                renders=[],qualification='Still review only; user identity acceptance remains pending.')
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
            canonicalize(a.out/(name+'.png'))
            report['renders'].append(dict(file=name+'.png',sha256=sha(a.out/(name+'.png')),
                frame=frame,camera=camera,matrix=[list(row) for row in scene.camera.matrix_world],
                lens=scene.camera.data.lens,samples=a.samples,size=a.size))
    if (sha(source)!=source_hash or sha(a.audit)!=audit_hash or
            any(sha(path)!=recipes[path.name] for path in recipe_files)):
        raise ValueError('Review source or worker changed during rendering')
    if a.maps:
        load_manifest(a.maps)
        if sha(a.maps/'manifest.json')!=maps_hash:raise ValueError('Review maps changed')
    (a.out/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(dict(report=str(a.out/'review.json'),source_unchanged=True)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--audit',type=Path,required=True)
    p.add_argument('--frames',default='1,107,112');p.add_argument('--size',type=int,default=768)
    p.add_argument('--cameras',default='portrait,motion')
    p.add_argument('--samples',type=int,default=32)
    p.add_argument('--maps',type=Path,help='Render the explicit full-character PBR conversion or validate its packed bindings')
    p.add_argument('--layout',choices=('udim','legacy'),default='udim')
    main(p.parse_args(sys.argv[sys.argv.index('--')+1:]))
