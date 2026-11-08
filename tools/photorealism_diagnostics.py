"""Development-only clay and neutral-light stills; no saved scene or metadata."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'wrapper'))
import eyes

def run(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False);source=Path(bpy.data.filepath);before=hashlib.sha256(source.read_bytes()).hexdigest()
    eyes.reset();scene=bpy.context.scene
    for name,location,energy in [('Key',(0,-.28,.10),.45),('Fill',(-.12,-.2,-.04),.25),('Apollo separation',(.12,.1,.1),0)]:
        obj=bpy.data.objects.get(name)
        if obj:obj.location=location;obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler();obj.data.energy=energy
    eyes.render(folder/'neutral-light.png')
    mat=bpy.data.materials.new('Diagnostic neutral clay');mat.use_nodes=True
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');shader.inputs['Base Color'].default_value=(.18,.18,.18,1);shader.inputs['Roughness'].default_value=.6
    human=bpy.data.objects['Apollo_Face']
    for slot in human.material_slots:slot.material=mat
    scene.camera.data.lens=70;scene.camera.location=(0,-.68,-.015);scene.camera.rotation_euler=(Vector((0,0,-.015))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    eyes.render(folder/'clay-front.png')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
    (folder/'diagnostics.json').write_text(json.dumps({'scene_sha256':before,'scope':'Inspection-only lighting/material/camera variations; no graded metadata and no scene save','images':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.png')}},indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',required=True,type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(a.folder)
