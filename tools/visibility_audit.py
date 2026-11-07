"""Render independent corner/random masks and a real half-pupil occlusion fault."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'wrapper'))
from blender_verify import prepare_masks
from reference_geometry import reference
import eyes


def run(dataset,folder,count,progress):
    dataset=Path(dataset);folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((dataset/('progress.json' if progress else 'dataset.json')).read_text(encoding='utf-8'))
    assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==manifest['run']['scene_sha256'],'Wrong scene'
    frames=manifest['frames'][:count]
    assert len(frames)==count,'Requested dataset frames are not complete yet'
    scene=bpy.context.scene;original=prepare_masks(scene)
    for frame in frames:
        i=frame['frame'];eyes.move(frame['input']['h'],frame['input']['v'])
        for mode in ['unoccluded','occluded']:
            for obj in scene.objects:
                if obj.type=='MESH':obj.hide_render=obj.name not in {'Pupil.L','Pupil.R'} if mode=='unoccluded' else original[obj.name]
            eyes.render(folder/mode/f'frame_{i:06d}.png')
        print('Visibility pose',i,flush=True)
    eyes.reset()
    for obj in scene.objects:
        if obj.type=='MESH':obj.hide_render=obj.name not in {'Pupil.L','Pupil.R'}
    eyes.render(folder/'fault_expected.png')
    point=reference('L',0,0,ipd=eyes.calibration()['ipd'])['pupil']
    ratio=.375/(point[1]+.4);x=point[0]*ratio;z=point[2]*ratio;y=-.025
    mesh=bpy.data.meshes.new('Injected occluder');mesh.from_pydata([(x,y,z-.005),(x+.006,y,z-.005),(x+.006,y,z+.005),(x,y,z+.005)],[],[(0,1,2,3)])
    obj=bpy.data.objects.new('Injected half-pupil occlusion',mesh);bpy.context.collection.objects.link(obj)
    material=bpy.data.materials.new('Injected black');material.use_nodes=True
    nodes=material.node_tree.nodes;nodes.clear();emission=nodes.new('ShaderNodeEmission');emission.inputs[0].default_value=(0,0,0,1);output=nodes.new('ShaderNodeOutputMaterial');material.node_tree.links.new(emission.outputs[0],output.inputs['Surface']);mesh.materials.append(material)
    for item in scene.objects:
        if item.type=='MESH':item.hide_render=original.get(item.name,False)
    eyes.render(folder/'fault_occluded.png')
    report={'frames':frames,'run':manifest['run'],'dataset':str(dataset.resolve()),'scene_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['tools/visibility_audit.py','tools/blender_verify.py','wrapper/eyes.py']},'blender':bpy.app.version_string}
    (folder/'evidence.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--folder',type=Path,required=True);p.add_argument('--count',type=int,default=25);p.add_argument('--progress',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(args.dataset,args.folder,args.count,args.progress)
