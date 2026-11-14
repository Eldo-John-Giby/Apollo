"""Pack a texture variant onto an existing GNM timeline without changing its rig."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_materials import bind_surface, surface_files
from gnm_run import variant_identity


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(args):
    source = Path(bpy.data.filepath)
    tiles = (1001, 1002, 1004)
    maps = {str(tile): args.maps / f'color.{tile}.png' for tile in tiles}
    maps.update(surface_files(args.maps))
    identity = variant_identity(source, args.maps, args.layout)
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / f'variant-{key}.blend'
    receipt = target.with_suffix('.json')
    if target.exists() or receipt.exists():
        stored = json.loads(receipt.read_text(encoding='utf-8'))
        if stored != {'inputs': identity, 'scene_sha256': digest(target)}:
            raise ValueError('Cached variant scene does not match its receipt')
        print(f'Verified cached variant timeline: {target}')
        return
    head = bpy.context.scene.objects['GNM Head']
    for tile in tiles:
        material = head.data.materials[tile - 1001]
        nodes, links = material.node_tree.nodes, material.node_tree.links
        shader = nodes.get('Principled BSDF')
        color = shader.inputs['Base Color']
        if len(color.links) != 1 or color.links[0].from_node.type != 'TEX_IMAGE':
            raise ValueError(f'Unexpected GNM base-color binding in tile {tile}')
        image = color.links[0].from_node
        image.image = bpy.data.images.load(str(maps[str(tile)].resolve()), check_existing=False)
        image.image.colorspace_settings.name = 'sRGB'
        image.image.pack()
        uv = nodes.new('ShaderNodeUVMap')
        uv.uv_map = 'GNM UDIM' if args.layout == 'udim' else 'GNM Region'
        coordinates = uv.outputs['UV']
        if args.layout == 'udim':
            offset = nodes.new('ShaderNodeVectorMath')
            offset.operation = 'SUBTRACT'
            offset.inputs[1].default_value = (tile - 1001, 0, 0)
            links.new(coordinates, offset.inputs[0])
            coordinates = offset.outputs[0]
        links.new(coordinates, image.inputs['Vector'])
        links.new(image.outputs['Color'], shader.inputs['Base Color'])
    bind_surface(head, args.maps, args.layout)
    bpy.context.scene['apollo_gnm_variant_inputs'] = json.dumps(identity, sort_keys=True)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(target.resolve()), compress=True)
    receipt.write_text(json.dumps({'inputs': identity, 'scene_sha256': digest(target)},
                                  indent=2) + '\n', encoding='utf-8')
    print(f'Packed variant timeline: {target}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maps', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--layout', choices=('udim', 'legacy'), required=True)
    prepare(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
