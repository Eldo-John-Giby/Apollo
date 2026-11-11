"""Add feathered brow pigment beneath the existing Apollo hair groom."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from portrait_refinement import eye_meshes, eyes, shader


def smooth(x):
    t = np.clip(x, 0, 1)
    return t*t*(3-2*t)


def fill_brows(face):
    # Project a soft pigment mask in the same world coordinates as the groom.
    # Keep the individual fibers, which supply the directional detail at its edges.
    xmin, xmax, zmin, zmax = -.065, .065, .004, .026
    width, height = 768, 160
    x, z = np.meshgrid(xmin+(np.arange(width)+.5)*(xmax-xmin)/width,
                       zmin+(np.arange(height)+.5)*(zmax-zmin)/height)
    t = (np.abs(x)-.0135)/.0465
    u = np.clip(t, 0, 1)
    center = .0122+.0051*np.sin(np.pi*u)-.0027*u**3
    center += np.sign(x)*.00025*np.sin(np.pi*u)
    thickness = .00305*(1-.90*u**2)*smooth(u/.14+.60)
    edge = np.abs(z-center)/thickness
    opacity = .91*smooth((1-edge)/.39)*smooth(t/.13)*smooth((1-t)/.09)
    pixels = np.ones((height,width,4), dtype=np.float32)
    pixels[:,:,:3] = opacity[:,:,None]
    image = bpy.data.images.new('Apollo feathered brow coverage', width=width, height=height)
    image.colorspace_settings.name = 'Non-Color'
    image.pixels.foreach_set(pixels.ravel())
    image.update()
    image.pack()

    material = next(m for m in face.data.materials if m.name.endswith('.body'))
    surface = shader(material)
    nodes, links = material.node_tree.nodes, material.node_tree.links
    base = surface.inputs['Base Color'].links[0].from_socket
    geometry = nodes.new('ShaderNodeNewGeometry')
    position = nodes.new('ShaderNodeSeparateXYZ')
    links.new(geometry.outputs['Position'],position.inputs[0])
    uv = nodes.new('ShaderNodeCombineXYZ')
    for source, destination, low, high in [('X','X',xmin,xmax),('Z','Y',zmin,zmax)]:
        mapping = nodes.new('ShaderNodeMapRange')
        mapping.inputs['From Min'].default_value = low
        mapping.inputs['From Max'].default_value = high
        links.new(position.outputs[source],mapping.inputs['Value'])
        links.new(mapping.outputs[0],uv.inputs[destination])
    texture = nodes.new('ShaderNodeTexImage')
    texture.image = image
    texture.extension = 'CLIP'
    links.new(uv.outputs[0],texture.inputs['Vector'])
    # Exclude rear-facing head surfaces from the front projection.
    front = nodes.new('ShaderNodeMapRange')
    front.inputs['From Min'].default_value = -.012
    front.inputs['From Max'].default_value = .027
    front.inputs['To Min'].default_value = 1
    front.inputs['To Max'].default_value = 0
    links.new(position.outputs['Y'],front.inputs['Value'])
    mask = nodes.new('ShaderNodeMath')
    mask.operation = 'MULTIPLY'
    links.new(texture.outputs['Color'],mask.inputs[0])
    links.new(front.outputs[0],mask.inputs[1])
    pigment = nodes.new('ShaderNodeMixRGB')
    pigment.label = 'Soft espresso pigment beneath brow fibers'
    pigment.inputs[2].default_value = (.041,.019,.011,1)
    links.new(mask.outputs[0],pigment.inputs[0])
    links.new(base,pigment.inputs[1])
    links.new(pigment.outputs[0],surface.inputs['Base Color'])


def build(output):
    source = Path(bpy.data.filepath).resolve()
    output = output.resolve()
    if output.exists():
        raise ValueError('Use a new scene path')
    eyes.reset()
    protected, calibration = eye_meshes(), eyes.calibration()
    fill_brows(bpy.data.objects['Apollo_Face'])
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
