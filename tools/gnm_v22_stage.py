"""Stage an authenticated development runtime for clean-extraction rehearsals."""
import argparse
import json
from pathlib import Path
import shutil

from gnm_run import VARIANTS,MODES
from gnm_pbr_manifest import load_manifest
from gnm_v22_variants import sha,verify_selected

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=('tools/gnm_run.py','tools/gnm_motion_variant.py','tools/gnm_texture_trial.py',
         'tools/gnm_materials.py','tools/gnm_portable.py','tools/gnm_pbr_manifest.py',
         'tools/gnm_v22_materials.py','tools/gnm_v22_audit.py','tools/submission_render.py',
         'apollo_core/__init__.py','apollo_core/submission_timing.py','apollo_core/png.py')


def timeline(directory,maps_hash):
    scene=directory/'expression.blend'
    prepared=json.loads(scene.with_suffix('.prepare.json').read_text(encoding='utf-8'))
    checked=json.loads((directory/'half-frame-check.json').read_text(encoding='utf-8'))
    appearance=json.loads((directory/'appearance-check.json').read_text(encoding='utf-8'))
    digest=sha(scene)
    if prepared['scene_sha256']!=digest or prepared['maps_manifest_sha256']!=maps_hash:
        raise ValueError('Stale packed timeline preparation')
    if checked['scene_sha256']!=digest or checked['status']!='passed_geometry_and_resources':
        raise ValueError('Stale or failed reopened timeline check')
    if (checked['verifier_sha256']!=sha(ROOT/'tools/gnm_v22_verify.py') or
            appearance['recipe_sha256']!=sha(ROOT/'tools/gnm_v22_appearance_check.py')):
        raise ValueError('Timeline evidence uses a different verifier recipe')
    if len(checked['frames'])!=383 or checked['frames']!=[1+i*.5 for i in range(383)]:
        raise ValueError('Need all integer and half-frame checks')
    if appearance['scene_sha256']!=digest or len(appearance['objects'])!=18:
        raise ValueError('Stale or incomplete whole-character appearance check')
    if appearance['passed'] is not True or any(
            report['portable_binding']['manifest_sha256']!=maps_hash for report in (checked,appearance)):
        raise ValueError('Appearance or PBR evidence does not match the runtime maps')
    if prepared['samples']<=0 or prepared['geometry_and_uv_unchanged'] is not True:
        raise ValueError('Invalid packed render preset or geometry preservation')
    return scene,prepared


def main(a):
    if a.out.exists():raise FileExistsError(a.out)
    maps={variant:load_manifest(a.textures/variant) for variant in VARIANTS}
    selected=maps['rose-brown']['source_sha256'];verify_selected(selected)
    if any(manifest['source_sha256']!=selected for manifest in maps.values()):
        raise ValueError('Runtime variants derive from different identities')
    default_hash=sha(a.textures/'rose-brown/manifest.json')
    scenes={mode:timeline(a.timelines/mode,default_hash) for mode in MODES}
    if any(prepared['selected_sha256']!=selected for _,prepared in scenes.values()):
        raise ValueError('Runtime scenes and textures derive from different identities')
    files={name:ROOT/name for name in RUNTIME}
    files.update({'model/neutral.blend':a.template/'neutral.blend',
                  'model/template.npz':a.template/'template.npz'})
    for variant,manifest in maps.items():
        for name in (*manifest['maps'],'manifest.json'):
            files[f'textures/{variant}/{name}']=a.textures/variant/name
    for mode,(scene,_) in scenes.items():files[f'timelines/{mode}/expression.blend']=scene
    files['model/character.blend']=scenes['generate-motion'][0]
    inputs={name:sha(path) for name,path in files.items()}
    a.out.mkdir(parents=True)
    for name,path in files.items():
        output=a.out/name;output.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,output)
        if sha(output)!=inputs[name] or sha(path)!=inputs[name]:
            raise ValueError('Runtime payload changed during staging: '+name)
    receipt=dict(schema=1,status='development_runtime_staged',sha256=inputs,
                 selected_sha256=scenes['generate-motion'][1]['selected_sha256'],
                 maps_manifest_sha256={variant:sha(a.textures/variant/'manifest.json') for variant in VARIANTS},
                 samples={mode:prepared['samples'] for mode,(_,prepared) in scenes.items()},
                 recipe_sha256=sha(__file__),
                 qualification='Development executable rehearsal only; no final sequences, licenses, review acceptance or release-readiness claim.')
    for mode in MODES:timeline(a.timelines/mode,default_hash)
    for variant in VARIANTS:load_manifest(a.textures/variant)
    (a.out/'runtime-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+str(a.out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('timelines','textures','template','out'):p.add_argument('--'+name,type=Path,required=True)
    main(p.parse_args())
