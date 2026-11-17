"""Lay out the saved baseline renders without resampling the detail crops."""
from pathlib import Path
import sys

from PIL import Image, ImageDraw


root = Path(__file__).resolve().parent

if '--final' in sys.argv:
    comparison = Image.new('RGB', (1424, 744), '#202020')
    label = ImageDraw.Draw(comparison)
    for x, title, path in (
        (8, 'Baseline, fixed camera', root/'00_baseline/front.png'),
        (716, 'Overhaul, fixed camera', root/'05_eval.png'),
    ):
        with Image.open(path) as image:
            panel = image.resize((700, 700), Image.Resampling.LANCZOS)
        label.text((x, 9), title, fill='white')
        comparison.paste(panel, (x, 33))
    comparison.save(root/'baseline_vs_overhaul.png')
    final_sheet = Image.new('RGB', (1500, 1050), '#202020')
    label = ImageDraw.Draw(final_sheet)
    with Image.open(root/'final_composited.png') as image:
        panel = image.resize((820, 820), Image.Resampling.LANCZOS)
    label.text((12, 16), 'Final portrait', fill='white')
    final_sheet.paste(panel, (12, 41))
    y = 16
    for name in ('eyes', 'mouth', 'cheek', 'hairline'):
        label.text((850, y), name + ' at 100%', fill='white')
        with Image.open(root/f'final_{name}.png') as image:
            final_sheet.paste(image, (850, y+20))
            y += image.height+35
    final_sheet.save(root/'final_contact_sheet.png')
    sys.exit(0)

source = root/'00_baseline'
sheet = Image.new('RGB', (1600, 1090), '#202020')
draw = ImageDraw.Draw(sheet)
panels = (
    ('front', 'Fixed front', (12, 15), (512, 512)),
    ('three-quarter-left', 'Three-quarter A', (544, 15), (512, 512)),
    ('three-quarter-right', 'Three-quarter B', (1076, 15), (512, 512)),
    ('eyes', 'Eyes at 100%', (12, 575), None),
    ('mouth', 'Mouth at 100%', (594, 575), None),
    ('hairline', 'Hairline at 100%', (12, 825), None),
)
for name, title, (x, y), size in panels:
    with Image.open(source/f'{name}.png') as image:
        panel = image.copy()
        if size:
            panel.thumbnail(size, Image.Resampling.LANCZOS)
        draw.text((x, y), title, fill='white')
        sheet.paste(panel, (x, y+23))
sheet.save(root/'00_baseline_contact_sheet.png')
