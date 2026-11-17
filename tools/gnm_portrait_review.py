"""Targeted hairline, right eyelid, eye reflection and ear refinement on v08."""
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from gnm_portrait_refine import aim, render, skin_tree, smooth, strands


def coordinates(vertices):
    return np.array([v.co[:] for v in vertices])


def evaluated(head):
    return coordinates(head.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices)


def curve_data(obj):
    field=obj.data.attributes['position'].data
    points=np.empty((len(field),3),dtype=np.float32)
    field.foreach_get('vector',points.ravel())
    return field,points


def balance_aperture(head, scene):
    basis=head.data.shape_keys.reference_key
    xyz=coordinates(basis.data)
    before=evaluated(head)
    x,y,z=before.T
    skin={i for p in head.data.polygons if p.material_index==0 for i in p.vertices}
    eye={i for p in head.data.polygons if p.material_index in (1,2,3,4) for i in p.vertices}
    ids=np.array(sorted(skin-eye))
    # Head-on rays measure the smaller opening on the right of the image.
    influence=np.exp(-((x-.031)/.012)**2-((z-.115)/.026)**2)
    upper=np.exp(-((y-.306)/.0031)**2)
    lower=np.exp(-((y-.298)/.0025)**2)
    xyz[ids,1]+=(influence*(.00043*upper-.00015*lower))[ids]
    edit=head.shape_key_add(name='Aperture balance | image right',from_mix=False)
    edit.data.foreach_set('co',xyz.astype(np.float32).ravel())
    edit.value=1
    bpy.context.view_layer.update()
    after=evaluated(head)
    tree=skin_tree(head,after)
    for obj in scene.objects:
        if obj.type!='CURVES':
            continue
        field,points=curve_data(obj)
        for c in obj.data.curves:
            i=c.first_point_index
            x,y,z=points[i]
            if not (.013 < x < .052 and .287 < y < .318 and z > .080):
                continue
            nearest,n,_,_=tree.find_nearest(Vector(points[i]))
            points[i:i+c.points_length]+=np.array(nearest+n*.000024)-points[i]
        field.foreach_set('vector',points.ravel())
    # Shift the right tear film with the lower lid, leaving the eyeball untouched.
    meniscus=scene.objects.get('Peak | lower tear meniscus 1')
    if meniscus:
        key=meniscus.shape_key_add(name='Lower lid follow | image right',from_mix=False)
        for vertex in key.data:
            vertex.co.y -= .00010
        key.value=1
    return tree


def soften_hairline(head,scene,tree):
    scalp=scene.objects['Portrait | swept chestnut hair']
    field,flat=curve_data(scalp)
    rows=flat.reshape(-1,12,3)
    roots=rows[:,0]
    x,y,z=roots.T
    front=smooth((z-.078)/.031)
    # Follow the actual dense row of follicles, including the lowered forehead.
    edge=np.full(len(rows),.371)
    bins=np.linspace(-.079,.079,37)
    samples=[]
    for a,b in zip(bins[:-1],bins[1:]):
        select=(x>=a)&(x<b)&(front>.55)&(y>.344)
        if np.count_nonzero(select)>12:
            samples.append(((a+b)*.5,float(np.percentile(y[select],9))))
    xs,ys=np.array(samples).T
    ys=np.convolve(np.pad(ys,2,mode='edge'),[.08,.22,.40,.22,.08],mode='valid')
    edge[:]=np.interp(x,xs,ys)
    radius=scalp.data.attributes['radius'].data
    values=np.empty(len(radius),dtype=np.float32)
    radius.foreach_get('value',values)
    radii=values.reshape(-1,12)
    feather=front*(1-smooth((y-edge+.002)/.009))*smooth((y-.343)/.008)
    radii*=1-.61*feather[:,None]
    radius.foreach_set('value',values)
    rng=np.random.default_rng(20391)
    t=np.linspace(0,1,7)
    hairs=[]
    widths=[]
    for h in rng.uniform(xs[0],xs[-1],1750):
        local=np.interp(h,xs,ys)
        uneven=.00125*np.sin(h*233+.5)+.00081*np.sin(h*588)
        vertical=local+uneven+rng.normal(-.0004,.0021)
        length=rng.uniform(.0013,.0044)
        row=[]
        for step in t:
            q=Vector((h+.35*length*step,vertical+length*step,.30))
            hit,n,_,_=tree.ray_cast(q,Vector((0,0,-1)))
            if hit is None or n.z<.38:
                break
            row.append(np.array(hit+n*(.000024+.0003*np.sin(np.pi*step))))
        if len(row)==len(t):
            hairs.append(row)
            widths.append(rng.uniform(.000007,.000016)*(1-.97*t))
    strands('Portrait | irregular hairline transition',head,np.array(hairs),np.array(widths),scalp.data.materials[0])


