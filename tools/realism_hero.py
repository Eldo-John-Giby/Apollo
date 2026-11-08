"""Presentation-only head portraits; never writes graded metadata or saves scene."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector


def run(folder):
    source=Path(bpy.data.filepath).resolve();before=hashlib.sha256(source.read_bytes()).hexdigest()
    folder=Path(folder).resolve()
    if folder.exists():raise ValueError('Use a new portrait folder')
    folder.mkdir(parents=True)
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'wrapper'))
    import eyes
    eyes.reset();scene=bpy.context.scene;camera=scene.camera
    original=(camera.matrix_world.copy(),camera.data.lens,scene.render.filepath)
    results=[]
    try:
        camera.data.lens=70
        for name,location in [('front',(0,-.68,-.015)),('three-quarter',(.25,-.64,.015))]:
            camera.location=location
            camera.rotation_euler=(Vector((0,0,-.015))-camera.location).to_track_quat('-Z','Y').to_euler()
            scene.render.filepath=str(folder/(name+'.png'))
            bpy.ops.render.render(write_still=True)
            results.append({'view':name,'camera_position':list(location),'focal_mm':70,
                            'image_sha256':hashlib.sha256((folder/(name+'.png')).read_bytes()).hexdigest()})
    finally:
        camera.matrix_world=original[0];camera.data.lens=original[1];scene.render.filepath=original[2]
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
    (folder/'portraits.json').write_text(json.dumps({'scope':'Presentation views only; outside the calibrated graded camera and metadata','scene_sha256':before,'views':results},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(args.folder)
