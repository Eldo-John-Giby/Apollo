"""Author the 120-second v22 product demo from authenticated release media.

No generated imagery, speech, music, or timing changes to the three mode clips.
Requires Pillow, NumPy, imageio-ffmpeg and the released submission ZIP.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H, FPS = 1920, 1080, 24
BG, FG, MUTED, ACCENT = '#F3F0E9', '#19212B', '#616B76', '#2449C6'
THEME = 'Ivory editorial: warm paper, charcoal, cobalt, Bahnschrift headings'
VARIANTS = ['rose-brown', 'golden-hazel', 'olive-amber', 'neutral-deep', 'cool-grey']
CHAPTERS = [
    (6, 'APOLLO', 'Meet Apollo. Controlled synthetic gaze for expressive virtual humans, developed by Team AICA for Samsung PRISM-XR.'),
    (12, 'Left', 'The Left mode coordinates both eyes in the viewer\'s screen direction. Watch the initial fixation, eyelid closure and reopening, followed by refixation and a second look.'),
    (12, 'Right', 'The Right mode mirrors that directional task. These are actual released renders, shown at their original playback speed. Packed Blender timelines preserve the complete motion for inspection.'),
    (12, 'Generate Motion', 'Generate Motion combines horizontal and vertical gaze with blinking and a return to neutral. Each demonstration runs for twelve seconds at twenty-four frames per second.'),
    (12, 'Material diversity', 'Five complete material variants combine four-K skin maps with separate two-K maps for each eye. Physically based surface properties accompany the color data, with explicit binding and provenance.'),
    (14, 'Native portability', 'A separate wrapping pathway applies the materials directly to the unchanged native target. Five variants, two UV layouts and three views form a thirty-case portability matrix, separate from the hero character.'),
    (20, 'Working software', 'The extracted package runs offline. Here, the standalone verifier checks the actual delivery and authenticates eight hundred thirty-one payload files. Blender then opens the packed Generate Motion timeline: one hundred ninety-two frames at twenty-four frames per second. The command-line interface selects each mode, material variant and UV layout.'),
    (12, 'Verification', 'The retained source records contain one hundred seventy-five passing tests per platform. The exact archive passed clean Windows and Linux runtime checks, with authenticated payloads, recovery behavior and invalid-input rejection.'),
    (12, 'Samsung XR', 'For Samsung XR research, Apollo provides controlled stimuli for virtual instruction, embodied assistance and avatar evaluation. These are proposed applications. Device integration and independent human review remain next steps.'),
    (8, 'Release', 'Apollo version zero point three. Expressive virtual humans, with engineering you can inspect and reproduce. Explore the complete release and its evidence.'),
]
assert sum(c[0] for c in CHAPTERS) == 120


def sha(data):
    return hashlib.sha256(data).hexdigest()


def capture_execution(archive, work, blender):
    """Capture genuine CLI results once, before any graphical treatment."""
    work.mkdir(parents=True, exist_ok=True)
    if (work/'actual-execution.json').exists():
        return
    runtime = work/'runtime'
    runtime.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as package:
        for info in package.infolist():
            if not (runtime/info.filename).resolve().is_relative_to(runtime.resolve()):
                raise ValueError('Unsafe archive path')
            package.extract(info, runtime)
    started = time.monotonic()
    result = subprocess.run([sys.executable, 'tools/gnm_bundle_verify.py', '--reject-extra'], cwd=runtime, check=True, capture_output=True, text=True)
    verifier = json.loads(result.stdout)
    assert verifier['files'] == 831
    (work/'actual-verifier-output.txt').write_text(result.stdout, encoding='utf-8')
    probe = work/'inspect_timeline.py'
    probe.write_text('import bpy,json\ns=bpy.context.scene\nprint("APOLLO_TIMELINE "+json.dumps({"first_frame":s.frame_start,"last_frame":s.frame_end,"fps":s.render.fps/s.render.fps_base,"engine":s.render.engine,"packed_images":sum(1 for i in bpy.data.images if i.packed_file or len(i.packed_files)>0)}))\n', encoding='utf-8')
    command = [str(blender), '--offline-mode', '-b', '--factory-startup', str((runtime/'timelines/generate-motion/expression.blend').resolve()), '--python-exit-code', '1', '-P', str(probe.resolve())]
    loaded = subprocess.run(command, check=True, capture_output=True, text=True)
    (work/'actual-blender-output.txt').write_text(loaded.stdout+'\n'+loaded.stderr, encoding='utf-8')
    line = next(x for x in loaded.stdout.splitlines() if x.startswith('APOLLO_TIMELINE '))
    timeline = json.loads(line.split(' ', 1)[1])
    assert (timeline['first_frame'], timeline['last_frame'], timeline['fps']) == (1, 192, 24)
    evidence = {'commands': ['python tools/gnm_bundle_verify.py --reject-extra', 'blender --offline-mode -b timelines/generate-motion/expression.blend --python inspect_timeline.py'], 'verifier': verifier, 'timeline': timeline, 'elapsed_seconds': round(time.monotonic()-started, 3), 'verifier_stdout_sha256': sha(result.stdout.encode()), 'blender_stdout_sha256': sha(loaded.stdout.encode())}
    (work/'actual-execution.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')


class Edit:
    def __init__(self, archive, work):
        self.work = work
        self.work.mkdir(parents=True, exist_ok=True)
        self.exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.fonts = {}
        self.images = {}
        self.provenance = {}
        with zipfile.ZipFile(archive) as package:
            manifest_bytes = package.read('manifest.json')
            manifest = json.loads(manifest_bytes)['sha256']
            selection = {
                'angle': 'judging/full/rose-brown/angle/image.png',
                'front': 'judging/full/rose-brown/front/full.png',
                'oblique': 'judging/full/rose-brown/oblique/image.png',
                'native': 'judging/native/rose-brown/front/fresh-texture-only.png',
            }
            selection.update({v: f'judging/full/{v}/front/full.png' for v in VARIANTS})
            for key, name in selection.items():
                data = package.read(name)
                assert sha(data) == manifest[name], f'Unauthenticated image: {name}'
                self.images[key] = Image.open(io.BytesIO(data)).convert('RGB')
                self.provenance[name] = sha(data)
        delivery = json.loads((ROOT/'milestones/v22-12-second-demonstrations-2026-11-22/delivery.json').read_text())
        publication = json.loads((ROOT/'out/stable-v0.3.0/publication.json').read_text()) if (ROOT/'out/stable-v0.3.0/publication.json').exists() else None
        self.video_paths = [ROOT/'videos'/name for name in ['left.mp4', 'right.mp4', 'generate_motion.mp4']]
        for p in self.video_paths:
            digest = sha(p.read_bytes())
            if publication:
                assert digest == publication['verified_assets'][p.name]['sha256'], p.name
            reader = imageio_ffmpeg.read_frames(str(p))
            metadata = next(reader)
            reader.close()
            assert metadata['fps'] == FPS and metadata['duration'] == 12 and metadata['source_size'] == (1024, 1024)
            self.provenance[p.relative_to(ROOT).as_posix()] = digest
        assert delivery['duration_seconds'] == 12 and delivery['frames_per_mode'] == 288
        self.stills = {}
        self.execution = json.loads((self.work/'actual-execution.json').read_text())
        assert self.execution['verifier']['manifest_sha256'] == sha(manifest_bytes)
        assert self.execution['verifier']['files'] == 831
        assert self.execution['timeline']['last_frame'] == 192

    def font(self, size, bold=False, mono=False):
        key = (size, bold, mono)
        if key not in self.fonts:
            name = 'consola.ttf' if mono else 'bahnschrift.ttf' if bold else 'segoeui.ttf'
            self.fonts[key] = ImageFont.truetype(str(Path('C:/Windows/Fonts')/name), size)
        return self.fonts[key]

    def text(self, image, value, xy, size=38, color=FG, bold=False, spacing=12):
        ImageDraw.Draw(image).multiline_text(xy, value, font=self.font(size, bold), fill=color, spacing=spacing)

    def shell(self, index):
        image = Image.new('RGB', (W, H), BG)
        self.text(image, 'APOLLO', (96, 54), 26, FG, True)
        self.text(image, 'AICA / SAMSUNG PRISM-XR', (1364, 58), 21, MUTED)
        ImageDraw.Draw(image).line((96, 111, 1824, 111), fill='#D3D0C9', width=1)
        if index not in [0, 9]:
            self.text(image, f'{index:02d}  /  {CHAPTERS[index][1].upper()}', (96, 143), 23, ACCENT, True)
        return image

    def picture(self, canvas, key, box, progress=0, zoom=0):
        x, y, w, h = box
        image = self.images[key]
        if zoom:
            scale = 1 + zoom * progress
            cw, ch = int(image.width/scale), int(image.height/scale)
            image = image.crop(((image.width-cw)//2, (image.height-ch)//2, (image.width+cw)//2, (image.height+ch)//2))
        image = image.resize((w, h), Image.Resampling.LANCZOS)
        canvas.paste(image, (x, y))

    def base(self, index):
        if index in self.stills:
            return self.stills[index].copy()
        c = self.shell(index)
        d = ImageDraw.Draw(c)
        if index == 0:
            self.text(c, 'APOLLO', (96, 260), 142, FG, True)
            self.text(c, 'Expression, precisely controlled.', (103, 463), 45, FG)
            self.text(c, 'Synthetic gaze for Samsung XR research', (105, 575), 29, ACCENT)
            self.text(c, 'TEAM AICA   /   v0.3.0', (105, 870), 24, MUTED)
        elif index in [1, 2, 3]:
            titles = {1: 'Coordinated\nbinocular gaze.', 2: 'Controlled\nrefixation.', 3: 'Expression\nin motion.'}
            descriptions = {1: 'Shared direction.\nEyelid closure. Reopening.', 2: 'A second look.\nA blink. A return to center.', 3: 'Horizontal and vertical gaze.\nBlink. Reset.'}
            self.text(c, titles[index], (96, 285), 80, FG, True, 6)
            self.text(c, descriptions[index], (103, 553), 34, MUTED)
            self.text(c, '24 fps  /  Original playback speed', (103, 833), 25, ACCENT)
            self.text(c, 'Actual released render sequence', (103, 887), 23, MUTED)
        elif index == 4:
            self.text(c, 'Five material identities.', (96, 215), 73, FG, True)
            self.text(c, 'Matched framing. Distinct skin and iris palettes.', (101, 321), 32, MUTED)
            for i, name in enumerate(VARIANTS):
                x = 100 + i*350
                self.picture(c, name, (x, 419, 320, 320))
                self.text(c, name, (x, 766), 26, FG)
            for x, value, label in [(100, '4K', 'Skin maps'), (665, '2K', 'Separate maps per eye'), (1230, 'PBR', 'Explicit surface properties')]:
                self.text(c, value, (x, 861), 62, ACCENT, True)
                self.text(c, label, (x+155, 891), 25, MUTED)
        elif index == 6:
            self.text(c, 'Extract. Verify. Inspect.', (96, 217), 73, FG, True)
            self.text(c, 'Actual command output, edited for presentation', (102, 327), 28, MUTED)
            self.text(c, 'Standalone verification', (102, 447), 32, ACCENT, True)
            self.text(c, 'Packed Blender timeline', (1110, 447), 32, ACCENT, True)
            self.text(c, 'Offline runtime / No authoring add-ons required', (102, 916), 30, MUTED)
        elif index == 5:
            self.text(c, 'The target stays native.', (96, 210), 73, FG, True)
            self.picture(c, 'front', (205, 352, 570, 570))
            self.picture(c, 'native', (1135, 352, 570, 570))
            self.text(c, 'V22 appearance', (205, 944), 29, FG, True)
            self.text(c, 'Unchanged GNM target', (1135, 944), 29, FG, True)
            self.text(c, '5 variants / 2 UV layouts / 3 views', (102, 308), 31, ACCENT)
        elif index == 7:
            self.text(c, 'Verified beyond the render.', (96, 217), 72, FG, True)
            for x, value, label in [(100, '175', 'Passing source tests per platform'), (720, '831', 'Verified base archive payloads'), (1340, '329', 'Verified supplement payloads')]:
                self.text(c, value, (x, 416), 121, ACCENT, True)
                self.text(c, label, (x, 597), 27, MUTED)
            self.text(c, 'Windows + Linux', (102, 773), 43, FG, True)
            self.text(c, 'Offline extraction. Verified-frame preservation. Missing-frame repair.', (102, 851), 30, MUTED)
            self.text(c, 'Cross-platform image comparison: three held neutral frames.', (102, 934), 24, MUTED)
        elif index == 8:
            self.text(c, 'Samsung XR research applications', (96, 211), 67, FG, True)
            self.text(c, 'Proposed uses for controlled synthetic gaze', (102, 319), 31, ACCENT)
            for y, title, desc in [(458, 'Virtual instruction', 'Repeatable attention cues for training scenarios'), (614, 'Embodied assistance', 'Controlled visual attention for spatial explanations'), (770, 'Avatar evaluation', 'Compare appearance and gaze under known inputs')]:
                self.text(c, title, (104, y), 40, FG, True)
                self.text(c, desc, (730, y+9), 29, MUTED)
            self.text(c, 'Device integration and independent human review remain future work.', (104, 948), 24, MUTED)
        elif index == 9:
            self.text(c, 'APOLLO', (96, 266), 127, FG, True)
            self.text(c, 'Expressive virtual humans.\nInspectable engineering.', (103, 465), 44, FG)
            self.text(c, 'Stable v0.3.0  /  Team AICA', (104, 693), 30, ACCENT)
            self.text(c, 'github.com/Eldo-John-Giby/Apollo', (104, 856), 27, MUTED)
        self.stills[index] = c.copy()
        return c

    def frame(self, index, n, video=None):
        duration = CHAPTERS[index][0]
        t, progress = n/FPS, n/(duration*FPS-1)
        c = self.base(index)
        if index == 0:
            self.picture(c, 'angle', (980, 132, 850, 850), progress, .035)
        elif index in [1, 2, 3] and video is not None:
            c.paste(video, (1010, 131))
        elif index == 6:
            command = 'python tools/gnm_bundle_verify.py\n--reject-extra'
            ImageDraw.Draw(c).multiline_text((104, 528), command, font=self.font(31, mono=True), fill=FG, spacing=18)
            if t >= 3:
                self.text(c, self.execution['verifier']['status'], (104, 681), 29, ACCENT)
                self.text(c, f"{self.execution['verifier']['files']} payload files authenticated", (104, 745), 28, MUTED)
            if t >= 7:
                self.text(c, 'Frames 1-192 at 24 fps', (1110, 531), 34, FG, True)
                self.text(c, 'Cycles / packed image resources', (1110, 597), 27, MUTED)
            if t >= 11:
                self.picture(c, 'front', (1170, 665, 210, 210))
                self.text(c, 'Released output', (1422, 752), 27, ACCENT)
        elif index == 9:
            self.picture(c, 'oblique', (1015, 153, 810, 810), progress, .025)
        # Restrained entry on authored graphics. The original demonstration clips
        # run uninterrupted, without fading or retiming their evidence frames.
        if index not in [1, 2, 3]:
            alpha = min(1, max(0, t/.32))
            if alpha < 1: c = Image.blend(Image.new('RGB', (W, H), BG), c, alpha)
        elapsed = sum(x[0] for x in CHAPTERS[:index]) + t
        d = ImageDraw.Draw(c)
        d.line((96, 1034, 1824, 1034), fill='#D3D0C9', width=2)
        d.line((96, 1034, 96+int(1728*elapsed/120), 1034), fill=ACCENT, width=2)
        if index == 9 and t > duration-.45:
            c = Image.blend(c, Image.new('RGB', (W, H), BG), (t-(duration-.45))/.45)
        return c

    def video_frame(self, index, seconds):
        path = self.video_paths[index-1]
        r = subprocess.run([self.exe, '-v', 'error', '-ss', str(seconds), '-i', str(path), '-vf', 'scale=820:820', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:1'], check=True, capture_output=True)
        return Image.frombytes('RGB', (820, 820), r.stdout)

    def preview(self):
        folder = self.work/'previews'
        folder.mkdir(exist_ok=True)
        for i, (duration, _, _) in enumerate(CHAPTERS):
            second = min(duration-1, 2)
            image = self.frame(i, second*FPS, self.video_frame(i, second) if i in [1, 2, 3] else None)
            image.save(folder/f'{i:02d}.png')
        sheet = Image.new('RGB', (1440, 4*300), '#dce0e5')
        for i in range(len(CHAPTERS)):
            image = Image.open(folder/f'{i:02d}.png').resize((480, 270), Image.Resampling.LANCZOS)
            x, y = i%3*480, i//3*300
            sheet.paste(image, (x, y))
            ImageDraw.Draw(sheet).text((x+12, y+274), f'{i+1:02d} / {CHAPTERS[i][1]}', fill='#111827', font=self.font(15))
        sheet.save(self.work/'storyboard.png')

    def render(self, target):
        segments = []
        for i, (duration, title, _) in enumerate(CHAPTERS):
            path = self.work/f'chapter-{i:02d}.mp4'
            segments.append(path)
            command = [self.exe, '-y', '-v', 'warning', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '4', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', str(path)]
            reader = None
            with (self.work/f'chapter-{i:02d}.log').open('w') as log:
                writer = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=log)
                try:
                    if i in [1, 2, 3]:
                        reader = imageio_ffmpeg.read_frames(str(self.video_paths[i-1]), pix_fmt='rgb24', output_params=['-vf', 'scale=820:820'])
                        next(reader)
                    for n in range(duration*FPS):
                        video = Image.frombytes('RGB', (820, 820), next(reader)) if reader else None
                        writer.stdin.write(self.frame(i, n, video).tobytes())
                finally:
                    writer.stdin.close()
                    if reader: reader.close()
                assert writer.wait() == 0, path
            print(f'Encoded {i+1:02d}/{len(CHAPTERS)}: {title}', flush=True)
        listing = self.work/'concat.txt'
        listing.write_text(''.join("file '"+p.resolve().as_posix()+"'\n" for p in segments), encoding='utf-8')
        subprocess.run([self.exe, '-y', '-v', 'warning', '-f', 'concat', '-safe', '0', '-i', str(listing), '-c', 'copy', '-movflags', '+faststart', str(target)], check=True)
        result = subprocess.run([self.exe, '-v', 'info', '-i', str(target), '-map', '0:v:0', '-f', 'null', '-'], check=True, capture_output=True, text=True)
        frames = int(re.findall(r'frame=\s*(\d+)', result.stderr)[-1])
        assert frames == 120*FPS
        assert 'Audio:' not in result.stderr
        (self.work/'decode.log').write_text(result.stderr, encoding='utf-8')
        return {'theme': THEME, 'duration_seconds': 120, 'decoded_frames': frames, 'width': W, 'height': H, 'fps': FPS, 'audio': 'None. Silent narration-ready master.', 'sha256': sha(target.read_bytes()), 'bytes': target.stat().st_size, 'sources': self.provenance, 'actual_execution': self.execution, 'editing': 'Authored typography, restrained still-image push-ins, frame-exact original-speed mode playback. Actual CLI results shown as edited excerpts.', 'scope': 'Edited product demonstration using actual Blender output. No real-time render-speed or deployed-device claim.', 'chapters': [{'start_seconds': sum(c[0] for c in CHAPTERS[:i]), 'duration_seconds': c[0], 'title': c[1]} for i, c in enumerate(CHAPTERS)]}


def write_script(path):
    lines = ['# Apollo two-minute demo: voice-over guide', '', 'Record one continuous human voice-over, using the ranges below as cues. The master is deliberately silent. The pace is approximately 145 words per minute, with room for natural pauses. Mode clips run at their original 24 fps. Proposed Samsung applications are identified explicitly.', '', 'Pronunciation: Apollo = uh-POL-oh; GNM = G-N-M; UV = U-V; PBR = P-B-R.', '']
    for i, (seconds, title, words) in enumerate(CHAPTERS):
        start = sum(c[0] for c in CHAPTERS[:i])
        clock = lambda n: f'{n//60:02}:{n%60:02}'
        lines.extend([f'## {clock(start)}–{clock(start+seconds)} · {title}', '', words, ''])
    lines.extend(['## Handoff', '', 'Master: `videos/apollo-demo-2min.mp4` (1920×1080, 24 fps, 120 seconds, H.264). Add the voice-over in your editor, preserve the 120-second timeline, and export H.264 at the same frame rate. Do not stretch the three mode clips. A restrained licensed music bed can be added beneath the human voice if desired.', '', 'Engineering boundary: source test records cover 175 passing tests per platform. The clean Windows/Linux runtime comparison covers three held neutral frames. Independent human review and organizer-model matching remain outstanding. The video demonstrates offline synthesis, rather than measured headset deployment or real-time rendering.', ''])
    path.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submission-archive', type=Path, required=True)
    parser.add_argument('--work', type=Path, default=ROOT/'out/submission-demo-2min')
    parser.add_argument('--out', type=Path, default=ROOT/'videos/apollo-demo-2min.mp4')
    parser.add_argument('--preview-only', action='store_true')
    parser.add_argument('--blender', type=Path, default=Path('C:/Program Files/Blender Foundation/Blender 4.5/blender.exe'))
    args = parser.parse_args()
    capture_execution(args.submission_archive, args.work, args.blender)
    edit = Edit(args.submission_archive, args.work)
    edit.preview()
    if not args.preview_only:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        receipt = edit.render(args.out)
        receipt['builder_sha256'] = sha(Path(__file__).read_bytes())
        (args.work/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
        write_script(ROOT/'docs/APOLLO_DEMO_VOICEOVER.md')
        print('VERIFIED_TWO_MINUTE_MASTER', args.out, flush=True)
