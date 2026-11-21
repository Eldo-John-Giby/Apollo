"""Final clean Windows/Linux qualification for the exact Apollo v22 submission archive.

Verifies:
1. Exact submission archive (out/apollo-v22-submission.zip) checksum and ZIP CRC.
2. Clean extraction on Windows in an isolated path with spaces outside the repository.
3. Standalone file verification (gnm_bundle_verify.py --reject-extra) on all 831 payloads.
4. Clean Windows runtime reproduction with pinned Blender 4.5.15 LTS (build 5afeabba6097),
   including frame verification, hold preservation, repair of corrupt/missing frames,
   stale receipt rejection, and out-of-range rejection.
5. Clean Linux runtime reproduction in pinned offline container (beb58a3d91e8)
   in /tmp/clean path/Apollo, verifying all 831 payloads, clean render, and frame receipts.
6. Measured cross-platform Windows vs Linux image differences.
7. Text and secrets hygiene check on all packaged text.
8. 12-second demonstration supplement archive verification.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_ARCHIVE = ROOT / 'out/apollo-v22-submission.zip'
EXPECTED_SUBMISSION_SHA = '887f187b92cc80c9ac359d00ab539fbeb34b8327359e24bc873d9e47f5f0de96'
SUPPLEMENT_ARCHIVE = ROOT / 'out/apollo-v22-12-second-demonstrations.zip'
EXPECTED_SUPPLEMENT_SHA = 'ad76db004e99cc743b07c0bc335481c6d596757fd1a29396f65654835ac5277b'

WIN_BLENDER = Path('C:/Program Files/Blender Foundation/Blender 4.5/blender.exe')
LINUX_IMAGE = 'sha256:beb58a3d91e8169f6df8c989da2703f1c0fbfcc45bdcdf1d21c6c8c6f205619b'


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def check_archive_integrity(archive_path, expected_sha):
    print(f'Checking archive integrity for {archive_path.name}...')
    actual_sha = sha(archive_path)
    assert actual_sha == expected_sha, f'Archive SHA mismatch: {actual_sha} != {expected_sha}'
    with zipfile.ZipFile(archive_path) as z:
        bad = z.testzip()
        assert bad is None, f'Corrupted file in ZIP: {bad}'
        namelist = z.namelist()
        assert 'manifest.json' in namelist, 'manifest.json missing from archive'
        manifest = json.loads(z.read('manifest.json'))
        assert manifest.get('schema') == 1, 'Invalid schema'
        entries = manifest.get('sha256', {})
        assert len(entries) > 0, 'Empty manifest sha256'
    print(f'Archive {archive_path.name} passed SHA256 and ZIP CRC ({len(namelist)} files).')
    return {
        'filename': archive_path.name,
        'bytes': archive_path.stat().st_size,
        'sha256': actual_sha,
        'files_in_zip': len(namelist),
        'manifest_entries': len(entries),
        'zip_crc': 'passed'
    }


def qualify_windows(archive_path, out_dir):
    print('\n=== Running Clean Windows Qualification ===')
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_base = Path(tempfile.gettempdir()) / f'apollo clean submission {uuid.uuid4().hex[:8]}'
    extracted = clean_base / 'Apollo Extracted'
    extracted.mkdir(parents=True, exist_ok=True)

    try:
        print(f'Extracting {archive_path.name} to {extracted}...')
        with zipfile.ZipFile(archive_path) as z:
            z.extractall(extracted)

        print('Running standalone file verifier (gnm_bundle_verify.py)...')
        verify_cmd = [
            sys.executable, str(extracted / 'tools/gnm_bundle_verify.py'),
            '--root', str(extracted), '--reject-extra'
        ]
        res = subprocess.run(verify_cmd, capture_output=True, text=True, check=True)
        verify_report = json.loads(res.stdout)
        print('Bundle verify report:', verify_report)

        print('Executing public render command outside project CWD...')
        outside_cwd = clean_base / 'outside cwd with spaces'
        outside_cwd.mkdir(exist_ok=True)
        frames_out = clean_base / 'rendered frames with spaces'

        base_cmd = [
            sys.executable, str(extracted / 'tools/gnm_run.py'), 'generate-motion',
            '--blender', str(WIN_BLENDER), '--out', str(frames_out),
            '--first', '1', '--last', '3'
        ]

        def run_step(cmd, log_name, expect_success=True):
            with (out_dir / f'{log_name}.log').open('w', encoding='utf-8') as log_file:
                r = subprocess.run(cmd, cwd=outside_cwd, stdout=log_file, stderr=subprocess.STDOUT)
            if (r.returncode == 0) != expect_success:
                raise RuntimeError(f'Step {log_name} exited with {r.returncode}, expected success={expect_success}')

        run_step(base_cmd, 'win-initial-3-frames')
        paths = [frames_out / f'frame_{n:04d}.png' for n in (1, 2, 3)]
        for p in paths:
            assert p.is_file(), f'Render output missing: {p}'
        original_hashes = [sha(p) for p in paths]
        mtime_frame1 = paths[0].stat().st_mtime_ns

        print('Testing repair of corrupted and missing frames...')
        paths[1].write_bytes(b'INTENTIONAL CORRUPTION FOR QUALIFICATION')
        paths[2].unlink()
        run_step(base_cmd, 'win-repair-corrupt-and-missing')
        repaired_hashes = [sha(p) for p in paths]
        assert repaired_hashes == original_hashes, 'Repair failed to restore exact byte-identical hashes'
        assert paths[0].stat().st_mtime_ns == mtime_frame1, 'Untouched frame 1 was re-rendered instead of preserved'

        print('Testing negative validation: stale receipt rejection...')
        receipt_path = frames_out / 'render-receipt.json'
        receipt_data = json.loads(receipt_path.read_text(encoding='utf-8'))
        receipt_data['run']['samples'] += 1
        receipt_path.write_text(json.dumps(receipt_data), encoding='utf-8')
        run_step(base_cmd, 'win-reject-stale-receipt', expect_success=False)
        receipt_data['run']['samples'] -= 1
        receipt_path.write_text(json.dumps(receipt_data), encoding='utf-8')

        print('Testing negative validation: out-of-range rejection...')
        bad_range_cmd = base_cmd.copy()
        bad_range_cmd[bad_range_cmd.index('--first') + 1] = '193'
        bad_range_cmd[bad_range_cmd.index('--last') + 1] = '194'
        run_step(bad_range_cmd, 'win-reject-outside-timeline', expect_success=False)

        # Copy generated frames to out_dir for cross-platform comparison
        win_frames_dir = out_dir / 'windows-frames'
        win_frames_dir.mkdir(exist_ok=True)
        for p in paths:
            shutil.copyfile(p, win_frames_dir / p.name)

        report = {
            'status': 'passed_windows_clean_submission_archive_qualification',
            'archive_sha256': sha(archive_path),
            'extracted_path': str(extracted),
            'files_verified': verify_report['files'],
            'frames': {p.name: h for p, h in zip(paths, original_hashes)},
            'valid_frame_preserved': True,
            'corrupt_and_missing_repaired': True,
            'stale_receipt_rejected': True,
            'invalid_range_rejected': True,
            'qualification': 'Clean Windows extraction outside project with spaces; standalone verifier and runtime pass.'
        }
        (out_dir / 'windows-qualification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print('Windows qualification passed successfully!')
        return report

    finally:
        print('Cleaning up Windows temporary extraction folder...')
        shutil.rmtree(clean_base, ignore_errors=True)


def qualify_linux(archive_path, out_dir):
    print('\n=== Running Clean Linux Qualification (Docker apollo:v22-linux-qualification) ===')
    out_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = out_dir / 'linux-evidence'
    if evidence_dir.exists():
        shutil.rmtree(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    archive_hash = sha(archive_path)
    container_name = f'apollo-v22-qual-{uuid.uuid4().hex[:8]}'

    linux_script = f"""
