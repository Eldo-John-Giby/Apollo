"""Restore licensed bare-scalp pigment only in the separate native texture output."""
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt

from gnm_groom_finish import scalp_coverage,soften_front_coverage
from gnm_skin_detail import surface_positions
from gnm_v22_variants import read,write,linear,encode,sha

UNCAPPED_SHA256='04f57d1256e6f5239ccd665dcaab09465c2f38fce3988628cc6b36cd3dd8d2b8'
RECIPES={name:sha(Path(__file__).with_name(name)) for name in
         ('gnm_v22_scalp.py','gnm_groom_finish.py','gnm_skin_detail.py','gnm_v22_variants.py')}


@lru_cache(maxsize=1)
def coverage(template,size,digest):
    if sha(template)!=digest:raise ValueError('Template changed before scalp rasterization')
    fields=surface_positions(Path(template),size,('ears',))
    valid=np.isfinite(fields[:,:,0]);positions=fields[valid,:3];x,y,z=positions.T
    ear=np.clip(fields[valid,3],0,1)
    density,old,_=scalp_coverage(positions)
    taper,_=soften_front_coverage(positions,density,np.zeros(len(positions)))
    mask=np.zeros(valid.shape,dtype=np.float32)
    mask[valid]=np.clip(np.maximum.reduce([density,old,taper])*(1-ear)*4,0,1)
    distance,nearest=distance_transform_edt(~valid,return_indices=True)
    padding=(~valid)&(distance<=32)
    mask[padding]=mask[nearest[0,padding],nearest[1,padding]]
    donors=np.zeros(valid.shape,dtype=bool)
    donors[valid]=(abs(x)<.035)&(y>.035)&(y<.055)&(z>.003)
    if donors.sum()<1000:raise ValueError('Insufficient forehead calibration skin')
    if sha(template)!=digest:raise ValueError('Template changed during scalp rasterization')
    return mask,donors


def calibrated_restore(color,base,bare,mask,donors):
    if color.shape!=base.shape or bare.shape!=base.shape or mask.shape!=base.shape[:2] or donors.shape!=mask.shape:
        raise ValueError('Scalp restoration dimensions differ')
    if not donors.any():raise ValueError('No forehead calibration skin')
    gain=np.median(linear(base[donors])/np.maximum(linear(bare[donors]),1e-4),axis=0)
    if not np.isfinite(gain).all() or np.any(gain<=0) or np.any(gain>=8):
        raise ValueError('Invalid forehead calibration gain')
    active=mask>0;result=color.copy()
    result[active]=encode(linear(color[active])*(1-mask[active,None])+linear(bare[active])*gain*mask[active,None])
    return result,gain


def restore(directory,template,uncapped):
    directory=Path(directory);template=Path(template);uncapped=Path(uncapped)
    if sha(uncapped)!=UNCAPPED_SHA256:raise ValueError('Unverified uncapped scalp source')
    if any(sha(Path(__file__).with_name(name))!=digest for name,digest in RECIPES.items()):
        raise ValueError('Scalp recipe changed after loading')
    recipe_hash=sha(__file__);template_hash=sha(template)
    color=read(directory/'texture-only-color.1001.png');base=read(directory/'color.1001.png')
    raw=cv2.imread(str(uncapped),cv2.IMREAD_UNCHANGED)
    if raw is None or raw.dtype!=np.uint8 or raw.shape!=color.shape:
        raise ValueError('Expected the pinned native-resolution RGB scalp atlas')
    bare=raw[:,:,::-1].astype(np.float32)/255
    mask,donors=coverage(str(template.resolve()),color.shape[0],template_hash)
    result,gain=calibrated_restore(color,base,bare,mask,donors)
    write(directory/'texture-only-color.1001.png',result)
    if (sha(uncapped)!=UNCAPPED_SHA256 or sha(template)!=template_hash or sha(__file__)!=recipe_hash
            or any(sha(Path(__file__).with_name(name))!=digest for name,digest in RECIPES.items())):
        raise ValueError('Scalp restoration input or recipe changed')
    return dict(source_atlas_sha256=UNCAPPED_SHA256,template_sha256=template_hash,
                recipe_sha256=recipe_hash,dependencies=RECIPES,linear_forehead_gain=gain.tolist(),affected_texels=int((mask>0).sum()),
                method='Restore verified uncapped photographic scalp calibrated to this variant forehead; retain all full-character maps.',
                qualification='Native texture derivation; five-set visual acceptance remains pending.')
