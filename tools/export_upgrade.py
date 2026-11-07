"""Stage a qualified technical release, with no invented registration identity."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
from make_bundle import qualified_candidate
from dataset_protocol import resume
ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export(upgrade,destination,delivery):
    upgrade=Path(upgrade).resolve();destination=Path(destination).resolve();delivery=Path(delivery).resolve()
    if destination.exists() or delivery.exists():raise ValueError('Use new release/delivery directories')
    candidate,required=qualified_candidate(upgrade/'candidate')
    reports={name:json.loads((upgrade/file).read_text(encoding='utf-8')) for name,file in {
        'dataset':'dataset-256/analysis.json','visibility':'dataset-visibility/report.json',
        'linux':'docker-candidate/verification_report.json','ui':'ui/operator-final/report.json',
        'lighting':'lighting-adversary/report.json','rehearsal':'release-rehearsal.json'}.items()}
    assert all(r['passed'] for r in reports.values()),'A release gate did not pass'
    assert reports['dataset']['frames']==256 and reports['visibility']['poses']==25
    manifest=json.loads((upgrade/'dataset-256/dataset.json').read_text(encoding='utf-8'))
    scene_hash=digest(candidate/'scene.blend')
    assert manifest['run']['scene_sha256']==scene_hash
    assert reports['linux']['artifact_hashes']['scene.blend']==scene_hash
    assert reports['ui']['scene_sha256']==scene_hash and reports['lighting']['scene_sha256']==scene_hash
    assert len(resume(upgrade/'dataset-256',manifest['run']))==256
    assert reports['dataset']['dataset_sha256']==digest(upgrade/'dataset-256/dataset.json')
    archive=upgrade/'apollo-competition.zip'
    assert reports['rehearsal']['archive_sha256']==digest(archive)
    assert reports['rehearsal']['scene_sha256']==scene_hash
    pptx=upgrade/'presentation-final/Apollo_Submission_ppt.pptx'
    with zipfile.ZipFile(pptx) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')])==10
    video=upgrade/'video/apollo-demo.mp4';assert video.is_file() and video.stat().st_size>100000
    receipt=json.loads((upgrade/'video/video-receipt.json').read_text());assert receipt['duration_seconds']==105 and receipt['decoded_frames']==2520 and abs(receipt['actual_duration_seconds']-105)<.2
    # Complete all checks before creating reviewable delivery directories.
    destination.mkdir(parents=True);delivery.mkdir(parents=True)
    for name in required:shutil.copy2(candidate/name,delivery/name)
    shutil.copytree(candidate/'renders',delivery/'renders')
    (delivery/'wrapper').mkdir();shutil.copy2(ROOT/'wrapper/eyes.py',delivery/'wrapper/eyes.py')
    for key,value in json.loads((candidate/'verification_report.json').read_text())['artifact_hashes'].items():
        assert digest(delivery/key)==value,'Unpacked delivery differs from qualified artifacts'
    files={'apollo-competition.zip':archive,'Apollo_Submission_ppt.pptx':pptx,'apollo-demo.mp4':video,
           'contact_sheet.png':candidate/'contact_sheet.png','verification_report.json':candidate/'verification_report.json',
           'verification_report.md':candidate/'verification_report.md','dataset.json':upgrade/'dataset-256/dataset.json',
           'dataset-analysis.json':upgrade/'dataset-256/analysis.json','dataset-visibility.json':upgrade/'dataset-visibility/report.json',
           'dataset-coverage.png':upgrade/'dataset-256/coverage.png','dataset-anchors.png':upgrade/'dataset-256/anchors.png',
           'linux-verification.json':upgrade/'docker-candidate/verification_report.json','release-rehearsal.json':upgrade/'release-rehearsal.json',
           'ui-rehearsal.json':upgrade/'ui/operator-final/report.json','lighting-adversary.json':upgrade/'lighting-adversary/report.json',
           'narration.txt':upgrade/'video/narration.txt','video-receipt.json':upgrade/'video/video-receipt.json'}
    for name,source in files.items():shutil.copy2(source,destination/name)
    for folder,prefix in [(candidate/'verification','native'),(upgrade/'docker-candidate/verification','linux'),(upgrade/'dataset-visibility','dataset-visibility')]:
        with zipfile.ZipFile(destination/(prefix+'-evidence.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for file in sorted(folder.rglob('*')):
                if file.is_file():z.write(file,Path(prefix)/file.relative_to(folder))
    # The complete research example is a separate local artifact, not the graded ZIP.
    with zipfile.ZipFile(upgrade/'dataset-256.zip','w',zipfile.ZIP_STORED) as z:
        for name in ['dataset.json','progress.json','analysis.json','coverage.png','anchors.png']:
            z.write(upgrade/'dataset-256'/name,Path('dataset-256')/name)
        for file in sorted((upgrade/'dataset-256/renders').glob('*.png')):
            z.write(file,Path('dataset-256/renders')/file.name)
    readme='''# Apollo competition technical release

This is an evidence-bound technical milestone, not an organizer submission.
The registered college/team identity and event upload links are team-owned.

Use the unpacked `delivery/apollo` directory for the conventional executable
layout, or extract `apollo-competition.zip`. Run `wrapper/eyes.py` directly in
Blender as described in its README. Optional controls and research tooling live
in the repository, outside the required wrapper path.

Native 4.5 and secondary 5.2 qualification, full Linux qualification, the actual
256-frame dataset and 25-pose visibility checks are recorded in the attached
reports. Local project checks are not official competition scores. The actual
complete dataset ZIP is generated separately under `out/upgrade/dataset-256.zip`;
its source manifest and measured analysis are retained here.

The 105-second video uses actual artifacts with local synthesized narration.
The editable deck retains a technical-prototype identity if team details have
not been supplied. Human naturalness preference and independent human usability
ratings are not invented. See `docs/UPGRADE_RUNBOOK.md` for reproduction commands.
'''
    (destination/'README.md').write_text(readme,encoding='utf-8',newline='\n')
    hashes={str(p.relative_to(destination)).replace('\\','/'):digest(p) for p in sorted(destination.rglob('*')) if p.is_file()}
    (destination/'MANIFEST.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8',newline='\n')
    return destination


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('upgrade',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--delivery',type=Path,required=True)
    a=p.parse_args();print(export(a.upgrade,a.out,a.delivery))
