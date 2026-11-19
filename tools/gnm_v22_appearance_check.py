"""Compare the whole neutral character with immutable v22, including groom materials."""
import argparse
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from gnm_v22_audit import SELECTED,sha,coords,appearance_signature


def geometry(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    if obj.type=='CURVES':
        data=evaluated.data
        values=np.empty(len(data.points)*3,dtype=np.float32)
        data.attributes['position'].data.foreach_get('vector',values)
        radii=np.empty(len(data.points),dtype=np.float32)
        data.attributes['radius'].data.foreach_get('value',radii)
        return values.reshape(-1,3),radii
    mesh=evaluated.to_mesh()
    values=coords(mesh.vertices);evaluated.to_mesh_clear()
    return values,None


def extra_material_settings(obj):
    return [[(node.bl_idname,{name:getattr(node,name) for name in
                ('parametrization','component','interpolation_type') if hasattr(node,name)})
             for node in material.node_tree.nodes] if material.use_nodes else []
            for material in obj.data.materials]


def main(a):
    scene=bpy.context.scene;candidate=Path(bpy.data.filepath);candidate_hash=sha(candidate)
    if sha(a.source)!=SELECTED or scene.get('apollo_identity_source_sha256')!=SELECTED:
        raise ValueError('Expected immutable selected v22 and its full-character derivation')
    if a.out.exists():raise FileExistsError(a.out)
    scene.frame_set(1)
    targets={o.name:o for o in scene.objects if not o.hide_render and o.type in ('MESH','CURVE','CURVES')}
    portable_binding=None
    if a.maps:
        from gnm_v22_materials import validate
        portable_binding=validate(targets['GNM Head'],a.maps,a.layout,full_character=True,require_packed=True)
    with bpy.data.libraries.load(str(a.source.resolve()),link=False) as (src,dst):
        names=list(src.objects);dst.objects=names.copy()
    originals=dict(zip(names,dst.objects))
    collection=bpy.data.collections.new('Apollo | disposable source comparison')
    scene.collection.children.link(collection)
    for obj in originals.values():collection.objects.link(obj)
    bpy.context.view_layer.update()
    expected={name:obj for name,obj in originals.items() if not obj.hide_render and obj.type in ('MESH','CURVE','CURVES')}
    if set(expected)!=set(targets):
        raise ValueError('Visible character components differ: missing='+str(sorted(set(expected)-set(targets)))+
                         '; added='+str(sorted(set(targets)-set(expected))))
    report=dict(scene_sha256=candidate_hash,selected_sha256=SELECTED,recipe_sha256=sha(__file__),
                objects={},native_eye_shift_is_intentional=True,passed=True,
                qualification='Whole-character neutral geometry/material comparison only; motion and visual review remain separate.')
    if portable_binding:report['portable_binding']=portable_binding
    for name,original in expected.items():
        target=targets[name]
        np.testing.assert_array_equal(np.asarray(target.matrix_world),np.asarray(original.matrix_world))
        converted=name=='GNM Head' and portable_binding is not None
        if not converted and extra_material_settings(target)!=extra_material_settings(original):
            raise ValueError('Material mode changed: '+name)
        source_signature=appearance_signature(original)
        target_signature=appearance_signature(target)
        if not converted and target_signature!=source_signature:
            raise ValueError('Material recipe changed: '+name)
        source_points,source_radius=geometry(original)
        target_points,target_radius=geometry(target)
        if source_points.shape!=target_points.shape:raise ValueError('Geometry dimensions changed: '+name)
        measured=np.ones(len(source_points),dtype=bool)
        if name=='GNM Head':
            eyes=sorted({i for f in original.data.polygons if f.material_index in (1,2,3,4) for i in f.vertices})
            measured[eyes]=False
        error=float(np.max(np.abs(source_points[measured]-target_points[measured])))
        if error>1e-6:raise ValueError(f'Neutral identity changed: {name}: {error} m')
        if source_radius is not None:np.testing.assert_array_equal(source_radius,target_radius)
        report['objects'][name]=dict(vertices_or_curve_points=len(source_points),max_neutral_error_m=error,
                                    material_signature=target_signature,source_material_signature=source_signature,
                                    material_comparison='validated_pbr_conversion' if converted else 'exact_selected_recipe',
                                    radii_exact=source_radius is not None)
    if sha(candidate)!=candidate_hash or sha(a.source)!=SELECTED:raise ValueError('Scene file changed during audit')
    a.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(dict(report=str(a.out),components=len(report['objects']),source_unchanged=True)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--maps',type=Path,help='Validate the intentional PBR head conversion while retaining exact groom checks')
    p.add_argument('--layout',choices=('udim','legacy'),default='udim')
    main(p.parse_args(sys.argv[sys.argv.index('--')+1:]))
