"""Independently inspect decoded delivery maps; visual wrapping remains a separate gate."""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

from gnm_pbr_manifest import load_manifest, ROLES, TILES


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_map(path, size, role):
    header=path.read_bytes()[:29]
    if header[:8]!=b'\x89PNG\r\n\x1a\n' or header[24]!=16 or header[25]!=2:
        raise ValueError('Expected 16-bit RGB PNG: '+path.name)
    image=cv2.imread(str(path),cv2.IMREAD_UNCHANGED)
    if image is None or image.dtype!=np.uint16 or image.shape!=(size,size,3):
        raise ValueError('Incorrect decoded map dimensions or precision: '+path.name)
    result=dict(size=[size,size],bit_depth=16,min=int(image.min()),max=int(image.max()))
    if role=='normal':
        # Uncovered UV pixels are black and do not represent tangent vectors.
        covered=np.any(image!=0,axis=2)
        if not covered.any():raise ValueError('Empty normal map: '+path.name)
        vectors=image[covered,::-1].astype(np.float32)*(2/65535)-1
        error=np.abs(np.linalg.norm(vectors,axis=1)-1)
        result.update(covered_pixels=int(covered.sum()),
                      unit_length_error_p95=float(np.percentile(error,95)),
                      unit_length_error_max=float(error.max()),
                      negative_z_pixels=int(np.count_nonzero(vectors[:,2]<0)))
        if result['negative_z_pixels'] or result['unit_length_error_p95']>.002:
            raise ValueError('Invalid tangent normal vectors: '+path.name)
    return result


def main(a):
    receipt=load_manifest(a.maps)
    master_hash=sha(a.maps/'manifest.json')
    root=Path(__file__).resolve().parents[1]/'milestones/gnm-portrait-final-2026-11-17'
    selection=json.loads((root/'final-selection.json').read_text(encoding='utf-8'))
    selected=root/selection['scene']
    expected=selection['sha256'][selection['scene']]
    if receipt['source_sha256']!=expected or sha(selected)!=expected:
        raise ValueError('Selected identity checksum mismatch')
    report=dict(manifest_sha256=master_hash,source_sha256=expected,recipe_sha256=sha(__file__),maps={})
    for role in ROLES:
        for tile in TILES:
            name=f'{role}.{tile}.png';entry=receipt['maps'][name]
            size=a.skin_size if tile==1001 else a.eye_size
            if entry['size']!=[size,size] or entry['colorspace']!=('sRGB' if role=='color' else 'Non-Color'):
                raise ValueError('Incorrect manifest map dimensions or color space: '+name)
            report['maps'][name]=dict(sha256=entry['sha256'],**check_map(a.maps/name,size,role))
    # Recheck payloads after decoding so concurrent changes cannot qualify.
    load_manifest(a.maps)
    if sha(a.maps/'manifest.json')!=master_hash or sha(selected)!=expected:
        raise ValueError('Inputs changed during map inspection')
    report.update(status='passed_map_encoding_and_normal_checks',
                  qualification='Map integrity and encoding only; fresh wrapping, seams, detail retention and visual acceptance remain separate gates.')
    if a.out.exists():raise FileExistsError(a.out)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+str(a.out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--maps',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--skin-size',type=int,default=4096);p.add_argument('--eye-size',type=int,default=2048)
    main(p.parse_args())
