"""Exercise the optional panel operators against the shipped public API."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import struct
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import live_controls as ui


def run(folder):
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=True)
    ui.register()
    try:
        settings=bpy.context.scene.apollo_controls
        settings.output=str(folder/'panel.png')
        bpy.ops.apollo.pose(h=1,v=0)
        assert (settings.h,settings.v)==(1,0)
        assert bpy.ops.apollo.render_pose()=={'FINISHED'}
        ui.eyes.render(folder/'api.png')
        digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        assert digest(folder/'panel.png')==digest(folder/'api.png')
        settings.sweep_folder=str(folder/'sweep')
        assert bpy.ops.apollo.sweep()=={'FINISHED'}
        records=json.loads((folder/'sweep/metadata.json').read_text(encoding='utf-8'))
        assert [r['frame'] for r in records]==list(range(10))
        for i in range(10):
            data=(folder/f'sweep/renders/frame_{i:02d}.png').read_bytes()
            assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(1024,1024)
        report={'passed':True,'pose_render_api_identical':True,'sweep_frames':len(records),
                'scene_sha256':digest(Path(bpy.data.filepath)),
                'panel_source_sha256':digest(ROOT/'tools/live_controls.py'),
                'blender':bpy.app.version_string,
                'scope':'Real Blender operators; interactive cardinal/reset and pose-render checks recorded separately.'}
        (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    finally:
        ui.eyes.reset();ui.unregister()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(args.folder)
