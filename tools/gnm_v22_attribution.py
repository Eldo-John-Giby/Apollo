"""Retain pinned attribution records and bind them to five texture manifests."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import shutil

from gnm_run import VARIANTS
from gnm_pbr_manifest import load_manifest

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(a):
    if a.out.exists():raise FileExistsError(a.out)
    provenance=ROOT/'assets/v22-provenance.json';inventory_hash=sha(provenance)
    inventory=json.loads(provenance.read_text(encoding='utf-8'))
    sources={}
    for name,digest in inventory['source_records'].items():
        relative=PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or '\\' in name:
            raise ValueError('Unsafe provenance record name')
        path=(ROOT/name).resolve()
        if not path.is_relative_to(ROOT.resolve()) or sha(path)!=digest:
            raise ValueError('Source record checksum mismatch: '+name)
        sources[name]=path
    manifests={}
    for variant in VARIANTS:
        manifest=load_manifest(a.textures/variant)
        if manifest['source_sha256']!=inventory['selected_sha256']:
            raise ValueError('Textures derive from a different selected character')
        manifests[variant]=sha(a.textures/variant/'manifest.json')
    a.out.mkdir(parents=True)
    files={}
    for name,path in {**sources,'assets/v22-provenance.json':provenance}.items():
        output=a.out/name;output.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,output);files[name]=sha(output)
        if files[name]!=sha(path):raise ValueError('Attribution copy changed')
    shutil.copyfile(ROOT/'assets/gnm/LICENSE.txt',a.out/'Google-GNM-LICENSE.txt')
    files['Google-GNM-LICENSE.txt']=sha(a.out/'Google-GNM-LICENSE.txt')
    text=(
        '# Apollo v22 asset attribution\n\n'
        'This record accompanies the listed texture-manifest hashes. It does not '
        'claim final visual acceptance or completion of the submission archive.\n\n'
        'Geometry uses pinned public Google GNM Head v3. The complete upstream '
        '[license and bundled notices](Google-GNM-LICENSE.txt) are retained from '
        'the exact Git revision in [its source record](assets/gnm/source.json). '
        'Apollo adds the documented v22 identity layer and authored groom while '
        'preserving native topology, vertex order and both UV layouts.\n\n'
        'Skin incorporates the Lee Perry-Smith / Infinite-Realities scan, converted '
        'by Morgan McGuire and Guedis Cardenas, with Unity adjustments by Keijiro '
        'Takahashi. See the retained [attribution](assets/gnm-scan/ATTRIBUTION.md), '
        '[source pin](assets/gnm-scan/source.json) and '
        '[CC-BY-3.0 license text](assets/gnm-scan/LICENSE.txt). Apollo transfers '
        'photographic pigment/relief to GNM UVs, adds authored complexion, '
        'roughness, masks, fibers and pigmentation variants, and uses documented '
        'CC0 MakeHuman fallback regions. These modifications are not endorsed '
        'by the source authors.\n\n'
        'MakeHuman fallback records are retained in '
        '[character attribution](assets/ATTRIBUTION.md) and '
        '[skin attribution](assets/photorealism-v2/ATTRIBUTION.md). Historical '
        'fallback meshes are source provenance, not the delivered GNM topology.\n\n'
        'Eye pigment incorporates Kookaaa’s CC0 photograph, “Close up shot of the '
        'human eye, 9 August 2024.” See [attribution](assets/gnm-eye-photo/ATTRIBUTION.md) '
        'and [source record](assets/gnm-eye-photo/source.json). Apollo reconstructs '
        'unobstructed iris sectors, excludes photographed flash/pupil, and authors '
        'additional pigmentation, relief and scleral detail.\n\n'
        +inventory['delivery']['detail_statement']+'\n\n'
        'The native texture-only scalp restoration uses the recorded uncapped '
        'derivative calibrated to each variant; projected brow pigment is authored. '
        'The full character retains its separate groom and original full-character '
        'map bindings.\n\n'
        '## Texture manifests\n\nVariant | SHA-256\n--- | ---\n'
        +''.join(f'{variant} | `{digest}`\n' for variant,digest in manifests.items()))
    (a.out/'ATTRIBUTION.md').write_text(text,encoding='utf-8')
    files['ATTRIBUTION.md']=sha(a.out/'ATTRIBUTION.md')
    if sha(provenance)!=inventory_hash or any(sha(path)!=inventory['source_records'][name] for name,path in sources.items()):
        raise ValueError('Provenance changed while collecting attribution')
    for variant,digest in manifests.items():
        load_manifest(a.textures/variant)
        if sha(a.textures/variant/'manifest.json')!=digest:raise ValueError('Texture manifest changed')
    report=dict(provenance_sha256=inventory_hash,selected_sha256=inventory['selected_sha256'],
                texture_manifests=manifests,files=files,recipe_sha256=sha(__file__),
                qualification='Pinned attribution/source retention and manifest linkage; final archive inclusion remains a separate gate.')
    (a.out/'attribution-receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+str(a.out),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--textures',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    main(p.parse_args())
