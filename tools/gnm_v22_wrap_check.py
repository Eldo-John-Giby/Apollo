"""Authenticate all five fresh-target wrap trials and compare both UV layouts."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from gnm_pbr_manifest import load_manifest,ROLES,TILES
from gnm_run import VARIANTS
from gnm_v22_variants import sha,verify_selected

VIEWS={'front':(False,False),'angle':(True,False),'oblique':(False,True)}
IMAGE='fresh-texture-only.png'
COMPARABLE=('source_sha256','maps_manifest_sha256','target_sha256','template_sha256',
            'recipe_sha256','angle','oblique','fresh_only','lights','device','camera_matrix',
            'camera_lens_mm','view_transform','exposure','seed','adaptive_sampling',
            'depth_of_field','motion_blur','dither_intensity','judging_policy','samples','size',
            'blender','blender_build')


def case(folder,expected):
    receipt=json.loads((folder/'comparison.json').read_text(encoding='utf-8'))
    if any(receipt.get(key)!=value for key,value in expected.items()):
        raise ValueError('Stale or mismatched wrap receipt: '+str(folder))
    binding=receipt['fresh_binding']
    if (binding['manifest_sha256']!=expected['maps_manifest_sha256'] or
            binding['layout']!=expected['layout'] or binding['full_character'] is not False):
        raise ValueError('Incorrect fresh-target binding: '+str(folder))
    path=folder/IMAGE
    if receipt['images'].get(IMAGE)!=sha(path):raise ValueError('Stale wrap image: '+str(folder))
    with Image.open(path) as opened:
        if opened.size!=(receipt['size'],receipt['size']):raise ValueError('Wrap dimensions differ')
        pixels=np.asarray(opened.convert('RGB'))
    return receipt,pixels


def compare(left,right):
    a,first=left;b,second=right
    if any(key not in a or key not in b for key in COMPARABLE):
        raise ValueError('Missing UV comparison settings')
    if any(a[key]!=b[key] for key in COMPARABLE):
        raise ValueError('UV comparison settings differ')
    delta=np.abs(first.astype(np.int16)-second.astype(np.int16))
    result=dict(max_absolute_rgb=int(delta.max()),p95_absolute_rgb=float(np.percentile(delta,95)),
                changed_pixels=int(np.any(delta,axis=2).sum()))
    if result['max_absolute_rgb']>1:raise ValueError('UV layouts differ by more than one RGB level')
    return result


def main(a):
    if a.out.exists():raise FileExistsError(a.out)
    root=Path(__file__).resolve().parents[1]
    recipes={name:sha(root/'tools'/name) for name in ('gnm_v22_wrap_trial.py',
        'gnm_v22_materials.py','gnm_pbr_manifest.py','gnm_v22_render_policy.py',
        'gnm_v22_audit.py','gnm_portrait_refine.py')}
    recipes['png.py']=sha(root/'apollo_core/png.py')
    target=sha(a.target);template=sha(a.template);results={};sources={};view_settings={}
    for variant in VARIANTS:
        maps=a.maps/variant;manifest=load_manifest(maps)
        selected=verify_selected(manifest['source_sha256'])
        manifest_hash=sha(maps/'manifest.json');sources[variant]=manifest_hash
        active={}
        for role in ROLES:
            for tile in TILES:
                name=manifest.get('texture_only',{}).get(role,f'{role}.{tile}.png') if tile==1001 else f'{role}.{tile}.png'
                active[name]=manifest['maps'][name]['sha256']
        for view,(angle,oblique) in VIEWS.items():
            pair=[];cases={}
            for layout in ('udim','legacy'):
                folder=a.source/variant/layout/view
                expected=dict(source_sha256=manifest['source_sha256'],maps_manifest_sha256=manifest_hash,
                    target_sha256=target,template_sha256=template,recipe_sha256=recipes,
                    layout=layout,angle=angle,oblique=oblique,fresh_only=True,
                    device='CPU',samples=a.samples,size=a.size)
                receipt,pixels=case(folder,expected)
                if receipt['fresh_binding']['active_maps']!=active:
                    raise ValueError('Fresh wrap used different map payloads')
                pair.append((receipt,pixels));cases[layout]=sha(folder/'comparison.json')
            results[f'{variant}/{view}']=dict(receipts=cases,**compare(*pair))
            settings={key:pair[0][0][key] for key in COMPARABLE if key!='maps_manifest_sha256'}
            if view in view_settings and settings!=view_settings[view]:
                raise ValueError('Judging conditions differ across variants')
            view_settings[view]=settings
        load_manifest(maps)
        if sha(maps/'manifest.json')!=manifest_hash or sha(selected)!=manifest['source_sha256']:
            raise ValueError('Wrap inputs changed during checking')
    if (sha(a.target)!=target or sha(a.template)!=template or
            any(sha(root/('apollo_core' if name=='png.py' else 'tools')/name)!=digest for name,digest in recipes.items())):
        raise ValueError('Wrap source or worker changed during checking')
    report=dict(status='passed_five_variant_three_view_uv_comparisons',cases=results,
                manifests=sources,target_sha256=target,template_sha256=template,
                recipe_sha256=sha(__file__),render_recipes=recipes,
                qualification='Thirty authenticated fresh-wrap renders and layout agreement only; visual acceptance and final render-detail qualification remain separate.')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+str(a.out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','maps','target','template','out'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--samples',type=int,required=True);p.add_argument('--size',type=int,required=True)
    main(p.parse_args())