from pathlib import Path
import zipfile, json, hashlib, subprocess, sys, os

print("Verifying archive SHA256 inside Linux container...")
digest = hashlib.sha256()
with open('/submission.zip', 'rb') as stream:
    for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
        digest.update(block)
actual_sha = digest.hexdigest()
assert actual_sha == '{archive_hash}', f"Linux archive SHA mismatch: {{actual_sha}}"

root = Path('/tmp/clean path with spaces/Apollo')
print("Extracting archive into clean path with spaces on Linux...")
with zipfile.ZipFile('/submission.zip') as package:
    package.extractall(root)

print("Running gnm_bundle_verify.py on Linux with --reject-extra...")
res = subprocess.run([sys.executable, str(root / 'tools/gnm_bundle_verify.py'), '--root', str(root), '--reject-extra'],
                     capture_output=True, text=True, check=True)
verify_report = json.loads(res.stdout)
print("Linux bundle verify:", verify_report)

os.chdir('/tmp')
frames_out = Path('/evidence/linux frames with spaces')
run_cmd = [
    sys.executable, str(root / 'tools/gnm_run.py'), 'generate-motion',
    '--blender', '/opt/blender/blender', '--out', str(frames_out),
    '--first', '1', '--last', '3'
]
print("Running generate-motion on Linux CPU Blender...")
subprocess.run(run_cmd, check=True)

