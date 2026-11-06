"""Self-contained absolute binocular gaze controls."""
import json
import os
from pathlib import Path
import sys
import shutil
import subprocess
import argparse
import time
import hashlib
try:
    import bpy
    from mathutils import Matrix, Vector
    from bpy_extras.object_utils import world_to_camera_view
except ImportError:
    bpy = None
# BEGIN CORE
"""apollo/core.py - pure-python (numpy only) reference math. No bpy imports. Frozen conventions: see 01_SOLUTION_TECHNICAL.md s3."""
import math
from dataclasses import dataclass, field
import numpy as np

@dataclass(frozen=True)
class Config:
    ipd: float = 0.063            # m, eyeball-center to eyeball-center
    pupil_depth: float = 0.0100   # m, rotation center -> pupil-plane center along optical axis
    target_dist: float = 0.350    # m forward of eye midpoint
    bound: float = 0.050          # m, +-bound on the fixation plane for h,v = +-1
    cam_dist: float = 0.400       # m forward of eye midpoint
    focal_mm: float = 100.0
    sensor_mm: float = 36.0
    res: int = 1024
    parallel: bool = False        # ablation: parallel eyes (no vergence)

    def __post_init__(self):
        for name in ('ipd', 'pupil_depth', 'target_dist', 'bound', 'cam_dist', 'focal_mm', 'sensor_mm'):
            value = getattr(self, name)
            if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
                raise ValueError(f'{name} must be finite and positive')
        if type(self.res) is not int or self.res <= 0:
            raise ValueError('res must be a positive integer')
        if self.pupil_depth >= self.cam_dist:
            raise ValueError('Pupil must remain in front of the camera')


def clamp(value):
    if isinstance(value, (bool, str)):
        raise ValueError('Gaze inputs must be finite numbers')
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('Gaze inputs must be finite numbers')
    return max(-1.0, min(1.0, value))

FWD = np.array([0.0, -1.0, 0.0])  # subject faces -Y (primary-position optical axis)

def eye_centers(c: Config):
    return {"L": np.array([+c.ipd / 2, 0.0, 0.0]), "R": np.array([-c.ipd / 2, 0.0, 0.0])}

def fixation_point(h: float, v: float, c: Config):
    return np.array([c.bound * h, -c.target_dist, c.bound * v])

