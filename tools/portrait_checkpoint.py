"""Package a passing targeted portrait checkpoint and matched still comparison."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def package(candidate, checks, output):
    candidate, checks, output = map(Path, (candidate, checks, output))
    if output.exists():
        raise ValueError('Use a new checkpoint folder')
    scene_sha = digest(candidate/'scene.blend')
    status = read(checks/'status.json')
    assert status['stage'] == 'targeted-checks-complete-awaiting-visual-review'
    assert status['scene_sha256'] == scene_sha
    receipt = read(candidate/'build.json')
    assert receipt['scene_sha256'] == scene_sha
    assert receipt['recipe_sha256'] == digest(ROOT/'build/portrait_refinement.py')
    assert receipt['brow_helper_sha256'] == digest(ROOT/'build/realism_scene.py')
    assert receipt['source_sha256'] == digest(ROOT/'milestones/photorealism-v2-candidate/scene.blend')
    for relative in ['scene-preflight.json', 'masks/report.json',
                     'poses/early-image-report.json', 'official/early-image-report.json']:
        report = read(checks/relative)
        assert report['passed'] and report['scene_sha256'] == scene_sha, relative
    assert read(checks/'geometry.json')['passed']
    benchmark = read(checks/'performance/benchmark.json')
    assert benchmark['completed'] and benchmark['scene_sha256'] == scene_sha
    times = {key: row['seconds'] for key, row in benchmark['profiles']['32']['poses'].items()}
    assert max(times.values()) <= 120
    resources = read(checks/'resources.json')
    assert 0 < resources['peak_process_rss_bytes'] <= 4*1024**3

    before = ROOT/'milestones/photorealism-v2-candidate/evidence/portraits'
    after = checks/'portraits'
    old, new = read(before/'portraits.json'), read(after/'portraits.json')
    assert new['scene_sha256'] == scene_sha
    assert len(old['views']) == len(new['views']) == 2
    for a, b in zip(old['views'], new['views']):
        for key in ['view', 'camera_position', 'focal_mm']:
            assert a[key] == b[key], 'Unmatched portrait camera'
        assert digest(before/(a['view']+'.png')) == a['image_sha256']
        assert digest(after/(b['view']+'.png')) == b['image_sha256']

    output.mkdir(parents=True)
    for name in ['scene.blend', 'build.json', 'scene-preflight.json']:
        shutil.copy2(candidate/name, output/name)
    shutil.copy2(ROOT/'milestones/photorealism-v2-candidate/ATTRIBUTION.md', output/'ATTRIBUTION.md')
    shutil.copytree(checks, output/'evidence', ignore=shutil.ignore_patterns('*.blend', '*.log'))
    font_path = Path('C:/Windows/Fonts/arial.ttf')
    font = ImageFont.truetype(str(font_path), 28) if font_path.exists() else ImageFont.load_default()
    sheet = Image.new('RGB', (2048, 2136), '#eeeeee')
    draw = ImageDraw.Draw(sheet)
    for row, view in enumerate(['front', 'three-quarter']):
        for col, (label, folder) in enumerate([('Before: v2', before), ('After: portrait refinement', after)]):
            draw.text((col*1024+18, row*1068+8), label, fill='#202838', font=font)
            with Image.open(folder/(view+'.png')) as im:
                assert im.size == (1024,1024)
                sheet.paste(im.convert('RGB'), (col*1024,row*1068+44))
    sheet.save(output/'before-after.jpg', quality=94, subsampling=0)
    summary = {
        'qualified': False,
        'scope': 'Native targeted development checks; not full release qualification',
        'scene_sha256': scene_sha,
        'cpu_frame_seconds': times,
        'peak_process_rss_bytes': resources['peak_process_rss_bytes'],
        'visibility': read(checks/'masks/report.json')['minimum_visible_dark_fraction'],
        'official_image_checks': read(checks/'official/early-image-report.json'),
        'review_required': True,
        'baseline_scene_sha256': old['scene_sha256'],
    }
    (output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    manifest = {str(p.relative_to(output)).replace('\\','/'):digest(p)
                for p in sorted(output.rglob('*')) if p.is_file()}
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--checks', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    package(args.candidate, args.checks, args.out)
