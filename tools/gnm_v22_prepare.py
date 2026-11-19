"""Pack authenticated v22 PBR appearance and a judging preset into a derived timeline."""
import argparse
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from gnm_v22_audit import SELECTED,sha,coords,appearance_signature
from gnm_v22_materials import bind,validate,load_manifest
from gnm_v22_render_policy import apply as judging_policy
from gnm_portable import relative_images


def main(a):
    source=Path(bpy.data.filepath);source_hash=sha(source)
    receipt_path=a.out.with_suffix('.prepare.json')
    if a.out.exists() or receipt_path.exists():raise FileExistsError(a.out)
    scene=bpy.context.scene;head=scene.objects['GNM Head']
    integration=json.loads(a.integration.read_text(encoding='utf-8'))
    if (scene.get('apollo_identity_source_sha256')!=SELECTED or integration['source_sha256']!=SELECTED
            or integration['scene_sha256']!=source_hash or integration['geometry_sha256']!=sha(a.geometry)):
        raise ValueError('Timeline and native/derived geometry do not match the integration receipt')
    audit=json.loads(a.source_audit.read_text(encoding='utf-8'))
    if audit['source_sha256']!=SELECTED or appearance_signature(head)!=audit['appearance_signature']:
        raise ValueError('Input timeline no longer has the authenticated selected appearance')
    root=Path(__file__).resolve().parents[1]
    selected=root/'milestones/gnm-portrait-final-2026-11-17/portrait_v22.blend'
    if sha(selected)!=SELECTED:raise ValueError('Selected source differs')
    manifest=load_manifest(a.maps);manifest_hash=sha(a.maps/'manifest.json')
    if manifest.get('variant','rose-brown')!='rose-brown':
        raise ValueError('Prepare the approved default; alternate variants use the existing runtime cache')
    recipes=('gnm_v22_prepare.py','gnm_v22_audit.py','gnm_v22_materials.py',
             'gnm_v22_render_policy.py','gnm_pbr_manifest.py','gnm_portable.py','gnm_run.py')
    recipe_hashes={name:sha(Path(__file__).with_name(name)) for name in recipes}
    integration_hash=sha(a.integration);geometry_hash=sha(a.geometry);audit_hash=sha(a.source_audit)
    # Keep the original source payloads across subsequent variant saves even
    # when their replaced materials become orphaned. Active PBR images retain
    # normal ownership so caches can retire only superseded bindings.
    original_images={item['name']:item['sha256'] for item in audit['images'] if item['packed']}
    for name,digest in original_images.items():
        image=bpy.data.images.get(name)
        if not image or not image.packed_file or __import__('hashlib').sha256(bytes(image.packed_file.data)).hexdigest()!=digest:
            raise ValueError('Original selected image payload differs: '+name)
        image.use_fake_user=True
    scene.frame_set(1)
    before=coords(head.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices)
    regions=np.array([p.material_index for p in head.data.polygons])
    uv={layer.name:np.array([tuple(p.uv) for p in layer.data]) for layer in head.data.uv_layers}
    bind(head,a.maps,'udim',full_character=True)
    scene.camera=scene.objects['GNM Camera']
    policy=judging_policy(scene,a.samples)
    scene.render.filepath='//frames/frame_'
    bpy.data.use_autopack=False
    for image in bpy.data.images:
        if image.source in ('FILE','TILED') and not image.packed_file:image.pack()
    relative_images(a.maps,a.out,map_root='//packed/v22-default')
    binding=validate(head,a.maps,'udim',full_character=True,require_packed=True)
    after=coords(head.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices)
    np.testing.assert_array_equal(before,after)
    np.testing.assert_array_equal(regions,[p.material_index for p in head.data.polygons])
    for layer in head.data.uv_layers:
        np.testing.assert_array_equal(uv[layer.name],np.array([tuple(p.uv) for p in layer.data]))
    scene['apollo_v22_maps_manifest_sha256']=manifest_hash
    scene['apollo_v22_judging_samples']=a.samples
    scene['apollo_v22_judging_policy_sha256']=recipe_hashes['gnm_v22_render_policy.py']
    scene['apollo_v22_judging_policy']=json.dumps(policy,sort_keys=True)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(a.out.resolve()),compress=True,relative_remap=False)
    load_manifest(a.maps)
    if (sha(source)!=source_hash or sha(selected)!=SELECTED or sha(a.maps/'manifest.json')!=manifest_hash
            or sha(a.integration)!=integration_hash or sha(a.geometry)!=geometry_hash or sha(a.source_audit)!=audit_hash
            or any(sha(Path(__file__).with_name(name))!=digest for name,digest in recipe_hashes.items())):
        raise ValueError('Preparation inputs or recipes changed during execution')
    report=dict(source_scene_sha256=source_hash,scene_sha256=sha(a.out),selected_sha256=SELECTED,
                integration_receipt_sha256=integration_hash,geometry_sha256=geometry_hash,
                source_audit_sha256=audit_hash,maps_manifest_sha256=manifest_hash,binding=binding,
                retained_original_images=original_images,
                samples=a.samples,judging_policy=policy,recipes=recipe_hashes,
                geometry_and_uv_unchanged=True,
                qualification='Packed appearance derivation only; reopened geometry/resource checks, render convergence and visual acceptance remain separate gates.')
    receipt_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(dict(scene=str(a.out),receipt=str(receipt_path))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('integration','geometry','source-audit','maps','out'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--samples',type=int,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.samples<=0:p.error('--samples must be positive')
    if a.out.suffix.lower()!='.blend':p.error('--out must be a .blend file')
    main(a)