def shortest_arc(a, b):
    """Unit quaternion (w,x,y,z) rotating unit(a) onto unit(b) about an axis perpendicular to both (Listing's law)."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    d = float(a @ b)
    if d < -1 + 1e-12:  # antiparallel: pick any perpendicular axis
        axis = np.cross(a, [1.0, 0, 0]);
        if np.linalg.norm(axis) < 1e-6: axis = np.cross(a, [0, 1.0, 0])
        axis /= np.linalg.norm(axis); return np.array([0.0, *axis])
    q = np.array([1.0 + d, *np.cross(a, b)])
    return q / np.linalg.norm(q)

def quat_to_mat(q):
    w, x, y, z = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])

def mat_to_euler_xyz(R):
    """Blender 'XYZ' euler: R = Rz @ Ry @ Rx. Returns (x,y,z) radians."""
    sy = -R[2, 0]; y = math.asin(max(-1.0, min(1.0, sy)))
    if abs(sy) < 1 - 1e-12:
        return [math.atan2(R[2, 1], R[2, 2]), y, math.atan2(R[1, 0], R[0, 0])]
    return [math.atan2(-R[1, 2], R[1, 1]), y, 0.0]

def intrinsics(c: Config):
    f = c.focal_mm / c.sensor_mm * c.res
    return np.array([[f, 0, c.res / 2], [0, f, c.res / 2], [0, 0, 1.0]])

def project(p_world, c: Config):
    """World point -> continuous pixel coords (origin = top-left corner of top-left pixel, y down).
    Camera at (0,-cam_dist,0) looking +Y, up +Z, image-right +X."""
    K = intrinsics(c); rel = np.asarray(p_world, float) - np.array([0.0, -c.cam_dist, 0.0])
    xc, yc, zc = rel[0], -rel[2], rel[1]            # camera frame: x right, y down, z forward
    return (K[0, 0] * xc / zc + K[0, 2], K[1, 1] * yc / zc + K[1, 2])

def eye_state(h, v, c: Config):
    h, v = clamp(h), clamp(v)
    P = fixation_point(h, v, c) if not c.parallel else None
    out = {}
    for name, C in eye_centers(c).items():
        tgt = P if P is not None else C + np.array([c.bound * h, -c.target_dist, c.bound * v])
        g = (tgt - C); g /= np.linalg.norm(g)
        q = shortest_arc(FWD, g); R = quat_to_mat(q); pupil = C + c.pupil_depth * g
        out[name] = dict(quat=q, R=R, euler=mat_to_euler_xyz(R), gaze=g, pupil3d=pupil, pupil2d=project(pupil, c))
    return out, P

def sweep_inputs(n=10):
    if type(n) is not int or n <= 0:
        raise ValueError('Sweep length must be a positive integer')
    return [(k, 2 * math.pi * k / n, math.sin(2 * math.pi * k / n), math.cos(2 * math.pi * k / n)) for k in range(n)]

def make_record(k, theta, h, v, c: Config, image_name):
    requested = (h, v)
    h, v = clamp(h), clamp(v)
    st, P = eye_state(h, v, c); f = lambda a: [float(x) for x in a]
    return {
        "frame": k, "theta": theta, "input": {"h": h, "v": v},
        "eye_rotation_L": f(st["L"]["euler"]), "eye_rotation_R": f(st["R"]["euler"]),
        "pupil_center_2D_L": f(st["L"]["pupil2d"]), "pupil_center_2D_R": f(st["R"]["pupil2d"]),
        "camera_matrix": intrinsics(c).tolist(),
        "extra": {"schema_version": "1.0", "image": image_name, "clamped": requested != (h, v),
                  "eye_quat_wxyz_L": f(st["L"]["quat"]), "eye_quat_wxyz_R": f(st["R"]["quat"]),
                  "optical_axis_world_L": f(st["L"]["gaze"]), "optical_axis_world_R": f(st["R"]["gaze"]),
                  "pupil_center_3D_world_L": f(st["L"]["pupil3d"]), "pupil_center_3D_world_R": f(st["R"]["pupil3d"]),
                  "fixation_point_world": f(P) if P is not None else None,
                  "gaze_vector_cam_L": f(gaze_cam(st["L"]["gaze"])), "gaze_vector_cam_R": f(gaze_cam(st["R"]["gaze"])),
                  "gaze_pitch_yaw_L": gaze_pitch_yaw(st["L"]["gaze"]), "gaze_pitch_yaw_R": gaze_pitch_yaw(st["R"]["gaze"]),
                  "pupil_ellipse_2D_L": pupil_ellipse_2d(st["L"]["pupil3d"], st["L"]["gaze"], PUPIL_RADIUS, c),
                  "pupil_ellipse_2D_R": pupil_ellipse_2d(st["R"]["pupil3d"], st["R"]["gaze"], PUPIL_RADIUS, c)},
    }

# ---- dataset-grade extras (UnityEyes / ETH-XGaze style annotations) ----
def gaze_cam(g_world):
    """World gaze unit vector -> camera frame (OpenCV: x right, y down, z forward). Camera looks along world +Y."""
    gx, gy, gz = g_world
    return np.array([gx, -gz, gy])

def gaze_pitch_yaw(g_world):
    """ETH-XGaze-style angles of the eye->target vector in the camera frame (radians).
    pitch = asin(-y_cam) (positive = looking up); yaw = atan2(-x_cam, -z_cam) (0 = looking straight at the camera)."""
    x, y, z = gaze_cam(g_world)
    return [math.asin(max(-1.0, min(1.0, -y))), math.atan2(-x, -z)]

def pupil_ellipse_2d(center3d, g_world, radius, c: Config, n=64):
    """Project the 3D pupil circle (plane perpendicular to the optical axis) and return its image ellipse.
    Returns dict(center=[cx,cy], semi_axes=[a,b], angle=radians of major axis from +x, image y down)."""
    g = np.asarray(g_world, float); g = g / np.linalg.norm(g)
    t = np.cross(g, [0.0, 0.0, 1.0]);
    if np.linalg.norm(t) < 1e-9: t = np.cross(g, [1.0, 0.0, 0.0])
    u = t / np.linalg.norm(t); w = np.cross(g, u)
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError('Pupil radius must be finite and positive')
    # Homography from the unit pupil circle to the image, then transform its conic.
    camera_rotation = np.array([[1., 0., 0.], [0., 0., -1.], [0., 1., 0.]])
    rel = np.asarray(center3d, float) - np.array([0., -c.cam_dist, 0.])
    H = intrinsics(c) @ camera_rotation @ np.column_stack((radius*u, radius*w, rel))
    inverse = np.linalg.inv(H)
    conic = inverse.T @ np.diag([1., 1., -1.]) @ inverse
    A, bvec = conic[:2, :2], conic[:2, 2]
    mu = -np.linalg.solve(A, bvec)
    scale = float(mu @ A @ mu - conic[2, 2])
    lam, vec = np.linalg.eigh(A / scale)
    if np.any(lam <= 0):
        raise ValueError('Projected pupil is not an ellipse')
    a, b = 1 / np.sqrt(lam)
    return {"center": [float(mu[0]), float(mu[1])], "semi_axes": [float(a), float(b)], "angle": math.atan2(vec[1, 0], vec[0, 0])}

def angle_from_primary(q):
    """Total rotation angle (radians) of an eye quaternion relative to primary position (for range assertions)."""
    return 2 * math.acos(max(-1.0, min(1.0, abs(q[0]))))

PUPIL_RADIUS = 0.002  # m (d = 4 mm)
MAX_ECCENTRICITY = math.radians(35.0)  # oculomotor-plausible bound; assert in dataset mode so pupils never roll into the skull
# END CORE
ROOT = Path(__file__).resolve().parent.parent
_RIG = None

class _Rig:
    def __init__(self):
        self.scene = bpy.context.scene
        self.cfg = Config(**json.loads(self.scene['apollo_calibration']))
        self.arm = bpy.data.objects[self.scene['apollo_armature']]
        self.bones = json.loads(self.scene['apollo_bones'])
        self.rest = {}
        for side, name in self.bones.items():
            pb = self.arm.pose.bones[name]
            world = self.arm.matrix_world @ pb.bone.matrix_local
            self.rest[side] = (world.copy(), Vector(pb['gf_pupil_local']))
        self.h = self.v = 0.
        self.clamped = False

    def apply(self, h, v):
        states, target = eye_state(h, v, self.cfg)
        for side, values in states.items():
            rest, _ = self.rest[side]
            rotation = Matrix(values['R'].tolist()) @ rest.to_3x3()
            desired = rotation.to_4x4()
            desired.translation = rest.translation
            self.arm.pose.bones[self.bones[side]].matrix = self.arm.matrix_world.inverted() @ desired
        if target is not None:
            bpy.data.objects['FixationTarget'].location = target.tolist()
        bpy.context.view_layer.update()
        self.h, self.v = h, v
        return states

    def record(self, k=0, theta=0., image=''):
        record = make_record(k, theta, self.h, self.v, self.cfg, image)
        evaluated = self.arm.evaluated_get(bpy.context.evaluated_depsgraph_get())
        for side in 'LR':
            pb = evaluated.pose.bones[self.bones[side]]
            measured = evaluated.matrix_world @ pb.matrix @ self.rest[side][1]
            expected = record['extra']['pupil_center_3D_world_'+side]
            if (measured - Vector(expected)).length > 1e-6:
                raise ValueError('Evaluated pupil position disagrees with analytic geometry')
            uv = world_to_camera_view(self.scene, self.scene.camera, measured)
            pixel = np.array([uv.x*self.cfg.res, (1-uv.y)*self.cfg.res])
            if np.linalg.norm(pixel - record['pupil_center_2D_'+side]) > 1e-3:
                raise ValueError('Camera projection disagrees with analytic intrinsics')
        record['extra']['clamped'] = self.clamped
        record['extra']['fixture'] = bool(self.scene.get('apollo_fixture', False))
        record['extra']['pose_sha256'] = hashlib.sha256(json.dumps({s:record['extra']['eye_quat_wxyz_'+s] for s in 'LR'},sort_keys=True).encode()).hexdigest()
        record['extra']['camera'] = {'position':[0.,-self.cfg.cam_dist,0.], 'focal_mm':self.cfg.focal_mm, 'sensor_mm':self.cfg.sensor_mm}
        record['extra']['render_samples'] = self.scene.cycles.samples
        record['extra']['calibration'] = json.loads(self.scene['apollo_calibration'])
        record['extra']['blender_version'] = bpy.app.version_string
        lights = []
        for obj in sorted(self.scene.objects, key=lambda obj:obj.name):
            if obj.type == 'LIGHT':
                lights.append({'name':obj.name,'matrix':[list(row) for row in obj.matrix_world], 'type':obj.data.type,'energy':obj.data.energy,'color':list(obj.data.color),'size':getattr(obj.data,'size',0.)})
        record['extra']['lighting_sha256'] = hashlib.sha256(json.dumps(lights,sort_keys=True).encode()).hexdigest()
        return record


def _rig():
    global _RIG
    if bpy is None:
        raise RuntimeError('This API requires Blender Python; use the CLI or run inside Blender')
    if 'apollo_calibration' not in bpy.context.scene:
        paths = [ROOT/'scene.blend', ROOT/'out/fixture/scene.blend']
        scene = next((p for p in paths if p.is_file()), None)
        if scene is None:
            raise FileNotFoundError('Build a scene first: python tasks.py scene')
        bpy.ops.wm.open_mainfile(filepath=str(scene))
        _RIG = None
    if _RIG is None or _RIG.scene != bpy.context.scene:
        _RIG = _Rig()
    return _RIG


def move(h, v):
    h2, v2 = clamp(h), clamp(v)
    rig = _rig()
    rig.clamped = (h2 != h or v2 != v)
    rig.apply(h2, v2)
    return state()


def reset():
    return move(0., 0.)


def state():
    return _rig().record()


def calibration():
    return json.loads(_rig().scene['apollo_calibration'])


def render(path=None):
    rig = _rig()
    path = Path(path) if path else ROOT/'output'/f'render_h{rig.h:+.4f}_v{rig.v:+.4f}.png'
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    record = rig.record(image=path.name)
    rig.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return {'path': str(path), 'record': record}


def sweep(n=10, out_dir=None, write_metadata=True):
    _rig()  # Load the scene before deriving the default output directory.
    destination = Path(out_dir) if out_dir else Path(bpy.data.filepath).parent
    destination.mkdir(parents=True, exist_ok=True)
    manifest = destination/'metadata.json'
    if write_metadata and manifest.exists():
        manifest.unlink()  # A failed regeneration must not leave a stale success manifest.
    records = []
    try:
        for k, theta, h, v in sweep_inputs(n):
            started = time.monotonic()
            move(h,v)
            path = destination/'renders'/f'frame_{k:02d}.png'
            render(path)
            records.append(_rig().record(k, theta, path.name))
            print(f'frame {k+1}/{n} theta={theta:.4f} h={h:.4f} v={v:.4f} t={time.monotonic()-started:.2f}s')
        if write_metadata:
            temp = manifest.with_suffix('.json.tmp')
            temp.write_text(json.dumps(records, indent=2, allow_nan=False)+'\n', encoding='utf-8')
            temp.replace(manifest)
        return records
    finally:
        reset()


def main():
    argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else (sys.argv[1:] if bpy is None else [])
    if bpy is None:
        blender = os.environ.get('BLENDER_BIN') or shutil.which('blender')
        if not blender:
            print('Blender unavailable. Set BLENDER_BIN to blender.exe.', file=sys.stderr)
            return 2
        return subprocess.call([blender,'-b','--factory-startup','--python-exit-code','1','-P',str(Path(__file__).resolve()),'--',*argv])
    p = argparse.ArgumentParser()
    p.add_argument('--h', type=float)
    p.add_argument('--v', type=float)
    p.add_argument('--out', type=Path)
    p.add_argument('--calibration', action='store_true')
    p.add_argument('--quality', choices=['draft','final'])
    p.add_argument('--sweep', action='store_true', help='Run the default ten-frame protocol')
    args = p.parse_args(argv)
    if (args.h is None) != (args.v is None):
        p.error('--h and --v must be supplied together')
    rig = _rig()
    if args.quality:
        rig.scene.cycles.samples = 32 if args.quality == 'draft' else 128
    if args.calibration:
        print(json.dumps(calibration(), indent=2))
    elif args.h is not None:
        move(args.h,args.v)
        render(args.out)
    else:
        sweep(out_dir=args.out)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
