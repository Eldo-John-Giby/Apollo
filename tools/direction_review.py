"""Build shuffled baseline/pose pairs for a human direction review."""
import argparse
import csv
import hashlib
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(candidate, output, seed):
    candidate = candidate.resolve()
    output = output.resolve()
    if output.exists():
        raise ValueError('Choose a new output directory')

    source = candidate/'evidence/directions'
    manifest = json.loads((candidate/'manifest.json').read_text(encoding='utf-8'))
    progress = json.loads((source/'progress.json').read_text(encoding='utf-8'))
    scene_hash = digest(candidate/'scene.blend')
    if progress['scene_sha256'] != scene_hash:
        raise ValueError('Direction evidence belongs to a different scene')
    names = ['baseline', 'left', 'right', 'up', 'down', 'reset']
    for path in [source/'progress.json', *[source/(name+'.png') for name in names]]:
        relative = path.relative_to(candidate).as_posix()
        if digest(path) != manifest['files'][relative]:
            raise ValueError('Source evidence hash mismatch for '+relative)
    if digest(source/'baseline.png') != digest(source/'reset.png'):
        raise ValueError('Reset must match the baseline')

    images = {}
    for name in names:
        with Image.open(source/(name+'.png')) as image:
            if image.size != (1024, 1024):
                raise ValueError('Expected native 1024-square source frames')
            images[name] = image.convert('RGB')

    order = names[1:]
    random.Random(seed).shuffle(order)
    participant = output/'participant'
    assessor = output/'assessor'
    participant.mkdir(parents=True)
    assessor.mkdir()
    try:
        font = ImageFont.truetype('arial.ttf', 28)
    except OSError:
        font = ImageFont.load_default(size=28)
    answers = []
    for index, name in enumerate(order, start=1):
        case = f'{index:02d}'
        pair = Image.new('RGB', (2048, 1104), '#20252d')
        pair.paste(images['baseline'], (0, 80))
        pair.paste(images[name], (1024, 80))
        draw = ImageDraw.Draw(pair)
        draw.text((24, 24), 'CENTER REFERENCE', font=font, fill='white')
        draw.text((1048, 24), 'TEST IMAGE '+case, font=font, fill='white')
        pair.save(participant/f'case-{case}.png')
        # Identical fixed crops preserve scale and pupil displacement.
        crop_box = (180, 410, 840, 590)
        eyes = Image.new('RGB', (1320, 240), '#20252d')
        eyes.paste(images['baseline'].crop(crop_box), (0, 60))
        eyes.paste(images[name].crop(crop_box), (660, 60))
        draw = ImageDraw.Draw(eyes)
        draw.text((16, 16), 'CENTER', font=font, fill='white')
        draw.text((676, 16), 'TEST '+case, font=font, fill='white')
        eyes.save(assessor/f'eye-detail-{case}.png')
        answers.append({'case': case, 'expected': name,
                        'image_sha256': digest(participant/f'case-{case}.png'),
                        'source_sha256': digest(source/(name+'.png'))})

    with (participant/'responses.csv').open('w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['observer', 'case', 'answer', 'confidence_1_to_5',
                         'which_eye_was_unclear', 'comments'])
        for observer in ['A', 'B', 'C']:
            for index in range(1, 6):
                writer.writerow([observer, f'{index:02d}', '', '', '', ''])

    instructions = """# Human direction review

Open only the participant folder when showing the test.
Show one case at a time with both panels visible at equal size. The left panel
is the center reference and the right panel is the test pose. Zoom the whole
pair uniformly if needed. Allow the observer to compare both eyes against center.

Ask which way the gaze changed relative to center, using the viewer's image
directions. Accept left, right, up, down, same or unsure. Ask for confidence from
1 to 5 and record any eye-specific confusion in responses.csv. For same, ask
whether they see a change. Keep the assessor folder hidden until all first-pass
answers are recorded. Avoid describing the previous observer's feedback.

After the first pass, the assessor may show the equally cropped eye-detail pair
and ask the question again. Record that as a separate second-pass observation.
The answer key describes image-space movement. The reset case matches center.
Three observer slots are provided. Leave unavailable answers blank.
"""
    (output/'RUN_TEST.md').write_text(instructions, encoding='utf-8')
    key = {'scene_sha256': scene_hash, 'shuffle_seed': seed,
           'coordinate_convention': 'viewer image directions', 'answers': answers,
           'source': str(source), 'operation': 'Unaltered native RGB images paired at equal scale',
           'responses_collected': False}
    (assessor/'answer-key.json').write_text(json.dumps(key, indent=2)+'\n', encoding='utf-8')
    lines = ['# Assessor answer key', '', '| Case | Expected answer |', '| --- | --- |']
    for answer in answers:
        expected = 'same / reset' if answer['expected'] == 'reset' else answer['expected']
        lines.append(f"| {answer['case']} | {expected} |")
    (assessor/'ANSWER_KEY.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('Created five baseline-paired cases and separate assessor key at', output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--seed', type=int, default=20261111)
    args = parser.parse_args()
    build(args.candidate, args.out, args.seed)
