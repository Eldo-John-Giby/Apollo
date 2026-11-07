"""Stage a qualified technical release, with no invented registration identity."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
from make_bundle import qualified_candidate
from dataset_protocol import resume
from verify import hashes,verifier_sources,evidence_hashes
ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export(upgrade,destination,delivery,profile='upgrade'):
    upgrade=Path(upgrade).resolve();destination=Path(destination).resolve();delivery=Path(delivery).resolve()
    if destination.exists() or delivery.exists():raise ValueError('Use new release/delivery directories')
    candidate,required=qualified_candidate(upgrade/'candidate')
    reports={name:json.loads((upgrade/file).read_text(encoding='utf-8')) for name,file in {
        'dataset':'dataset-256/analysis.json','visibility':'dataset-visibility/report.json',
        'linux':'docker-candidate/verification_report.json','ui':'ui/operator-final/report.json',
        'lighting':'lighting-adversary/report.json','rehearsal':'release-rehearsal.json','rebuild':'look-rebuild-report.json'}.items()}
    assert all(r['passed'] for r in reports.values()),'A release gate did not pass'
    linux=reports['linux'];linux_folder=upgrade/'docker-candidate'
    assert linux['production'] and all(linux['checks'][f'V{i}']['status']=='PASS' for i in range(1,18))
    assert linux['artifact_hashes']==hashes(linux_folder)
    assert linux['verifier_sha256']==verifier_sources() and linux['evidence_sha256']==evidence_hashes(linux_folder)
    assert profile in ('upgrade','realism')
    assert reports['dataset']['frames']==256 and reports['visibility']['poses']==(113 if profile=='realism' else 25)
    manifest=json.loads((upgrade/'dataset-256/dataset.json').read_text(encoding='utf-8'))
    scene_hash=digest(candidate/'scene.blend')
    assert manifest['run']['scene_sha256']==scene_hash
    for key,name in {'wrapper_sha256':'wrapper/eyes.py','generator_sha256':'tools/generate_dataset.py','protocol_sha256':'tools/dataset_protocol.py','reference_sha256':'tools/reference_geometry.py'}.items():
        assert manifest['run'][key]==digest(ROOT/name)
    assert all(value==digest(ROOT/'tools'/name) for name,value in reports['dataset']['analysis_sources'].items())
    assert reports['linux']['artifact_hashes']['scene.blend']==scene_hash
    assert reports['ui']['scene_sha256']==scene_hash and reports['lighting']['scene_sha256']==scene_hash
    assert reports['ui']['panel_source_sha256']==digest(ROOT/'tools/live_controls.py')
    assert reports['visibility']['scene_sha256']==scene_hash
    assert reports['rebuild']['candidate_scene_sha256']==scene_hash
    recipe='build/realism_scene.py' if profile=='realism' else 'build/upgrade_looks.py'
    assert reports['rebuild']['recipe_source_sha256']==digest(ROOT/recipe)
    if profile=='realism':
        assert reports['rebuild']['config_sha256']==digest(ROOT/'build/realism_config.json')
        visual=json.loads((upgrade/'visual-review.json').read_text())
        assert visual['passed'] and visual['scene_sha256']==scene_hash
        samples=json.loads((upgrade/'sample-review.json').read_text())
        assert samples['passed'] and samples['scene_sha256']==scene_hash
        categories=visual['categories']
        assert set(categories)=={'socket_integration','eye_appearance','skin_response','grooming','pupil_readability'}
        assert all(1<=v['baseline']<=5 and 1<=v['candidate']<=5 for v in categories.values())
        assert sum(v['candidate']>v['baseline'] for v in categories.values())>=3
        assert any(categories[k]['candidate']>categories[k]['baseline'] for k in ['socket_integration','eye_appearance'])
        assert categories['pupil_readability']['candidate']>=categories['pupil_readability']['baseline']
        for review in [visual,samples]:
            assert review['reviewed_artifacts']
            for name,value in review['reviewed_artifacts'].items():
                path=(upgrade/name).resolve();assert path.is_relative_to(upgrade)
                assert digest(path)==value,'Reviewed image changed'
        benchmark=json.loads((upgrade/'samples/benchmark.json').read_text())
        assert samples['benchmark_sha256']==digest(upgrade/'samples/benchmark.json')
        assert benchmark['completed'] and set(benchmark['profiles'])=={'32','64','128'}
        assert benchmark['worker_sha256']==digest(ROOT/'tools/benchmark_render.py')
        assert benchmark['wrapper_sha256']==digest(ROOT/'wrapper/eyes.py')
        selected=samples['selected_samples'];assert selected==manifest['run']['samples']
        assert selected==json.loads((ROOT/'build/realism_config.json').read_text())['samples']
        assert digest(upgrade/'samples'/str(selected)/'center.png')==digest(candidate/'verification/baseline.png')
        assert digest(upgrade/'samples'/str(selected)/'up.png')==digest(candidate/'verification/up.png')
        from realism_visibility import poses
        stress=json.loads((upgrade/'stress-rgb/dataset.json').read_text())
        assert stress['run']['scene_sha256']==scene_hash
        assert stress['run']['worker_sha256']==digest(ROOT/'tools/realism_visibility.py')
        assert [(f['input']['h'],f['input']['v']) for f in stress['frames']]==poses()
        assert all(digest(upgrade/'stress-rgb'/f['extra']['image'])==f['extra']['image_sha256'] for f in stress['frames'])
    visibility_folder=upgrade/'dataset-visibility'
    assert reports['visibility']['evidence_sha256']==digest(visibility_folder/'evidence.json')
    assert reports['visibility']['analysis_source_sha256']==digest(ROOT/'tools/analyze_visibility.py')
    assert all(digest(visibility_folder/name)==value for name,value in reports['visibility']['mask_sha256'].items())
    assert len(resume(upgrade/'dataset-256',manifest['run']))==256
    assert reports['dataset']['dataset_sha256']==digest(upgrade/'dataset-256/dataset.json')
    archive=upgrade/'apollo-competition.zip'
    assert reports['rehearsal']['archive_sha256']==digest(archive)
    assert reports['rehearsal']['scene_sha256']==scene_hash
    pptx=upgrade/'presentation-final/Apollo_Submission_ppt.pptx'
    with zipfile.ZipFile(pptx) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')])==10
    deck_receipt=upgrade/'deck-build/validation-final.json'
    deck_validation=json.loads(deck_receipt.read_text())
    assert deck_validation['finalSha256']==digest(pptx)
    assert deck_validation['packageIntegrity']['status']=='pass' and deck_validation['firstPartyImport']['passed']
    native_receipt=upgrade/'presentation-final/native-review.json'
    native_review=json.loads(native_receipt.read_text())
    assert native_review['passed'] and native_review['reviewed_slides']==10 and native_review['presentation_sha256']==digest(pptx)
    assert len(native_review['native_png_sha256'])==10
    assert all(digest(upgrade/'presentation-final/native'/name)==value for name,value in native_review['native_png_sha256'].items())
    video=upgrade/'video/apollo-demo.mp4';assert video.is_file() and video.stat().st_size>100000
    receipt=json.loads((upgrade/'video/video-receipt.json').read_text());assert receipt['duration_seconds']==105 and receipt['decoded_frames']==2520 and abs(receipt['actual_duration_seconds']-105)<.2
    video_review_path=upgrade/'video/visual-review.json'
    video_review=json.loads(video_review_path.read_text())
    assert video_review['passed'] and video_review['video_sha256']==digest(video)
    assert len(video_review['reviewed_timestamps_seconds'])>=10
    # Complete all checks before creating reviewable delivery directories.
    destination.mkdir(parents=True);delivery.mkdir(parents=True)
    for name in required:shutil.copy2(candidate/name,delivery/name)
    shutil.copytree(candidate/'renders',delivery/'renders')
    (delivery/'wrapper').mkdir();shutil.copy2(ROOT/'wrapper/eyes.py',delivery/'wrapper/eyes.py')
    for key,value in json.loads((candidate/'verification_report.json').read_text())['artifact_hashes'].items():
        assert digest(delivery/key)==value,'Unpacked delivery differs from qualified artifacts'
    files={'apollo-competition.zip':archive,'Apollo_Submission_ppt.pptx':pptx,'apollo-demo.mp4':video,
           'contact_sheet.png':candidate/'contact_sheet.png','verification_report.json':candidate/'verification_report.json',
           'verification_report.md':candidate/'verification_report.md',
           'dataset-analysis.json':upgrade/'dataset-256/analysis.json','dataset-visibility.json':upgrade/'dataset-visibility/report.json',
           'dataset-coverage.png':upgrade/'dataset-256/coverage.png','dataset-anchors.png':upgrade/'dataset-256/anchors.png',
           'linux-verification.json':upgrade/'docker-candidate/verification_report.json','release-rehearsal.json':upgrade/'release-rehearsal.json',
           'linux-qualification.log':upgrade/'docker-candidate/qualification.log',
           'linux-preflight-geometry.json':upgrade/'docker-candidate/preflight-geometry.json',
           'ui-rehearsal.json':upgrade/'ui/operator-final/report.json','lighting-adversary.json':upgrade/'lighting-adversary/report.json',
           'narration.txt':upgrade/'video/narration.txt','video-receipt.json':upgrade/'video/video-receipt.json',
           'video-visual-review.json':video_review_path,
           'look-rebuild-report.json':upgrade/'look-rebuild-report.json',
           'presentation-validation.json':deck_receipt,'presentation-native-review.json':native_receipt,
           'tests-native.log':upgrade/'tests-final-native.log','tests-linux.log':upgrade/'docker-candidate/tests-final.log'}
    for name,source in files.items():shutil.copy2(source,destination/name)
    if profile=='realism':
        for name in ['visual-review.json','sample-review.json']:
            shutil.copy2(upgrade/name,destination/name)
        shutil.copytree(upgrade/'comparisons',destination/'comparisons')
        shutil.copytree(upgrade/'portraits',destination/'portraits')
        shutil.copytree(upgrade/'stress-rgb',destination/'visibility-stress')
        with zipfile.ZipFile(destination/'sample-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
            for file in sorted((upgrade/'samples').rglob('*')):
                if file.is_file():z.write(file,Path('samples')/file.relative_to(upgrade/'samples'))
    for folder,prefix in [(candidate/'verification','native'),(upgrade/'docker-candidate/verification','linux'),(upgrade/'dataset-visibility','dataset-visibility'),(upgrade/'ui/operator-final','ui'),(upgrade/'lighting-adversary','lighting'),(upgrade/'presentation-final/native','presentation')]:
        with zipfile.ZipFile(destination/(prefix+'-evidence.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for file in sorted(folder.rglob('*')):
                if file.is_file():z.write(file,Path(prefix)/file.relative_to(folder))
    example=destination/'dataset-256';example.mkdir()
    for name in ['dataset.json','progress.json','analysis.json','coverage.png','anchors.png']:
        shutil.copy2(upgrade/'dataset-256'/name,example/name)
    shutil.copytree(upgrade/'dataset-256/renders',example/'renders')
    assert len(resume(example,manifest['run']))==256,'Staged research images differ'
    # Keep the complete research corpus separate from the graded ten-frame ZIP.
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

From the repository root (writes a separate replay, preserving shipped images):

```powershell
blender -b delivery/apollo/scene.blend --python-exit-code 1 -P delivery/apollo/wrapper/eyes.py -- --out out/replay
```

- [Unpacked executable delivery](../../delivery/apollo/README.md)
- [Ten-frame development ZIP](apollo-competition.zip)
- [Measured native report](verification_report.md) and [Linux report](linux-verification.json)
- [Contact sheet](contact_sheet.png), [105-second video](apollo-demo.mp4), [editable deck](Apollo_Submission_ppt.pptx)
- [Complete research manifest](dataset-256/dataset.json) and [image analysis](dataset-analysis.json)
- [Per-file checksums](MANIFEST.json)

Native 4.5 and secondary 5.2 qualification, full Linux qualification, the actual
256-frame dataset and pose-grid visibility checks are recorded in the attached
reports. Local project checks are not official competition scores. The complete
256-image research example is in `dataset-256/`; an additional ZIP is generated
under the working output's `dataset-256.zip`. Keep its seeded manifest and images together.

The 105-second video uses actual artifacts with local synthesized narration.
The editable deck retains a technical-prototype identity if team details have
not been supplied. Human naturalness preference and independent human usability
ratings are not invented. See `docs/UPGRADE_RUNBOOK.md` for reproduction commands.
'''
    if profile=='realism':
        readme=readme.replace('delivery/apollo','delivery/'+delivery.name)
        readme+='\nThe realism profile includes 113 mask-tested poses, matched comparisons, sample\nexperiments and separate presentation-only portraits. Recheck extracted masks\nwith tools/analyze_visibility.py --dataset pointing to visibility-stress.\n'
    (destination/'README.md').write_text(readme,encoding='utf-8',newline='\n')
    manifest_hashes={str(p.relative_to(destination)).replace('\\','/'):digest(p) for p in sorted(destination.rglob('*')) if p.is_file()}
    (destination/'MANIFEST.json').write_text(json.dumps(manifest_hashes,indent=2)+'\n',encoding='utf-8',newline='\n')
    return destination


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('upgrade',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--delivery',type=Path,required=True)
    p.add_argument('--profile',choices=['upgrade','realism'],default='upgrade')
    a=p.parse_args();print(export(a.upgrade,a.out,a.delivery,a.profile))