def blend_temple_junction(scene, tree):
    grooms=(('Portrait | swept chestnut hair',12),
            ('Peak | front hairline fibers',7),
            ('Portrait | irregular hairline transition',7))
    t=np.linspace(0,1,12)
    for name, steps in grooms:
        obj=scene.objects[name]
        field,points=curve_data(obj)
        rows=points.reshape(-1,steps,3)
        x,y,z=rows[:,0].T
        side=np.sign(x)
        # Change the corner itself where the swept top turns into the side.
        a=abs(x)
        lateral=np.exp(-((a-.053)/.016)**2)
        frontal=smooth((z-.051)/.021)
        vertical=np.exp(-((y-(.368-.72*(a-.053)))/.018)**2)
        region=lateral*frontal*vertical
        wave=np.sin(390*x+95*z)+.42*np.sin(870*x-110*z)
        for i in np.flatnonzero(region>.11):
            amount=region[i]
            for j,u in enumerate(t if steps==12 else np.linspace(0,1,steps)):
                old=Vector(rows[i,j])
                hit,n,_,_=tree.find_nearest(old)
                height=max(.000024,(old-hit).dot(n))
                shift=Vector((
                    float(amount*side[i]*(.0024*(1-u)+.0047*u*wave[i])),
                    float(amount*(.0072+.0011*wave[i])*(1-.62*u)),
                    float(-amount*.0057*(1-.42*u)),
                ))
                hit,n,_,_=tree.find_nearest(hit+shift)
                rows[i,j]=hit+n*height
        field.foreach_set('vector',points.ravel())
        if steps==12:
            radius=obj.data.attributes['radius'].data
            widths=np.empty(len(radius),dtype=np.float32)
            radius.foreach_get('value',widths)
            widths.reshape(-1,steps)[:]*=1-(region*(.52+.10*wave))[:,None]
            radius.foreach_set('value',widths)


def finish_materials(head,scene):
    for slot in (2,4):
        copy=head.data.materials[slot].copy()
        copy.name=f'cornea_v09_{slot}'
        head.data.materials[slot]=copy
        tree=copy.node_tree
        film=next(n for n in tree.nodes if n.type=='BSDF_GLASS')
        film.inputs['Roughness'].default_value=.036
        destination=film.outputs[0].links[0].to_socket
        refract=tree.nodes.new('ShaderNodeBsdfRefraction')
        refract.inputs['IOR'].default_value=film.inputs['IOR'].default_value
        refract.inputs['Roughness'].default_value=.026
        reflection=tree.nodes.new('ShaderNodeMixShader')
        reflection.label='Subdued corneal reflection'
        reflection.inputs[0].default_value=.39
        tree.links.new(film.outputs[0],reflection.inputs[1])
        tree.links.new(refract.outputs[0],reflection.inputs[2])
        tree.links.new(reflection.outputs[0],destination)
    fill=scene.objects['Beauty fill'].data
    if hasattr(fill,'specular_factor'):
        fill.specular_factor=.22
    copy=head.data.materials[0].copy()
    copy.name='skin_v09 ears'
    head.data.materials[0]=copy
    nodes,links=copy.node_tree.nodes,copy.node_tree.links
    p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    x,y,z=coordinates(head.data.vertices).T
    side=abs(x)
    ears=smooth((side-.069)/.014)*smooth((y-.224)/.025)*smooth((.329-y)/.030)
    bowl=ears*np.exp(-((y-.276)/.020)**2-((z-.061)/.024)**2)
    data=head.data.attributes.new('Ear cartilage tone and relief','FLOAT','POINT')
    data.data.foreach_set('value',(ears*.32+bowl*.68).astype(np.float32))
    mask=nodes.new('ShaderNodeAttribute')
    mask.attribute_name=data.name
    tint=nodes.new('ShaderNodeMixRGB')
    tint.blend_type='MULTIPLY'
    tint.inputs[2].default_value=(.90,.71,.69,1)
    links.new(mask.outputs['Fac'],tint.inputs[0])
    links.new(p.inputs['Base Color'].links[0].from_socket,tint.inputs[1])
    links.new(tint.outputs[0],p.inputs['Base Color'])
    for name,value in (('Roughness',.81),('Specular IOR Level',.12)):
        socket=p.inputs[name]
        blend=nodes.new('ShaderNodeMix')
        blend.data_type='FLOAT'
        links.new(mask.outputs['Fac'],blend.inputs[0])
        links.new(socket.links[0].from_socket,blend.inputs[2])
        blend.inputs[3].default_value=value
        links.new(blend.outputs[0],socket)
    tc=nodes.new('ShaderNodeTexCoord')
    noise=nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=890
    noise.inputs['Detail'].default_value=2.4
    links.new(tc.outputs['Object'],noise.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value=.000082
    links.new(mask.outputs['Fac'],bump.inputs['Strength'])
    links.new(noise.outputs['Fac'],bump.inputs['Height'])
    links.new(p.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
    links.new(bump.outputs[0],p.inputs['Normal'])


def main():
    scene=bpy.context.scene
    head=scene.objects['GNM Head']
    root=Path(bpy.data.filepath).resolve().parent
    output=root/'realism_pass'/'12_review'
    output.mkdir(exist_ok=True)
    version=root/'portrait_v12.blend'
    if version.exists():
        raise FileExistsError(version)
    scene.cycles.time_limit=0
    scene.cycles.adaptive_threshold=.045
    scene.use_nodes=False
    before=root/'realism_pass'/'09_review'/'before.png'
    if before.is_file():
        (output/'before.png').write_bytes(before.read_bytes())
    else:
        render(scene,output,'before',850,48)
    tree=balance_aperture(head,scene)
    soften_hairline(head,scene,tree)
    blend_temple_junction(scene,tree)
    finish_materials(head,scene)
    scene.use_nodes=True
    scene.cycles.time_limit=540
    scene.cycles.samples=1024
    scene.cycles.adaptive_threshold=.01
    scene.render.resolution_x=scene.render.resolution_y=1400
    scene.render.filepath='//realism_pass/12_review/final.png'
    bpy.ops.wm.save_as_mainfile(filepath=str(version),compress=True)
    scene.use_nodes=False
    scene.cycles.time_limit=0
    scene.cycles.adaptive_threshold=.045
    render(scene,output,'final',850,64)
    aim(scene.camera,(.40,-.72,.03),(0,0,-.025))
    render(scene,output,'three-quarter',850,48)

if __name__=='__main__':
    main()
