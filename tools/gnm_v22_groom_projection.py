"""Export selected brow/scalp strand projections into unchanged native skin UVs."""
import argparse
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from apollo_core.identity import barycentric
from gnm_v22_audit import SELECTED,sha,coords


def main(a):
    source=Path(bpy.data.filepath)
    if sha(source)!=SELECTED:raise ValueError('Expected immutable selected v22')
    if a.out.exists():raise FileExistsError(a.out)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    h=bpy.context.scene.objects['GNM Head']
    ev=h.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
    vertices=coords(mesh.vertices)
    tris=[t for t in mesh.loop_triangles if mesh.polygons[t.polygon_index].material_index==0]
    ids=np.array([tuple(t.vertices) for t in tris],dtype=np.int32)
    uv=np.array([[tuple(mesh.uv_layers['GNM Region'].data[i].uv) for i in t.loops] for t in tris])
    tree=BVHTree.FromPolygons(vertices.tolist(),ids.tolist(),all_triangles=True)
    ev.to_mesh_clear()
    rows=[];radii=[];classes=[];strand_ids=[];strand_id=0;reports={}
    for obj in bpy.context.scene.objects:
        if obj.type!='CURVES' or obj.hide_render:
            continue
        brow='brow' in obj.name.lower()
        scalp=any(text in obj.name.lower() for text in ('swept chestnut','hairline','crown and temple'))
        if not brow and not scalp:continue
        data=obj.data
        flat=np.empty(len(data.points)*3,dtype=np.float32)
        data.attributes['position'].data.foreach_get('vector',flat);points=flat.reshape(-1,3)
        # All selected groom objects share native head-local coordinates.
        if not np.allclose(np.array(obj.matrix_world),np.array(h.matrix_world),atol=1e-7,rtol=0):
            raise ValueError('Unexpected groom coordinate frame '+obj.name)
        radius=np.empty(len(data.points),dtype=np.float32)
        data.attributes['radius'].data.foreach_get('value',radius)
        hits=[tree.find_nearest(Vector(p)) for p in points]
        face_ids=np.array([x[2] for x in hits],dtype=np.int32)
        near=np.array([tuple(x[0]) for x in hits])
        weights=barycentric(near,vertices[ids[face_ids]])
        coordinates=np.einsum('ni,nij->nj',weights,uv[face_ids])
        xyz=vertices[ids[face_ids]];tex=uv[face_ids]
        area3=np.linalg.norm(np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0]),axis=1)
        a2=tex[:,1]-tex[:,0];b2=tex[:,2]-tex[:,0]
        area2=np.abs(a2[:,0]*b2[:,1]-a2[:,1]*b2[:,0])
        uv_radius=radius*np.sqrt(area2/np.maximum(area3,1e-15))
        skipped=0;segments=0
        for curve in data.curves:
            start=curve.first_point_index;end=start+curve.points_length
            for i in range(start,end-1):
                # Do not draw a spurious diagonal across a UV island boundary.
                if np.linalg.norm(coordinates[i+1]-coordinates[i])>.06:
                    skipped+=1;continue
                rows.append(np.stack((coordinates[i],coordinates[i+1])))
                radii.append((uv_radius[i],uv_radius[i+1]));classes.append(1 if brow else 0)
                strand_ids.append(strand_id)
                segments+=1
            strand_id+=1
        reports[obj.name]=dict(curves=len(data.curves),segments=segments,seam_crossings_skipped=skipped)
        print('PROJECTED '+obj.name,flush=True)
    np.savez_compressed(a.out,segments=np.asarray(rows,dtype=np.float32),
                        radii=np.asarray(radii,dtype=np.float32),brow=np.asarray(classes,dtype=bool),
                        strand_ids=np.asarray(strand_ids,dtype=np.int32))
    if sha(source)!=SELECTED:raise ValueError('Selected source changed')
    report=dict(source_sha256=SELECTED,projection_sha256=sha(a.out),objects=reports,
                recipe_sha256=sha(__file__),
                qualification='Unreviewed flat pigment projection; UV seam crossings require rendered inspection.')
    a.out.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(report),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    main(p.parse_args(sys.argv[sys.argv.index('--')+1:]))
