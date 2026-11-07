"""Validate completed dataset pixels and plot coverage without production math."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from dataset_protocol import inputs,resume
from reference_geometry import reference
from pixel_oracle import measure


def validate_camera(record):
    cfg=record['extra']['calibration']
    if (cfg['target_dist'],cfg['bound'],cfg['cam_dist'],cfg['pupil_depth'],cfg['res'],cfg['parallel'])!=(.35,.05,.4,.01,1024,False):
        raise ValueError('Unsupported calibration')
    if (cfg['focal_mm'],cfg['sensor_mm'])!=(100.,36.):raise ValueError('Unsupported camera optics')
    f=100/36*1024
    expected=np.array([[f,0,512],[0,f,512],[0,0,1]])
    matrix=np.asarray(record['camera_matrix'],dtype=float)
    if matrix.shape!=(3,3) or not np.isfinite(matrix).all() or not np.allclose(matrix,expected,atol=1e-8,rtol=0):raise ValueError('Dataset camera matrix mismatch')
    camera=record['extra']['camera']
    if camera!={'position':[0.,-.4,0.],'focal_mm':100.,'sensor_mm':36.}:raise ValueError('Dataset camera pose mismatch')


def analyze(folder):
    folder=Path(folder);manifest=json.loads((folder/'dataset.json').read_text(encoding='utf-8'))
    frames=resume(folder,manifest['run'])
    if frames!=manifest['frames'] or len(frames)!=manifest['run']['count']:raise ValueError('Incomplete/inconsistent dataset')
    results=[]
    for record in frames:
        cfg=record['extra']['calibration']
        validate_camera(record)
        image=np.asarray(Image.open(folder/record['extra']['image']).convert('L'))
        if image.shape!=(1024,1024):raise ValueError('Wrong image resolution')
        for side in 'LR':
            r=reference(side,record['input']['h'],record['input']['v'],ipd=cfg['ipd'],lens=cfg['focal_mm'],sensor=cfg['sensor_mm'])
            annotated=np.asarray(record['pupil_center_2D_'+side],dtype=float)
            if annotated.shape!=(2,) or not np.isfinite(annotated).all() or np.linalg.norm(annotated-r['pixel'])>=.001:raise ValueError('Dataset pupil annotation mismatch')
            angles=np.asarray(record['eye_rotation_'+side],dtype=float)
            if angles.shape!=(3,) or not np.isfinite(angles).all():raise ValueError('Invalid rotation annotation')
            x,y,z=angles;cx,sx=np.cos(x),np.sin(x);cy,sy=np.cos(y),np.sin(y);cz,sz=np.cos(z),np.sin(z)
            rotation=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
            if np.max(np.abs(rotation-r['rotation']))>=1e-5:raise ValueError('Dataset rotation annotation mismatch')
            radius=cfg['focal_mm']/cfg['sensor_mm']*1024*.002/(r['pupil'][1]+.4)
            result=measure(image,r['pixel'],radius)
            result.update(frame=record['frame'],eye=side);results.append(result)
    report={'passed':True,'frames':len(frames),'max_pixel_oracle_error_px':max(x['error_px'] for x in results),'method':'Independent geometry-guided connected dark surface; not blind detection or a visibility-mask qualification.','dataset_sha256':hashlib.sha256((folder/'dataset.json').read_bytes()).hexdigest(),'measurements':results}
    (folder/'analysis.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    poses=inputs(len(frames),manifest['run']['seed'])
    fig,axis=plt.subplots(figsize=(5,5));axis.scatter(*np.array(poses).T,s=12);axis.set(xlim=(-1.1,1.1),ylim=(-1.1,1.1),xlabel='Horizontal input',ylabel='Vertical input',title=f'Seeded gaze coverage: {len(frames)} frames');axis.set_aspect('equal');axis.grid(alpha=.3);fig.tight_layout();fig.savefig(folder/'coverage.png',dpi=160);plt.close(fig)
    sheet=Image.new('RGB',(1024,820),'#151b24');draw=ImageDraw.Draw(sheet)
    for i,r in enumerate(frames[:9]):
        x,y=(i%3)*340,(i//3)*270
        with Image.open(folder/r['extra']['image']) as im:sheet.paste(im.resize((256,256)),(x,y))
        draw.text((x+258,y+10),f"{r['input']['h']:+.0f}\n{r['input']['v']:+.0f}",fill='white')
    sheet.save(folder/'anchors.png')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);args=p.parse_args();r=analyze(args.folder)
    print({k:v for k,v in r.items() if k!='measurements'})
