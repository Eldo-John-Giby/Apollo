from pathlib import Path
import sys,json
import bpy,numpy as np
from mathutils import Vector
sys.path.insert(0,str(Path.cwd()/'tools'))
from gnm_soft_face_review import surface
from gnm_feedback_still import coords
from gnm_portrait_refine import render,aim,skin_tree,strands
s=bpy.context.scene;h=s.objects['GNM Head'];root=Path(bpy.data.filepath).parent
out=root/'realism_pass'/'22_review';out.mkdir(parents=True,exist_ok=True)
assert not (root/'portrait_v22.blend').exists()
current=surface(h);x,y,z=current.T
front=np.clip((z-.105)/.018,0,1)
upper=np.exp(-(x/.021)**4-((y-.2362)/.0034)**2)
lower=np.exp(-(x/.0215)**4-((y-.2286)/.0040)**2)
delta=np.zeros_like(current)
delta[:,2]=front*(.00125*upper+.00185*lower)
delta[:,1]=front*(.00025*upper-.00030*lower)
allowed={i for f in h.data.polygons if f.material_index==0 for i in f.vertices}
protected={i for f in h.data.polygons if f.material_index in (1,2,3,4) for i in f.vertices}
delta[list(set(range(len(x)))-(allowed-protected))]=0
basis=coords(h.data.shape_keys.reference_key.data)
key=h.shape_key_add(name='Lip volume | upper tubercle and lower cushion')
key.data.foreach_set('co',(basis+delta).astype(np.float32).ravel());key.value=1
bpy.context.view_layer.update();tree=skin_tree(h,surface(h))
report={}
for name in ('Portrait | fitted directional brows','Portrait | fuller brow fibers'):
 old=s.objects.get(name)
 if old is None or old.hide_render:continue
 attr=old.data.attributes['position'].data;flat=np.empty(len(attr)*3,dtype=np.float32);attr.foreach_get('vector',flat);points=flat.reshape(-1,3)
 ra=old.data.attributes['radius'].data;radius=np.empty(len(ra),dtype=np.float32);ra.foreach_get('value',radius)
 rows=[];radii=[]
 for c in old.data.curves:
  a=c.first_point_index;b=a+c.points_length
  row=points[a:b].copy()
  if row[0,0]<0:continue
  rows.append(row);radii.append(radius[a:b].copy())
  mirror=row.copy();mirror[:,0]*=-1
  hit,n,_,_=tree.find_nearest(Vector(mirror[0]))
  mirror+=np.asarray(hit+n*.000025)-mirror[0]
  rows.append(mirror);radii.append(radius[a:b].copy())
 old.hide_render=True;old.hide_set(True)
 strands(name+' | balanced v22',h,np.array(rows),np.array(radii),old.data.materials[0])
 report[name]=len(rows)
(out/'changes.json').write_text(json.dumps({'brows':report,'max_lip_displacement_mm':float(np.linalg.norm(delta,axis=1).max()*1000)},indent=2)+'\n')
s.render.filepath='//realism_pass/22_review/final.png'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'portrait_v22.blend'),compress=True)
s.use_nodes=False;s.cycles.time_limit=0;s.cycles.adaptive_threshold=.04;s.render.use_border=False
render(s,out,'final',1000,40)
aim(s.camera,(.36,-.75,.035),(0,0,-.025))
render(s,out,'three-quarter',1000,40)
