"""Remove authoring paths from packed GNM images without changing their bytes."""
import argparse
import hashlib
import os
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_run import surface_files


def relative_images(maps, destination, map_root=None):
    maps = Path(maps)
    if map_root is None:
        try:
            map_root = '//' + os.path.relpath(maps.resolve(), Path(destination).resolve().parent)
        except ValueError:  # Different Windows drives; images remain self-contained.
            map_root = '//textures/' + maps.name
    map_root = map_root.replace('\\', '/').rstrip('/')
    if not map_root.startswith('//'):
        raise ValueError('Packed map root must be Blender-relative (//...)')
    paths = [maps / f'color.{tile}.png' for tile in (1001, 1002, 1004)]
    paths.extend(surface_files(maps).values())
    expected = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    for image in bpy.data.images:
        if image.source not in ('FILE', 'TILED'):
            continue
        if not image.packed_file or len(image.packed_files) != 1:
            raise ValueError(f'Expected one packed image payload: {image.name}')
        original = bytes(image.packed_file.data)
        digest = hashlib.sha256(original).hexdigest()
        name = image.filepath.replace('\\', '/').rsplit('/', 1)[-1]
        # Retained, unused material nodes may still own an older image. Give
        # these a unique unpack location instead of colliding with active maps.
        path = (f'{map_root}/{name}' if expected.get(name) == digest
                else f'//packed/{digest[:16]}-{name}')
        image.filepath = path
        image.packed_files[0].filepath = path
        if bytes(image.packed_file.data) != original:
            raise ValueError(f'Changing an image path changed its payload: {image.name}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maps', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--map-root', help='Relative image directory in the delivered archive')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    if args.out.exists():
        raise FileExistsError(args.out)
    bpy.ops.file.pack_all()
    relative_images(args.maps, args.out, args.map_root)
    bpy.context.scene.render.filepath = '//frames/frame_'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.out.resolve()), compress=True,
                              relative_remap=False)


if __name__ == '__main__':
    main()
