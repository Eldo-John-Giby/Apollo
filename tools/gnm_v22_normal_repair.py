"""Derive an audited map set with isolated inverted tangent-normal texels repaired."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil

import cv2
import numpy as np
from gnm_pbr_manifest import load_manifest

MAX_PIXELS=64
MAX_FRACTION=1e-5


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def repair(image):
    if image.dtype!=np.uint16 or image.ndim!=3 or image.shape[2]!=3:
        raise ValueError('Expected decoded 16-bit RGB tangent normals')
    bad=image[:,:,2]<32768
    count=int(bad.sum())
    if count>MAX_PIXELS or count/bad.size>MAX_FRACTION:
        raise ValueError('Widespread inverted normals require source correction, not isolated repair')
    result=image.copy();changes=[]
    for y,x in zip(*np.where(bad)):
        y0,y1=max(0,y-2),min(image.shape[0],y+3)
        x0,x1=max(0,x-2),min(image.shape[1],x+3)
        neighbors=image[y0:y1,x0:x1][~bad[y0:y1,x0:x1]].astype(np.float64)*(2/65535)-1
        if len(neighbors)<5:raise ValueError('Insufficient valid local normal support')
        vector=np.median(neighbors,axis=0)
        length=np.linalg.norm(vector)
        if length<.25 or vector[2]<=0:raise ValueError('Ambiguous local normal neighborhood')
        vector/=length
        result[y,x]=np.rint(np.clip((vector+1)/2,0,1)*65535).astype(np.uint16)
        changes.append(dict(pixel=[int(x),int(y)],before_rgb=image[y,x].tolist(),
                            after_rgb=result[y,x].tolist(),valid_neighbors=len(neighbors)))
    np.testing.assert_array_equal(result[~bad],image[~bad])
    if np.any(result[:,:,2]<32768):raise ValueError('Repair left inverted normals')
    return result,changes


def main(a):
    if a.out.exists():raise FileExistsError(a.out)
    receipt=load_manifest(a.master);master_hash=sha(a.master/'manifest.json')
    source_root=Path(__file__).resolve().parents[1]/'milestones/gnm-portrait-final-2026-11-17'
    selection=json.loads((source_root/'final-selection.json').read_text(encoding='utf-8'))
    selected=source_root/selection['scene'];expected=selection['sha256'][selection['scene']]
    if receipt['source_sha256']!=expected or sha(selected)!=expected:
        raise ValueError('Selected v22 source differs')
    recipe_hash=sha(__file__)
    name='normal.1001.png';raw=cv2.imread(str(a.master/name),cv2.IMREAD_UNCHANGED)
    if raw is None:raise ValueError('Cannot decode skin normal map')
    fixed,changes=repair(raw[:,:,::-1])
    a.out.mkdir(parents=True)
    for filename in receipt['maps']:shutil.copy2(a.master/filename,a.out/filename)
    if not cv2.imwrite(str(a.out/name),fixed[:,:,::-1],[cv2.IMWRITE_PNG_COMPRESSION,6]):
        raise OSError('Cannot write repaired skin normal map')
    derived=copy.deepcopy(receipt)
    derived['maps'][name]['sha256']=sha(a.out/name)
    derived['maps'][name].pop('min',None);derived['maps'][name].pop('max',None)
    derived['normal_repair']=dict(master_manifest_sha256=master_hash,
        original_map_sha256=receipt['maps'][name]['sha256'],recipe_sha256=recipe_hash,
        algorithm='5x5 valid-neighbor component median, unit normalization; only negative tangent-Z texels changed',
        maximum_pixels=MAX_PIXELS,maximum_fraction=MAX_FRACTION,
        changed_pixels=len(changes),changed_fraction=len(changes)/(fixed.shape[0]*fixed.shape[1]),changes=changes)
    derived['qualification']='Isolated normal artifact repair; decoded checks and matched appearance review pending.'
    load_manifest(a.master)
    if sha(a.master/'manifest.json')!=master_hash or sha(selected)!=expected or sha(__file__)!=recipe_hash:
        raise ValueError('Source or recipe changed during repair')
    for filename in receipt['maps']:
        if filename!=name and sha(a.out/filename)!=receipt['maps'][filename]['sha256']:
            raise ValueError('Unrelated map changed: '+filename)
    (a.out/'manifest.json').write_text(json.dumps(derived,indent=2)+'\n',encoding='utf-8')
    load_manifest(a.out)
    print('RESULT '+json.dumps(dict(manifest=str(a.out/'manifest.json'),changed_pixels=len(changes))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--master',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    main(p.parse_args())
