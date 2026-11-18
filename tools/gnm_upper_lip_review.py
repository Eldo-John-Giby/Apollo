"""Add upper vermilion projection to the latest balanced portrait."""
from pathlib import Path
import sys
import bpy,numpy as np
sys.path.insert(0,str(Path.cwd()/'tools'))
from gnm_soft_face_review import surface
from gnm_feedback_still import coords
from gnm_portrait_refine import render,aim,smooth
s=bpy.context.scene;h=s.objects['GNM Head'];root=Path(bpy.data.filepath).parent
out=root/'realism_pass'/'23_review';out.mkdir(parents=True,exist_ok=True)
assert not (root/'portrait_v23.blend').exists()
current=surface(h);x,y,z=current.T
mask=np.exp(-(x/.0205)**4-((y-.2368)/.0030)**2)
mask*=smooth((y-.2328)/.0015)*smooth((z-.108)/.016)
delta=np.zeros_like(current)
delta[:,2]=.0014*mask*(.85+.15*np.exp(-(x/.007)**2))
delta[:,1]=.00028*mask
skin={i for f in h.data.polygons if f.material_index==0 for i in f.vertices}
eyes={i for f in h.data.polygons if f.material_index in (1,2,3,4) for i in f.vertices}
delta[list(set(range(len(x)))-(skin-eyes))]=0
basis=coords(h.data.shape_keys.reference_key.data)
key=h.shape_key_add(name='Upper lip | forward vermilion volume')
key.data.foreach_set('co',(basis+delta).astype(np.float32).ravel());key.value=1
s.render.filepath='//realism_pass/23_review/final.png'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'portrait_v23.blend'),compress=True)
s.use_nodes=False;s.cycles.time_limit=0;s.cycles.adaptive_threshold=.04;s.render.use_border=False
render(s,out,'final',1000,40)
aim(s.camera,(.36,-.75,.035),(0,0,-.025))
render(s,out,'three-quarter',1000,40)
