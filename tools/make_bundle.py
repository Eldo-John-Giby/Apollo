"""Package a production candidate; fixture scenes are never eligible."""
import argparse
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile
from validate_metadata import validate_artifacts
from verify import hashes
ROOT = Path(__file__).resolve().parents[1]


def bundle(folder, team):
    if not re.fullmatch(r'[A-Za-z0-9]+_[A-Za-z0-9_]+',team) or any(t in team.lower() for t in ['teamname','yourteam','placeholder']):
        raise ValueError('Supply the registered CollegeName_TeamName')
    folder = Path(folder).resolve()
    records = validate_artifacts(folder)
    if any(r.get('extra',{}).get('fixture',True) for r in records):
        raise ValueError('Development or unclassified fixtures cannot be submitted')
    report = json.loads((folder/'verification_report.json').read_text())
    if report.get('production') is not True or report.get('passed') is not True:
        raise ValueError('Production verification must pass before packaging')
    if any(report.get('checks',{}).get(f'V{i}',{}).get('status')!='PASS' for i in range(1,18)):
        raise ValueError('All seventeen verification checks must pass')
    if report.get('artifact_hashes') != hashes(folder):
        raise ValueError('Artifacts changed since verification; rerun verify')
    required = ['scene.blend','metadata.json','contact_sheet.png','README.md','ATTRIBUTION.md','verification_report.json','verification_report.md']
    for name in required:
        if not (folder/name).is_file(): raise ValueError(f'Missing {name}')
    output = folder.parent/(team+'.zip')
    with tempfile.TemporaryDirectory(dir=folder.parent) as temporary:
        stage = Path(temporary)/team
        stage.mkdir()
        for name in required: shutil.copy2(folder/name,stage/name)
        shutil.copytree(folder/'renders',stage/'renders')
        (stage/'wrapper').mkdir()
        shutil.copy2(ROOT/'wrapper/eyes.py',stage/'wrapper/eyes.py')
        archive = Path(temporary)/'candidate.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for path in sorted(stage.rglob('*')):
                if path.is_file(): z.write(path,path.relative_to(stage.parent))
        if archive.stat().st_size >= 60*1024*1024: raise ValueError('Bundle exceeds 60 MiB budget')
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None: raise ValueError('ZIP integrity failure')
            extracted = Path(temporary)/'extracted'
            z.extractall(extracted)
            validate_artifacts(extracted/team)
        archive.replace(output)
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder',type=Path)
    parser.add_argument('--team',required=True)
    args = parser.parse_args()
    print(bundle(args.folder,args.team))
