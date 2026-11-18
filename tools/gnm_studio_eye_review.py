from pathlib import Path
import sys
import bpy
import numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path.cwd()/'tools'))
from gnm_soft_face_review import surface
from gnm_portrait_refine import skin_tree,strands,render,aim
s=bpy.context.scene
h=s.objects['GNM Head']
r=Path(bpy.data.filepath).parent
o=r/'realism_pass'/'19_review'
o.mkdir(parents=True,exist_ok=True)
assert not (r/'portrait_v19.blend').exists()
tree=skin_tree(h,surface(h))
old=s.objects['Natural v17 lower lashes']
old.hide_render=True
old.hide_set(True)
rows=[]
radii=[]
rng=np.random.default_rng(1919)
t=np.linspace(0,1,9)
for ob in s.objects:
 if ob.type!='CURVE' or not ob.name.startswith('Peak | lower tear meniscus'):continue
 samples=np.array([p.co[:] for p in ob.data.splines[0].bezier_points])
 samples=samples[np.argsort(abs(samples[:,0]))]
 for u in np.linspace(.15,.94,62):
  seed=np.array([np.interp(u,np.linspace(0,1,len(samples)),samples[:,j]) for j in range(3)])
  seed[1]-=.00038
  seed[2]+=.00018
  hit,n,_,_=tree.find_nearest(Vector(seed))
  root=np.array(hit+n*.000018)
  length=(.0011+.0013*np.sin(np.pi*u))*rng.uniform(.78,1.15)
  side=np.sign(root[0])
  rows.append(root+length*np.column_stack((side*(.43*u-.08)*t,-.36*t-.53*t*t,.82*t-.13*t*t)))
  radii.append(rng.uniform(.000028,.000044)*(1-.997*t)**.8)
strands('Natural v19 lower lid margin lashes',h,np.array(rows),np.array(radii),old.data.materials[0])
for side in (-1,1):
 ob=s.objects[f'Peak | inner canthus {side}']
 keys=ob.data.shape_keys.key_blocks
 keys['Natural v17 tear corner visibility'].value=0
 keys['Fitted tear corner fold'].value=.55
 mat=ob.data.materials[0].copy()
 ob.data.materials[0]=mat
 p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 p.inputs['Base Color'].default_value=(.27,.115,.105,1)
 p.inputs['Roughness'].default_value=.32
 p.inputs['Coat Weight'].default_value=.12
# Smaller offset key and low fill make anatomical relief readable.
key=s.objects['Beauty key'];key.data=key.data.copy()
aim(key,(-.48,-.50,.34),(0,0,-.02))
key.data.size=.38
key.data.size_y=.50
key.data.energy=34
fill=s.objects['Beauty fill'];fill.data=fill.data.copy();fill.data.energy=4.5
s.camera.data.dof.use_dof=False
s.render.filepath='//realism_pass/19_review/final.png'
bpy.ops.wm.save_as_mainfile(filepath=str(r/'portrait_v19.blend'),compress=True)
s.use_nodes=False
s.cycles.time_limit=0
s.cycles.adaptive_threshold=.04
s.render.use_border=False
render(s,o,'final',1000,48)
s.render.use_border=True
s.render.use_crop_to_border=True
s.render.border_min_x=.27;s.render.border_max_x=.77
s.render.border_min_y=.53;s.render.border_max_y=.86
render(s,o,'upper-face',1560,48)
s.render.use_border=False
aim(s.camera,(.36,-.75,.035),(0,0,-.025))
render(s,o,'three-quarter',850,40)
