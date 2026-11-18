"""Continue face detail above the brows and refine sclera and tear corners on v12."""
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from gnm_portrait_refine import render, smooth
from gnm_feedback_still import coords


def node(tree, kind, label):
    item=tree.nodes.new(kind)
    item.label=label
    return item


def tint(tree, source, factor, rgb, label, operation='MULTIPLY'):
    mix=node(tree,'ShaderNodeMixRGB',label)
    mix.blend_type=operation
    mix.inputs[2].default_value=(*rgb,1)
    tree.links.new(source,mix.inputs[1])
    tree.links.new(factor,mix.inputs[0])
    return mix.outputs[0]


def multiplier(tree,a,b,label):
    m=node(tree,'ShaderNodeMath',label)
    m.operation='MULTIPLY'
    tree.links.new(a,m.inputs[0])
    if isinstance(b,(int,float)):
        m.inputs[1].default_value=b
    else:
        tree.links.new(b,m.inputs[1])
    return m.outputs[0]


def forehead(head):
    material=head.data.materials[0].copy()
    material.name='skin_v13 forehead detail'
    head.data.materials[0]=material
    tree=material.node_tree
    p=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
    x,y,z=coords(head.data.vertices).T
    central=smooth((.076-abs(x))/.023)
    mask=smooth((y-.310)/.022)*smooth((.394-y)/.027)*smooth((z-.055)/.045)*central
    field=head.data.attributes.new('Forehead detail falloff','FLOAT','POINT')
    field.data.foreach_set('value',mask.astype(np.float32))
    region=node(tree,'ShaderNodeAttribute','Feather through brow and temples')
    region.attribute_name=field.name
    fac=region.outputs['Fac']
    tc=node(tree,'ShaderNodeTexCoord','Local skin coordinates').outputs['Object']
    noise=node(tree,'ShaderNodeTexNoise','Broad forehead complexion')
    noise.inputs['Scale'].default_value=123
    noise.inputs['Detail'].default_value=2.4
    tree.links.new(tc,noise.inputs['Vector'])
    mapped=node(tree,'ShaderNodeMapRange','Patch contrast')
    mapped.inputs['From Min'].default_value=.37
    mapped.inputs['From Max'].default_value=.69
    tree.links.new(noise.outputs['Fac'],mapped.inputs['Value'])
    mottle=multiplier(tree,fac,mapped.outputs[0],'Localized vascular tone')
    base=p.inputs['Base Color'].links[0].from_socket
    color=tint(tree,base,mottle,(.92,.81,.79),'Forehead tone breakup')
    cells=node(tree,'ShaderNodeTexVoronoi','Forehead follicle spacing')
    cells.inputs['Scale'].default_value=1780
    tree.links.new(tc,cells.inputs['Vector'])
    pore=node(tree,'ShaderNodeMapRange','Pore pit and pigment')
    pore.interpolation_type='SMOOTHSTEP'
    pore.inputs['From Min'].default_value=.075
    pore.inputs['From Max'].default_value=.255
    pore.inputs['To Min'].default_value=1
    pore.inputs['To Max'].default_value=0
    tree.links.new(cells.outputs['Distance'],pore.inputs['Value'])
    pits=multiplier(tree,pore.outputs[0],fac,'Forehead pores only')
    color=tint(tree,color,pits,(.79,.65,.61),'Subtle pore pigment')
    tree.links.new(color,p.inputs['Base Color'])
    bump=node(tree,'ShaderNodeBump','Fine forehead surface relief')
    bump.invert=True
    bump.inputs['Distance'].default_value=.000090
    tree.links.new(multiplier(tree,fac,.58,'Forehead bump weight'),bump.inputs['Strength'])
    tree.links.new(pore.outputs[0],bump.inputs['Height'])
    tree.links.new(p.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
    tree.links.new(bump.outputs[0],p.inputs['Normal'])


def vessels(head,path):
    image=bpy.data.images.load(str(path.resolve()),check_existing=False)
    image.colorspace_settings.name='Non-Color'
    image.pack()
    for slot in (1,3):
        material=head.data.materials[slot].copy()
        material.name=f'eye_v13 visible sclera {slot}'
        head.data.materials[slot]=material
        tree=material.node_tree
        p=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
        base=p.inputs['Base Color'].links[0].from_socket
        coords=node(tree,'ShaderNodeTexCoord','Sclera projection')
        scale=node(tree,'ShaderNodeVectorMath','Scale to bilateral vessel map')
        scale.operation='MULTIPLY'
        scale.inputs[1].default_value=(1/.110,1/.037,0)
        tree.links.new(coords.outputs['Object'],scale.inputs[0])
        translate=node(tree,'ShaderNodeVectorMath','Translate to vessel map')
        translate.operation='ADD'
        translate.inputs[1].default_value=(.5,-.284/.037,0)
        tree.links.new(scale.outputs[0],translate.inputs[0])
        field=node(tree,'ShaderNodeTexImage','Packed branching capillaries')
        field.extension='CLIP'
        field.image=image
        tree.links.new(translate.outputs[0],field.inputs['Vector'])
        albedo=next(n for n in tree.nodes if n.type=='TEX_IMAGE' and n!=field
                    and n.image and n.image.name.startswith('color.'))
        radial=node(tree,'ShaderNodeVectorMath','Native iris radius')
        radial.operation='DISTANCE'
        radial.inputs[1].default_value=(.5,.5,0)
        tree.links.new(albedo.inputs['Vector'].links[0].from_socket,radial.inputs[0])
        gate=node(tree,'ShaderNodeMapRange','Clear of the iris and limbus')
        gate.interpolation_type='SMOOTHSTEP'
        gate.inputs['From Min'].default_value=.195
        gate.inputs['From Max'].default_value=.225
        tree.links.new(radial.outputs['Value'],gate.inputs['Value'])
        amount=multiplier(tree,field.outputs['Color'],gate.outputs[0],'Visible sclera only')
        c=tint(tree,base,amount,(.78,.28,.24),'Faint rose capillary branches')
        tree.links.new(c,p.inputs['Base Color'])
    for slot in (2,4):
        material=head.data.materials[slot].copy()
        material.name=f'cornea_v13 calmer reflections {slot}'
        head.data.materials[slot]=material
        nt=material.node_tree
        mix=next(n for n in nt.nodes if n.label=='Subdued corneal reflection')
        mix.inputs[0].default_value=.65
        glass=next(n for n in nt.nodes if n.type=='BSDF_GLASS')
        glass.inputs['Roughness'].default_value=.042


def inner_corners(scene):
    for sign in (-1,1):
        corner=scene.objects[f'Peak | inner canthus {sign}']
        basis=corner.data.shape_keys.reference_key if corner.data.shape_keys else corner.shape_key_add(name='Basis')
        points=coords(basis.data)
        center=points.mean(0)
        relative=points-center
        x,y,z=relative.T
        # Give the caruncle a low, tapered fold where it joins the lower waterline.
        flare=1+.32*smooth((sign*x+.0005)/.001)
        local=np.column_stack((x*1.46,y*flare-.12*sign*x,z*.87))
        local[:,2]+=.000077*np.exp(-((x+.00008*sign)/.00015)**2-((y+.00016)/.0003)**2)
        key=corner.shape_key_add(name='Fitted tear corner fold',from_mix=False)
        key.data.foreach_set('co',(center+local).astype(np.float32).ravel())
        key.value=1
        mat=corner.data.materials[0].copy()
        mat.name=f'Warm caruncle v13 {sign}'
        corner.data.materials[0]=mat
        nt=mat.node_tree
        p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
        p.inputs['Base Color'].default_value=(.32,.122,.104,1)
        p.inputs['Roughness'].default_value=.43
        p.inputs['Coat Weight'].default_value=.07
        p.inputs['Subsurface Weight'].default_value=.30


def main():
    scene=bpy.context.scene
    head=scene.objects['GNM Head']
    root=Path(bpy.data.filepath).resolve().parent
    natural='--natural-vessels' in sys.argv
    portrait_scale=natural or '--portrait-scale-vessels' in sys.argv
    stronger=portrait_scale or '--readable-vessels' in sys.argv
    number=16 if natural else 15 if portrait_scale else 14 if stronger else 13
    review=f'{number}_review'
    out=root/'realism_pass'/review
    version=root/f'portrait_v{number}.blend'
    if version.exists():
        raise FileExistsError(version)
    if stronger:
        image=bpy.data.images.load(str((out/'sclera-vessels.png').resolve()),check_existing=False)
        image.colorspace_settings.name='Non-Color'
        image.pack()
        for slot in (1,3):
            material=head.data.materials[slot].copy()
            material.name=f'eye_v{number} scleral vessels {slot}'
            head.data.materials[slot]=material
            nodes=material.node_tree.nodes
            next(n for n in nodes if n.label=='Packed branching capillaries').image=image
            pigment=next(n for n in nodes if n.label=='Faint rose capillary branches')
            pigment.inputs[2].default_value=(.64,.10,.11,1) if portrait_scale else (.68,.22,.20,1)
            if natural:
                pigment.inputs[2].default_value=(.61,.16,.15,1)
    else:
        vessels(head,out/'sclera-vessels.png')
        forehead(head)
        inner_corners(scene)
    scene.render.filepath=f'//realism_pass/{review}/final.png'
    bpy.ops.wm.save_as_mainfile(filepath=str(version),compress=True)
    scene.use_nodes=False
    scene.cycles.time_limit=0
    scene.cycles.adaptive_threshold=.04
    if portrait_scale:
        render(scene,out,'final',900,48)
    scene.render.use_border=True
    scene.render.use_crop_to_border=True
    scene.render.border_min_x=.27
    scene.render.border_max_x=.77
    scene.render.border_min_y=.53
    scene.render.border_max_y=.86
    render(scene,out,'upper-face',1560,64)
    if not portrait_scale:
        scene.render.use_border=False
        render(scene,out,'final',900,48)

if __name__=='__main__':
    main()
