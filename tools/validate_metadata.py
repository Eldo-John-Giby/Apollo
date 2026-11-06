"""Validate shipped image and metadata artifacts without Blender."""
import argparse
from pathlib import Path
import sys
import json
import jsonschema
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from gazeforge_core.metadata import load
from PIL import Image


def validate_artifacts(folder):
    folder = Path(folder)
    records = load(folder/'metadata.json')
    schema = json.loads((ROOT/'metadata.schema.json').read_text(encoding='utf-8'))
    jsonschema.Draft202012Validator(schema).validate(records)
    expected = {f'frame_{k:02d}.png' for k in range(10)}
    actual = {p.name for p in (folder/'renders').glob('*.png')}
    if actual != expected:
        raise ValueError('Expected exactly frame_00.png through frame_09.png')
    for name in sorted(expected):
        with Image.open(folder/'renders'/name) as im:
            if im.size != (1024,1024) or im.format != 'PNG':
                raise ValueError(f'Invalid image: {name}')
            im.verify()
    return records

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder',type=Path)
    args = parser.parse_args()
    validate_artifacts(args.folder)
    print('PASS: ten-frame artifacts')
