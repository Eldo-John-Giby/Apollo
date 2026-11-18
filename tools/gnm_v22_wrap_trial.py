"""Matched source/baked v22 stills and optional fresh native-target wrapping."""
import argparse
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from gnm_v22_audit import SELECTED,coords,sha
from gnm_v22_materials import bind,validate,load_manifest
from gnm_portrait_refine import aim,render


def main(a):
    source=Path(bpy.data.filepath)
    if sha(source)!=SELECTED:
        raise ValueError('Expected selected v22 for matched judging setup')
    if a.out.exists():
        raise FileExistsError(a.out)
    load_manifest(a.maps)
    manifest_hash=sha(a.maps/'manifest.json')
    recipe_files=[Path(__file__),Path(__file__).with_name('gnm_v22_materials.py'),
                  Path(__file__).with_name('gnm_pbr_manifest.py'),
                  Path(__file__).with_name('gnm_v22_audit.py'),
                  Path(__file__).with_name('gnm_portrait_refine.py')]
    recipes={path.name:sha(path) for path in recipe_files}
    target_hash=sha(a.target) if a.target else None
    template_hash=sha(a.template) if a.template else None
    a.out.mkdir(parents=True)
    scene=bpy.context.scene;head=scene.objects['GNM Head']
    scene.camera=scene.objects['Portrait | neutral 85mm']
    aim(scene.camera,(.4 if a.angle else 0,-.82,.03),(0,0,-.025));scene.camera.data.lens=85
    scene.camera.data.dof.use_dof=False
    scene.render.engine='CYCLES'
    scene.cycles.device='CPU';scene.cycles.seed=20261119
    scene.cycles.use_animated_seed=False;scene.cycles.use_adaptive_sampling=False
    scene.cycles.time_limit=0;scene.render.use_motion_blur=False
    if a.oblique:
        aim(scene.objects['Beauty key'],(.22,-.29,.22),(0,0,-.035))
    bpy.context.view_layer.update()
    lighting={obj.name:dict(matrix=[list(row) for row in obj.matrix_world],
                          energy=obj.data.energy,color=list(obj.data.color),
                          size=getattr(obj.data,'size',None),hidden=obj.hide_render)
              for obj in scene.objects if obj.type=='LIGHT'}
    render(scene,a.out,'source-full',a.size,a.samples)
    bind(head,a.maps,a.layout,full_character=True)
    full_binding=validate(head,a.maps,a.layout,full_character=True,require_packed=False)
    render(scene,a.out,'baked-full',a.size,a.samples)
    fresh_binding=None
    if a.target:
        with bpy.data.libraries.load(str(a.target.resolve()),link=False) as (src,dst):
            dst.objects=['GNM Head']
        fresh=dst.objects[0]
        if fresh is None or fresh.data.shape_keys or fresh.modifiers:
            raise ValueError('Fresh target is not a neutral native mesh')
        with np.load(a.template,allow_pickle=False) as template:
            np.testing.assert_array_equal(coords(fresh.data.vertices),template['vertices'].astype(np.float32))
            np.testing.assert_array_equal(np.array([list(f.vertices) for f in fresh.data.polygons]),template['quads'])
            for name,key in [('GNM UDIM','udim'),('GNM Region','legacy')]:
                uv=np.array([tuple(p.uv) for p in fresh.data.uv_layers[name].data],dtype=np.float32)
                np.testing.assert_array_equal(uv.ravel(),template[key].astype(np.float32).ravel())
        # Keep the same judging lights and camera; replace all visible character
        # geometry with the freshly loaded, unenhanced native head.
        for obj in list(scene.objects):
            if obj.type in ('MESH','CURVE','CURVES'):
                bpy.data.objects.remove(obj,do_unlink=True)
        fresh.name='GNM Head';scene.collection.objects.link(fresh)
        bind(fresh,a.maps,a.layout)
        fresh_binding=validate(fresh,a.maps,a.layout,full_character=False,require_packed=False)
        render(scene,a.out,'fresh-texture-only',a.size,a.samples)
    report=dict(source_sha256=SELECTED,maps_manifest_sha256=manifest_hash,
                target_sha256=target_hash,layout=a.layout,
                recipe_sha256=recipes,full_binding=full_binding,fresh_binding=fresh_binding,
                template_sha256=template_hash,
                angle=a.angle,oblique=a.oblique,lights=lighting,device=scene.cycles.device,
                camera_matrix=[list(row) for row in scene.camera.matrix_world],
                camera_lens_mm=scene.camera.data.lens,view_transform=scene.view_settings.view_transform,
                exposure=scene.view_settings.exposure,seed=scene.cycles.seed,
                adaptive_sampling=False,depth_of_field=False,motion_blur=False,
                samples=a.samples,size=a.size,
                images={p.name:sha(p) for p in a.out.glob('*.png')},
                qualification='Visual wrapping experiment only; no release or review acceptance implied.')
    if sha(source)!=SELECTED:
        raise ValueError('Selected source changed')
    load_manifest(a.maps)
    if sha(a.maps/'manifest.json')!=manifest_hash or any(sha(path)!=recipes[path.name] for path in recipe_files):
        raise ValueError('Wrapping inputs or recipes changed during rendering')
    if (a.target and sha(a.target)!=target_hash) or (a.template and sha(a.template)!=template_hash):
        raise ValueError('Fresh target or template changed during rendering')
    (a.out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(report),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--maps',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--layout',choices=('udim','legacy'),default='udim')
    p.add_argument('--target',type=Path);p.add_argument('--template',type=Path)
    p.add_argument('--size',type=int,default=768);p.add_argument('--samples',type=int,default=32)
    p.add_argument('--oblique',action='store_true');p.add_argument('--angle',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if a.target and not a.template:p.error('--target requires --template for native geometry validation')
    main(a)
