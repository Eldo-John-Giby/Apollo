"""Refine nose proportions and add freckles and lipstick to a packed Apollo scene."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from portrait_refinement import eye_meshes, eyes, shader, smoothstep


def refine_nose(face):
    world = face.matrix_world
    local_vector = world.inverted().to_3x3()
    keys = face.data.shape_keys
    for index, vertex in enumerate(face.data.vertices):
        x, y, z = world @ vertex.co
        band = smoothstep((-.016-z)/.015)*smoothstep((z+.068)/.017)
        lateral = smoothstep((.032-abs(x))/.014)
        front = smoothstep((-.004-y)/.018)
        weight = band*lateral*front
        if not weight:
            continue
        tip = math.exp(-(x/.019)**2-((z+.047)/.013)**2)
        delta = local_vector @ Vector((-.23*x*weight, .0025*tip*weight, 0))
        if keys:
            for block in keys.key_blocks:
                block.data[index].co += delta
        vertex.co += delta
    face.data.update()


def sharpen_jaw(face):
    world = face.matrix_world
    to_local = world.inverted().to_3x3()
    keys = face.data.shape_keys
    for index, vertex in enumerate(face.data.vertices):
        x, y, z = world @ vertex.co
        width = abs(x)
        if not (-.132 < z < -.055 and -.065 < y < .100):
            continue
        lower_face = smoothstep((-.055-z)/.018)*smoothstep((z+.132)/.014)
        side = smoothstep((width-.027)/.021)*smoothstep((.086-width)/.016)
        jaw_height = -.112 + .56*max(0, width-.023)
        ridge = math.exp(-((z-jaw_height)/.010)**2-((y-.033)/.050)**2)
        cheek = math.exp(-((z+.071)/.013)**2-((y-.008)/.040)**2)
        below = math.exp(-((z-jaw_height+.019)/.013)**2-((y-.030)/.043)**2)
        angle = math.exp(-((width-.061)/.015)**2-((y-.047)/.027)**2)
        chin = math.exp(-(width/.023)**2-((z+.108)/.012)**2)*smoothstep((.010-y)/.027)
        offset = to_local @ (lower_face * Vector((
            math.copysign(side, x)*((.004 + .004*angle)*ridge-.0018*cheek-.003*below),
            side*(.0014*cheek-.0015*ridge)-.0035*chin,
            -.004*angle*ridge*side,
        )))
        if keys:
            for block in keys.key_blocks:
                block.data[index].co += offset
        vertex.co += offset
    face.data.update()


def complexion(face, softer_freckles=False):
    material = next(m for m in face.data.materials if m.name.endswith('.body'))
    p = shader(material)
    nodes, links = material.node_tree.nodes, material.node_tree.links
    base = p.inputs['Base Color'].links[0].from_socket
    mask = face.data.attributes.new('Apollo cheek and nose pigment', 'FLOAT', 'POINT')
    weights = []
    for vertex in face.data.vertices:
        x, y, z = face.matrix_world @ vertex.co
        cheeks = math.exp(-((abs(x)-.042)/.021)**2-((z+.030)/.019)**2)
        nose = math.exp(-(x/.019)**2-((z+.029)/.018)**2)
        weights.append(max(cheeks, .82*nose)*smoothstep((.040-y)/.052))
    mask.data.foreach_set('value', weights)
    region = nodes.new('ShaderNodeAttribute')
    region.attribute_name = mask.name
    warmth = nodes.new('ShaderNodeMixRGB')
    warmth.blend_type = 'MULTIPLY'
    warmth.inputs[0].default_value = .62
    warmth.inputs[2].default_value = (.98, .79, .67, 1)
    links.new(base, warmth.inputs[1])
    flush = nodes.new('ShaderNodeMixRGB')
    flush.blend_type = 'MULTIPLY'
    flush.inputs[2].default_value = (1.01, .88, .86, 1)
    links.new(region.outputs['Fac'], flush.inputs[0])
    links.new(warmth.outputs[0], flush.inputs[1])

    coords = nodes.new('ShaderNodeTexCoord')
    cells = nodes.new('ShaderNodeTexVoronoi')
    cells.inputs['Scale'].default_value = 310
    links.new(coords.outputs['Object'], cells.inputs['Vector'])
    dot = nodes.new('ShaderNodeMapRange')
    dot.interpolation_type = 'SMOOTHERSTEP'
    dot.inputs['From Min'].default_value = .10
    dot.inputs['From Max'].default_value = .27 if softer_freckles else .32
    dot.inputs['To Min'].default_value = 1
    dot.inputs['To Max'].default_value = 0
    links.new(cells.outputs['Distance'], dot.inputs['Value'])
    amount = nodes.new('ShaderNodeMath')
    amount.operation = 'MULTIPLY'
    links.new(dot.outputs[0], amount.inputs[0])
    links.new(region.outputs['Fac'], amount.inputs[1])
    freckles = nodes.new('ShaderNodeMixRGB')
    freckles.label = 'Soft copper freckles across cheeks and nose'
    freckles.blend_type = 'MULTIPLY'
    freckles.inputs[2].default_value = (.72, .61, .54, 1) if softer_freckles else (.47, .34, .26, 1)
    links.new(amount.outputs[0], freckles.inputs[0])
    links.new(flush.outputs[0], freckles.inputs[1])
    links.new(freckles.outputs[0], p.inputs['Base Color'])


def lipstick(face):
    material = next(m for m in face.data.materials if m.name.endswith('.lips'))
    p = shader(material)
    nodes, links = material.node_tree.nodes, material.node_tree.links
    pigment = next(n for n in nodes if n.label == 'Feathered warm rose lip pigment')
    pigment.inputs[2].default_value = (.95, .39, .52, 1)
    folds = p.inputs['Normal'].links[0].from_node
    folds.inputs['Distance'].default_value = .00017
    rough = p.inputs['Roughness'].links[0].from_node
    rough.inputs['To Min'].default_value = .32
    rough.inputs['To Max'].default_value = .47
    p.inputs['Coat Roughness'].default_value = .34
    # Pigment settles into the same vertical relief that drives the lip normal.
    creases = nodes.new('ShaderNodeMapRange')
    creases.inputs['From Min'].default_value = .25
    creases.inputs['From Max'].default_value = .49
    creases.inputs['To Min'].default_value = .7
    creases.inputs['To Max'].default_value = 0
    links.new(folds.inputs['Height'].links[0].from_socket, creases.inputs['Value'])
    intensity = nodes.new('ShaderNodeMath')
    intensity.operation = 'MULTIPLY'
    links.new(creases.outputs[0], intensity.inputs[0])
    links.new(folds.inputs['Strength'].links[0].from_socket, intensity.inputs[1])
    groove_color = nodes.new('ShaderNodeMixRGB')
    groove_color.blend_type = 'MULTIPLY'
    groove_color.inputs[2].default_value = (.56, .35, .45, 1)
    links.new(intensity.outputs[0], groove_color.inputs[0])
    links.new(pigment.outputs[0], groove_color.inputs[1])
    links.new(groove_color.outputs[0], p.inputs['Base Color'])


def build(output, defined_jaw=False):
    source = Path(bpy.data.filepath).resolve()
    output = output.resolve()
    if output.exists():
        raise ValueError('Use a new scene path')
    eyes.reset()
    protected, calibration = eye_meshes(), eyes.calibration()
    face = bpy.data.objects['Apollo_Face']
    refine_nose(face)
    if defined_jaw:
        sharpen_jaw(face)
    complexion(face, softer_freckles=defined_jaw)
    lipstick(face)
    for vertical in (-1, 0, 1):
        eyes.move(0, vertical)
        bpy.context.view_layer.update()
        key = face.data.shape_keys.key_blocks['Vertical lid follow']
        assert abs(key.value-vertical) < .001
    eyes.reset()
    assert eye_meshes() == protected and eyes.calibration() == calibration
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
    output.with_suffix('.json').write_text(json.dumps({
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'scene_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'recipe_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'defined_jaw': defined_jaw,
    }, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--defined-jaw', action='store_true', help='Define the jaw and soften freckles')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    build(args.out, defined_jaw=args.defined_jaw)
