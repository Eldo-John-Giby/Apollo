from pathlib import Path
import sys
import bpy
import numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path.cwd()/'tools'))
from gnm_soft_face_review import surface
from gnm_feedback_still import coords
from gnm_portrait_refine import render,aim,smooth,skin_tree
s=bpy.context.scene;h=s.objects['GNM Head'];root=Path(bpy.data.filepath).parent
out=root/'realism_pass'/'20_review';out.mkdir(parents=True,exist_ok=True)
assert not (root/'portrait_v20.blend').exists()
p=surface(h);x,y,z=p.T;a=abs(x)
gate=smooth((a-.070)/.012)*smooth((y-.230)/.012)*smooth((.325-y)/.014)
g=lambda cy,cz,sy,sz:np.exp(-((y-cy)/sy)**2-((z-cz)/sz)**2)
bowl=g(.277,.060,.014,.012)
fold=g(.290,.067,.017,.0045)
lobe=g(.244,.063,.009,.012)
delta=np.zeros_like(p)
delta[:,2]=gate*(-.0015*bowl+.00085*fold+.0006*lobe)
delta[:,0]=np.sign(x)*gate*(-.00065*bowl+.00035*fold)
basis=coords(h.data.shape_keys.reference_key.data)
key=h.shape_key_add(name='Ear refinement | concha antihelix and lobe')
key.data.foreach_set('co',(basis+delta).astype(np.float32).ravel());key.value=1
# Increase the lower fringe using the visible v17 anchors, offset toward the rim.
groom=s.objects['Natural v17 lower lashes']
new=groom.copy();new.data=groom.data.copy();new.name='Natural v20 visible lower lashes';s.collection.objects.link(new)
new.hide_render=False;new.hide_set(False)
s.objects['Natural v19 lower lid margin lashes'].hide_render=True
s.objects['Natural v19 lower lid margin lashes'].hide_set(True)
bpy.context.view_layer.update();tree=skin_tree(h,surface(h))
attr=new.data.attributes['position'].data
flat=np.empty(len(attr)*3,dtype=np.float32);attr.foreach_get('vector',flat);pts=flat.reshape(-1,3)
for c in new.data.curves:
 row=pts[c.first_point_index:c.first_point_index+c.points_length]
 old=row[0].copy();seed=old.copy();seed[1]+=.00020
 hit,n,_,_=tree.find_nearest(Vector(seed));anchor=np.array(hit+n*.000035)
 row[:]=anchor+(row-old)*np.array((1,.90,1.20))
attr.foreach_set('vector',flat)
radius=new.data.attributes['radius'].data
rr=np.empty(len(radius),dtype=np.float32);radius.foreach_get('value',rr);radius.foreach_set('value',rr*1.30)
mat=h.data.materials[0].copy();h.data.materials[0]=mat;mat.name='Skin v20 ear cartilage'
nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
a2=h.data.attributes.new('Ear v20 fold pigment','FLOAT','POINT');a2.data.foreach_set('value',(gate*(.18+.35*bowl)).astype(np.float32))
mask=nt.nodes.new('ShaderNodeAttribute');mask.attribute_name=a2.name
mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(1.0,.83,.79,1)
nt.links.new(mask.outputs['Fac'],mix.inputs[0]);nt.links.new(bs.inputs['Base Color'].links[0].from_socket,mix.inputs[1]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
s.render.filepath='//realism_pass/20_review/final.png'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'portrait_v20.blend'),compress=True)
s.use_nodes=False;s.cycles.time_limit=0;s.cycles.adaptive_threshold=.05;s.render.use_border=False
render(s,out,'final',900,32)
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=.27;s.render.border_max_x=.77;s.render.border_min_y=.53;s.render.border_max_y=.86
render(s,out,'eyes',1560,40)
s.render.use_border=False
aim(s.camera,(.48,-.64,.025),(0,0,-.025))
render(s,out,'ears-three-quarter',1100,40)
