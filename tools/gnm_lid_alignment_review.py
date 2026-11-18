from pathlib import Path
import sys,json
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path.cwd()/'tools'))
from gnm_soft_face_review import surface
from gnm_feedback_still import coords
from gnm_portrait_refine import render,skin_tree
s=bpy.context.scene;h=s.objects['GNM Head'];root=Path(bpy.data.filepath).parent
out=root/'realism_pass'/'21_review';out.mkdir(parents=True,exist_ok=True)
assert not (root/'portrait_v21.blend').exists()
p=surface(h);faces=[list(f.vertices) for f in h.data.polygons]
full=BVHTree.FromPolygons([Vector(v) for v in p],faces,all_triangles=False)
skin=skin_tree(h,p)
def ocular(x,y):
 hit,n,i,d=full.ray_cast(Vector((x,y,.25)),Vector((0,0,-1)))
 return i is not None and h.data.polygons[i].material_index in (1,2,3,4)
def edges(x):
 ys=np.linspace(.289,.315,261);ok=[y for y in ys if ocular(x,y)]
 if not ok:return None
 return min(ok),max(ok)
report={}
for name,upper in [('Natural v17 upper lashes',True),('Natural v20 visible lower lashes',False)]:
 ob=s.objects[name];ob.data=ob.data.copy()
 attr=ob.data.attributes['position'].data;flat=np.empty(len(attr)*3,dtype=np.float32);attr.foreach_get('vector',flat);pts=flat.reshape(-1,3)
 moved=0
 for c in ob.data.curves:
  row=pts[c.first_point_index:c.first_point_index+c.points_length];old=row[0].copy();edge=edges(old[0])
  if edge is None:continue
  y=edge[1]+.00020 if upper else edge[0]-.00020
  hit,n,_,_=skin.ray_cast(Vector((old[0],y,.25)),Vector((0,0,-1)))
  if hit is None:continue
  anchor=np.array(hit+n*.000025);row+=anchor-old;moved+=1
 attr.foreach_set('vector',flat);report[name]=moved
for side in (-1,1):
 # Find each exposed inner corner independently, including existing asymmetry.
 candidates=[]
 for x in np.linspace(.015,.024,91):
  e=edges(side*x)
  if e and e[1]-e[0]>.0005:candidates.append((x,e));break
 x,e=candidates[0];y=sum(e)/2
 hit,n,_,_=skin.ray_cast(Vector((side*(x-.00020),y,.25)),Vector((0,0,-1)))
 ob=s.objects[f'Peak | inner canthus {side}'];cur=surface(ob);center=cur.mean(0)
 target=np.array((side*(x+.00010),y,hit.z+.00012))
 local=(cur-center)*np.array((1.3,.80,1.2))
 basis=coords(ob.data.shape_keys.reference_key.data)
 key=ob.shape_key_add(name='Fitted v21 exposed medial tear tissue')
 key.data.foreach_set('co',(basis+target+local-cur).astype(np.float32).ravel());key.value=1
 mat=ob.data.materials[0].copy();ob.data.materials[0]=mat
 bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 bs.inputs['Base Color'].default_value=(.32,.105,.090,1);bs.inputs['Roughness'].default_value=.34
 report[str(side)]={'corner':target.tolist(),'aperture':e}
(out/'alignment.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.filepath='//realism_pass/21_review/final.png'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'portrait_v21.blend'),compress=True)
s.use_nodes=False;s.cycles.time_limit=0;s.cycles.adaptive_threshold=.04
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=.27;s.render.border_max_x=.77;s.render.border_min_y=.53;s.render.border_max_y=.86
render(s,out,'eyes',1800,40)
s.render.use_border=False
render(s,out,'final',900,32)
