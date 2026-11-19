"""Create separate flat groom pigment maps; retain the full v22 maps unchanged."""
import argparse
import copy
import json
from pathlib import Path
import shutil

import cv2
import numpy as np

from gnm_v22_variants import read,write,linear,encode,sha,verify_selected
from gnm_pbr_manifest import load_manifest


def flatten(directory,recipe):
    directory=Path(directory)
    color=read(directory/'color.1001.png')
    source=cv2.imread(str(directory/recipe['overlay']),cv2.IMREAD_UNCHANGED)
    if source is None or source.shape[2]!=4 or source.dtype!=np.uint16:
        raise ValueError('Expected a 16-bit RGBA authored pigment overlay')
    alpha=source[:,:,3].astype(np.float32)/65535
    pigment=linear(source[:,:,[2,1,0]].astype(np.float32)/65535)
    if alpha.shape!=color.shape[:2]:
        size=(color.shape[1],color.shape[0])
        premultiplied=cv2.resize(pigment*alpha[:,:,None],size,interpolation=cv2.INTER_AREA)
        alpha=cv2.resize(alpha,size,interpolation=cv2.INTER_AREA)
        pigment=premultiplied/np.maximum(alpha[:,:,None],1e-8)
    result=encode(linear(color)*(1-alpha[:,:,None])+pigment*alpha[:,:,None])
    write(directory/recipe['color'],result)
    roughness=read(directory/'roughness.1001.png')
    # Data maps use direct values, not the sRGB conversion above.
    roughness=roughness*(1-alpha[:,:,None])+.65*alpha[:,:,None]
    write(directory/recipe['roughness'],roughness)


def main(a):
    if a.out.exists():raise FileExistsError(a.out)
    master=load_manifest(a.master)
    selected=verify_selected(master['source_sha256'])
    projection=json.loads(a.overlay.with_suffix('.json').read_text(encoding='utf-8'))
    if projection['source_sha256']!=master['source_sha256'] or sha(a.overlay)!=projection['overlay_sha256']:
        raise ValueError('Overlay and source identity do not match')
    if getattr(a,'uncapped',None) and projection.get('brows_only') is not True:
        raise ValueError('Bare-scalp restoration requires a brow-only overlay')
    a.out.mkdir(parents=True)
    for name in master['maps']:shutil.copy2(a.master/name,a.out/name)
    recipe=dict(overlay='groom-overlay.1001.png',color='texture-only-color.1001.png',
                roughness='texture-only-roughness.1001.png')
    shutil.copy2(a.overlay,a.out/recipe['overlay'])
    flatten(a.out,recipe)
    receipt=copy.deepcopy(master)
    if getattr(a,'uncapped',None):
        from gnm_v22_scalp import restore
        receipt['scalp_restoration']=restore(a.out,a.template,a.uncapped)
    receipt.update(texture_only=recipe,texture_only_recipe_sha256=sha(__file__),
                   overlay_projection=projection,
                   qualification='Unreviewed texture-only groom projection; full-character base maps are unchanged.')
    for role in ('overlay','color','roughness'):
        path=a.out/recipe[role]
        receipt['maps'][path.name]=dict(sha256=sha(path),
                                       colorspace='Non-Color' if role=='roughness' else 'sRGB')
    for name in master['maps']:
        if sha(a.out/name)!=master['maps'][name]['sha256']:
            raise ValueError('Full-character map changed '+name)
    (a.out/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    if sha(selected)!=master['source_sha256']:raise ValueError('Selected identity changed')
    load_manifest(a.out)
    print('RESULT '+json.dumps(dict(manifest=str(a.out/'manifest.json'),full_maps_unchanged=True)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('master','overlay','out'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--uncapped',type=Path);p.add_argument('--template',type=Path)
    a=p.parse_args()
    if (a.uncapped is None)!=(a.template is None):p.error('--uncapped and --template are required together')
    main(a)
