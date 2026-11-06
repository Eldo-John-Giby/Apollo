"""Blender framing experiment; save chosen calibration then rerun official sweep."""
import argparse
from dataclasses import replace,asdict
import json
from pathlib import Path
import sys
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wrapper'))
import eyes


def run(folder):
    from bpy_extras.object_utils import world_to_camera_view
    folder=Path(folder)
    rig=eyes._rig();scene=rig.scene
    rows=[]
    for focal in range(85,136,5):
        scene.camera.data.lens=focal
        rig.cfg=replace(rig.cfg,focal_mm=float(focal))
        eyes.reset()
        margins=[]
        for side in 'LR':
            obj=bpy.data.objects['Sclera.'+side].evaluated_get(bpy.context.evaluated_depsgraph_get())
            for vertex in obj.data.vertices:
                uv=world_to_camera_view(scene,scene.camera,obj.matrix_world@vertex.co)
                margins.append(min(uv.x,1-uv.x,uv.y,1-uv.y))
        base=eyes.state()
        eyes.move(1,0);right=eyes.state()
        shift=min(right['pupil_center_2D_'+side][0]-base['pupil_center_2D_'+side][0] for side in 'LR')
        for label,h,v in [('center',0,0),('right',1,0),('up',0,1)]:
            eyes.move(h,v);eyes.render(folder/'framing'/str(focal)/(label+'.png'))
        rows.append({'focal_mm':focal,'eye_sphere_margin':min(margins),'right_shift_px':shift,'eligible':min(margins)>=.08 and shift>=8})
    eligible=[row for row in rows if row['eligible']]
    if not eligible: raise ValueError('No focal length satisfies eye margin/displacement gates')
    chosen=max(eligible,key=lambda row:row['focal_mm'])
    scene.camera.data.lens=chosen['focal_mm']
    rig.cfg=replace(rig.cfg,focal_mm=float(chosen['focal_mm']))
    scene['gazeforge_calibration']=json.dumps(asdict(rig.cfg))
    eyes.reset()
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),compress=True)
    (folder/'framing_report.json').write_text(json.dumps({'chosen':chosen,'measurements':rows,'limitation':'Eye sphere bounds only. Review brows/lashes and face crop manually before submission.'},indent=2),encoding='utf-8')
    print('Framing calibration changed: rerun sweep and verification')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(args.folder)
