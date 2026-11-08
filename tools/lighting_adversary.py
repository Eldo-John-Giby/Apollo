"""Render a deliberately broken lighting setup and require rejection."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'wrapper'))
import eyes
from reference_geometry import reference
from pixel_oracle import measure


def run(folder):
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=True)
    eyes.reset();scene=bpy.context.scene
    expected=eyes.state()['extra']['lighting_sha256']
    for obj in scene.objects:
        if obj.type=='LIGHT':obj.data.energy=0
    if scene.world and scene.world.use_nodes:
        for node in scene.world.node_tree.nodes:
            if node.type=='BACKGROUND':node.inputs['Strength'].default_value=0
    result=eyes.render(folder/'dark-fault.png')['record']
    actual=result['extra']['lighting_sha256']
    image=bpy.data.images.load(str(folder/'dark-fault.png'),check_existing=False)
    rgb=np.asarray(image.pixels[:],dtype=float).reshape(1024,1024,4)[::-1,:,:3]
    srgb=np.where(rgb<=.0031308,12.92*rgb,1.055*np.maximum(rgb,0)**(1/2.4)-.055)
    pixels=(srgb@np.array([.299,.587,.114]))*255
    rejections={}
    for side in 'LR':
        r=reference(side,0,0,ipd=eyes.calibration()['ipd'])
        radius=100/36*1024*.002/(r['pupil'][1]+.4)
        try:measure(pixels,r['pixel'],radius)
        except ValueError as exc:rejections[side]=str(exc)
    report={'passed':expected!=actual and len(rejections)==2,'lighting_signature_rejected':expected!=actual,
            'pixel_fault_rejections':rejections,'blender':bpy.app.version_string,
            'scene_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
            'scope':'Disposable rendered loss-of-illumination fault; not universal detector robustness.'}
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    assert report['passed'],report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(a.folder)
