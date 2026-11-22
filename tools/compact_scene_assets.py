"""Losslessly externalize packed images in a derived judge-package scene (Blender)."""
import bpy
import hashlib
import json
import os
import sys
from pathlib import Path

target = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
root = Path(sys.argv[sys.argv.index('--') + 2]).resolve()
index = json.loads((root / 'asset-index.json').read_text())
records = []
for image in bpy.data.images:
    if not image.packed_files:
        continue
    if image.source != 'FILE' or len(image.packed_files) != 1:
        raise RuntimeError('Unsupported packed image: ' + image.name)
    data = bytes(image.packed_file.data)
    digest = hashlib.sha256(data).hexdigest()
    relative = index.get(digest, 'assets/' + digest + '.png')
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(data)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    image.unpack(method='REMOVE')
    image.filepath = '//' + os.path.relpath(path, target.parent).replace('\\', '/')
    records.append({'image': image.name, 'path': relative, 'sha256': digest})
target.parent.mkdir(parents=True, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(target), compress=True, relative_remap=False)
target.with_suffix('.assets.json').write_text(json.dumps(records, indent=2) + '\n')
print('EXTERNALIZED', len(records), 'images', str(target), flush=True)
