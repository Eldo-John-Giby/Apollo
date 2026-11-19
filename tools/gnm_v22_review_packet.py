"""Build a randomized still/packed-playback packet from an explicit hashed source list."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import shutil
import sys
from zipfile import ZipFile,ZIP_DEFLATED

from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from apollo_core.png import canonicalize
from gnm_v22_review_gate import VARIANTS,MODES,DIRECTIONS,response_template,sha


def authenticated(root,entry,suffix):
    path=(root/entry['file']).resolve()
    if path.suffix.lower()!=suffix or not path.is_file() or sha(path)!=entry['sha256']:
        raise ValueError('Missing or changed review input: '+entry['file'])
    return path


def validate(spec):
    appearance=spec['appearance'];motion=spec['motion'];directions=spec['directions']
    for entry in appearance+motion:
        if type(entry.get('candidate')) is not bool:raise ValueError('Explicit candidate flag required')
    coverage={(e.get('variant'),e.get('output')) for e in appearance if e['candidate']}
    if coverage!={(v,o) for v in VARIANTS for o in ('full','texture_only')}:
        raise ValueError('Need all five full and texture-only variants')
    if not {'rc5','v22'}.issubset({e.get('reference') for e in appearance if not e['candidate']}):
        raise ValueError('Need rc5 and v22 reference cases')
    if {e.get('mode') for e in motion if e['candidate']}!=set(MODES):
        raise ValueError('Need all three packed motion modes')
    if any(e.get('mode') not in MODES for e in motion):raise ValueError('Unknown motion mode')
    if set(e['expected'] for e in directions)!=set(DIRECTIONS):
        raise ValueError('Need all four cardinal directions')
    if any(not e.get('images') for e in appearance):raise ValueError('Appearance images required')


def board(paths,out,case):
    sheet=Image.new('RGB',(1280,668*((len(paths)+1)//2)),'#20262b')
    draw=ImageDraw.Draw(sheet)
    for index,path in enumerate(paths):
        with Image.open(path) as opened:
            image=opened.convert('RGB');image.thumbnail((640,640),Image.Resampling.LANCZOS)
            x=(index%2)*640;y=(index//2)*668
            sheet.paste(image,(x+(640-image.width)//2,y+28+(640-image.height)//2))
            draw.text((x+12,y+8),f'{case} / view {index+1}',fill='white')
    sheet.save(out);canonicalize(out)


def main(a):
    if a.out.exists():raise FileExistsError(a.out)
    spec_hash=sha(a.spec);spec=json.loads(a.spec.read_text(encoding='utf-8'));validate(spec)
    root=a.spec.resolve().parent;inputs=[]
    def image(entry):
        path=authenticated(root,entry,'.png');inputs.append((path,entry['sha256']));return path
    prepared={}
    for group in ('appearance','directions','motion'):
        prepared[group]=[]
        for entry in spec[group]:
            if group=='appearance':payload=[image(e) for e in entry['images']]
            elif group=='directions':payload=[image(entry['neutral']),image(entry['judgment'])]
            else:
                path=authenticated(root,entry['scene'],'.blend')
                inputs.append((path,entry['scene']['sha256']));payload=[path]
            prepared[group].append((entry,payload))
    # Bind the reviewed candidate to the complete explicit list, including
    # scenes, views and references; this is not a submission acceptance receipt.
    candidate_hash=hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    a.out.mkdir(parents=True);reviewer=a.out/'reviewer';reviewer.mkdir()
    key=dict(candidate_sha256=candidate_hash,source_spec_sha256=spec_hash,
             directions={},appearance={},motion={},packet_files={})
    rng=random.Random(a.seed)
    for group,prefix in (('appearance','A'),('directions','C'),('motion','M')):
        entries=prepared[group];rng.shuffle(entries)
        for index,(entry,paths) in enumerate(entries,1):
            case=f'{prefix}{index:02d}'
            if group=='motion':
                output=reviewer/f'{case}.blend';shutil.copyfile(paths[0],output)
                key[group][case]={k:entry[k] for k in ('candidate','mode')}
            else:
                output=reviewer/f'{case}.png';board(paths,output,case)
                for view,path in enumerate(paths,1):
                    detail=reviewer/f'{case}-view-{view}.png'
                    with Image.open(path) as opened:opened.convert('RGB').save(detail)
                    canonicalize(detail);key['packet_files'][detail.name]=sha(detail)
                if group=='directions':key[group][case]=entry['expected']
                else:key[group][case]={k:entry[k] for k in ('candidate','variant','output','reference') if k in entry}
            key['packet_files'][output.name]=sha(output)
    (reviewer/'REVIEW_INSTRUCTIONS.md').write_text(
        'Review independently before discussing results or consulting the assessor key.\n\n'
        'For C cases the left image is neutral and the right image is the judgment. '
        'Answer left, right, up, down or unclear in viewer-screen space.\n\n'
        'Rate every A case from 1 to 5 for skin, eyes, lips, ears, brows/lashes and '
        'overall realism. Inspect at full size as well as the sheet.\n\n'
        'Open each M scene locally in pinned Blender 4.5.15 LTS and play frames 1–192 '
        'at 24 fps. Rate motion naturalness from 1 to 5 and inspect blink, reopening, '
        'gaze holds, lash roots and tear corners. Packed scene internals may reveal '
        'the mode; do not inspect names or custom properties before the first pass. '
        'Live viewport playback is for motion review, not final skin/eye rendering.\n\n'
        'Record severe defects with case, category and notes; use [] only if none. '
        'Complete the independent-first-pass attestation explicitly. Missing ratings '
        'and blank defect reviews cannot pass. Return responses.json.\n',encoding='utf-8')
    key_path=a.out/'assessor-key.json';key_path.write_text(json.dumps(key,indent=2)+'\n',encoding='utf-8')
    responses=response_template(key,sha(key_path))
    (reviewer/'responses.json').write_text(json.dumps(responses,indent=2)+'\n',encoding='utf-8')
    if sha(a.spec)!=spec_hash or any(sha(path)!=digest for path,digest in inputs):
        raise ValueError('Review sources changed during packaging')
    archive=a.out/'apollo-v22-independent-review.zip'
    with ZipFile(archive,'x',compression=ZIP_DEFLATED) as package:
        for path in sorted(reviewer.iterdir()):package.write(path,path.name)
    receipt=dict(candidate_sha256=candidate_hash,key_sha256=sha(key_path),archive_sha256=sha(archive),
                 source_spec_sha256=spec_hash,recipe_sha256=sha(__file__),seed=a.seed,
                 qualification='Hashed randomized review packet only; no human ratings, identity approval or release qualification inferred.')
    (a.out/'packet-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+str(archive),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seed',type=int,default=20261119)
    main(p.parse_args())
