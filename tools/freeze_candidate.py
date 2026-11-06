"""Create an evidence-bound development archive, independent of team registration."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile
from make_bundle import qualified_candidate,ROOT
from validate_metadata import validate_artifacts


def freeze(folder,output):
    folder,required=qualified_candidate(folder)
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        temporary=Path(temporary);stage=temporary/'apollo-development';stage.mkdir()
        for name in required:shutil.copy2(folder/name,stage/name)
        for name in ['sweep.gif','comparison.png','performance_baseline.json']:
            if (folder/name).is_file():shutil.copy2(folder/name,stage/name)
        shutil.copytree(folder/'renders',stage/'renders')
        (stage/'wrapper').mkdir();shutil.copy2(ROOT/'wrapper/eyes.py',stage/'wrapper/eyes.py')
        with (stage/'README.md').open('r',encoding='utf-8') as f:readme=f.read()
        (stage/'README.md').write_text('# Apollo development freeze\n\nLocal development milestone; not an organizer submission.\n\n'+readme,encoding='utf-8')
        manifest={str(p.relative_to(stage)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in stage.rglob('*') if p.is_file()}
        (stage/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        candidate=temporary/'freeze.zip'
        with zipfile.ZipFile(candidate,'w',zipfile.ZIP_DEFLATED) as archive:
            for p in sorted(stage.rglob('*')):
                if p.is_file():archive.write(p,p.relative_to(temporary))
        with zipfile.ZipFile(candidate) as archive:
            assert archive.testzip() is None,'ZIP integrity failure'
            extracted=temporary/'extracted';archive.extractall(extracted)
            root=extracted/'apollo-development'
            validate_artifacts(root)
            assert all(hashlib.sha256((root/name).read_bytes()).hexdigest()==value for name,value in manifest.items()),'Extraction hashes differ'
        candidate.replace(output)
    return output


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();print(freeze(args.folder,args.out))
