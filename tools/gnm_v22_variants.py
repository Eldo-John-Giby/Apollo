"""Derive tissue-aware pigmentation variants while preserving the v22 default bytes."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil

import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt

from gnm_skin_detail import surface_positions
from gnm_run import VARIANTS

PIGMENT={'golden-hazel':(.16,.07,.010),'olive-amber':(.34,.19,-.004),
         'neutral-deep':(2.1,1.4,.025),'cool-grey':(-.035,-.012,.018)}
IRIS={'golden-hazel':(.30,.25,.105),'olive-amber':(.40,.24,.070),
      'neutral-deep':(.19,.095,.045),'cool-grey':(.25,.31,.33)}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    image=cv2.imread(str(path),cv2.IMREAD_UNCHANGED)
    if image is None or image.dtype!=np.uint16 or image.ndim!=3:
        raise ValueError('Expected 16-bit RGB master '+str(path))
    return image[:,:,::-1].astype(np.float32)/65535


def linear(rgb):
    return np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)


def encode(rgb):
    rgb=np.clip(rgb,0,1)
    return np.where(rgb<=.0031308,rgb*12.92,1.055*np.power(rgb,1/2.4)-.055)


def write(path,rgb):
    array=np.rint(np.clip(rgb,0,1)*65535).astype(np.uint16)[:,:,::-1]
    if not cv2.imwrite(str(path),array,[cv2.IMWRITE_PNG_COMPRESSION,6]):
        raise OSError(path)


def build(a):
    if a.out.exists():raise FileExistsError(a.out)
    master=json.loads((a.master/'manifest.json').read_text(encoding='utf-8'))
    root=Path(__file__).resolve().parents[1]
    selection_root=root/'milestones/gnm-portrait-final-2026-11-17'
    selection=json.loads((selection_root/'final-selection.json').read_text(encoding='utf-8'))
    selected=selection_root/selection['scene']
    expected=selection['sha256'][selection['scene']]
    if sha(selected)!=expected or master['source_sha256']!=expected:
        raise ValueError('Selected identity or master provenance mismatch')
    required={f'{role}.{tile}.png' for role in ('color','roughness','specular','normal') for tile in (1001,1002,1004)}
    if not required.issubset(master['maps']):raise ValueError('Incomplete master texture set')
    for name,entry in master['maps'].items():
        if sha(a.master/name)!=entry['sha256']:raise ValueError('Corrupt master '+name)
    source=read(a.master/'color.1001.png');size=source.shape[0]
    if source.shape[1]!=size:raise ValueError('Skin atlas must be square')
    fields=surface_positions(a.template,size,('upper_lip','lower_lip'))
    valid=np.isfinite(fields[:,:,0])
    distance,nearest=distance_transform_edt(~valid,return_indices=True)
    padding=(~valid)&(distance<=master['margin_px'])
    fields[padding]=fields[nearest[0,padding],nearest[1,padding]]
    covered=valid|padding
    flat=fields[covered];positions=flat[:,:3];lip=np.clip(flat[:,3:].max(axis=1),0,1)
    a.out.mkdir(parents=True)
    for variant in VARIANTS:
        target=a.out/variant;target.mkdir()
        for name in master['maps']:shutil.copy2(a.master/name,target/name)
        receipt=copy.deepcopy(master)
        receipt.update(variant=variant,variant_recipe_sha256=sha(__file__),
                       master_manifest_sha256=sha(a.master/'manifest.json'),
                       template_sha256=sha(a.template),
                       pigmentation='Surface-local melanin absorption with separate vermilion and blood-rich tissue response; original photographic variation retained.',
                       qualification='Unreviewed pigmentation derivative; no grade or visual acceptance implied.')
        if variant!='rose-brown':
            skin_delta,lip_delta,blood=PIGMENT[variant]
            result=source.copy();colors=linear(source[covered])
            # Coherent spatial fields cross UV seams and cover ears and neck.
            x,y,z=positions.T
            anterior=np.clip((z-.050)/.035,0,1)
            cheek=np.exp(-((np.abs(x)-.040)/.025)**2-((y+.025)/.035)**2)*anterior
            ear=np.exp(-((np.abs(x)-.073)/.014)**2-((y+.025)/.045)**2)
            regional=1+.055*np.sin(x*57+y*19+z*31)+.08*cheek-.045*ear
            delta=skin_delta*regional*(1-lip)+lip_delta*lip
            absorption=np.array((.54,.94,1.35),dtype=np.float32)
            colors*=np.exp(-delta[:,None]*absorption)
            # Hemoglobin-rich tissue changes separately from melanin, avoiding
            # a global RGB tint over lips, cartilage and thin periocular skin.
            tissue=np.clip(.6*cheek+.75*ear+.8*lip,0,1)
            colors*=np.exp(blood*tissue[:,None]*np.array((.35,-.3,-.4),dtype=np.float32))
            result[covered]=encode(colors)
            write(target/'color.1001.png',result)
            for tile in (1002,1004):
                original=read(a.master/f'color.{tile}.png');eye=linear(original)
                yy,xx=np.mgrid[:eye.shape[0],:eye.shape[1]].astype(np.float32)
                radius=np.hypot((xx+.5)/eye.shape[1]-.5,(yy+.5)/eye.shape[0]-.5)
                mask=np.clip((radius-.04985)/.005,0,1)*np.clip((.184924-radius)/.006,0,1)
                iris=mask>.8
                mean=eye[iris].mean(axis=0)
                desired=linear(np.array(IRIS[variant],dtype=np.float32))
                # Retain the distinct left/right photographic fibers and crypts.
                recolored=np.clip(eye*desired/np.maximum(mean,.0001),0,1)
                eye=eye*(1-mask[:,:,None])+recolored*mask[:,:,None]
                write(target/f'color.{tile}.png',encode(eye))
        for name,entry in receipt['maps'].items():entry['sha256']=sha(target/name)
        if variant=='rose-brown':
            assert all(receipt['maps'][n]['sha256']==master['maps'][n]['sha256'] for n in master['maps'])
            receipt['pigmentation']='Unchanged approved v22; existing CLI identifier retained.'
        (target/'manifest.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
        print('RESULT '+json.dumps(dict(variant=variant,manifest=str(target/'manifest.json'))),flush=True)
    if sha(selected)!=expected:raise ValueError('Selected identity changed during build')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('master','template','out'):p.add_argument('--'+name,type=Path,required=True)
    build(p.parse_args())
