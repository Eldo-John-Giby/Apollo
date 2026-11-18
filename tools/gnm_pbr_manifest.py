"""Validate portable PBR texture manifests without importing Blender."""
import hashlib
import json
from pathlib import Path
import re

ROLES=('color','roughness','specular','normal')
TILES=(1001,1002,1004)


def is_pbr(maps):
    maps=Path(maps)
    if (maps/'normal.1001.png').exists():return True
    manifest=maps/'manifest.json'
    if manifest.is_file():
        receipt=json.loads(manifest.read_text(encoding='utf-8'))
        return isinstance(receipt,dict) and ('corneas' in receipt or 'material_settings' in receipt)
    return False


def load_manifest(maps):
    maps=Path(maps)
    receipt=json.loads((maps/'manifest.json').read_text(encoding='utf-8'))
    required={f'{role}.{tile}.png' for role in ROLES for tile in TILES}
    if not required.issubset(receipt['maps']):raise ValueError('Incomplete PBR manifest')
    for name,entry in receipt['maps'].items():
        if not re.fullmatch(r'[a-z0-9][a-z0-9._-]*\.png',name):
            raise ValueError('Invalid PBR map filename')
        path=maps/name
        if not path.is_file():raise ValueError('Missing PBR map '+name)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('Texture checksum mismatch '+name)
    for role,name in receipt.get('texture_only',{}).items():
        if role not in ('overlay','color','roughness') or name not in receipt['maps']:
            raise ValueError('Invalid texture-only map binding')
    if not all(str(tile) in receipt['material_defaults'] and str(tile) in receipt['material_settings'] for tile in TILES):
        raise ValueError('Incomplete PBR material settings')
    if set(receipt['corneas'])!={'2','4'}:raise ValueError('Incomplete native corneal recipe')
    return receipt


def files(maps):
    maps=Path(maps);receipt=load_manifest(maps)
    paths={name:maps/name for name in receipt['maps']}
    paths['manifest']=maps/'manifest.json'
    return paths
