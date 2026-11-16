"""Lay out the saved baseline renders without resampling the detail crops."""
from pathlib import Path

from PIL import Image, ImageDraw


root = Path(__file__).resolve().parent
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
