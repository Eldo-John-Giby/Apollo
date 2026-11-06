"""Measure and visualize the five-direction API check using image-only detectors."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw
from grader_sim import gray, detect, template_shift

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

CARDINALS = [('left', 0, -1), ('right', 0, 1), ('up', 1, -1), ('down', 1, 1)]


def measure(reference, images, reset_identical):
    """No commanded/metadata pupil coordinates are passed to either detector."""
    center = detect(reference)
    rows, failures = [], []
    for name, axis, sign in CARDINALS:
        found = detect(images[name])
        template = template_shift(reference, images[name])
        for side in 'LR':
            for detector, delta in [('ellipse', found[side]-center[side]),
                                    ('template', template[side])]:
                row = {'direction': name, 'eye': side, 'detector': detector,
                       'dx_px': float(delta[0]), 'dy_px': float(delta[1]),
                       'signed_motion_px': float(sign*delta[axis]),
                       'cross_axis_px': float(abs(delta[1-axis]))}
                row['passed'] = row['signed_motion_px'] >= 8 and row['cross_axis_px'] < .5
                rows.append(row)
                if not row['passed']:
                    failures.append(f'{name}/{side}/{detector}: motion={delta.tolist()}')
    reset_centers = detect(images['reset'])
    reset_error = max(float(np.linalg.norm(reset_centers[s]-center[s])) for s in 'LR')
    if not reset_identical:
        failures.append('Reset PNG is not byte-identical to the baseline')
    return {'passed': not failures, 'reset_identical': bool(reset_identical),
            'reset_detection_error_px': reset_error, 'measurements': rows,
            'failures': failures}


def create(folder):
    folder = Path(folder)
    evidence = folder/'verification'
    progress = json.loads((evidence/'progress.json').read_text())
    if 'reset_identical' not in progress:
        raise ValueError('Direction renders have not finished')
    reference = gray(evidence/'baseline.png')
    images = {n: gray(evidence/(n+'.png')) for n in ['left','right','up','down','reset']}
    report = measure(reference, images, progress['reset_identical'])
    # Independently compare measured template displacement with analytic metadata.
    # Detection has already completed without consulting those annotations.
    baseline = detect(reference)
    from apollo_core.core import Config, eye_state
    cfg = Config(**progress['config'])
    expected_center = eye_state(0,0,cfg)[0]
    maximum = 0.
    for name in images:
        measured = template_shift(reference, images[name])
        for side in 'LR':
            expected = (np.array(progress['directions'][name]['pupil_center_2D_'+side])
                        - expected_center[side]['pupil2d'])
            maximum = max(maximum, float(np.linalg.norm(measured[side]-expected)))
    report['max_template_annotation_error_px'] = maximum
    if maximum >= 1.5:
        report['passed'] = False
        report['failures'].append(f'Template annotation error {maximum:.6f} px')
    # Enlarged crops expose lid/lash interference and the actual small motion.
    sheet = Image.new('RGB', (1500, 690), '#151b24')
    draw = ImageDraw.Draw(sheet)
    for col, name in enumerate(['left','right','up','down','reset']):
        x = col*300
        draw.text((x+12,12), name.upper(), fill='white')
        with Image.open(evidence/(name+'.png')) as source:
            sheet.paste(source.resize((300,300)), (x,35))
            for row, side in enumerate(['R','L']):
                cx,cy = baseline[side]
                box = (int(cx)-85, int(cy)-40, int(cx)+85, int(cy)+40)
                crop = source.crop(box).resize((289,136))
                y = 360+row*160
                sheet.paste(crop,(x+5,y))
                draw.text((x+8,y-18), 'Anatomical '+side+' (1.7x)', fill='white')
                guide_x=x+5+(cx-box[0])*289/170
                guide_y=y+(cy-box[1])*136/80
                draw.line((guide_x,y,guide_x,y+136), fill='#777777')
                draw.line((x+5,guide_y,x+294,guide_y), fill='#777777')
    draw.text((12,673), 'Gray crosshairs mark baseline pupil centers; crops enlarged equally. '+
              ('PASS' if report['passed'] else 'FAIL: see direction_report.json'), fill='white')
    sheet.save(evidence/'directions.png')
    (evidence/'direction_report.json').write_text(json.dumps(report,indent=2)+'\n')
    lines = ['# Five-direction check', '', f"Passed: {report['passed']}",
             f"Reset byte-identical: {report['reset_identical']}",
             f"Maximum template/annotation error: {maximum:.6f} px", '',
             '| Direction | Eye | Detector | dx px | dy px | Pass |',
             '| --- | --- | --- | ---: | ---: | --- |']
    for r in report['measurements']:
        lines.append(f"| {r['direction']} | {r['eye']} | {r['detector']} | {r['dx_px']:.4f} | {r['dy_px']:.4f} | {r['passed']} |")
    lines += ['', *report['failures']]
    (evidence/'direction_report.md').write_text('\n'.join(lines)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    result = create(args.folder)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
