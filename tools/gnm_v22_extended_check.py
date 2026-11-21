"""Reopen and compare extended animation channels and assets to the original scene."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def channels():
    return {(action.name, curve.data_path, curve.array_index): curve
            for action in bpy.data.actions for curve in action.fcurves}


def geometry_signature():
    h = hashlib.sha256()
    for name in ('GNM Head', 'Apollo | native motion reference'):
        obj = bpy.context.scene.objects[name]
        assert not obj.modifiers, name
        for key in obj.data.shape_keys.key_blocks:
            data = np.empty(len(key.data)*3, dtype=np.float32)
            key.data.foreach_get('co', data)
            h.update(key.name.encode());h.update(data.tobytes())
        for uv in obj.data.uv_layers:
            data = np.empty(len(uv.data)*2, dtype=np.float32)
            uv.data.foreach_get('uv', data)
            h.update(uv.name.encode());h.update(data.tobytes())
        h.update(str([tuple(p.vertices) for p in obj.data.polygons]).encode())
    return h.hexdigest()


def packed_images():
    return {im.name: hashlib.sha256(bytes(im.packed_file.data)).hexdigest()
            for im in bpy.data.images if im.source in ('FILE', 'TILED')}


def material_signature():
    # Authenticate material nodes and defaults, without hashing incidental UI positions.
    records = []
    for material in bpy.data.materials:
        if not material.use_nodes:
            records.append((material.name, tuple(material.diffuse_color)))
            continue
        nodes = []
        for node in material.node_tree.nodes:
            values = []
            for socket in node.inputs:
                if hasattr(socket, 'default_value'):
                    value = socket.default_value
                    if isinstance(value, (int, float, str, bool)):
                        values.append((socket.identifier, value))
                    elif hasattr(value, '__iter__'):
                        values.append((socket.identifier, list(value)))
            nodes.append((node.name, node.bl_idname, values,
                          getattr(getattr(node, 'image', None), 'name', None)))
        links = [(l.from_node.name, l.from_socket.identifier,
                  l.to_node.name, l.to_socket.identifier) for l in material.node_tree.links]
        records.append((material.name, nodes, links))
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()


def main(args):
    extended = Path(bpy.data.filepath)
    report = json.loads(extended.with_suffix('.extension.json').read_text())
    assert sha(extended) == report['scene_sha256']
    assert sha(args.source) == report['original_scene_sha256']
    assert bpy.context.scene.frame_end == 288 and not bpy.data.libraries
    current = channels()
    # Original quarter-frame samples plus every added frame.
    times = [1+i*.25 for i in range(765)] + list(range(193, 289))
    expected_times = [float(t) if t <= 192 else report['source_frames'][int(t)-1]
                      for t in times]
    values = {key: [float(curve.evaluate(t)) for t in times] for key, curve in current.items()}
    geometry, images, materials = geometry_signature(), packed_images(), material_signature()
    bpy.ops.wm.open_mainfile(filepath=str(args.source.resolve()), load_ui=False)
    reference = channels()
    assert set(reference) == set(values), 'Animated channels were added or lost'
    worst = max(abs(value-float(reference[key].evaluate(t)))
                for key, series in values.items() for value, t in zip(series, expected_times))
    assert worst < 1e-6, ('Reopened channel mismatch', worst)
    assert geometry == geometry_signature(), 'Geometry or UV changed'
    assert images == packed_images(), 'Packed textures changed'
    assert materials == material_signature(), 'Shaders changed'
    result = dict(passed=True, mode=report['mode'], scene_sha256=report['scene_sha256'],
                  original_scene_sha256=report['original_scene_sha256'],
                  checked_times=len(times), animated_channels=len(reference),
                  maximum_channel_error=worst, geometry_uv_unchanged=True,
                  packed_textures_unchanged=True, shaders_unchanged=True,
                  recipe_sha256=sha(__file__),
                  qualification='Fresh-process scene/channel/asset comparison. Human motion review remains separate.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print('EXTENSION_REOPEN_CHECK', json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args(sys.argv[sys.argv.index('--')+1:]))
