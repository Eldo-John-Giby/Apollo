import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

parser = argparse.ArgumentParser(description='Measure and repair projection misses on the GNM skin atlas.')
parser.add_argument('--template', type=Path, required=True)
parser.add_argument('--bake', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
with Image.open(args.bake) as image:
    rgb = np.array(image.convert('RGB'))
h, w = rgb.shape[:2]
with np.load(args.template) as data:
    uv = data['legacy'][data['tiles'] == 1001]
coords = np.rint(uv * (w - 1, -(h - 1)) + (0, h - 1)).astype(np.int32)
skin = np.zeros((h, w), dtype=np.uint8)
cv2.fillPoly(skin, list(coords), 1)
# OpenCV's joint even/odd fill can leave shared edges; fill per quad for a union.
for quad in coords:
    cv2.fillConvexPoly(skin, quad, 1)
hit = rgb.max(axis=2) > 5
missing = skin.astype(bool) & ~hit
if not np.any(hit):
    raise ValueError('No usable projection in the skin bake')
distance, index = distance_transform_edt(~hit, return_indices=True)
filled = rgb[tuple(index)]
Image.fromarray(filled).save(args.out)
report = {'expected_texels': int(skin.sum()), 'filled_texels': int(missing.sum()),
          'projection_coverage': 1 - float(missing.sum() / skin.sum()),
          'max_fill_distance_px': float(distance[missing].max()) if missing.any() else 0}
args.out.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
print(report)
