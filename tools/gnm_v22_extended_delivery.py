"""Verify, encode, and package the 12-second v22 demonstration supplement.

The preserved 192-frame technical submission is not rewritten. The supplement
contains new 288-frame timelines, the original frames plus authenticated GPU
extension frames, and three 12-second H.264 demonstration videos.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MODES = ('left', 'right', 'generate-motion')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')


def deliver(base, supplement, ffmpeg):
    inventory = json.loads((base/'delivery-inventory.json').read_text())
    summary = dict(status='verified_12_second_demonstration_supplement',
                   release_ready=False, frames_per_mode=288, fps=24, duration_seconds=12,
                   samples=512, resolution=[1024, 1024],
                   original_inventory_sha256=sha(base/'delivery-inventory.json'),
                   modes={}, qualification='Frame provenance, image integrity, video decode and technical extension checks. Independent human acceptance remains separate.')
    workers = {sha(ROOT/'tools/gnm_v22_extend.py')}
    for path in (supplement/'provenance').glob('worker-*.py'):
        workers.add(sha(path))
    validated = set()
    for mode in MODES:
        scene = supplement/'timelines'/mode/'expression.blend'
        build = json.loads(scene.with_suffix('.extension.json').read_text())
        receipt_path = supplement/'frames'/mode/'render-receipt.json'
        receipt = json.loads(receipt_path.read_text())
        run = receipt['run']
        assert build['mode'] == run['mode'] == mode
        assert sha(scene) == build['scene_sha256'] == run['scene_sha256']
        assert build['original_scene_sha256'] == inventory['modes'][mode]['scene_sha256']
        assert build['script_sha256'] in workers and run['worker_sha256'] in workers
        assert run['device'] == 'GPU' and run['backend'] == 'CUDA' and '3090' in run['gpu']
        assert run['resolution'] == [1024, 1024] and run['samples'] == 512 and run['fps'] == 24
        assert run['range'] == [193, 288]
        assert build['original_channel_error'] < 1e-7 and build['frames'] == 288
        assert set(receipt['frames']) == {f'frame_{f:04d}.png' for f in range(193, 289)}
        records = {}
        pose_hashes = {}
        joined = supplement/'joined-frames'/mode
        joined.mkdir(parents=True, exist_ok=True)
        for frame in range(1, 289):
            name = f'frame_{frame:04d}.png'
            source = (base if frame <= 192 else supplement)/'frames'/mode/name
            expected = (inventory['modes'][mode]['frames'][name] if frame <= 192
                        else receipt['frames'][name]['sha256'])
            assert sha(source) == expected, (mode, frame, 'image hash mismatch')
            if expected not in validated:
                with Image.open(source) as image:
                    assert image.size == (1024, 1024)
                    image.verify()
                validated.add(expected)
            if frame > 192:
                pose = build['pose_ids'][frame-1]
                assert pose not in pose_hashes or pose_hashes[pose] == expected
                pose_hashes[pose] = expected
                reused = receipt['frames'][name]['reused_frame']
                if reused is not None:
                    assert 193 <= reused < frame
                    assert build['pose_ids'][reused-1] == pose
                    assert receipt['frames'][f'frame_{reused:04d}.png']['sha256'] == expected
            target = joined/name
            if not target.exists():
                os.link(source, target)
            else:
                assert sha(target) == expected
            records[name] = dict(sha256=expected, source='preserved-original' if frame <= 192 else 'GPU-extension')
        video = supplement/'videos'/('generate_motion.mp4' if mode == 'generate-motion' else mode+'.mp4')
        video.parent.mkdir(exist_ok=True)
        if not video.exists():
            subprocess.run([ffmpeg, '-v', 'error', '-framerate', '24', '-start_number', '1',
                            '-i', str(joined/'frame_%04d.png'), '-frames:v', '288',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '15',
                            '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                            '-color_primaries', 'bt709', '-color_trc', 'bt709',
                            '-colorspace', 'bt709', '-an', str(video)], check=True)
        # Count every decoded frame and its timestamps, rather than trust a header.
        decoded = subprocess.run([ffmpeg, '-v', 'error', '-i', str(video), '-map', '0:v:0',
                                  '-f', 'framemd5', '-'], capture_output=True, text=True, check=True)
        rows = [r for r in decoded.stdout.splitlines() if r and not r.startswith('#')]
        assert len(rows) == 288, (mode, 'wrong decoded frame count')
        assert '#tb 0: 1/24' in decoded.stdout
        assert [int(r.split(',')[2]) for r in rows] == list(range(288))
        summary['modes'][mode] = dict(scene_sha256=sha(scene),
            extension_receipt_sha256=sha(receipt_path), frames=records,
            rendered_unique_extension_poses=sum(v['reused_frame'] is None for v in receipt['frames'].values()),
            video=dict(filename=video.name, bytes=video.stat().st_size,
                       sha256=sha(video), decoded_frames=288, duration_seconds=12))
        print('DELIVERY_MODE_VERIFIED', mode, flush=True)
    save(supplement/'delivery.json', summary)
    return summary


def package(supplement, base_archive, output):
    assert not output.exists(), 'Refuse to overwrite an existing delivery archive'
    assert (supplement/'delivery.json').is_file()
    report = json.loads((supplement/'delivery.json').read_text())
    payloads = {}
    for folder in ('timelines', 'frames', 'videos', 'checks', 'provenance'):
        for path in (supplement/folder).rglob('*'):
            if path.is_file():
                payloads[path.relative_to(supplement).as_posix()] = path
    payloads['delivery.json'] = supplement/'delivery.json'
    payloads['docs/V22_12_SECOND_DEMOS.md'] = ROOT/'docs/V22_12_SECOND_DEMOS.md'
    for name in ('gnm_v22_extend.py', 'gnm_v22_extended_check.py',
                 'gnm_v22_extended_delivery.py', 'gnm_v22_image_check.py'):
        payloads['tools/'+name] = ROOT/'tools'/name
    payloads['apollo_core/png.py'] = ROOT/'apollo_core/png.py'
    payloads['apollo_core/__init__.py'] = ROOT/'apollo_core/__init__.py'
    files = {name: sha(path) for name, path in payloads.items()}
    manifest = dict(schema=1, status='verified_12_second_demonstration_supplement',
                    release_ready=False, frames_per_video=288, fps=24,
                    duration_seconds=12, resolution=[1024, 1024], samples=512,
                    preserved_base_archive=dict(filename=base_archive.name,
                        sha256=sha(base_archive)), sha256=files,
                    qualification='Extended demonstrations; original submission acceptance gates remain separate.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        for name, path in sorted(payloads.items()):
            assert sha(path) == files[name], 'Payload changed during packaging'
            archive.write(path, name)
        with zipfile.ZipFile(base_archive) as original:
            for name in original.namelist():
                if name.startswith('licenses/') and not name.endswith('/'):
                    data = original.read(name)
                    archive.writestr(name, data)
                    files[name] = hashlib.sha256(data).hexdigest()
        archive.writestr('manifest.json', json.dumps(manifest, indent=2)+'\n')
    # Independently read every member, checking the public content hash manifest.
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist()))
        for name, digest in files.items():
            h = hashlib.sha256()
            with archive.open(name) as stream:
                for chunk in iter(lambda: stream.read(8*1024*1024), b''):
                    h.update(chunk)
            assert h.hexdigest() == digest, name
    checksum = sha(output)
    output.with_suffix('.zip.sha256').write_text(checksum+'  '+output.name+'\n')
    save(supplement/'archive-check.json', dict(passed=True, bytes=output.stat().st_size,
         sha256=checksum, files=len(files), all_payload_hashes_verified=True,
         archive_crc_verified=True, release_ready=False))
    print('SUPPLEMENT_PACKAGE_VERIFIED', output.name, checksum, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--supplement', type=Path, required=True)
    parser.add_argument('--ffmpeg', required=True)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--base-archive', type=Path)
    args = parser.parse_args()
    deliver(args.base.resolve(), args.supplement.resolve(), args.ffmpeg)
    if args.archive:
        assert args.base_archive, '--base-archive is required with --archive'
        package(args.supplement.resolve(), args.base_archive.resolve(), args.archive.resolve())
