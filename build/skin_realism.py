"""Add pore relief, skin tone variation and varying sheen to the packed portrait."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from portrait_refinement import eye_meshes, eyes, shader


def refine_skin(face):
    material = next(mat for mat in face.data.materials if mat.name.endswith('.body'))
    surface = shader(material)
    nodes, links = material.node_tree.nodes, material.node_tree.links
    coords = nodes.new('ShaderNodeTexCoord')
    geometry = nodes.new('ShaderNodeNewGeometry')
    axes = nodes.new('ShaderNodeSeparateXYZ')
    links.new(geometry.outputs['Position'], axes.inputs[0])
    face_mask = nodes.new('ShaderNodeMapRange')
    face_mask.interpolation_type = 'SMOOTHERSTEP'
    face_mask.inputs['From Min'].default_value = -.152
    face_mask.inputs['From Max'].default_value = -.097
    face_mask.inputs['To Min'].default_value = .25
    links.new(axes.outputs['Z'], face_mask.inputs['Value'])

    # Millimeter-scale variation in skin pigment and sheen.
    patches = nodes.new('ShaderNodeTexNoise')
    patches.label = 'Fine complexion variation'
    patches.inputs['Scale'].default_value = 280
    patches.inputs['Detail'].default_value = 2
    links.new(coords.outputs['Object'], patches.inputs['Vector'])
    tint = nodes.new('ShaderNodeValToRGB')
    tint.color_ramp.elements[0].position = .22
    tint.color_ramp.elements[0].color = (.82, .68, .67, 1)
    tint.color_ramp.elements[1].position = .78
    tint.color_ramp.elements[1].color = (1.12, 1.08, 1.05, 1)
    links.new(patches.outputs['Fac'], tint.inputs['Fac'])
    brow = next(n for n in nodes if n.label == 'Soft espresso pigment beneath brow fibers')
    color = nodes.new('ShaderNodeMixRGB')
    color.blend_type = 'MULTIPLY'
    tint_weight = nodes.new('ShaderNodeMath')
    tint_weight.operation = 'MULTIPLY'
    tint_weight.inputs[1].default_value = .34
    links.new(face_mask.outputs[0], tint_weight.inputs[0])
    links.new(tint_weight.outputs[0], color.inputs[0])
    links.new(brow.inputs[1].links[0].from_socket, color.inputs[1])
    links.new(tint.outputs[0], color.inputs[2])
    links.new(color.outputs[0], brow.inputs[1])

    # Preserve the existing fine grain and add shallow depressions for pores.
    pores = nodes.new('ShaderNodeTexVoronoi')
    pores.label = 'Skin pores'
    pores.inputs['Scale'].default_value = 2950
    links.new(coords.outputs['Object'], pores.inputs['Vector'])
    relief = nodes.new('ShaderNodeMapRange')
    relief.interpolation_type = 'SMOOTHERSTEP'
    relief.inputs['From Min'].default_value = .10
    relief.inputs['From Max'].default_value = .37
    links.new(pores.outputs['Distance'], relief.inputs['Value'])
    bump = nodes.new('ShaderNodeBump')
    bump.label = 'Shallow pore relief'
    bump.inputs['Distance'].default_value = .000060
    pore_weight = nodes.new('ShaderNodeMath')
    pore_weight.operation = 'MULTIPLY'
    pore_weight.inputs[1].default_value = .30
    links.new(face_mask.outputs[0], pore_weight.inputs[0])
    links.new(pore_weight.outputs[0], bump.inputs['Strength'])
    links.new(surface.inputs['Normal'].links[0].from_socket, bump.inputs['Normal'])
    links.new(relief.outputs[0], bump.inputs['Height'])
    links.new(bump.outputs[0], surface.inputs['Normal'])

    roughness = nodes.new('ShaderNodeMapRange')
    roughness.inputs['To Min'].default_value = -.025
    roughness.inputs['To Max'].default_value = .115
    links.new(patches.outputs['Fac'], roughness.inputs['Value'])
    balance = nodes.new('ShaderNodeMath')
    balance.operation = 'ADD'
    links.new(surface.inputs['Roughness'].links[0].from_socket, balance.inputs[0])
    links.new(roughness.outputs[0], balance.inputs[1])
    links.new(balance.outputs[0], surface.inputs['Roughness'])
    surface.inputs['Specular IOR Level'].default_value = .25
    surface.inputs['Subsurface Weight'].default_value = .060


def build(output):
    source = Path(bpy.data.filepath).resolve()
    output = output.resolve()
    if output.exists():
        raise ValueError('Use a new scene path')
    eyes.reset()
    protected, calibration = eye_meshes(), eyes.calibration()
    refine_skin(bpy.data.objects['Apollo_Face'])
    assert protected == eye_meshes() and calibration == eyes.calibration()
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
    output.with_suffix('.json').write_text(json.dumps({
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'scene_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'recipe_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    build(parser.parse_args(sys.argv[sys.argv.index('--')+1:]).out)
