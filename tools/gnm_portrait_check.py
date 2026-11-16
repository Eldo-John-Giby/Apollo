"""Reopen and compare a portrait candidate with its supplied source in Blender."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(a):
    sys.path.insert(0,str(a.skills/'scenario-blender-expert/scripts'))
    import bx_audit
    if a.portable_maps:
        from gnm_portable import relative_images
        relative_images(a.portable_maps,bpy.data.filepath,map_root='//textures')
        bpy.context.scene.render.filepath='//renders/portrait.png'
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True,relative_remap=False)
    head=bpy.context.scene.objects['GNM Head']
    candidate_images={n.image for m in head.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    for image in candidate_images:assert image.packed_file,image.name+' not packed'
    height_stats=[]
    for node in head.data.materials[0].node_tree.nodes:
        if node.type=='TEX_IMAGE' and 'height' in node.name.lower():
            im=node.image;pixels=np.empty(len(im.pixels),dtype=np.float32)
            im.pixels.foreach_get(pixels);rgb=pixels.reshape(-1,4)[:,:3]
            payload=bytes(im.packed_file.data)
            stats={'image':im.name,'min':float(rgb.min()),'max':float(rgb.max()),'std':float(rgb[:,0].std()),'png_bits':payload[24] if payload[:8]==b'\x89PNG\r\n\x1a\n' else None}
            height_stats.append(stats)
            if a.require_relief:
                assert im.colorspace_settings.name=='Non-Color'
                assert stats['png_bits']==16 and stats['std']>.005,'Height precision or relief was lost'
    with bpy.data.libraries.load(str(a.source.resolve()),link=False) as (src,dst):
        dst.objects=['GNM Head']
    original=dst.objects[0]
    p=np.array([v.co[:] for v in original.data.vertices])
    basis=np.array([v.co[:] for v in head.data.shape_keys.key_blocks[0].data])
    assert np.array_equal(p,basis),'Neutral Basis changed'
    assert [tuple(f.vertices) for f in head.data.polygons]==[tuple(f.vertices) for f in original.data.polygons]
    for uv in head.data.uv_layers:
        np.testing.assert_array_equal(np.array([v.uv[:] for v in uv.data]),np.array([v.uv[:] for v in original.data.uv_layers[uv.name].data]))
    ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    co=np.array([v.co[:] for v in mesh.vertices]);ev.to_mesh_clear()
    eyes=sorted({i for f in original.data.polygons if f.material_index in [1,2,3,4] for i in f.vertices})
    np.testing.assert_array_equal(co[eyes],p[eyes])
    from mathutils.bvhtree import BVHTree
    tree=BVHTree.FromPolygons([Vector(v) for v in co],[list(f.vertices) for f in head.data.polygons if f.material_index==0])
    groom={}
    for ob in bpy.context.scene.objects:
        if ob.type!='CURVES':continue
        data=ob.data
        points=np.empty(len(data.points)*3,dtype=np.float32)
        data.attributes['position'].data.foreach_get('vector',points);points=points.reshape(-1,3)
        radius=np.empty(len(data.points),dtype=np.float32);data.attributes['radius'].data.foreach_get('value',radius)
        assert np.isfinite(points).all() and np.isfinite(radius).all() and (radius>0).all()
        roots=np.array([points[c.first_point_index] for c in data.curves])
        distances=np.array([tree.find_nearest(Vector(v))[3] for v in roots])
        groom[ob.name]={'strands':len(data.curves),'points':len(data.points),'max_root_offset_mm':float(distances.max()*1000),'radius_um':[float(radius.min()*1e6),float(radius.max()*1e6)]}
        assert distances.max()<.00025,f'{ob.name} has detached roots: {distances.max()*1000:.6f} mm'
    # The native combined model deliberately contains independent eyeball,
    # corneal, mouth and skin components. Keep the raw gate and its baseline.
    baseline=bx_audit.deliverable([original],profile='render',evaluated=False)
    visible_meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render]
    candidate=bx_audit.deliverable(visible_meshes,profile='render')
    new_errors=sorted(set(candidate['errors'])-set(baseline['errors']))
    report={'source_sha256':sha(a.source),'scene_sha256':sha(bpy.data.filepath),
            'blender':bpy.app.version_string,'vertices':len(p),'quads':len(head.data.polygons),
            'source_basis_exact':True,'native_topology_exact':True,'both_uv_layouts_exact':True,
            'native_eye_vertices_exact':True,'packed_images':len(candidate_images),'height_maps':height_stats,'groom':groom,
            'baseline_render_gate':baseline,'candidate_render_gate':candidate,
            'new_render_gate_errors':new_errors,'qualification':'Still portrait only. Motion, engine export and organizer evaluation not tested.'}
    a.out.write_text(json.dumps(report,indent=2,default=str)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps({'report':str(a.out),'new_render_gate_errors':new_errors}),flush=True)
    if new_errors:raise RuntimeError('New render gate errors require review')
    if a.matched:
        # Compare actual final materials against the source camera and lamps.
        from gnm_portrait_refine import aim, render
        scene=bpy.context.scene;scene.camera=scene.objects['GNM Camera']
        scene.view_settings.exposure=-.85
        for name,pos,power,size in [('Key',(-.13,-.29,.22),10,.20),('Fill',(.20,-.33,.04),4,.24),('Rim',(-.14,.10,.18),8,.16)]:
            lamp=scene.objects[name];aim(lamp,pos,(0,0,-.035));lamp.data.energy=power;lamp.data.size=size
        render(scene,a.out.parent,'front-matched-final',1024,48)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--skills',type=Path,default=Path('C:/Users/eldoj/.codex/skills'))
    p.add_argument('--matched',action='store_true')
    p.add_argument('--portable-maps',type=Path)
    p.add_argument('--require-relief',action='store_true')
    main(p.parse_args(sys.argv[sys.argv.index('--')+1:]))
