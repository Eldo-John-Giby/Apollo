"""Add regional complexion and sheen to the isolated GNM portrait."""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_feedback_still import coords, product
from gnm_portrait_refine import aim, render, smooth


def complexion(head):
    tree = head.data.materials[0].node_tree
    nodes, links = tree.nodes, tree.links
    shader = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
    x, y, z = coords(head.data.vertices).T
    side = np.abs(x)
    front = smooth((z-.080)/.027)
    cheeks = np.exp(-((side-.042)/.026)**2-((y-.275-.010*x)/.020)**2)
    nose = np.exp(-(x/.016)**2-((y-.271)/.018)**2)
    orbital = np.exp(-((side-.032)/.021)**2-((y-.290-.025*x)/.009)**2)
    forehead = np.exp(-(x/.031)**2-((y-.342)/.026)**2)

    def mask(name, values):
        attribute = head.data.attributes.new(name, 'FLOAT', 'POINT')
        attribute.data.foreach_set('value', values.astype(np.float32))
        node = nodes.new('ShaderNodeAttribute')
        node.attribute_name = attribute.name
        return node.outputs['Fac']

    def tint(source, factor, name, rgb):
        node = nodes.new('ShaderNodeMixRGB')
        node.blend_type = 'MULTIPLY'
        node.label = name
        node.inputs[2].default_value = (*rgb, 1)
        links.new(source, node.inputs[1])
        links.new(factor, node.inputs[0])
        return node.outputs[0]

    source = shader.inputs['Base Color'].links[0].from_socket
    color = tint(source, mask('Cheek and nasal color', front*(.82*cheeks+.52*nose)),
                 'Warm cheeks and nose', (1.0, .813, .802))
    color = tint(color, mask('Infraorbital color', front*orbital),
                 'Muted undertone below the lower eyelids', (.80, .823, .91))

    coordinates = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.label = 'Broad irregular undertone'
    noise.inputs['Scale'].default_value = 205
    noise.inputs['Detail'].default_value = 2.6
    links.new(coordinates.outputs['Object'], noise.inputs['Vector'])
    color = tint(color, noise.outputs['Fac'], 'Low contrast complexion mottling', (.91, .855, .846))
    links.new(color, shader.inputs['Base Color'])

    # Keep the forehead and nasal bridge slightly oilier than the cheeks.
    region = mask('Regional skin sheen', front*(.70*nose+.78*forehead))
    roughness = nodes.new('ShaderNodeMath')
    roughness.operation = 'SUBTRACT'
    links.new(shader.inputs['Roughness'].links[0].from_socket, roughness.inputs[0])
    links.new(product(nodes, links, region, .080), roughness.inputs[1])
    links.new(roughness.outputs[0], shader.inputs['Roughness'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args(sys.argv[sys.argv.index('--')+1:]).out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    path = out/'portrait.blend'
    if path.exists():
        raise FileExistsError(path)
    scene = bpy.context.scene
    complexion(scene.objects['GNM Head'])
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
    render(scene, out, 'front', 850, 32)
    aim(scene.camera, (.40, -.72, .03), (0, 0, -.025))
    render(scene, out, 'three-quarter', 850, 32)
    scene.render.use_border = True
    scene.render.use_crop_to_border = True
    scene.render.border_min_x = .28
    scene.render.border_max_x = .76
    scene.render.border_min_y = .21
    scene.render.border_max_y = .71
    render(scene, out, 'face-detail', 1350, 48)


if __name__ == '__main__':
    main()
