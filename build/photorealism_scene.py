"""Isolated v2 appearance construction; preserves the calibrated eye system."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wrapper'))
import eyes

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def organize():
    scene=bpy.context.scene
    groups={name:bpy.data.collections.get(name) or bpy.data.collections.new(name) for name in ['Apollo Face','Apollo Eyes','Apollo Groom','Apollo Lighting','Apollo Helpers']}
    for group in groups.values():
        if group.name not in scene.collection.children:scene.collection.children.link(group)
    for obj in list(scene.objects):
        if obj.type=='LIGHT' or obj.type=='CAMERA':key='Apollo Lighting'
        elif obj.name.startswith(('Pupil.','Iris.','Sclera.')):key='Apollo Eyes'
        elif obj.type in {'ARMATURE','EMPTY'} or obj.hide_render:key='Apollo Helpers'
        elif any(s in obj.name.lower() for s in ['groom','eyelash','eyebrow']):key='Apollo Groom'
        else:key='Apollo Face'
        target=groups[key]
        if obj.name not in target.objects:target.objects.link(obj)
        for collection in list(obj.users_collection):
            if collection!=target:collection.objects.unlink(obj)
        if obj.hide_render:obj.hide_set(True)
        obj.select_set(False)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.overlay.show_overlays=False
                area.spaces.active.region_3d.view_perspective='CAMERA'
    scene.cycles.seed=0;scene.cycles.use_animated_seed=False;scene.cycles.use_adaptive_sampling=False

def anatomy():
    from mathutils import Vector,Matrix
    from bl_ext.blender_org.mpfb.entities.objectproperties import HumanObjectProperties
    from bl_ext.blender_org.mpfb.services.targetservice import TargetService
    human=bpy.data.objects['Apollo_Face']
    def evaluated_points():
        ev=human.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        points=[human.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear();return points
    old=evaluated_points();groups=[]
    for cx in [-eyes.calibration()['ipd']/2,eyes.calibration()['ipd']/2]:
        ids=[i for i,p in enumerate(old) if .012<((p.x-cx)**2+p.z*p.z)**.5<.019 and -.02<p.y<.012]
        if len(ids)<10:raise ValueError('Insufficient orbital anchors')
        groups.append(ids)
    centers=[sum((old[i] for i in ids),Vector())/len(ids) for ids in groups]
    HumanObjectProperties.set_value('gender',0.0,entity_reference=human)
    HumanObjectProperties.set_value('age',0.5,entity_reference=human)
    TargetService.reapply_macro_details(human);bpy.context.view_layer.update()
    new=evaluated_points()
    if len(new)!=len(old):raise ValueError('Morph changed evaluated topology')
    nc=[sum((new[i] for i in ids),Vector())/len(ids) for ids in groups]
    scale=(centers[1]-centers[0]).length/(nc[1]-nc[0]).length
    oldmid=(centers[0]+centers[1])/2;newmid=(nc[0]+nc[1])/2
    human.matrix_world=Matrix.Translation(oldmid)@Matrix.Scale(scale,4)@Matrix.Translation(-newmid)@human.matrix_world
    for obj in bpy.data.objects:
        if 'groom' in obj.name.lower():obj.hide_set(True);obj.hide_render=True
    bpy.context.view_layer.update()
    return {'macro':TargetService.get_macro_info_dict_from_basemesh(human),'orbital_alignment_scale':scale,'orbital_anchor_counts':[len(g) for g in groups]}


def build(folder,stage='baseline'):
    folder=Path(folder).resolve()
    if folder.exists():raise ValueError('Use a new output folder')
    source=Path(bpy.data.filepath);source_sha=digest(source)
    before=eyes.calibration();eyes.reset()
    protected={name:hashlib.sha256(json.dumps([list(v.co) for v in bpy.data.objects[name].data.vertices]).encode()).hexdigest() for side in 'LR' for name in ['Pupil.'+side,'Iris.'+side,'Sclera.'+side]}
    organize()
    morph=anatomy() if stage=='anatomy' else None
    for name,want in protected.items():
        actual=hashlib.sha256(json.dumps([list(v.co) for v in bpy.data.objects[name].data.vertices]).encode()).hexdigest()
        assert actual==want,'Changed protected eye mesh: '+name
    assert eyes.calibration()==before
    folder.mkdir(parents=True)
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),compress=True)
    sys.path.insert(0,str(ROOT/'tools'))
    from scene_preflight import run
    run(folder/'scene-preflight.json')
    (folder/'build.json').write_text(json.dumps({'stage':stage,'source_sha256':source_sha,'scene_sha256':digest(folder/'scene.blend'),'recipe_sha256':digest(Path(__file__)),'protected_eye_mesh_sha256':protected,'anatomy':morph,'qualified':False,'scope':'P0 clean baseline; anatomy/material/groom development remains pending'},indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--folder',required=True,type=Path);parser.add_argument('--stage',choices=['baseline','anatomy'],default='baseline')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);build(args.folder,args.stage)