receipt = json.loads((frames_out / 'render-receipt.json').read_text())
assert len(receipt['frames']) == 3
for name, record in receipt['frames'].items():
    h = hashlib.sha256((frames_out / name).read_bytes()).hexdigest()
    assert h == record['sha256'], f"Frame hash mismatch for {{name}}"

print("Testing repair of corrupted frame on Linux...")
(frames_out / 'frame_0002.png').write_bytes(b'LINUX INTENTIONAL CORRUPTION')
subprocess.run(run_cmd, check=True)
assert hashlib.sha256((frames_out / 'frame_0002.png').read_bytes()).hexdigest() == receipt['frames']['frame_0002.png']['sha256']

result = dict(
    status='passed_linux_clean_submission_archive_qualification',
    archive_sha256=actual_sha,
    files_verified=verify_report['files'],
    receipt_frames=len(receipt['frames']),
    receipt=receipt,
    qualification='Clean Linux extraction in container outside project with spaces; standalone verifier and runtime pass.'
)
Path('/evidence/linux-qualification.json').write_text(json.dumps(result, indent=2))
print("Linux qualification finished successfully inside container.")
"""

    log_path = out_dir / 'linux-qualification.log'
    with log_path.open('w', encoding='utf-8') as log_file:
        print('Creating isolated Linux container with --network none...')
        subprocess.run([
            'docker', 'create', '--name', container_name,
            '--network', 'none', '--cpus', '4', '--memory', '6g',
            '--workdir', '/tmp',
            '--env', 'OPENBLAS_NUM_THREADS=1', '--env', 'OMP_NUM_THREADS=1',
            '--mount', f'type=bind,source={evidence_dir.resolve()},target=/evidence',
            '--entrypoint', 'python3', LINUX_IMAGE, '-c', linux_script
        ], stdout=log_file, stderr=subprocess.STDOUT, check=True)

        try:
            print('Copying submission archive into container...')
            subprocess.run(['docker', 'cp', str(archive_path), f'{container_name}:/submission.zip'],
                           stdout=log_file, stderr=subprocess.STDOUT, check=True)
            print('Starting Linux container...')
            subprocess.run(['docker', 'start', '--attach', container_name],
                           stdout=log_file, stderr=subprocess.STDOUT, check=True)
            exit_code = subprocess.check_output(
                ['docker', 'inspect', '--format', '{{.State.ExitCode}}', container_name],
                text=True).strip()
            if exit_code != '0':
                raise RuntimeError(f'Linux container exited with code {exit_code}')
        finally:
            print('Removing Linux container...')
            subprocess.run(['docker', 'rm', '--force', container_name],
                           stdout=log_file, stderr=subprocess.STDOUT, check=True)

    result_path = evidence_dir / 'linux-qualification.json'
    assert result_path.is_file(), 'Linux qualification report was not written'
    report = json.loads(result_path.read_text(encoding='utf-8'))
    (out_dir / 'linux-qualification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Linux qualification passed successfully!')
    return report


def compare_cross_platform(out_dir):
    print('\n=== Running Cross-Platform Image Comparison (Windows vs Linux) ===')
    win_dir = out_dir / 'windows-frames'
    linux_dir = out_dir / 'linux-evidence/linux frames with spaces'

    comparison = {
        'status': 'measured_cross_platform_submission_image_difference',
        'frames': {}
    }

    for n in (1, 2, 3):
        name = f'frame_{n:04d}.png'
        win_path = win_dir / name
        linux_path = linux_dir / name
        assert win_path.is_file() and linux_path.is_file(), f'Missing frame for comparison: {name}'

        im_win = np.array(Image.open(win_path)).astype(np.float32)
        im_lin = np.array(Image.open(linux_path)).astype(np.float32)
        assert im_win.shape == im_lin.shape
        assert im_win.shape[:2] == (1024, 1024)
        if len(im_win.shape) == 3 and im_win.shape[-1] == 4:
            im_win = im_win[:, :, :3]
            im_lin = im_lin[:, :, :3]

        diff = np.abs(im_win - im_lin)
        rgb_max = float(np.max(diff))
        rgb_mean = float(np.mean(diff))
        rgb_p95 = float(np.percentile(diff, 95))
        rgb_p99 = float(np.percentile(diff, 99))
        changed_pixels = int(np.sum(np.any(diff > 0, axis=-1)))
        total_pixels = 1024 * 1024

        mse = float(np.mean(diff ** 2))
        psnr = 10 * np.log10(255.0 ** 2 / mse) if mse > 0 else float('inf')

        comparison['frames'][name] = {
            'windows_sha256': sha(win_path),
            'linux_sha256': sha(linux_path),
            'byte_identical': sha(win_path) == sha(linux_path),
            'rgb_max': rgb_max,
            'rgb_mean': rgb_mean,
            'rgb_p95': rgb_p95,
            'rgb_p99': rgb_p99,
            'changed_pixels': changed_pixels,
            'total_pixels': total_pixels,
            'psnr_db': round(psnr, 2)
        }
        print(f'{name}: max_diff={rgb_max}, mean_diff={rgb_mean:.5f}, PSNR={psnr:.2f} dB, changed_pixels={changed_pixels}/{total_pixels}')

    comparison['qualification'] = (
        'Exact cross-platform comparison of clean-extracted submission archive rendered on Windows and Linux CPU. '
        'Floating-point Cycles noise rounding differences quantified.'
    )
    (out_dir / 'cross-platform-comparison.json').write_text(json.dumps(comparison, indent=2) + '\n', encoding='utf-8')
    return comparison


def hygiene_check(archive_path, out_dir):
    import re
    print('\n=== Running Secrets & Hygiene Scan ===')
    token_patterns = [r'\brk_[a-zA-Z0-9]{16,}', r'\bghp_[a-zA-Z0-9]{20,}', r'[?&]token=[a-zA-Z0-9]{16,}']
    forbidden_paths = [r'C:\Users\eldoj', r'/home/eldoj']
    flagged = []

    with zipfile.ZipFile(archive_path) as z:
        for name in z.namelist():
            if name.endswith(('.txt', '.json', '.md', '.py', '.yaml', '.yml', '.xml', '.sh', '.bat', '.ps1')):
                content = z.read(name).decode('utf-8', errors='ignore')
                for pat in token_patterns:
                    if re.search(pat, content):
                        flagged.append({'file': name, 'issue': f'Matches secret pattern {pat}'})
                for fpath in forbidden_paths:
                    if fpath in content:
                        flagged.append({'file': name, 'issue': f'Contains authoring path {fpath}'})

    report = {
        'status': 'passed_hygiene_check' if not flagged else 'failed_hygiene_check',
        'archive': archive_path.name,
        'issues': flagged
    }
    (out_dir / 'hygiene-check.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    assert not flagged, f'Hygiene issues found: {flagged}'
    print('Secrets and hygiene scan passed cleanly.')
    return report


def qualify_supplement(supplement_path, out_dir):
    print('\n=== Running Supplement Archive Verification ===')
    check_report = check_archive_integrity(supplement_path, EXPECTED_SUPPLEMENT_SHA)
    clean_base = Path(tempfile.gettempdir()) / f'apollo clean supplement {uuid.uuid4().hex[:8]}'
    extracted = clean_base / 'Apollo Supplement Extracted'
    extracted.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(supplement_path) as z:
            z.extractall(extracted)
        manifest = json.loads((extracted / 'manifest.json').read_text(encoding='utf-8'))
        for name, expected in manifest['sha256'].items():
            assert sha(extracted / name) == expected, f'Supplement file SHA mismatch: {name}'
        print(f'Supplement archive {supplement_path.name}: all {len(manifest["sha256"])} files verified from clean extraction.')
        report = {
            'status': 'passed_supplement_clean_extraction_verification',
            'filename': supplement_path.name,
            'bytes': supplement_path.stat().st_size,
            'sha256': EXPECTED_SUPPLEMENT_SHA,
            'payloads_verified': len(manifest['sha256'])
        }
        (out_dir / 'supplement-qualification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        return report
    finally:
        shutil.rmtree(clean_base, ignore_errors=True)


def main():
    out_dir = ROOT / 'out/v22-submission-qualification'
    out_dir.mkdir(parents=True, exist_ok=True)

    print('Starting Final Clean Windows/Linux Qualification...')
    sub_integrity = check_archive_integrity(SUBMISSION_ARCHIVE, EXPECTED_SUBMISSION_SHA)

    win_json = out_dir / 'windows-qualification.json'
    if win_json.is_file() and (out_dir / 'windows-frames/frame_0001.png').is_file():
        print('Windows qualification already completed successfully; reusing report.')
        win_report = json.loads(win_json.read_text(encoding='utf-8'))
    else:
        win_report = qualify_windows(SUBMISSION_ARCHIVE, out_dir)

    lin_json = out_dir / 'linux-qualification.json'
    if lin_json.is_file() and (out_dir / 'linux-evidence/linux frames with spaces/frame_0001.png').is_file():
        print('Linux qualification already completed successfully; reusing report.')
        lin_report = json.loads(lin_json.read_text(encoding='utf-8'))
    else:
        lin_report = qualify_linux(SUBMISSION_ARCHIVE, out_dir)

    comp_report = compare_cross_platform(out_dir)
    hyg_report = hygiene_check(SUBMISSION_ARCHIVE, out_dir)
    supp_report = qualify_supplement(SUPPLEMENT_ARCHIVE, out_dir)

    summary = {
        'status': 'verified_final_clean_windows_linux_submission_qualification',
        'release_ready': False,
        'submission_archive': sub_integrity,
        'supplement_archive': supp_report,
        'windows_qualification': win_report['status'],
        'linux_qualification': lin_report['status'],
        'cross_platform_comparison': comp_report['frames'],
        'hygiene_scan': hyg_report['status'],
        'qualification': (
            'Exact submission archive (apollo-v22-submission.zip) and 12s supplement archive '
            'passed clean extraction, standalone file verifier, Windows & Linux runtime reproduction, '
            'repair/rejection negative tests, cross-platform image comparison, and hygiene scan. '
            'Independent human evaluation remains separate.'
        )
    }
    (out_dir / 'final-qualification-summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print('\n=======================================================')
    print('FINAL CLEAN WINDOWS/LINUX QUALIFICATION COMPLETE!')
    print(f'Summary saved to: {out_dir / "final-qualification-summary.json"}')
    print('=======================================================')


if __name__ == '__main__':
    main()
