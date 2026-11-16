"""Refine canthal sclera tone and corneal reflection under matched lighting."""
import argparse
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_lash_study import eye_crop
from gnm_portrait_refine import render


def ocular_materials(head):
    for eye, (surface_slot, cornea_slot) in enumerate(((1, 2), (3, 4))):
        tree = head.data.materials[surface_slot].node_tree
        surface = next(node for node in tree.nodes if node.type == 'BSDF_PRINCIPLED')
        color = surface.inputs['Base Color'].links[0].from_socket
        coords = tree.nodes.new('ShaderNodeTexCoord')
        axes = tree.nodes.new('ShaderNodeSeparateXYZ')
        tree.links.new(coords.outputs['Object'], axes.inputs[0])
        x = tree.nodes.new('ShaderNodeMath')
        x.operation = 'ABSOLUTE'
        tree.links.new(axes.outputs['X'], x.inputs[0])
        tone = tree.nodes.new('ShaderNodeMapRange')
        tone.label = 'Medial sclera and caruncle color transition'
        tone.interpolation_type = 'SMOOTHSTEP'
        tone.inputs['From Min'].default_value = .0180 if eye == 0 else .0185
        tone.inputs['From Max'].default_value = .0245
        tone.inputs['To Min'].default_value = .94
        tone.inputs['To Max'].default_value = 0
        tree.links.new(x.outputs[0], tone.inputs['Value'])

        tint = tree.nodes.new('ShaderNodeMixRGB')
        tint.label = 'Warm tissue at the inner corner'
        tint.blend_type = 'MULTIPLY'
        tint.inputs[2].default_value = (.88, .72, .68, 1)
        tree.links.new(tone.outputs[0], tint.inputs[0])
        tree.links.new(color, tint.inputs[1])
        tree.links.new(tint.outputs[0], surface.inputs['Base Color'])
        surface.inputs['Specular IOR Level'].default_value = .035

        cornea = head.data.materials[cornea_slot].node_tree
        film = next(node for node in cornea.nodes if node.type == 'BSDF_GLASS')
        film.inputs['Roughness'].default_value = .028


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args(sys.argv[sys.argv.index('--')+1:]).out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    path = out/'portrait.blend'
    if path.exists():
        raise FileExistsError(path)
    scene = bpy.context.scene
    ocular_materials(scene.objects['GNM Head'])
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
    eye_crop(scene, out, 'eyes-after')
    render(scene, out, 'front', 850, 32)


if __name__ == '__main__':
    main()
