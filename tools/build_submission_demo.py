"""Author the 120-second v22 product demo from authenticated release media.

Actual released imagery, authored scientific schematics and human-narration timing.
No synthetic speech, stock imagery or retiming of the rendered motion excerpts.
Requires Pillow, NumPy, imageio-ffmpeg and the released submission ZIP.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
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
    (6, 'APOLLO', 'Meet Apollo. Expressive virtual humans, with facial appearance and eye movement engineered together for Samsung XR research.'),
    (12, 'Coordinated behavior', 'Apollo combines binocular gaze, eyelid closure and refixation in a controllable facial performance. The selected identity remains recognizable as the eyes move, close and reopen.'),
    (12, 'Analytical fixation', 'Alongside native GNM animation, our analytical research module solves each eye toward one shared fixation target. A calibrated camera connects physical pupil geometry to inspectable image coordinates.'),
    (14, 'Identity transport', 'We build on Google GNM motion and transport the selected identity through local surface rotations. The method preserves facial offsets while protected eye components retain their native coordinates. Appearance follows expression without redefining the ocular reference.'),
    (12, 'Material construction', 'Detailed appearance comes from separate material channels: color, roughness, specular response and surface normals. Four-K skin and distinct two-K eye maps support controlled shading, backed by attributed source assets.'),
    (10, 'Surface attachments', 'Hair, brows, lashes and tear-region details need to follow the face. Surface-triangle anchors and local frames carry these attachments with the deforming geometry.'),
    (10, 'Controlled variation', 'Five material palettes share the same character geometry. This separates changes in appearance from changes in anatomy, supporting consistent comparisons under matched framing.'),
    (12, 'Native portability', 'Apollo also applies textures directly to the unchanged native target. Five palettes, two UV layouts and three views create thirty portability cases, separate from the full character presentation.'),
    (8, 'Independent evidence', 'Native-motion comparisons, appearance-component checks and image diagnostics support the visual result. Source-bound records make those checks traceable to the delivered artifacts.'),
    (14, 'Samsung XR relevance', 'For Samsung XR, controlled gaze can support virtual instructors, embodied assistants and avatar evaluation. Apollo provides reproducible facial stimuli for that research, with device integration as the next step. These are proposed applications, rather than deployed headset features.'),
    (10, 'APOLLO', 'Apollo brings detailed materials, identity-preserving motion and native-target portability into one inspectable system. A precise foundation for expressive virtual humans and Samsung XR research.'),
]
VIDEO_SCENES = {1: ('left.mp4', 0.0), 3: ('right.mp4', 0.0), 5: ('generate_motion.mp4', 2.0)}
assert sum(c[0] for c in CHAPTERS) == 120


def sha(data):
    return hashlib.sha256(data).hexdigest()


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
                'eyes': 'judging/overviews-and-details/full-rose-brown-eyes.png',
                'color': 'textures/rose-brown/color.1001.png',
                'roughness': 'textures/rose-brown/roughness.1001.png',
                'normal': 'textures/rose-brown/normal.1001.png',
            }
            selection.update({v: f'judging/full/{v}/front/full.png' for v in VARIANTS})
            for key, name in selection.items():
                data = package.read(name)
                assert sha(data) == manifest[name], f'Unauthenticated image: {name}'
                self.images[key] = Image.open(io.BytesIO(data)).convert('RGB')
                self.provenance[name] = sha(data)
        delivery = json.loads((ROOT/'milestones/v22-12-second-demonstrations-2026-11-22/delivery.json').read_text())
        self.video_paths = [ROOT/'videos'/name for name in ['left.mp4', 'right.mp4', 'generate_motion.mp4']]
        for p in self.video_paths:
            digest = sha(p.read_bytes())
            mode = 'generate-motion' if p.stem == 'generate_motion' else p.stem
            assert digest == delivery['modes'][mode]['video']['sha256'], p.name
            reader = imageio_ffmpeg.read_frames(str(p))
            metadata = next(reader)
            reader.close()
            assert metadata['fps'] == FPS and metadata['duration'] == 12 and metadata['source_size'] == (1024, 1024)
            self.provenance[p.relative_to(ROOT).as_posix()] = digest
        assert delivery['duration_seconds'] == 12 and delivery['frames_per_mode'] == 288
        self.observations = json.loads((ROOT/'milestones/submission-demo-2026-11-22/pupil-observations.json').read_text())['modes']['left']
        for name, key in [('apollo-cinematic-eye.png', 'cinematic'), ('apollo-eye-detail-hd.png', 'eyes-hd')]:
            data = (ROOT/'docs/images'/name).read_bytes()
            receipt = json.loads((ROOT/'docs/images/apollo-v22-media-provenance.json').read_text())['derived_high_resolution_stills'][name]
            assert receipt['geometry_unchanged'] and receipt['image_sha256'] == sha(data)
            self.images[key] = Image.open(io.BytesIO(data)).convert('RGB')
            self.provenance['docs/images/'+name] = sha(data)
        self.stills = {}

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
        if index not in [0, 10]:
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
        if index == 0:
            self.picture(c, 'angle', (100, 130, 900, 900))
            self.text(c, 'APOLLO', (1330, 245), 88, FG, True)
            self.text(c, 'Expression,\nengineered.', (1335, 405), 48, FG)
            self.text(c, 'Synthetic gaze\nfor Samsung XR research', (1337, 635), 29, ACCENT)
            self.text(c, 'TEAM AICA / v0.3.0', (1337, 905), 24, MUTED)
        elif index == 1:
            self.text(c, 'Coordinated eyes. Preserved identity.', (96, 190), 64, FG, True)
            self.text(c, 'SYNCHRONIZED OCULAR DETAIL', (1010, 325), 26, ACCENT, True)
            self.text(c, 'Screen-left eye', (1010, 636), 27, FG, True)
            self.text(c, 'Screen-right eye', (1425, 636), 27, FG, True)
            self.text(c, 'Source-image pupil centroids / pixels', (1010, 814), 26, MUTED)
            self.text(c, 'Measured from rendered PNGs.\nImage diagnostics, rather than geometric labels.', (1010, 864), 25, MUTED)
            self.text(c, 'Original motion / 24 fps', (96, 985), 22, ACCENT)
        elif index == 2:
            self.text(c, 'One target. Two independent gaze rays.', (96, 216), 63, FG, True)
            self.text(c, 'Analytical research module / separate from native GNM animation', (103, 315), 29, ACCENT)
        elif index == 3:
            self.text(c, 'Motion inherited.\nIdentity preserved.', (96, 260), 76, FG, True, 8)
            self.text(c, 'Native Google GNM poses\nLocal rotation of identity offsets\nProtected eye coordinates', (103, 505), 32, MUTED, spacing=23)
            self.text(c, 'Surface-local identity transport', (103, 897), 26, ACCENT)
        elif index == 4:
            self.text(c, 'Material detail,\nlayer by layer.', (96, 252), 78, FG, True, 8)
            self.text(c, '4K skin / distinct 2K eye maps', (103, 493), 31, ACCENT)
            self.text(c, 'Color, roughness, specular response\nand tangent-space normals.', (103, 566), 30, MUTED)
            self.text(c, 'Actual material maps and rendered detail', (103, 921), 24, MUTED)
            for x, key, label in [(830, 'color', 'BASE COLOR'), (1168, 'roughness', 'ROUGHNESS'), (1506, 'normal', 'NORMAL')]:
                self.picture(c, key, (x, 374, 300, 300))
                self.text(c, label, (x, 697), 22, ACCENT, True)
            self.picture(c, 'eyes-hd', (1080, 754, 480, 270))
        elif index == 5:
            self.text(c, 'The details\nfollow the face.', (96, 266), 77, FG, True, 8)
            self.text(c, 'Surface-triangle anchors\nDeformation-aware local frames', (103, 510), 31, MUTED, spacing=19)
            self.text(c, 'Hair, brows, lashes and tear details', (103, 869), 26, ACCENT)
        elif index == 6:
            self.text(c, 'One geometry. Five material palettes.', (96, 214), 65, FG, True)
            self.text(c, 'Controlled variation under matched framing', (103, 319), 32, MUTED)
            for i, name in enumerate(VARIANTS):
                x = 100+i*350
                self.picture(c, name, (x, 423, 320, 320))
                self.text(c, name, (x, 770), 26, FG)
            self.text(c, 'Appearance changes. The underlying character stays consistent.', (103, 905), 33, ACCENT)
        elif index == 7:
            self.text(c, 'The target stays native.', (96, 211), 74, FG, True)
            self.text(c, '5 palettes / 2 UV layouts / 3 views', (103, 316), 32, ACCENT)
            self.picture(c, 'front', (205, 361, 565, 565))
            self.picture(c, 'native', (1135, 361, 565, 565))
            self.text(c, 'Full v22 identity and groom', (205, 945), 28, FG, True)
            self.text(c, 'Texture-only native GNM target', (1135, 945), 28, FG, True)
        elif index == 8:
            self.text(c, 'The engineering is inspectable.', (96, 217), 71, FG, True)
            for x, value, caption in [(100, '383', 'Integer and half-frame samples\nper base motion mode'), (720, '18', 'Appearance components\nchecked per mode'), (1340, '175', 'Passing source tests\nper platform')]:
                self.text(c, value, (x, 432), 120, ACCENT, True)
                self.text(c, caption, (x, 611), 28, MUTED, spacing=14)
            self.text(c, 'Native reference comparisons. Image diagnostics. Source-bound evidence.', (103, 869), 30, FG)
            self.text(c, 'Independent human review remains outstanding.', (103, 947), 24, MUTED)
        elif index == 9:
            self.text(c, 'A research foundation for Samsung XR', (96, 216), 64, FG, True)
            self.text(c, 'Proposed applications for controlled visual attention', (103, 319), 30, ACCENT)
            for y, title, desc in [(460, 'Virtual instructors', 'Repeatable attention and expression in training'), (615, 'Embodied assistants', 'Visual cues that accompany spatial explanations'), (770, 'Avatar evaluation', 'Controlled inputs for appearance and gaze studies')]:
                self.text(c, title, (104, y), 40, FG, True)
                self.text(c, desc, (735, y+10), 29, MUTED)
            self.text(c, 'Device integration and evaluation remain future work.', (104, 948), 24, MUTED)
        elif index == 10:
            self.text(c, 'APOLLO', (96, 267), 127, FG, True)
            self.text(c, 'Expressive humans.\nControlled by design.', (103, 467), 47, FG)
            self.text(c, 'Appearance, motion and native compatibility', (104, 691), 29, ACCENT)
            self.text(c, 'Team AICA / Samsung PRISM-XR', (104, 858), 27, MUTED)
        self.stills[index] = c.copy()
        return c

    def fixation(self, canvas, t):
        import math
        d = ImageDraw.Draw(canvas)
        target = (1310, 605-155*math.sin(2*math.pi*t/6))
        d.line((1310, 390, 1310, 810), fill='#C8C3B9', width=3)
        d.line((1310, 445, 1310, 765), fill='#C87927', width=5)
        self.text(canvas, 'Fixation plane', (1190, 357), 26, MUTED)
        self.text(canvas, '+5 cm', (1340, 426), 23, '#A55A15')
        self.text(canvas, '-5 cm', (1340, 744), 23, '#A55A15')
        for name, eye, color in [('L', (235, 500), '#3A8682'), ('R', (235, 710), '#C87927')]:
            d.line((eye[0], eye[1], target[0], target[1]), fill=color, width=3)
            d.ellipse((eye[0]-44, eye[1]-44, eye[0]+44, eye[1]+44), fill='#FFFFFF', outline=FG, width=2)
            ray = np.array(target)-np.array(eye);ray = ray/np.linalg.norm(ray)*20
            pupil = (eye[0]+ray[0], eye[1]+ray[1])
            d.ellipse((pupil[0]-10, pupil[1]-10, pupil[0]+10, pupil[1]+10), fill=ACCENT)
            self.text(canvas, name, (148, eye[1]-21), 30, FG, True)
        d.ellipse((target[0]-12, target[1]-12, target[0]+12, target[1]+12), fill='#C87927')
        d.ellipse((230, 600, 240, 610), fill=FG)
        self.text(canvas, 'M', (150, 584), 24, MUTED)
        d.polygon([(1610, 576), (1555, 605), (1610, 634), (1610, 620), (1690, 620), (1690, 590), (1610, 590)], fill=ACCENT)
        self.text(canvas, 'Camera locked', (1535, 673), 24, MUTED)
        for y, x2, label in [(875, 1310, '35 cm fixation distance'), (952, 1595, '40 cm render camera')]:
            d.line((235, y, x2, y), fill=MUTED, width=2)
            for x in [235, x2]: d.line((x, y-9, x, y+9), fill=MUTED, width=2)
            self.text(canvas, label, (650, y-44), 25, FG)
        self.text(canvas, 'Plan-view schematic / not to scale', (1400, 983), 20, MUTED)

    def frame(self, index, n, video=None):
        duration = CHAPTERS[index][0]
        t, progress = n/FPS, n/(duration*FPS-1)
        c = self.base(index)
        if index in VIDEO_SCENES and video is not None:
            c.paste(video.resize((680, 680), Image.Resampling.LANCZOS) if index == 1 else video, (150, 285) if index == 1 else (1010, 131))
        if index == 1 and video is not None:
            row = self.observations[min(n, len(self.observations)-1)]
            reference = self.observations[0]['image_pupil_centroids_px']
            for key, x, fx0, fx1 in [('screen-left', 1010, .20, .43), ('screen-right', 1425, .57, .80)]:
                box = (int(820*fx0), int(820*.37), int(820*fx1), int(820*.51))
                tile = video.crop(box).resize((365, 220), Image.Resampling.LANCZOS)
                xy = row['image_pupil_centroids_px'][key]
                if xy is not None:
                    cx = (xy[0]/1024*820-box[0])*365/(box[2]-box[0])
                    cy = (xy[1]/1024*820-box[1])*220/(box[3]-box[1])
                    d = ImageDraw.Draw(tile)
                    d.line((cx-12, cy, cx+12, cy), fill='#57E0D1', width=2)
                    d.line((cx, cy-12, cx, cy+12), fill='#57E0D1', width=2)
                    self.text(c, f'x {xy[0]:.2f}  y {xy[1]:.2f}', (x, 687), 24, ACCENT)
                    if reference[key] is not None:
                        dx, dy = xy[0]-reference[key][0], xy[1]-reference[key][1]
                        self.text(c, f'dx {dx:+.2f}  dy {dy:+.2f}', (x, 734), 24, MUTED)
                else:
                    self.text(c, 'Pupil undetected / occluded', (x, 687), 22, MUTED)
                c.paste(tile, (x, 390))
            self.text(c, f'SOURCE FRAME {n+1:03d} / 288', (1010, 965), 23, ACCENT, True)
        elif index == 2:
            self.fixation(c, t)
        elif index == 3:
            d = ImageDraw.Draw(c)
            for x, label in [(105, 'Native pose'), (395, 'Local rotation'), (685, 'V22 identity')]:
                self.text(c, label, (x, 765), 24, ACCENT, True)
            for x in [320, 610]:
                amount = min(1, max(0, (t-.5)/1.5))
                d.line((x, 783, x+int(52*amount), 783), fill=ACCENT, width=2)
        elif index == 5:
            # Diagram of local attachment frames, separate from actual render.
            d = ImageDraw.Draw(c)
            offset = 9*np.sin(t*2)
            vertices = [(150, 731+offset), (355, 681-offset), (510, 760+offset)]
            d.polygon(vertices, fill='#E3E0D9', outline=MUTED)
            anchor = tuple(np.mean(vertices, axis=0))
            tangent = np.array(vertices[1])-np.array(vertices[0])
            tangent = tangent/np.linalg.norm(tangent)
            normal = np.array([tangent[1], -tangent[0]])
            d.ellipse((anchor[0]-6, anchor[1]-6, anchor[0]+6, anchor[1]+6), fill=ACCENT)
            d.line([anchor, tuple(np.array(anchor)+normal*59)], fill=ACCENT, width=3)
            d.line([anchor, tuple(np.array(anchor)+tangent*70)], fill='#3A8682', width=3)
            self.text(c, 'Attachment-frame schematic', (525, 713), 20, MUTED)
        elif index == 6:
            d = ImageDraw.Draw(c);active = min(4, int(progress*5));x = 100+active*350
            d.line((x, 825, x+320, 825), fill=ACCENT, width=4)
        elif index == 10:
            self.picture(c, 'angle', (1015, 153, 810, 810), progress, .035)
        if index not in VIDEO_SCENES:
            alpha = min(1, max(0, t/.26))
            if alpha < 1:c = Image.blend(Image.new('RGB', (W, H), BG), c, alpha)
        elapsed = sum(x[0] for x in CHAPTERS[:index])+t
        d = ImageDraw.Draw(c)
        d.line((96, 1034, 1824, 1034), fill='#D3D0C9', width=2)
        d.line((96, 1034, 96+int(1728*elapsed/120), 1034), fill=ACCENT, width=2)
        if index == 10 and t > duration-.45:
            c = Image.blend(c, Image.new('RGB', (W, H), BG), (t-(duration-.45))/.45)
        return c

    def video_frame(self, index, seconds):
        file, start = VIDEO_SCENES[index]
        path = ROOT/'videos'/file
        seconds = min(11.95, seconds+start)
        r = subprocess.run([self.exe, '-v', 'error', '-ss', str(seconds), '-i', str(path), '-vf', 'scale=820:820', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:1'], check=True, capture_output=True)
        return Image.frombytes('RGB', (820, 820), r.stdout)

    def preview(self):
        folder = self.work/'previews'
        folder.mkdir(exist_ok=True)
        for i, (duration, _, _) in enumerate(CHAPTERS):
            second = min(duration-1, 2)
            image = self.frame(i, second*FPS, self.video_frame(i, second) if i in VIDEO_SCENES else None)
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
                    if i in VIDEO_SCENES:
                        file, start = VIDEO_SCENES[i]
                        reader = imageio_ffmpeg.read_frames(str(ROOT/'videos'/file), input_params=['-ss', str(start)], pix_fmt='rgb24', output_params=['-vf', 'scale=820:820'])
                        next(reader)
                    for n in range(duration*FPS):
                        if reader:
                            try: video = Image.frombytes('RGB', (820, 820), next(reader))
                            except StopIteration: pass  # Editorial hold after the original 12-second source.
                        else: video = None
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
        return {'theme': THEME, 'duration_seconds': 120, 'decoded_frames': frames, 'width': W, 'height': H, 'fps': FPS, 'audio': 'None. Silent narration-ready master.', 'sha256': sha(target.read_bytes()), 'bytes': target.stat().st_size, 'sources': self.provenance, 'purpose': 'Product showcase: mechanisms, differentiation and Samsung XR research relevance', 'editing': 'Authored technical schematics, animated fixation rays, native identity and attachment explanations, actual rendered footage at original speed. Right-mode editorial ending hold: two seconds.', 'scope': 'Edited product demonstration using actual Blender output. No real-time render-speed or deployed-device claim.', 'chapters': [{'start_seconds': sum(c[0] for c in CHAPTERS[:i]), 'duration_seconds': c[0], 'title': c[1]} for i, c in enumerate(CHAPTERS)]}


def write_script(path):
    lines = ['# Apollo two-minute demo: voice-over guide', '', 'Record one continuous human voice-over, using the ranges below as cues. The master is deliberately silent. The pace is approximately 145 words per minute, with room for natural pauses. Recorded footage runs at its original 24 fps. This script replaces the earlier walkthrough narration. Proposed Samsung applications are identified explicitly.', '', 'Pronunciation: Apollo = uh-POL-oh; GNM = G-N-M; UV = U-V; PBR = P-B-R.', '']
    for i, (seconds, title, words) in enumerate(CHAPTERS):
        start = sum(c[0] for c in CHAPTERS[:i])
        clock = lambda n: f'{n//60:02}:{n%60:02}'
        lines.extend([f'## {clock(start)}–{clock(start+seconds)} · {title}', '', words, ''])
    lines.extend(['## Handoff', '', 'Master: `VITVellore_AICA_Demo.mp4` (1920×1080, 24 fps, 120 seconds, H.264). Add the voice-over in your editor, preserve the 120-second timeline, and export H.264 at the same frame rate. Do not stretch the rendered motion excerpts. The analytical fixation diagram explains the separate research module, rather than the native GNM animation controller. A restrained licensed music bed can be added beneath the human voice if desired.', '', 'Engineering boundary: source test records cover 175 passing tests per platform. The clean Windows/Linux runtime comparison covers three held neutral frames. Independent human review and organizer-model matching remain outstanding. The video demonstrates offline synthesis, rather than measured headset deployment or real-time rendering.', ''])
    path.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submission-archive', type=Path, required=True)
    parser.add_argument('--work', type=Path, default=ROOT/'out/submission-demo-2min')
    parser.add_argument('--out', type=Path, default=ROOT/'VITVellore_AICA_Demo.mp4')
    parser.add_argument('--preview-only', action='store_true')
    args = parser.parse_args()
    edit = Edit(args.submission_archive, args.work)
    edit.preview()
    if not args.preview_only:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        receipt = edit.render(args.out)
        receipt['builder_sha256'] = sha(Path(__file__).read_bytes())
        (args.work/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
        write_script(ROOT/'docs/APOLLO_DEMO_VOICEOVER.md')
        print('VERIFIED_TWO_MINUTE_MASTER', args.out, flush=True)
