"""Add skin and eye surface detail and vertical lid motion to the packed portrait."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'build'))
from portrait_refinement import eyes, eye_meshes, shader, smoothstep


def skin_detail(face):
    mat = next(m for m in face.data.materials if m.name.endswith('.body'))
    p = shader(mat)
    bump = p.inputs['Normal'].links[0].from_node
    bump.inputs['Distance'].default_value = .000032
    bump.inputs['Strength'].default_value = .20
    rough = p.inputs['Roughness'].links[0].from_node
    attr = face.data.attributes.new('Apollo facial oil distribution', 'FLOAT', 'POINT')
    values = []
    for vertex in face.data.vertices:
        x, y, z = face.matrix_world @ vertex.co
        nose = math.exp(-(x/.018)**2-((z+.031)/.032)**2)
        forehead = math.exp(-(x/.039)**2-((z-.040)/.028)**2)
        values.append(max(nose, forehead)*smoothstep((.065-y)/.040))
    attr.data.foreach_set('value', values)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    mask = nodes.new('ShaderNodeAttribute')
    mask.attribute_name = attr.name
    balance = nodes.new('ShaderNodeMath')
    balance.operation = 'MULTIPLY_ADD'
    balance.inputs[1].default_value = -.085
    links.new(mask.outputs['Fac'], balance.inputs[0])
    links.new(rough.outputs[0], balance.inputs[2])
    links.new(balance.outputs[0], p.inputs['Roughness'])


def iris_reflection():
    mat = bpy.data.objects['Iris.L'].data.materials[0]
    p = shader(mat)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    uv = next(node for node in nodes if node.type == 'TEX_COORD')
    separate = nodes.new('ShaderNodeSeparateXYZ')
    links.new(uv.outputs['UV'], separate.inputs[0])
    dome = nodes.new('ShaderNodeCombineXYZ')
    links.new(separate.outputs['X'], dome.inputs['X'])
    links.new(separate.outputs['Y'], dome.inputs['Y'])
    dome.inputs['Z'].default_value = 1
    normal = nodes.new('ShaderNodeNormalMap')
    normal.inputs['Strength'].default_value = .85
    links.new(dome.outputs[0], normal.inputs['Color'])
    links.new(normal.outputs[0], p.inputs['Coat Normal'])
    p.inputs['Coat Weight'].default_value = .48
    p.inputs['Coat Roughness'].default_value = .09


def moving_lids(face, ipd):
    target = bpy.data.objects['FixationTarget']
    objects = [face] + [bpy.data.objects[name] for name in (
        'Apollo lid wet margins', 'Apollo tapered eyelashes', 'Apollo upper lid crease')]
    for obj in objects:
        obj.shape_key_add(name='Basis')
        follow = obj.shape_key_add(name='Vertical lid follow')
        follow.slider_min = -1
        inverse = obj.matrix_world.inverted()
        for vertex, key in zip(obj.data.vertices, follow.data):
            point = obj.matrix_world @ vertex.co
            lateral = abs(abs(point.x)-ipd/2)
            across = smoothstep((.015-lateral)/.006)
            upper = smoothstep((point.z+.001)/.003)*smoothstep((.015-point.z)/.008)
            lower = smoothstep(-point.z/.002)*smoothstep((point.z+.011)/.006)
            depth = smoothstep((.005-point.y)/.010)
            point.z += across*depth*(.0010*upper + .00022*lower)
            key.co = inverse @ point
        driver = follow.driver_add('value').driver
        variable = driver.variables.new()
        variable.name = 'height'
        variable.type = 'TRANSFORMS'
        variable.targets[0].id = target
        variable.targets[0].transform_type = 'LOC_Z'
        variable.targets[0].transform_space = 'WORLD_SPACE'
        driver.expression = 'min(1,max(-1,height*20))'
    return objects


def build(output):
    source = Path(bpy.data.filepath)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    output = output.resolve()
    if output.exists() or output == source.resolve():
        raise ValueError('Use a new scene path')
    eyes.reset()
    calibration = eyes.calibration()
    protected = eye_meshes()
    face = bpy.data.objects['Apollo_Face']
    skin_detail(face)
    iris_reflection()
    lids = moving_lids(face, calibration['ipd'])
    values = {}
    for vertical in (-1, 0, 1):
        eyes.move(0, vertical)
        bpy.context.view_layer.update()
        weights = [obj.data.shape_keys.key_blocks['Vertical lid follow'].value for obj in lids]
        if any(abs(weight-vertical) > .001 for weight in weights):
            raise RuntimeError(f'Lid response at {vertical}: {weights}')
        values[vertical] = weights
    eyes.reset()
    assert calibration == eyes.calibration() and protected == eye_meshes()
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
    output.with_suffix('.json').write_text(json.dumps({
        'source_sha256': source_hash,
        'scene_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'lid_weights': values,
    }, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    build(parser.parse_args(sys.argv[sys.argv.index('--')+1:]).out)
