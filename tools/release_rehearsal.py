"""Reproduce the actual archive and the final dataset checkpoint in isolation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile
ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(blender,archive,dataset,scene,output):
    archive=Path(archive).resolve();dataset=Path(dataset).resolve();scene=Path(scene).resolve()
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    before={p.name:digest(p) for p in [dataset/'dataset.json',dataset/'progress.json']}
    manifest=json.loads((dataset/'dataset.json').read_text(encoding='utf-8'))
    assert len(manifest['frames'])==256,'Rehearsal requires the complete example'
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        temporary=Path(temporary);cwd=temporary/'unfamiliar cwd';cwd.mkdir()
        env=os.environ.copy()
        for key in ['BLENDER_USER_CONFIG','BLENDER_USER_SCRIPTS','BLENDER_USER_DATAFILES']:
            destination=temporary/key;destination.mkdir();env[key]=str(destination)
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None;z.extractall(temporary/'extracted')
        bundle=temporary/'extracted/apollo-development'
        packaged=json.loads((bundle/'MANIFEST.json').read_text())
        assert all(digest(bundle/name)==sha for name,sha in packaged.items())
        expected={name:digest(bundle/name) for name in ['metadata.json']+[f'renders/frame_{i:02d}.png' for i in range(10)]}
        command=[str(blender),'-b','--factory-startup','--python-exit-code','1','-P',str(bundle/'wrapper/eyes.py')]
        subprocess.run(command,cwd=cwd,env=env,check=True)
        assert all(digest(bundle/name)==sha for name,sha in expected.items()),'Extracted archive regeneration differs'
        generator=[str(blender),'-b','--factory-startup',str(scene),'--python-exit-code','1','-P',str(ROOT/'tools/generate_dataset.py'),'--']
        settings=['--count','256','--seed',str(manifest['run']['seed']),'--samples',str(manifest['run']['samples'])]
        subprocess.run(generator+['--folder',str(dataset)]+settings,cwd=cwd,env=env,check=True)
        assert all(digest(dataset/name)==sha for name,sha in before.items()),'Completed resume changed manifest'
        resumed=temporary/'resumed';(resumed/'renders').mkdir(parents=True)
        # Copy only completed files. Never hardlink a file the renderer may overwrite.
        for record in manifest['frames'][:-1]:
            src=dataset/record['extra']['image'];target=resumed/record['extra']['image']
            try:os.link(src,target)
            except OSError:shutil.copy2(src,target)
        progress={'run':manifest['run'],'frames':manifest['frames'][:-1]}
        (resumed/'progress.json').write_text(json.dumps(progress,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        subprocess.run(generator+['--folder',str(resumed)]+settings,cwd=cwd,env=env,check=True)
        assert digest(resumed/'dataset.json')==digest(dataset/'dataset.json'),'Resumed metadata differs'
        assert all(digest(resumed/r['extra']['image'])==r['extra']['image_sha256'] for r in manifest['frames']),'Resumed image differs'
    result={'passed':True,'archive_sha256':digest(archive),'scene_sha256':digest(scene),'dataset_sha256':digest(dataset/'dataset.json'),
            'extracted_archive_regenerated_identically':True,'different_cwd_and_clean_user_config':True,
            'completed_256_resume_unchanged':True,'interrupted_255_to_256_identical':True,
            'scope':'Automated operator rehearsal, not a claimed independent human usability study.'}
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--blender',required=True);p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--dataset',type=Path,required=True);p.add_argument('--scene',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(run(a.blender,a.archive,a.dataset,a.scene,a.out))
