"""Render distinct isolated eye/lid looks; preserve eye geometry and calibration.

Requires the installed MPFB addon in the disposable build process for lash refit.
No addon is needed to render the packed candidate afterward.
"""
import argparse
from pathlib import Path
import sys
import bpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'wrapper'))
import eyes


def style_iris(material,cool):
    nodes=material.node_tree.nodes;links=material.node_tree.links
    shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    fibers=next(n for n in nodes if n.type=='VALTORGB' and len(n.color_ramp.elements)==2)
    fibers.color_ramp.elements[0].color=(.12,.20,.24,1) if cool else (.18,.12,.055,1)
    fibers.color_ramp.elements[1].color=(.32,.46,.48,1) if cool else (.48,.32,.13,1)
    uv=next(n for n in nodes if n.type=='TEX_COORD')
    distance=nodes.new('ShaderNodeVectorMath');distance.operation='DISTANCE'
    links.new(uv.outputs['UV'],distance.inputs[0]);distance.inputs[1].default_value=(.5,.5,0)
    # At UV radius .41, the colored iris ends at 5.33 mm. The existing annulus
    # remains intact and transitions to sclera; pupil radius/depth never change.
    boundary=nodes.new('ShaderNodeValToRGB')
    boundary.color_ramp.elements[0].position=.40
    boundary.color_ramp.elements[0].color=(0,0,0,1)
    boundary.color_ramp.elements[1].position=.43
    boundary.color_ramp.elements[1].color=(1,1,1,1)
    links.new(distance.outputs['Value'],boundary.inputs[0])
    color=shader.inputs['Base Color'].links[0].from_socket
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX'
    links.new(boundary.outputs[0],mix.inputs[0]);links.new(color,mix.inputs[1])
    mix.inputs[2].default_value=(.8,.8,.75,1)
    links.new(mix.outputs[0],shader.inputs['Base Color'])


def run(folder,variants=('B','C'),optimized=False):
    source=Path(bpy.data.filepath).resolve();folder=Path(folder).resolve()
    if source.parent==folder:raise ValueError('Separate candidate output required')
    for variant in variants:
        bpy.ops.wm.open_mainfile(filepath=str(source));eyes._RIG=None;eyes.reset()
        from bl_ext.blender_org.mpfb.services.clothesservice import ClothesService
        human=bpy.data.objects['Apollo_Face']
        for side in ['left','right']:
            human.data.shape_keys.key_blocks['eye-'+side+'-opened-up'].value=.55 if variant=='B' else .45
        bpy.context.view_layer.update()
        ClothesService.fit_clothes_to_human(bpy.data.objects['Apollo_Face.eyelashes01'],human,set_parent=False)
        seen=set()
        for name in ['Sclera.L','Sclera.R','Iris.L','Iris.R']:
            obj=bpy.data.objects[name]
            for material in obj.data.materials:
                if material.name in seen:continue
                seen.add(material.name)
                shader=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
                shader.inputs['Roughness'].default_value=.45 if name.startswith('Sclera') else .55
                shader.inputs['Specular IOR Level'].default_value=.12 if name.startswith('Sclera') else .08
                if name.startswith('Iris'):style_iris(material,variant=='C')
        if variant=='C':
            key=bpy.data.objects['Key'];key.location=(-.16,-.20,.13)
            key.rotation_euler=(-key.location).to_track_quat('-Z','Y').to_euler()
            key.data.energy=.22;key.data.size=.14
            bpy.data.objects['Fill'].data.energy=.015
        if optimized:
            cycles=bpy.context.scene.cycles
            cycles.max_bounces=2;cycles.diffuse_bounces=1;cycles.glossy_bounces=1
            cycles.transmission_bounces=0
        destination=folder/variant;destination.mkdir(parents=True,exist_ok=True)
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=str(destination/'scene.blend'),compress=True)
        eyes.render(destination/'center.png')
        print('Look candidate',variant,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--folder',type=Path,required=True)
    parser.add_argument('--variant',choices=['B','C','both'],default='both')
    parser.add_argument('--optimized',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    run(args.folder,('B','C') if args.variant=='both' else (args.variant,),args.optimized)
