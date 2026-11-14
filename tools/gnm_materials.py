"""Shared optional portable surface-map bindings for stills and cached motion."""
import bpy
from gnm_run import surface_files


def bind_surface(head, maps, layout):
    paths = surface_files(maps)
    if not paths:
        return
    # The separate native corneal shell supplies surface reflections. Avoid a
    # second glossy lobe on the underlying pigment/pupil surface.
    for tile in (1002, 1004):
        eye = head.data.materials[tile - 1001].node_tree.nodes.get('Principled BSDF')
        eye.inputs['Specular IOR Level'].default_value = .05
        eye.inputs['Roughness'].default_value = .48
    material = head.data.materials[0]
    nodes, links = material.node_tree.nodes, material.node_tree.links
    shader = nodes.get('Principled BSDF')
    color = shader.inputs['Base Color'].links[0].from_node
    coordinates = color.inputs['Vector'].links[0].from_socket
    textures = {}
    for role, path in paths.items():
        node = nodes.new('ShaderNodeTexImage')
        node.name = f'GNM portable {role}'
        node.image = bpy.data.images.load(str(path.resolve()), check_existing=False)
        node.image.colorspace_settings.name = 'Non-Color'
        links.new(coordinates, node.inputs['Vector'])
        textures[role] = node
    links.new(textures['roughness'].outputs['Color'], shader.inputs['Roughness'])
    bump = nodes.new('ShaderNodeBump')
    bump.name = 'GNM physical skin relief'
    bump.inputs['Distance'].default_value = .00009
    bump.inputs['Strength'].default_value = .65
    links.new(textures['height'].outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], shader.inputs['Normal'])
    shader.inputs['Subsurface Weight'].default_value = .055
    shader.inputs['Subsurface Scale'].default_value = .001
