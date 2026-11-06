# APOLLO — Implementation Plan for AI Coding Agents

**Project:** Samsung PRISM-XR Hackathon 2026 · Track 01 · Synthetic Eye Movement & Virtual Camera Rendering
**Audience:** Codex / Claude Code agents, plus one human operator (Eldo's team).
**Read first:** `01_SOLUTION_TECHNICAL.md` (the spec, conventions and rationale). This file is the *how* and *in what order*. If the two ever disagree, `01` wins on conventions and numbers; this file wins on process.

**Today:** Fri 6 Nov 2026. **Registration closes Sun 8 Nov, 11:59 PM. Final submission Wed 18 Nov, 11:59 PM.** Internal freeze: **Mon 16 Nov**. Target submission: **Tue 17 Nov** (24 h buffer).

---

## 0. Agent brief (paste this at the top of every agent session)

> You are building **Apollo**, a Blender-based synthetic eye-movement pipeline that is graded on a deterministic 100-point rubric. The goal is a *provably correct, grader-proof* submission, not a flashy one.
>
> Non-negotiable rules:
> 1. **Frozen conventions** (units, axes, signs, naming, pixel origin, sweep) are defined in `01_SOLUTION_TECHNICAL.md` §3. Never change them. If you think one is wrong, stop and write the reasoning in `DECISIONS.md` for the human.
> 2. **Never guess Blender API behaviour.** Write a ≤ 20-line experiment script, run it headless, print the result, then code against what you observed. Blender is 4.5 LTS (reference) and 5.2 LTS (secondary).
> 3. **No GUI context.** All scripts run with `blender -b … -P …` or pip `bpy`. Use `bpy.ops` only for `render.render` (and build-time operators that have no data-API equivalent, wrapped in explicit context overrides). Pose changes use the data API.
> 4. **Every task ends with tests executed and their output shown.** A task with no passing test is not done.
> 5. **`main` must always be shippable** after Gate G1: `make bundle` must produce a valid ZIP at every merge.
> 6. **Licences:** use only CC0 assets (MPFB2 system assets, Skins 01/02, CC0 eyebrows/lashes). **No** CC-BY (e.g. "System eye materials 03"), no non-commercial assets, no FLAME/SMPL. Log every asset in `extras/ATTRIBUTION.md`.
> 7. Do not invent citations. Do not claim a test passed unless you ran it.
> 8. Prefer small, boring, deterministic code. One file `wrapper/eyes.py` must stay self-contained (stdlib + `bpy` + `mathutils` + `numpy`).

---

## 1. Timeline and gates

| Day | Date | Focus | Gate |
|---|---|---|---|
| D0 | Fri 6 Nov | **Human:** register team, email organizers, build base character (H1). **Agent A:** P0 scaffolding + core math + schema | — |
| D1 | Sat 7 Nov | Finish P0. Inspect character (T1.1). Start scene build | — |
| D2 | Sun 8 Nov | **Registration deadline (human, before 11:59 PM)**. Scene build + Tier-A eyes. First end-to-end sweep | **G1: first sweep** |
| D3–4 | 9–10 Nov | Wrapper hardening (P2). Verifier V1–V7 (P3) | — |
| D5 | Tue 10/Wed 11 Nov | AnatomEye (Tier B) | **G2: go/no-go on AnatomEye** |
| D6 | Thu 12 Nov | Framing, lighting, iris contrast, detectors V8–V10, V14 | — |
| D7 | Fri 13 Nov | Packaging, Docker, cross-version, README | **G3: ship candidate #1 (full verify green)** |
| D8–9 | 14–15 Nov | Polish, demo video, slides, optional wow-features | — |
| D10 | Mon 16 Nov | **FREEZE.** Only bug fixes after this | — |
| D11 | Tue 17 Nov | Final clean-room test, submit | **Submitted** |
| D12 | Wed 18 Nov | Buffer only | — |

**Gate definitions**
- **G1 (first sweep):** `make sweep` produces 10 PNGs + `metadata.json` from `scene.blend` headless; core tests pass; ugly is fine. If not reached by end of D2, stop feature work and fix only this.
- **G2 (AnatomEye go/no-go):** AnatomEye eyes sit in the sockets with no visible gaps or lash clipping, pupil never occluded at the extremes, and V3, V4, V7 pass. If not, **ship Tier A** and spend the days on verification and polish instead.
- **G3 (ship candidate):** `make verify` is all green on 4.5 LTS; secondary 5.2 LTS run passes V1–V7, V12; ZIP validated in a clean directory.

**If time runs out, cut in this order:** W-features → eyelid coupling → AnatomEye (fall back to Tier A) → Docker → 5.2 LTS test. **Never cut:** V1–V7, V10, V12, V13, V15, the README, the contact sheet, the demo video, on-time submission.

---

## 2. Human-only tasks (cannot be automated)

### H0 — today (30 min)
1. **Register the team** via the Google Form (verify the URL on the slide, the transcribed one has unreliable characters). Team name `CollegeName_TeamName` (e.g. `VIT_<YourTeamName>`). Max 4 members from one college; one theme per team. **Deadline Sun 8 Nov 11:59 PM, do it today.** The submission link is only sent to registered teams.
2. Email `prism@samsung.com` with the questions in `01` §14. Send it after registering so you can quote the team name.
3. Create a public (or shared) GitHub repo. Keep the repo private until you decide to publish; the form wants a public or shared link at submission.

### H1 — build the base character (1–2 h, Blender GUI, once)
Goal: `assets/base_character.blend` containing an MPFB human with a skeleton, skin textures, eyebrows and lashes.
1. Install **Blender 4.5 LTS** (portable zip is fine). Install **MPFB 2.0.17** via *Edit → Preferences → Get Extensions → search "MPFB"*.
2. In MPFB's settings/asset library, install the asset packs from the MakeHuman community asset-pack page: **MakeHuman system assets**, **Skins 01** (natural female) and/or **Skins 02** (natural male) — all CC0. Skip any CC-BY pack.
3. *New human* (from a preset or defaults). Pick an adult, neutral-expression face. **Open the eyes wide enough that no part of the pupil area can be covered by the upper lid** (use MakeHuman eye-opening/eye-size modifiers; the exact modifier names depend on the MPFB version, explore the "Modeling → Eyes" panel). Make the interpupillary distance look natural.
4. Apply a CC0 **skin** material. Add **eyebrows** and **eyelashes** (system assets). **No hair, no clothes.** Keep the stock eyes for now.
5. *Rigging → Standard rig → "Default"* (the 163-bone default skeleton; "default no toes" is also fine). Do not use Rigify (extra complexity, no benefit).
6. Move/rotate nothing. Save as `assets/base_character.blend`. Write the MPFB version, Blender version, and each asset name + licence into `extras/ATTRIBUTION.md`.
7. Screenshot the head from the front (for your own sanity).

*MPFB's UI changes between versions. If a step differs, follow the official MPFB docs rather than guessing; the only hard requirements are the final contents above.*

### H2 — before submission
Record the voice-over (or screen-record per the storyboard), upload the video (YouTube unlisted or Drive "anyone with link" **and test the link while logged out**), fill the final form, and keep a screenshot of the confirmation.

---

## 3. Repository layout

```
apollo/
├── Makefile
├── README.md                    # becomes bundle README (generated sections from verify)
├── DECISIONS.md                 # any deviation or open question, dated
├── docs/01_SOLUTION_TECHNICAL.md  docs/02_IMPLEMENTATION_PLAN.md
├── assets/base_character.blend  # from H1 (git-lfs or plain; < 100 MB)
├── build/
│   ├── inspect_character.py     # T1.1
│   ├── build_scene.py           # T1.2–T1.7, deterministic, idempotent
│   └── anatom_eye.py            # T1.5 (Tier B)
├── wrapper/
│   └── eyes.py                  # self-contained; embeds a copy of core math
├── apollo_core/
│   ├── core.py                  # pure math (reference below); source of truth
│   └── test_core.py
├── tools/
│   ├── verify.py                # V1–V17 driver
│   ├── validate_metadata.py
│   ├── grader_sim.py            # blind detectors A and B, direction suite
│   ├── contact_sheet.py
│   ├── framing_sweep.py
│   ├── make_bundle.py           # build + validate ZIP
│   └── sync_core.py             # copies core.py into wrapper/eyes.py between markers
├── metadata.schema.json
├── Dockerfile  requirements.txt
└── out/                         # build products (gitignored): scene.blend, renders/, metadata.json, bundle zip
```

**Core-math sync rule:** `wrapper/eyes.py` must be self-contained, so it embeds the contents of `apollo_core/core.py` between `# BEGIN CORE` / `# END CORE` markers, written by `tools/sync_core.py`. A test fails if the embedded copy differs from `core.py`.

**Makefile targets:** `test` (pure-Python tests), `scene` (build `out/scene.blend`), `sweep` (run the default sweep headless), `verify` (V1–V17 and report), `sheet`, `bundle`, `docker`, `all` (= test, scene, sweep, verify, sheet, bundle).

---

## 4. Environment

- **Reference:** Blender 4.5 LTS (Python 3.11). Scripts must run via `blender -b <file> -P <script> -- <args>`. Env var `BLENDER_BIN` points at the binary.
- **pip route:** `pip install bpy==4.5.<latest 4.5.x on PyPI>` into Python 3.11 (a 4.5.12 wheel exists for Linux/Windows/macOS at the time of writing). Each Blender release supports exactly one Python version.
- **Secondary:** Blender 5.2 LTS (released Jul 2026). Avoid APIs that changed in 5.x: do not touch the compositor node tree or EEVEE; use Cycles only. Keep a compat shim in `eyes.py` if anything differs.
- **Python deps outside Blender (tools only):** `numpy`, `pillow`, `opencv-python-headless`, `pytest`, `jsonschema`. The wrapper itself needs none beyond what ships with Blender.
- **Dockerfile:** `FROM python:3.11-slim`, apt-install the usual headless GL/X libs `bpy` needs (`libgl1 libxi6 libxxf86vm1 libxfixes3 libxrender1 libsm6 libxkbcommon0 libegl1` or whatever the first import error asks for), `pip install bpy==<pinned> numpy …`, copy the bundle, `CMD ["python","wrapper/eyes.py"]`. Agent must **actually build and run it** and record the wall-clock time.

---

## 5. Reference implementation: pure math (tested)

This is the single source of truth for rotations, projection and the sweep. It was run against the tests below (11 passed). Do not "improve" the conventions. Extend only by adding.

`apollo_core/core.py`

```python
"""apollo/core.py - pure-python (numpy only) reference math. No bpy imports. Frozen conventions: see 01_SOLUTION_TECHNICAL.md s3."""
from __future__ import annotations
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
    h = float(max(-1.0, min(1.0, h))); v = float(max(-1.0, min(1.0, v)))
    P = fixation_point(h, v, c) if not c.parallel else None
    out = {}
    for name, C in eye_centers(c).items():
        tgt = P if P is not None else C + np.array([c.bound * h, -c.target_dist, c.bound * v])
        g = (tgt - C); g /= np.linalg.norm(g)
        q = shortest_arc(FWD, g); R = quat_to_mat(q); pupil = C + c.pupil_depth * g
        out[name] = dict(quat=q, R=R, euler=mat_to_euler_xyz(R), gaze=g, pupil3d=pupil, pupil2d=project(pupil, c))
    return out, P

def sweep_inputs(n=10):
    return [(k, 2 * math.pi * k / n, math.sin(2 * math.pi * k / n), math.cos(2 * math.pi * k / n)) for k in range(n)]

def make_record(k, theta, h, v, c: Config, image_name):
    st, P = eye_state(h, v, c); f = lambda a: [float(x) for x in a]
    return {
        "frame": k, "theta": theta, "input": {"h": h, "v": v},
        "eye_rotation_L": f(st["L"]["euler"]), "eye_rotation_R": f(st["R"]["euler"]),
        "pupil_center_2D_L": f(st["L"]["pupil2d"]), "pupil_center_2D_R": f(st["R"]["pupil2d"]),
        "camera_matrix": intrinsics(c).tolist(),
        "extra": {"schema_version": "1.0", "image": image_name,
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
    ph = np.linspace(0.0, 2 * math.pi, n, endpoint=False)
    pts = np.array([project(center3d + radius * (math.cos(p) * u + math.sin(p) * w), c) for p in ph])
    mu = pts.mean(0); lam, vec = np.linalg.eigh(np.cov((pts - mu).T, bias=True))
    a, b = math.sqrt(2 * lam[1]), math.sqrt(2 * lam[0])
    return {"center": [float(mu[0]), float(mu[1])], "semi_axes": [a, b], "angle": math.atan2(vec[1, 1], vec[0, 1])}

def angle_from_primary(q):
    """Total rotation angle (radians) of an eye quaternion relative to primary position (for range assertions)."""
    return 2 * math.acos(max(-1.0, min(1.0, abs(q[0]))))

PUPIL_RADIUS = 0.002  # m (d = 4 mm)
MAX_ECCENTRICITY = math.radians(35.0)  # oculomotor-plausible bound; assert in dataset mode so pupils never roll into the skull
```

`apollo_core/test_core.py`

```python
import math, numpy as np
from core import *
C=Config()
def test_sweep():
    s=sweep_inputs()
    assert len(s)==10 and s[0][2]==0 and abs(s[0][3]-1)<1e-15
    assert abs(s[3][2]-0.9510565162951536)<1e-15 and abs(s[3][3]+0.30901699437494734)<1e-15
    assert abs(s[3][1]-1.8849555921538759)<1e-15
def test_rest():
    q=shortest_arc(FWD,FWD); assert np.allclose(q,[1,0,0,0])
def test_gaze_hits_target():
    for h,v in [(0,0),(1,0),(-1,1),(0.3,-0.7)]:
        st,P=eye_state(h,v,C)
        for n,Ce in eye_centers(C).items():
            g=st[n]["R"]@FWD; assert np.allclose(g,st[n]["gaze"],atol=1e-12)
            t=np.dot(P-Ce,g); assert np.linalg.norm(Ce+t*g-P)<1e-12
def test_no_torsion_listing():
    # rotation axis perpendicular to primary direction
    for h,v in [(1,1),(-1,0.5),(0,-1)]:
        st,_=eye_state(h,v,C)
        for n in 'LR':
            q=st[n]["quat"]; assert abs(q[1:]@FWD)<1e-12
def test_center_px():
    st,_=eye_state(0,0,C)
    assert abs(st["L"]["pupil2d"][0]-735.1828745)<1e-5 and abs(st["L"]["pupil2d"][1]-512)<1e-9
    assert abs(st["R"]["pupil2d"][0]-288.8171255)<1e-5
def test_directions():
    c0,_=eye_state(0,0,C)
    for (h,v,sx,sy) in [(1,0,+1,0),(-1,0,-1,0),(0,1,0,-1),(0,-1,0,+1)]:  # image y is down
        s,_=eye_state(h,v,C)
        for n in 'LR':
            dx=s[n]["pupil2d"][0]-c0[n]["pupil2d"][0]; dy=s[n]["pupil2d"][1]-c0[n]["pupil2d"][1]
            if sx: assert dx*sx>9 and abs(dy)<0.2
            if sy: assert dy*sy>9 and abs(dx)<0.2
def test_euler_roundtrip():
    for h,v in [(1,1),(-1,0.2)]:
        st,_=eye_state(h,v,C)
        for n in 'LR':
            x,y,z=st[n]["euler"]
            Rx=np.array([[1,0,0],[0,math.cos(x),-math.sin(x)],[0,math.sin(x),math.cos(x)]])
            Ry=np.array([[math.cos(y),0,math.sin(y)],[0,1,0],[-math.sin(y),0,math.cos(y)]])
            Rz=np.array([[math.cos(z),-math.sin(z),0],[math.sin(z),math.cos(z),0],[0,0,1]])
            assert np.allclose(Rz@Ry@Rx, st[n]["R"], atol=1e-12)
def test_clockwise():
    c0,_=eye_state(0,0,C); pts=[]
    for k,th,h,v in sweep_inputs():
        s,_=eye_state(h,v,C); pts.append((s["L"]["pupil2d"][0]-c0["L"]["pupil2d"][0], -(s["L"]["pupil2d"][1]-c0["L"]["pupil2d"][1])))
    ang=[math.atan2(y,x) for x,y in pts]
    d=[(ang[(i+1)%10]-ang[i]+math.pi)%(2*math.pi)-math.pi for i in range(10)]
    assert all(x<0 for x in d)   # decreasing math-angle (y up) == clockwise on screen
def test_record_keys():
    r=make_record(3,*sweep_inputs()[3][1:],C,"frame_03.png")
    assert list(r)[:8]==["frame","theta","input","eye_rotation_L","eye_rotation_R","pupil_center_2D_L","pupil_center_2D_R","camera_matrix"]

def test_gaze_angles_and_ellipse():
    st,_=eye_state(0,0,C)
    p,y=gaze_pitch_yaw(st["L"]["gaze"]); assert abs(p)<1e-12
    assert y>0 and abs(y-math.radians(5.1427645))<1e-6     # converged eye: nasal yaw, small
    up,_=eye_state(0,1,C); assert gaze_pitch_yaw(up["L"]["gaze"])[0]>0.13   # looking up => positive pitch
    e=pupil_ellipse_2d(st["L"]["pupil3d"],st["L"]["gaze"],PUPIL_RADIUS,C)
    assert abs(e["center"][0]-st["L"]["pupil2d"][0])<0.01 and abs(e["center"][1]-st["L"]["pupil2d"][1])<0.01
    assert 12<e["semi_axes"][0]<16 and e["semi_axes"][1]<=e["semi_axes"][0]   # ~ 2mm radius = ~14 px
def test_eccentricity_bound():
    for h,v in [(1,1),(-1,-1),(1,-1)]:
        st,_=eye_state(h,v,C)
        for n in 'LR': assert angle_from_primary(st[n]["quat"])<MAX_ECCENTRICITY
```

**Expected numbers (agent must reproduce these in the real scene within tolerance):** L pupil at reset (735.1829, 512.0000), R pupil (288.8171, 512.0000); pupil shift at the 5 cm bound ≈ 10.4 px; per-eye rotation at center ±5.143° about world Z; vergence 10.286°. See `01` §17.

---

## 6. Phase P1 — Scene construction (Blender, headless)

### T1.1 `build/inspect_character.py`
Print and save `out/inspect.json`:
- Armature name, object transforms; for every bone matching `/eye|head|neck/i`: name, parent, head/tail (local and world), roll, `matrix_local`.
- Every mesh object: name, vertex count, world bounding box, materials, modifiers, vertex groups.
- Stock eye meshes: world-space center (bounding-box center), best-fit sphere radius, forward-pointing pole direction.
- Measured: interpupillary distance (distance between eye centers), head width, which way the character faces, texture image names and sizes.
- Acceptance: file produced; **write the observed bone names and the eye-center-vs-bone-head distances into `DECISIONS.md`**. Everything below must use observed names, not assumptions (`eye.L`/`eye.R` are *likely*, not guaranteed).

### T1.2 `build/build_scene.py` (idempotent; loads `assets/base_character.blend`, saves `out/scene.blend`)
1. **Orientation and origin:** ensure the character faces −Y (rotate the root object about Z if needed). Translate the character root so the **midpoint of the two eyeball centers = (0,0,0)**. Do not scale the character; measure IPD and set `Config.ipd` to the measured value rounded to 0.1 mm (assert 58–68 mm). If the two eye centers are not symmetric about x=0 and at identical y,z (tolerance 0.05 mm), snap the **eye bone heads** to `(±ipd/2, 0, 0)` using edit bones, then re-verify.
2. **Units:** `scene.unit_settings.system='METRIC'`, `scale_length=1.0`.
3. **Camera** `Camera.Gaze`: location `(0, −0.400, 0)`, rotation Euler `(π/2, 0, 0)`, `lens=100`, `sensor_width=36`, `sensor_fit='HORIZONTAL'`, `shift_x=shift_y=0`, `clip_start=0.05`, `clip_end=5`, perspective, no DOF. Set as `scene.camera`.
4. **Empties:** `EyeMidpoint` (0,0,0); `FixationTarget` (0,−0.350,0); optional hidden `FixationBounds` wireframe plane/box ±0.05 m at y=−0.35 (hide_render=True, for the GUI audience).
5. **Lights:** 1 area key (large, soft), 1 weak area fill, neutral gray world. **No animation data, no drivers** on any light/camera/world. Pick the key position so the corneal catchlight lands away from the pupil (tuned in P5). Store a canonical JSON of all light params → `scene["apollo_lighting"]`.
6. **Render settings:** Cycles, CPU, `samples=128` (tunable), `use_adaptive_sampling=False`, `seed=0`, `use_animated_seed=False`, OIDN denoise on, `film_transparent=False`, `view_transform='Standard'`, `look='None'`, resolution 1024×1024 @ 100 %, PNG 8-bit RGB, fixed compression. `scene.frame_set(1)`.
7. **Calibration block:** `scene["apollo_calibration"] = json.dumps({...Config values, measured IPD, conventions...})`.
8. **Pose:** leave the scene saved in the `reset` pose (applied via the same function the wrapper uses).
9. **Pack and clean:** `bpy.ops.file.pack_all()`, downscale any image > 2048 px, purge orphans, `bpy.ops.wm.save_as_mainfile(filepath=..., compress=True)`.
- **Acceptance:** `out/scene.blend` opens headless with no missing files; V1 passes.

### T1.3 Tier A eyes (do this first; it is the safety net)
Keep the stock MPFB eyes. Add a black **pupil disc** object (d = 4 mm) skinned 100 % to each eye bone (vertex group named exactly like the bone + Armature modifier), placed on the stock eye's forward pole, offset by +0.1 mm beyond the measured sphere radius so it is visible. Use that offset as `pupil_depth` for Tier A (so `Config.pupil_depth = sphere_radius + 0.0001`). Store the rest-pose pupil-center offset in the eye bone's local space as a custom property for the wrapper.
- Acceptance: a first full sweep renders; pupil moves in the correct directions. **This is G1.**

### T1.4 Tier B: `build/anatom_eye.py` (AnatomEye)
Parametric generator (all lengths in meters from `Config`/an `EyeParams` dataclass) producing for each side:
- **Sclera:** UV/ico sphere r = 12.0 mm, center = eye bone head (exactly).
- **Cornea:** spherical cap (r ≈ 7.8 mm), apex ≈ 13.2 mm from center, transparent shell. Agent must compute the cap so it intersects the sclera sphere cleanly (no gap). Material: transparent + glossy reflection layer, **no refraction** (IOR 1.0 transmission or mix-shader with transparency), keep reflection on.
- **Iris:** disc or shallow cone at pupil-plane depth (10.0 mm from the center), diameter 11.7 mm, UV-mapped, shader with radial fibre pattern (noise/wave texture stretched radially) over an image texture (CC0) or a procedural colour ramp. **Light iris (blue/green/light hazel)** so the pupil is high-contrast.
- **Pupil:** separate disc, d = 4.0 mm, at the pupil-plane depth +0.05 mm in front of the iris, pure black emission-free shader, **128-segment** circle so centroids are symmetric.
- **Skinning:** each part gets a vertex group named after the eye bone (weight 1.0 for all verts) and an Armature modifier. **Do not use bone parenting** (its transform origin is the bone *tail*, a known trap).
- **Calibration:** measure `pupil_center − eye_center` from geometry after building, rotate the *mesh* so that this vector equals the world rest optical axis `(0,−1,0)` (at the rest pose), assert the angle error < 1e-9 rad, store the offset in the eye bone's local space (custom prop `gf_pupil_local`).
- Hide or delete the stock eye meshes (`hide_render=True`, `hide_viewport=True`); keep their data out of the saved file if possible (smaller file).
- **Acceptance (G2):** zoomed render shows no gap between lids and eyeball, no lash clipping, no skin-through; pupil visible at all extremes; V3, V4, V7 pass.

### T1.5 Materials and look
- Skin: the MPFB CC0 material as imported (check it works under Cycles CPU, reduce SSS cost if render time > budget).
- Verify the **catchlight** (corneal reflection of the key light) lies on the iris, away from the pupil, in all 10 frames and at the extremes. Adjust key light position/size, not the eyes.
- Pupil/iris contrast: iris luminance within the pupil's neighbourhood should be ≥ 4× the pupil luminance (measured by V8/V14).

---

## 7. Phase P2 — `wrapper/eyes.py`

Contract (see `01` §8). Implementation skeleton for the Blender-bound part (the core block is embedded between markers). **Agents must verify every `bpy` call against the installed version**; names below are the known-stable ones.

```python
# ---- wrapper/eyes.py (skeleton) ----
import sys, os, json, math, hashlib, shutil, subprocess
from pathlib import Path
try:
    import bpy, mathutils
    from mathutils import Matrix, Vector
    from bpy_extras.object_utils import world_to_camera_view
    HAVE_BPY = True
except ImportError:
    HAVE_BPY = False

# BEGIN CORE
# (contents of apollo_core/core.py, written by tools/sync_core.py)
# END CORE

ROOT = Path(__file__).resolve().parent.parent if "__file__" in globals() else Path.cwd()
BONES = {"L": "eye.L", "R": "eye.R"}          # replace with observed names from T1.1 (read from scene custom prop)

class _Rig:
    def __init__(self):
        self.scene = bpy.context.scene
        self.cfg = _load_cfg(self.scene)                    # from scene["apollo_calibration"]
        self.arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
        self.rest = {}
        for s in "LR":
            pb = self.arm.pose.bones[BONES[s]]
            M = self.arm.matrix_world @ pb.bone.matrix_local
            self.rest[s] = (M.to_quaternion().to_matrix(),          # world rest orientation (orthonormal)
                            M.translation.copy(),                   # world head position
                            Vector(pb.get("gf_pupil_local")))       # pupil offset in bone-local space
        self.h = self.v = 0.0

    def apply(self, h, v):
        st, P = eye_state(h, v, self.cfg)                           # core math, doubles
        for s in "LR":
            pb = self.arm.pose.bones[BONES[s]]
            Rrest, head_w, _ = self.rest[s]
            R_des = Matrix(st[s]["R"].tolist()) @ Rrest             # world delta applied on world rest
            M_world = Matrix.Translation(head_w) @ R_des.to_4x4()
            pb.matrix = self.arm.matrix_world.inverted() @ M_world  # data API, no bpy.ops
        bpy.context.view_layer.update()
        self.h, self.v = h, v
        return st, P

    def measured_pupil_world(self, s):
        pb = self.arm.pose.bones[BONES[s]]
        return (self.arm.matrix_world @ pb.matrix) @ self.rest[s][2]   # bone-local offset -> world

def _rig():  # lazy singleton; auto-load scene.blend if no armature is open
    global _RIG
    if "_RIG" not in globals() or _RIG is None:
        if not any(o.type == "ARMATURE" for o in bpy.data.objects):
            bpy.ops.wm.open_mainfile(filepath=str(_find_scene_blend()))
        _RIG = _Rig()
    return _RIG

def move(h, v):
    h2, v2 = clamp(h), clamp(v)                       # also record clamped flag
    return _rig().apply(h2, v2)

def reset():
    return move(0.0, 0.0)

def render(path=None):
    r = _rig(); sc = r.scene
    path = Path(path) if path else ROOT / "output" / f"render_h{r.h:+.4f}_v{r.v:+.4f}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return {"path": str(path), "record": _record_now(r)}
```

Required behaviours, each with a test in `tools/verify.py`:
- `move` is **absolute**; `reset() == move(0,0)`; any call order gives identical pose (V11).
- The metadata record is built from **core math (doubles)**, then **asserted against measured values** (pose-bone matrix → Euler; evaluated pupil → projection; `world_to_camera_view` ×1024 with y flipped). Tolerances: rotation 1e-5 rad, pupil 3D 1e-6 m, 2D 1e-3 px for the cross-check implementations. On violation, raise (never write a bad record silently).
- `sweep(n=10)`: for k in 0…9: `move(sin θ, cos θ)`; `render(renders/frame_%02d.png)`; collect records; write `metadata.json` (array); finish with `reset()`.
- Default `__main__` behaviour (no args): full sweep into `<bundle>/renders` and `<bundle>/metadata.json`. Args after `--`: `--sweep`, `--h X --v Y --out F`, `--verify`, `--calibration`, `--quality draft|final`, `--parallel`.
- **Relaunch:** if `bpy` is unavailable, locate Blender (`BLENDER_BIN`, then `PATH`) and re-exec `blender -b scene.blend -P eyes.py -- <args>`; otherwise print an actionable error and exit 2.
- Records include the dataset-style extras that `core.make_record` already produces: `gaze_vector_cam_*`, `gaze_pitch_yaw_*`, `pupil_ellipse_2D_*`. Keep them under `extra`; never at top level.
- JSON: convert every `mathutils` object to plain lists of floats; `allow_nan=False`.
- Path handling: `Path(__file__)`-relative; fall back to CWD search for `scene.blend` if `__file__` is missing (exec'd by a harness).
- Logging: single-line progress (`frame 3/10 θ=1.885 h=0.951 v=-0.309 t=12.4s`), total time at the end, exit code 0 only on success.

---

## 8. Phase P3 — Verification (`tools/verify.py`, `tools/grader_sim.py`)

Implement V1–V17 from `01` §11. Implementation notes:

- **V7 pixel-truth (the crown jewel).** For each frame: run Blender with a *mask scene variant*: set every object except the two pupil discs to `hide_render=True`; pupil material = white emission; world = black; no other lights; Cycles 16–32 spp, no denoise, `view_transform='Standard'`. Output 8-bit (or 16-bit) PNG. Compute the **intensity-weighted centroid** per pupil (split the image into left/right halves, or label connected components) using pixel centers at `(i+0.5, j+0.5)`. Compare against `pupil_center_2D_*` from `metadata.json`. Pass: < 0.5 px (target ≤ 0.2 px) for all 20 pupil/frame pairs. Rendering the pupil unoccluded isolates the projection pipeline (camera, intrinsics, pixel convention, pose) from occlusion; occlusion is V14.
- **V14 visibility.** Using the V7 mask as the expected pupil area: in the final frame, the fraction of mask pixels that are pupil-dark (luma below a threshold derived from the reset frame) must be ≥ 0.98, and no catchlight (very bright) pixels inside the mask.
- **V6 dual projection:** compute `world_to_camera_view(scene, cam, p)` → `(x·1024, (1−y)·1024)`; compare with core `project`. Agreement < 1e-3 px.
- **V8 blind detector A:** grayscale → restrict to the central horizontal band → threshold at a low percentile → connected components → keep the two most circular blobs of plausible area → fit ellipse (OpenCV) → centers. Compare with metadata: < 1 px. Must not read metadata when detecting.
- **V9 blind detector B:** take the reset frame's eye crops (±70 px around the iris) as templates; `cv2.matchTemplate` (normalized correlation) on each frame's neighbourhood; sub-pixel by parabola fit; compute displacement vs reset; compare direction and magnitude to the analytic shift (< 1.5 px error).
- **V10 direction suite:** render 5 frames via the public API only: `move(-1,0)` Left, `move(1,0)` Right, `move(0,1)` Up, `move(0,-1)` Down, `reset()`. Assert on *both* detectors: correct sign; magnitude ≥ 8 px; cross-talk (orthogonal component) < 0.5 px; `reset()` frame **byte-identical** to the baseline center frame.
- **V12 determinism:** two full sweeps; compare SHA-256 of every PNG and of `metadata.json`.
- **V15 bundle:** unzip into a temp dir; run with `BLENDER_USER_CONFIG`/`SCRIPTS` pointed at an empty dir (no add-ons); confirm no pink/missing textures (`bpy.data.images[*].has_data` and `filepath` sanity, all packed); run `eyes.py` from a *different* CWD; compare outputs to shipped renders (hash).
- **V17 annotation sanity:** ellipse center vs projected pupil center < 0.02 px; ellipse semi-axes ≈ 14.6 px at the chosen framing; pitch/yaw consistent with the camera-frame gaze vector; every eye rotation < 35° (`MAX_ECCENTRICITY`). Raise before writing metadata if violated.
- **Report:** write `extras/verification_report.md` with a table of V1–V17, measured numbers (max residuals, timings), Blender/OS/CPU info, git commit.

All of V1–V17 gate `make verify`'s exit code.

---

## 9. Phase P4 — Packaging, contact sheet, README

### `tools/contact_sheet.py` → `contact_sheet.png`
5 × 2 grid of the 10 renders (each downscaled to ~512 px, total ≈ 2560 × 1024 or two rows of five). Per tile: frame index, θ in degrees, (h, v), a small clock-hand dial showing the commanded direction, **pupil crosshairs drawn from `metadata.json`**, and a faint ring at the reset-pupil position so the shift is obvious. Footer: conventions in one line.

### `tools/make_bundle.py`
Builds `VIT_<TeamName>/` with the exact layout in `01` §12, runs `validate_metadata`, `verify --bundle`, and zips. Assert: `renders/` has exactly 10 PNGs named `frame_00.png … frame_09.png`; sizes 1024×1024; ZIP < 60 MB; top-level folder name equals the ZIP stem. **Confirm the team-name string against the registration slide before the final build.**

### README.md (bundle) — required sections
1. **TL;DR** and the one-command run (`blender -b scene.blend -P wrapper/eyes.py`; Docker; pip-bpy).
2. Versions tested (Blender 4.5 LTS primary, 5.2 LTS secondary), OS, CPU, measured runtime.
3. **Conventions table** (copy of `01` §3).
4. **Calibration table** (measured, not assumed) + framing-sweep table and the chosen focal length.
5. Wrapper API with examples (`move`, `reset`, `render`, `sweep`).
6. Metadata schema description with a real record.
7. **Verification summary** (the V1–V17 table from the last run, residuals).
8. Reproducibility and determinism statement.
9. Known limitations (from `01` §16).
10. Asset attribution and licences.
11. Troubleshooting (Blender not found, headless GL libs, etc.).

---

## 10. Phase P5 — Optimization loops (after G2)

1. **Framing sweep** (`tools/framing_sweep.py`): for f in 85…135 mm step 5, render the reset frame and an Up/Right frame; record (a) pupil shift px, (b) eye-region margins, (c) whether lashes/brows clip. Choose the largest f meeting margins ≥ 8 %. Update `Config.focal_mm`, regenerate everything. Table goes in README.
2. **Lighting/catchlight pass:** iterate key light position/size until V14 passes at all 10 frames and extremes; constant lighting thereafter (hash locked).
3. **Detector-robustness pass:** run V8/V9 at 3 deliberately harsh settings (slightly different denoise, ±10 % brightness) to ensure margin; raise iris brightness/contrast if needed.
4. **Performance:** profile; target ≤ 30 s/frame final on 8 cores. Levers: samples, denoise, SSS samples, light bounces, texture size, remove unseen geometry. Print timings in README. Provide `--quality draft` (≤ 5 s/frame).
5. **Eyelid coupling (P2 priority):** only if time allows and only if it never causes pupil occlusion.

---

## 11. Phase P6 — Demo video and presentation

### Video (target 100–110 s; satisfies both "1–2 min" and "≤ 3 min")
Storyboard:
| Time | Visual | Voice-over point |
|---|---|---|
| 0:00–0:10 | Title; split image: 2D sliding pupil vs 3D rotating eyeball | Synthetic gaze data gap; why planar pupil sliding is wrong |
| 0:10–0:35 | Blender viewport: eye bones, pivot at eyeball center, fixation target at 35 cm, camera at 40 cm (orthographic diagram overlay) | Calibration, binocular fixation, Listing's law |
| 0:35–1:05 | The 10 clockwise frames playing as a loop with pupil crosshairs and the dial | Sweep θ_k, h = sin, v = cos, metadata |
| 1:05–1:25 | Terminal: `make verify`, report scrolling to all PASS; zoom on "pixel-truth residual 0.1 px" | Provably exact ground truth |
| 1:25–1:40 | Wrapper code: `eyes.move(1,0); eyes.render()`; then dataset-mode montage (W1) | One command; scales to training data |

Record with OBS; render the 10-frame loop as MP4/GIF via `ffmpeg`. Keep audio clean; add burned-in captions. Test playback logged-out.

### Presentation (PPT/PDF, name per convention; content required by the form)
1. Title: Theme ID, project title, team details.
2. Problem in our own words (data gap, privacy, extreme angles; why 3D rotation).
3. Solution overview + **architecture diagram** (base character → build_scene → wrapper → render → metadata → verifier).
4. Geometry slide: pivot, optical axis, fixation point, ray diagram, formulas.
5. Results: contact sheet, shift table, verification table (residuals).
6. Tools and technology stack (Blender 4.5 LTS, MPFB2 CC0, Python, Cycles CPU, OpenCV for verification, Docker).
7. Innovation highlights (pixel-truth verifier, grader-proof API, dataset mode, live-aim mode).
8. Limitations and future work (honest list from `01` §16).

---

## 12. Phase P7 — Wow features (only after G3; none may touch the graded path)

- **W1 dataset mode:** `extras/generate_dataset.py --n 1000 --seed 0` renders random (h,v) inside the unit square with the same record schema, plus optional per-frame random key-light jitter (clearly labelled as dataset mode; the graded sweep stays fixed-light). Report frames/hour on CPU.
- **W2 live-aim mode:** constraints on the eye bones (`DAMPED_TRACK` to `FixationTarget`), **muted by default**, enabled by a scene custom property for GUI demos. Parity test: with constraints enabled, the resulting eye orientations equal the analytic ones to < 1e-6 rad. The wrapper must work identically with constraints muted.
- **W3 refraction ablation:** `--refractive-cornea` experiment; measure and plot residual px vs gaze; one slide.

---

## 13. Test matrix and "definition of done"

| Layer | Tests | Runs where |
|---|---|---|
| Core math | `pytest apollo_core` (11 given + extend) | any Python |
| Schema | `validate_metadata.py` against `metadata.schema.json` | any Python |
| Scene | V1, V2, V3, V4, V5 | Blender headless |
| Pixels | V6, V7, V8, V9, V10, V14 | Blender + OpenCV |
| Repro | V11, V12, V15, V16 | Blender, clean dir, two versions |

**Done =** G3 achieved; clean-room run from the unzipped bundle on a machine that never saw the repo reproduces the shipped PNG hashes (same Blender build) or matches within the documented tolerance; README complete; contact sheet and video done; submission form filed.

---

## 14. Final submission runbook (Tue 17 Nov)

1. `git tag v1.0-submission`. `make clean && make all` from a fresh clone on a clean machine (or fresh Docker).
2. Unzip the produced ZIP into an empty folder on a different machine if possible. Run `blender -b scene.blend -P wrapper/eyes.py` from a *different* working directory. Compare hashes with the shipped renders.
3. Check: ZIP name = `team_name.zip`, inner folder = `team_name/`, exactly 10 PNGs, metadata array of 10, README renders correctly, contact sheet present, size < 60 MB.
4. Video ≤ 3 min uploaded; link tested logged-out. Presentation named per convention. GitHub repo public/shared with README.
5. Submit via the form link sent to registered teams. **One submission per team.** Screenshot the confirmation. Email a copy of the ZIP to every team member and to cloud storage.
6. Do **not** touch anything after submission except to re-submit if a defect is found and the form allows it (check). Buffer day is for emergencies only.

---

## 15. Agent assignment suggestions

| Agent | Scope | Needs Blender? |
|---|---|---|
| **A (core/verify)** | P0, `core.py`, schema, validator, `grader_sim.py` detectors on synthetic test images, contact sheet, bundle tool | No (until D4) |
| **B (Blender)** | T1.1–T1.5, `build_scene.py`, `anatom_eye.py`, `eyes.py` | Yes |
| **C (QA/docs)** | verify driver, determinism, cross-version, Docker, README, demo/slide assets | Yes |

**Prompt for Agent B (copy/paste):**
> Read `docs/01_SOLUTION_TECHNICAL.md` and `docs/02_IMPLEMENTATION_PLAN.md` fully. Implement T1.1 first and show me its output. Then implement T1.2 and T1.3 so that `make sweep` produces 10 PNGs and a valid `metadata.json` from a scene built from `assets/base_character.blend`. Use the reference math in `apollo_core/core.py`; do not change conventions. Run headless only. Before using any bpy call you are not 100 % sure about, write a tiny experiment script and print its output. Report which bone names, eye geometry measurements, and measured IPD you observed. Stop at Gate G1 and summarize the results with numbers.

**Prompt for Agent A:**
> Read both docs. Set up the repo, Makefile and `pytest` for `apollo_core`. Write `metadata.schema.json` and `tools/validate_metadata.py` (exact key order and types as in `01` §9). Implement `tools/grader_sim.py` with blind detector A (threshold + ellipse fit) and detector B (template matching) and test both on synthetic images that you render with numpy (an iris disc and a black pupil at known sub-pixel positions on a skin-like background with noise). Prove sub-pixel accuracy numbers. Do not touch Blender code.

**Prompt for Agent C:**
> Read both docs. Once `out/scene.blend` and `wrapper/eyes.py` exist, implement `tools/verify.py` V1–V17 exactly as specified in §8, including the mask-render variant for V7. Produce `extras/verification_report.md`. Then Dockerize, run cross-version checks on Blender 4.5 LTS and 5.2 LTS, and report any API drift.

---

## 16. Appendix: pitfalls checklist for agents

- **Bone parenting uses the bone tail**: skin meshes with vertex groups + Armature modifier instead.
- **`world_to_camera_view` returns y from the bottom**: convert with `y_px = (1 − y)·1024`.
- **Blender matrices are float32**: compute metadata in doubles from core math; use Blender values only for cross-checks.
- **`pb.matrix` needs `view_layer.update()`** before reading back evaluated transforms.
- **Square render + `sensor_fit`**: set `HORIZONTAL` explicitly so `f_px = f/36·1024` holds.
- **Textures must be packed** and downscaled, otherwise the grader's machine shows pink.
- **Do not add a render-time script handler or driver** that depends on frame or time.
- **`bpy.ops.wm.open_mainfile` resets the module state**: re-init the rig singleton after loading.
- **PNG color management:** `Standard` view transform, `Look: None`, no exposure/gamma tweaks.
- **Left/right:** anatomical `L` = +X = image right. Do not "fix" this.
- **Threading:** do not render in parallel processes with the same output path.
- **Wrapper stays self-contained:** no imports from the repo's other folders at runtime.
