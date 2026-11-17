"""Apply the portrait's finishing compositor and preview it on the rendered still."""
from pathlib import Path
import sys
import bpy

source = Path(bpy.data.filepath).resolve()
folder = source.parent/'realism_pass'


def compositor(scene, image=None):
    scene.use_nodes = True
    tree = scene.node_tree
    nodes, links = tree.nodes, tree.links
    node = nodes.new('CompositorNodeImage' if image else 'CompositorNodeRLayers')
    if image:
        node.image = image
    glare = nodes.new('CompositorNodeGlare')
    glare.glare_type = 'FOG_GLOW'
    glare.inputs['Threshold'].default_value = 1.6
    glare.inputs['Smoothness'].default_value = .25
    glare.inputs['Strength'].default_value = .06
    glare.inputs['Size'].default_value = .22
    links.new(node.outputs['Image'], glare.inputs['Image'])
    lens = nodes.new('CompositorNodeLensdist')
    lens.inputs['Dispersion'].default_value = .002
    lens.inputs['Fit'].default_value = True
    links.new(glare.outputs['Image'], lens.inputs['Image'])
    ellipse = nodes.new('CompositorNodeEllipseMask')
    ellipse.inputs['Size'].default_value = (.94, .96)
    blur = nodes.new('CompositorNodeBlur')
    blur.filter_type = 'GAUSS'
    blur.inputs['Size'].default_value = (320, 320)
    links.new(ellipse.outputs[0], blur.inputs['Image'])
    vignette = nodes.new('CompositorNodeMixRGB')
    vignette.blend_type = 'MULTIPLY'
    vignette.inputs[0].default_value = .07
    links.new(lens.outputs[0], vignette.inputs[1])
    links.new(blur.outputs[0], vignette.inputs[2])
    grain = nodes.new('CompositorNodeTexture')
    grain.texture = bpy.data.textures.new('Portrait fine grain', type='NOISE')
    texture = nodes.new('CompositorNodeMixRGB')
    texture.blend_type = 'SOFT_LIGHT'
    texture.inputs[0].default_value = .02
    links.new(vignette.outputs[0], texture.inputs[1])
    links.new(grain.outputs['Value'], texture.inputs[2])
    output = next(n for n in nodes if n.type == 'COMPOSITE')
    links.new(texture.outputs[0], output.inputs['Image'])


scene = bpy.context.scene
if '--' not in sys.argv:
    compositor(scene)
    scene.render.filepath='//realism_pass/final_composited.png'
    bpy.ops.wm.save_as_mainfile(filepath=str(source.with_name('portrait_v08.blend')),
                               compress=True,copy=True)
else:
    folder=Path(sys.argv[sys.argv.index('--')+1]).resolve()
    plate=bpy.data.images.load(str(folder/'final.png'))
    scene.render.engine='CYCLES'
    scene.cycles.samples=1
    for obj in scene.objects:
        obj.hide_render=obj.type!='CAMERA'
    scene.render.resolution_x,scene.render.resolution_y=plate.size
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='Standard'
    scene.view_settings.look='None'
    compositor(scene,plate)
    scene.render.filepath=str(folder/'final_composited.png')
    bpy.ops.render.render(write_still=True)
