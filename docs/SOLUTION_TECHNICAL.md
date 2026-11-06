# GAZEFORGE — Track 01 Winning Solution (Technical Specification)

**Samsung PRISM-XR Hackathon 2026 · Theme 1 / Track 01 · Synthetic Eye Movement & Virtual Camera Rendering**
**Doc status:** v1.0, written 6 Nov 2026. Companion file: `02_IMPLEMENTATION_PLAN.md` (hand that one to the coding agents; hand them this one as context).

---

## 0. The thesis in one paragraph

The rubric is deterministic and cheap to satisfy *partially*. Almost every team will get a face, two eyes that move, ten PNGs and a JSON. The teams that lose points will lose them on **ambiguity** (axis signs, left/right naming, JSON shape), **fragility** (wrapper breaks when the grader calls it differently, Blender version drift, unpacked textures), and **invisibility** (pupil shift too small to see, pupil hard to detect). GazeForge wins by being **correct by construction, self-verifying, and unmistakable**:

1. **Score-by-construction.** Every rubric line maps to a specific design decision and a specific automated test that proves it (Section 1).
2. **Physically honest.** True 3D spherical eyeball rotation about the true center, binocular fixation on a real 3D point at 35 cm, Listing's-law-compliant (torsion-free) rotations, metric scale audited. Not texture sliding.
3. **Self-auditing.** A one-command verifier re-renders a debug pass, measures pupil centroids *from pixels*, and proves they match the analytic ground truth to a fraction of a pixel. Judges get a PASS/FAIL report, not our word.
4. **Grader-proof.** The wrapper works from `blender -b`, from `pip install bpy` Python, and from a cold start, with no UI context, from any working directory, in any call order.

Nothing in this document guarantees first place. It removes every *avoidable* way to lose, and adds the evidence layer that wins ties.

---

## 1. Rubric reverse-engineering → design mapping (100 pts)

| Rubric line | Pts | How a grader could test it | Our design response | Proof artifact |
|---|---:|---|---|---|
| **Calibration** | 20 | Open `scene.blend`, read camera/target/eye positions; check resolution; check metadata `camera_matrix`; check lighting is constant | Eye midpoint at world origin. Camera at exactly `(0, −0.400, 0)` m facing `+Y`. Fixation empty at `(0, −0.350, 0)` m. Metric units, scale 1.0. Named empties. 1024×1024. Zero lens shift, zero distortion. All lights static (no keyframes/drivers). Calibration block stored as scene custom property and asserted on every load | `calibration_audit` in verifier, printed table in README |
| **Automation** | 20 | Run our wrapper or our pipeline unattended; check reproducibility; read README | Single entry point `eyes.py` is importable AND runnable (`blender -b scene.blend -P wrapper/eyes.py`). Default run = full 10-frame sweep + metadata. Fixed seed, Cycles CPU, headless, no GUI operators. Dockerfile + pinned versions. Exit codes. Bit-identical re-runs on the same machine | `make all`, `make verify`, determinism hash test |
| **Direction pass/fail** | 40 | Compare pupil position vs center for Left/Right/Up/Down/Reset, by eye or by script. **All five must pass** | Pupil shift ≈ 10 px (≈ 37 % of pupil diameter) at the 5 cm bound, chosen via lens/framing optimization. Black pupil against a *light* iris for detector-friendly contrast. Eyes wide open, pupils never occluded. No cross-talk (Up has dx≈0). `reset()` is pixel-identical to the initial state | Grader-simulator suite (3 independent detectors), annotated contact sheet |
| **Sequence & metadata** | 20 | Parse `metadata.json`; check 10 records, θ_k, h=sin, v=cos, key names, plausible values, JSON validity | Exact slide schema keys at top level, in slide order; full-double precision; no NaN; JSON Schema validator; extra fields isolated under `extra` so they cannot break a strict reader | `metadata.schema.json` + validator, cross-check of metadata vs pixels |

**Where points are most likely lost by competitors (and where we aim to be unassailable):**

1. Direction check judged by eye with a 3–5 px shift → "can't tell". *Fix: framing optimization + annotated sheet.*
2. Wrapper only works inside the Blender GUI or with a hard-coded path. *Fix: path-independent, context-free API.*
3. Fake eyes (texture shift or rotation about the wrong pivot) fail "spherical rotation about physical centers". *Fix: AnatomEye with explicit pivot assertions.*
4. 2D pupil centers computed in the wrong image convention (Y flipped, half-pixel off). *Fix: two independent projection implementations + pixel-measured check.*

---

## 2. What we keep and discard from the research

**Keep (high value):**
- MPFB2 (MakeHuman plugin for Blender) as the face source: assets are CC0. Verified: MPFB2 2.0.17 (Jul 2026) supports Blender 4.2 LTS and newer, and the MakeHuman project states core assets and exported models are CC0.
- The pinhole/analytic-projection principle: compute 2D ground truth analytically, then cross-check against the rendered image. (This is the single best idea in the research.)
- Quaternion-based rotation, no `bpy.ops` for pose changes, no GUI-context dependence.
- Binocular convergence at 35 cm (each eye aims at the shared 3D target from its own center). The "strabismus" warning is correct.
- Listing's law as a correctness argument.
- FLAME licence warning (research-only terms). We avoid it.
- **Dataset-style annotations** (from the UnityEyes / U2Eyes / OpenEDS discussion in the recon and literature files): gaze as pitch/yaw, a gaze vector in the camera frame, pupil/iris described as an ellipse, and the rule that the pupil center must be reported even if the lid hides it. Added to the `extra` block (Section 9) at near-zero cost, because a Samsung gaze-estimation team will look for exactly these fields.
- **Rotation-limit sanity** (from the Blender eye-tracker project in the recon file: pupils must never roll into the skull). We assert every commanded eye rotation stays under 35°; the graded sweep peaks around 13°.

**Discard or downgrade:**
- PyTorch3D / OpenDR: the challenge is explicitly Blender; adding a second renderer is risk with no rubric gain.
- CATS plugin: VRChat tooling, GPL, GUI-bound. Irrelevant to our math.
- "Pupil is at the bone tail": fragile. We define the pupil center explicitly as geometry (an empty parented to the eye bone at a calibrated depth).
- "Evaluators likely use pixel-differencing/IoU": unsupported speculation. We design to survive *any* grader (human, metadata-only, or image-based).
- **Citation correction (second read-through).** The literature file credits a "Straumann et al. 2014" paper for Listing's law and the half-angle rule. The paper at that DOI is real (*Kinematics of Visually-Guided Eye Movements*, PLOS ONE 9(4):e95234, 2014), but the authors are **Hess & Thomassen**, not Straumann & Zee, and it is about smooth-pursuit tracking kinematics. It does discuss the half-angle rule, but the file's specific claims (such as the "accumulated torsion per motion segment" figure) are not something I could trace to it. Rule: **cite only what you have opened.** For Listing's law, the Wong (2004) review is a better source (it appears in the file's own works-cited list and is real: Wong, *Surv. Ophthalmol.* 2004), alongside the classic Tweed & Vilis and Haslwanter papers. Papers I am comfortable naming because they exist and are on-topic: FLAME (Li et al., SIGGRAPH Asia 2017), Bermano et al. (eyelids, TOG 2015), Bérard et al. (high-quality eye capture, Disney 2014), OpenEDS (Garbin et al., 2019), Świrski, Bulling & Dodgson (pupil tracking, ETRA 2012), Zhang (calibration, TPAMI 2000), and the RIT-Eyes / NVGaze / UnityEyes line of synthetic-eye work.

---

## 3. Frozen conventions (the "contract")

Every number in the metadata depends on these. They are frozen, documented in the README, and echoed in the metadata `extra` block. **No agent may change them without updating this section and the verifier.**

| Item | Convention |
|---|---|
| Units | Meters. `scene.unit_settings.system='METRIC'`, `scale_length=1.0` |
| World axes | Blender right-handed. Subject faces **−Y**. Up is **+Z**. Image right is **+X**. |
| Origin | **Eye midpoint = (0,0,0)** (midpoint of the two eyeball centers) |
| Forward | `−Y`. "35 cm forward" ⇒ y = −0.350 |
| Camera | Position `(0, −0.400, 0)`, looks along `+Y`, up = `+Z`. Euler XYZ = (90°, 0°, 0°). Optical axis passes through the origin |
| Fixation target | `P(h,v) = (0.05·h, −0.350, 0.05·v)` m, with h,v ∈ [−1, 1] |
| Input signs (screen-space) | `h = +1` → pupils move toward **image right**. `v = +1` → pupils move toward **image up** |
| Sweep | `θ_k = 2πk/10`, `h = sin θ_k`, `v = cos θ_k`, k = 0…9. k=0 is straight up. Because h>0 is image-right, the sequence is **clockwise as seen in the renders** (top → right → bottom → left) |
| Eye naming | `L`/`R` are **anatomical** (`eye.L` = subject's left = **+X** = appears on the **image right**). Image-side aliases are provided in `extra` so either reading of "left" is available |
| Pixel coordinates | Continuous image coordinates, origin at the **top-left corner of the top-left pixel**, x right, y down. Image centre = (512.0, 512.0). Pixel (i,j) covers [i,i+1)×[j,j+1) |
| Rotation angles | Radians, Euler `XYZ` (Blender order; `R = Rz·Ry·Rx`), expressed in the **world frame**, as the rotation of each eyeball relative to its *primary position* (optical axis = −Y, parallel, torsion-free). Quaternion (w,x,y,z) also provided |
| `frame` index | 0-based, equal to k |
| Float precision | Full double precision, no rounding (JSON `repr`) |

**Why screen-space signs?** The brief says the 10 renders are "clockwise" and starts at "top". With `h = sin θ`, the second frame has h>0; for the picture to rotate clockwise the pupils must go to image right. This is the only self-consistent reading. Sections 14 and 15 list the hedges.

---

## 4. Scene calibration spec

| Parameter | Value | Rationale |
|---|---|---|
| Interpupillary distance (eyeball center to center) | 63.0 mm | Adult mean |
| Eyeball (sclera sphere) radius | 12.0 mm | Axial length ≈ 24 mm |
| Pupil-plane depth from rotation center | 10.0 mm | Corneal apex ≈ 13 mm from rotation center; pupil ≈ 3 mm behind apex |
| Pupil diameter | 4.0 mm | Typical indoor-light value |
| Iris diameter | 11.7 mm | Anatomical mean |
| Camera focal length | **100 mm** (35 mm-equivalent, sensor width 36 mm) | See Section 5 |
| Sensor fit / shift / distortion | AUTO, shift 0/0, no distortion | Idealized pinhole |
| Clip start / end | 0.05 m / 5 m | Avoid clipping at 40 cm |
| Resolution | 1024 × 1024, 100 %, PNG 8-bit RGB, compression fixed | Brief |
| Lighting | 1 large area light (key), 1 weak area fill, neutral gray world. All static | "Constant lighting" |
| Renderer | Cycles, CPU, fixed seed, adaptive sampling off, OIDN denoise | Determinism, no GPU requirement |

**Metric audit:** after generating the MPFB character, scale the character object uniformly so the measured eyeball-center distance is 63.0 mm, then verify head width, eye size and eyelid aperture are plausible. Record measured values in the README ("we measured, we did not assume").

---

## 5. Camera and framing: the decision that quietly decides 40 points

At the ±5 cm bound, a 35 cm fixation target is only **±8.13°** off axis. The pupil physically moves ≈ 1.4 mm. Pixel shift depends only on framing:

| Focal length | Frame width at 40 cm | mm/px | Pupil shift at 5 cm bound (px) | Verdict |
|---|---:|---:|---:|---|
| 50 mm (Blender-style default) | 28.8 cm | 0.281 | 5.2 | "Can you see it?" Too risky |
| 85 mm | 16.9 cm | 0.165 | 8.8 | Acceptable |
| **100 mm** | **14.4 cm** | **0.141** | **10.4** | **Chosen: face region still reads as a face, shift clearly visible** |
| 120 mm | 12.0 cm | 0.117 | 12.5 | Fallback if needed, eyes only |

(All values from the tested reference math in the implementation plan.) At 100 mm the pupil (4 mm) spans ≈ 28 px and the iris ≈ 83 px, so the shift is about 37 % of the pupil diameter, which is unmistakable in a side-by-side and trivially detectable by any algorithm.

The frame covers both eyes, brows and nose bridge (14.4 cm wide). **Framing optimization task for the build:** sweep f ∈ [85, 135] mm and pick the largest f such that both full eyes, lashes and brows keep ≥ 8 % margin from the frame edge. Default expectation: 100 mm. The choice and the sweep table go in the README.

**Intrinsics (derived, then asserted):**
`f_px = f_mm / sensor_mm × 1024 = 100/36 × 1024 = 2844.4444`; `cx = cy = 512`; `K = [[2844.444,0,512],[0,2844.444,512],[0,0,1]]`.

---

## 6. Eye model and articulation (the heart of "spherical rotation about physical centers")

### 6.1 AnatomEye: parametric eyeball replacing the stock eyes

Stock MakeHuman eyes bake the pupil into a texture, which makes a *geometric* pupil center ambiguous. We replace them with a small procedural eye generated by script (bmesh), parented to the MPFB eye bones:

| Part | Geometry | Material |
|---|---|---|
| Sclera | Sphere, r = 12.0 mm, centered **exactly at the bone head** (the rotation center) | Off-white image/procedural texture with subtle veins, SSS low |
| Cornea | Spherical cap (r_c ≈ 7.8 mm), apex ≈ 13.2 mm from center, transparent shell | **Non-refractive** transparent + glossy reflection layer (see 6.5) |
| Iris | Disc/cone at pupil-plane depth, diameter 11.7 mm, textured (radial fibers + image texture) | **Light iris** (blue/green/light hazel) for pupil contrast |
| Pupil | Separate disc object, d = 4.0 mm, at pupil-plane depth, exactly centered on the optical axis | Pure black. Has a **debug material swap** (magenta emission) used only by the verifier |
| Pupil center empty | `PupilCenter.L/R`, child of the eye bone, at +10.0 mm along the calibrated optical axis | None (this is the ground-truth 3D point) |

The stock eye proxies are hidden/deleted; eyelids, lashes, brows and skin stay from MPFB, so the model is still the textured MPFB face. A **fallback tier** (Section 15, R3) keeps stock eyes with an explicit pupil marker if AnatomEye fails its gates.

### 6.2 Optical axis and pupil center (definition, not assumption)

The optical axis of each eye in rest pose is `a₀ = (0, −1, 0)` in world coordinates (calibrated at build time from geometry, never hard-coded from bone orientation: the build script measures `pupil_center − eye_center` and rotates the mesh so this equals −Y, then asserts it). The 3D ground-truth pupil center is

`p_e = C_e + d_p · g_e`, `d_p = 10.0 mm`, `g_e` = unit optical axis in world.

### 6.3 Gaze rotation: binocular fixation with Listing's-law-compliant rotations

For gaze input (h, v):

1. Fixation point `P = (0.05h, −0.35, 0.05v)`.
2. For each eye with center `C_e` (L at +x, R at −x): `g_e = (P − C_e)/‖P − C_e‖`.
3. Eye orientation = **shortest-arc rotation** `q_e` taking the primary axis `a₀` to `g_e`:
   `q = (1 + a₀·g, a₀ × g)` normalized (with the antiparallel case guarded).
4. Apply `q_e` as the eyeball's world orientation (via `pose_bone.matrix` composed from the bone's rest matrix; **no `bpy.ops`**).

**Why this is correct.** A shortest-arc rotation from the primary direction uses a rotation axis perpendicular to both `a₀` and `g`, i.e. an axis that lies in Listing's plane. That *is* Listing's law (zero torsion relative to the primary position), so the iris never accumulates false roll across the clockwise sweep, which naive "yaw then pitch" Euler composition would (Fick-style torsion ≈ ½·h·v, here ≈ 0.5° at the corners). Torsion about the optical axis does not move the pupil *center*, so this is a realism and rigor property rather than a score property, but it is cheap, testable and lets us claim anatomical validity honestly.

**Binocular note (honest limitation):** near-fixation physiology tilts Listing's plane slightly with vergence (the "L2" extension). At 35 cm the vergence is 10.3° and the resulting cyclo-offset is far below the visible threshold; we apply the plain law, quantify it, and list it under limitations.

**Resulting ranges** (from the tested reference math): at the extremes each eye rotates about ±8.1° vertically and between −13.1° and +3.0° (left eye, h from −1 to +1) horizontally, with a baseline convergence of ±5.14° per eye at center.

### 6.4 `reset()` semantics

`reset()` ≡ `move(0, 0)`: both eyes converge on the center target `(0, −0.35, 0)`. The saved `.blend` is stored in exactly this pose, so "initial state" = "reset state" = a pixel-identical frame. (`move` is **absolute**, never cumulative, so call order cannot change results.) Parallel-eyes mode exists as an ablation flag only.

### 6.5 Why a non-refractive cornea

A physically refractive cornea displaces the *apparent* pupil by a fraction of a pixel to a few pixels off-axis. Ground truth would then differ from the picture. We deliberately render the cornea as a transparent shell with specular reflection but no refraction, so that **geometric pupil center == rendered pupil center** and the verifier can prove agreement at sub-pixel level. A `--refractive-cornea` experiment flag measures and reports the residual (a nice "we understand the physics and chose precision" talking point).

### 6.6 Eyelids

At ±8° eccentricity, lid–cornea interference is negligible, so v1 does not drive lids. (Optional polish, P2: map `v` to a small upper-lid shape-key/bone coupling, following the idea in the eyelid-reconstruction literature that lids track vertical gaze.) The build gate requires **zero pupil occlusion** in all 10 frames and at the extremes.

---

## 7. Face rig (MPFB2)

- Blender **4.5 LTS** as the reference build environment (Python 3.11, matching the PyPI `bpy` wheels, widest evaluator compatibility). Secondary test on **5.2 LTS**. Recent MPFB2 2.0.x releases fixed Blender-5 shader-node incompatibilities; use the latest (2.0.17 at time of writing).
- Character: default MPFB human, **Standard rig → "Default"** skeleton, skin from the CC0 Skins 01/02 packs, CC0 eyebrows and lashes, no hair, no clothing. Textures downscaled to ≤ 2K and **packed into the .blend**.
- **Do not** use the "System eye materials 03" pack: it is CC-BY (attribution burden); we use our own iris texture.
- Eyes opened wider via a MakeHuman eye-opening modifier so the pupil is never occluded.
- Eye bones `eye.L` / `eye.R` (names to be confirmed by the build script, not assumed). Bone heads are snapped to the eyeball centers.

---

## 8. Wrapper API contract (`wrapper/eyes.py`, single file, stdlib + bpy/mathutils/numpy)

```python
import eyes
eyes.move(h, v)          # absolute gaze, h,v in [-1,1]; clamps with a recorded flag; returns state dict
eyes.reset()             # == move(0,0)
eyes.render(path=None)   # renders 1024x1024 PNG, returns {"path":..., "record":{...metadata...}}
eyes.sweep(n=10, out_dir=None, write_metadata=True)   # the clockwise protocol
eyes.state()             # current (h,v), rotations, pupil centers, pose hash
eyes.calibration()       # the frozen calibration block
```

Guarantees:
- Works under `blender -b scene.blend -P harness.py`, under pip `bpy`, from any CWD (paths resolved from `__file__`).
- Auto-loads `scene.blend` (found relative to the bundle) if no scene is open.
- `python eyes.py` / `blender -b scene.blend -P eyes.py` with no args runs the **full default sweep** and writes `renders/` + `metadata.json` next to the bundle root. With args: `-- --h 0.3 --v -1 --out x.png`, `--verify`, `--calibration`.
- No `bpy.ops` except `render.render(write_still=True)`. No UI context dependence.
- Deterministic: same inputs ⇒ same pose hash ⇒ same pixels (same machine, same Blender build).
- `render()` with no path writes to `output/` (never into `renders/`, which is reserved for the 10 official frames).
- If launched with plain Python and no `bpy`, the CLI re-execs Blender via `BLENDER_BIN` or `PATH`.

---

## 9. Metadata schema

`metadata.json` is a **JSON array of 10 records** (literal reading of "one record per render"). Top-level keys match the slide exactly and in the slide's order; anything extra lives under `extra`.

```json
{
  "frame": 3,
  "theta": 1.8849555921538759,
  "input": { "h": 0.9510565162951536, "v": -0.30901699437494734 },
  "eye_rotation_L": [0.04407, -0.001009, 0.045789],
  "eye_rotation_R": [0.043034, -0.004796, 0.221931],
  "pupil_center_2D_L": [745.069915, 515.213043],
  "pupil_center_2D_R": [298.449611, 515.135645],
  "camera_matrix": [[2844.4444444444443, 0, 512], [0, 2844.4444444444443, 512], [0, 0, 1]],
  "extra": {
    "schema_version": "1.0",
    "image": "frame_03.png",
    "conventions": { "units": "m", "world": "Blender RH, subject faces -Y, up +Z", "pixel_origin": "top-left corner of top-left pixel, y down", "angles": "radians, Euler XYZ, world frame, relative to primary position", "LR": "anatomical (eye.L at +X, image right)" },
    "eye_rotation_L_deg": [2.52, -0.06, 2.62],
    "eye_rotation_R_deg": [2.47, -0.27, 12.72],
    "eye_quat_wxyz_L": [0.999495, 0.022039, 0.0, 0.022898],
    "eye_quat_wxyz_R": [0.993611, 0.021649, 0.0, 0.110763],
    "optical_axis_world_L": [0.0, 0.0, 0.0],
    "optical_axis_world_R": [0.0, 0.0, 0.0],
    "pupil_center_3D_world_L": [0.031958, -0.00998, -0.000441],
    "pupil_center_3D_world_R": [-0.029299, -0.009745, -0.00043],
    "fixation_point_world": [0.047553, -0.35, -0.015451],
    "gaze_vector_cam_L": [0.0, 0.0, 0.0],
    "gaze_pitch_yaw_L": [0.0, 0.0],
    "pupil_ellipse_2D_L": { "center": [745.07, 515.21], "semi_axes": [14.6, 14.5], "angle": 0.0 },
    "camera": { "position": [0, -0.4, 0], "euler_xyz_rad": [1.5707963267948966, 0, 0], "focal_mm": 100.0, "sensor_mm": 36.0, "extrinsics_world_to_camera_4x4": [] },
    "pupil_center_2D_image_left_eye": [298.449611, 515.135645],
    "pupil_center_2D_image_right_eye": [745.069915, 515.213043],
    "pupil_center_2D_norm_L": [0.727607, 0.503138],
    "lighting_sha256": "…",
    "pose_sha256": "…",
    "clamped": false
  }
}
```

(Values for the keys that were computed above are from the tested reference implementation; the `optical_axis_world_*`, `gaze_vector_cam_*`, `gaze_pitch_yaw_*`, ellipse and hash fields are filled by the real pipeline, and `core.py` already generates all of them for both eyes. Gaze angles follow the ETH-XGaze style: camera frame x right, y down, z forward; `pitch = asin(−y)` (positive = looking up), `yaw = atan2(−x, −z)` (0 = looking straight at the camera). The rotation values in this example are for the frame-3 inputs.)

Companion `metadata.schema.json` + `tools/validate_metadata.py` (also invoked by `make verify`) enforce: 10 records, k = 0…9, θ_k exact to 1e-12, h = sin θ, v = cos θ to 1e-12, finite numbers, pupil centers inside the image, pixel agreement with the render.

**Honest note:** whether the real harness wants an array, an object with a `frames` key, or per-frame files is not visible in the slides. The array is the literal reading. The `README` documents the format; the ambiguity ledger (Section 14) asks the organizers.

---

## 10. Rendering, lighting, determinism

- Cycles CPU, `seed=0`, `use_animated_seed=False`, adaptive sampling off, fixed sample count (target 96–128 spp), OIDN denoise, `film_transparent=False`, view transform **Standard**, fixed filter size.
- Lighting: one large soft area light at upper-left front for the key, a low-intensity fill, neutral gray world. Position the key so the corneal catchlight sits on the iris/upper-left region away from the pupil in **all 10 frames** (checked by the detector suite). All light parameters hashed into `lighting_sha256`.
- Persistent data and a single Blender process for the whole sweep (load once, render ten times).
- Performance target (to be measured and printed): ≤ 30 s/frame on a typical 8-core laptop at final quality, ≤ 5 s/frame at `--quality draft`.
- Determinism contract: same machine and Blender build ⇒ identical PNG SHA-256 for repeated runs; across machines, expect pixel-level agreement within a small tolerance (documented).

---

## 11. Verification suite (`tools/verify.py`, driven by `make verify`)

| # | Check | Pass criterion |
|---|---|---|
| V1 | Calibration audit | Camera pos, orientation, target pos, resolution, units, shift=0, lights static: exact |
| V2 | Metric audit | IPD 63.0±0.1 mm, eyeball r = 12.0±0.05 mm, pivot = bone head < 1e-6 m |
| V3 | Pivot/rotation audit | Measured optical axis (pupil center − eye center) vs commanded `g_e`: error < 1e-5 rad for 1000 random (h,v) |
| V4 | Fixation audit | Both gaze rays pass within < 1e-5 m of `P(h,v)` (binocular convergence) |
| V5 | Listing/torsion audit | Torsion relative to Listing's plane < 1e-6 rad over the sweep |
| V6 | Dual projection | Own pinhole math vs `bpy_extras.object_utils.world_to_camera_view`: agree < 1e-3 px |
| V7 | **Pixel-truth** | Debug render (pupil magenta-emissive) → weighted centroid from pixels vs `pupil_center_2D`: **< 0.5 px** target 0.2 px, all 10 frames, both eyes |
| V8 | Blind detector A | Threshold + ellipse-fit pupil detector on the *final* frames vs metadata: < 1.0 px |
| V9 | Blind detector B | Template matching vs the reset frame: shift direction correct for L/R/U/D, magnitude ≥ 8 px |
| V10 | Direction suite | Left, Right, Up, Down, Reset: signs correct; cross-talk < 0.5 px; Reset returns to center within 0.0 px (pixel-identical) |
| V11 | Order independence | 200 random move/reset sequences: pose hash depends only on last (h,v) |
| V12 | Determinism | Two full runs ⇒ identical SHA-256 for all PNGs and metadata |
| V13 | Schema | Validates against `metadata.schema.json`, θ/h/v exact |
| V14 | Occlusion/visibility | Pupil fully visible in all frames and extremes; catchlight does not overlap pupil |
| V15 | Bundle | ZIP layout, file names, size, `scene.blend` opens headless with **no missing textures** (all packed), no add-on dependency |
| V16 | Cross-version | Pipeline passes on Blender 4.5 LTS and 5.2 LTS (secondary) |
| V17 | Annotation sanity | Pupil-ellipse center within 0.02 px of the projected pupil center; ellipse semi-axes ≈ 14.6 px (2 mm radius at this framing); gaze pitch/yaw consistent with `gaze_vector_cam`; every eye rotation < 35° from primary |

`make verify` prints a one-page PASS/FAIL table and writes `extras/verification_report.md`. The README embeds the table from the final run.

---

## 12. Submission bundle

```
VIT_<TeamName>.zip
└── VIT_<TeamName>/
    ├── scene.blend              # textured MPFB face, AnatomEye eyes, rig, camera, target, lights; textures packed
    ├── wrapper/
    │   └── eyes.py              # move / reset / render / sweep, self-contained
    ├── renders/
    │   └── frame_00.png … frame_09.png    # exactly 10 PNGs
    ├── metadata.json            # array of 10 records
    ├── README.md
    ├── contact_sheet.png        # annotated, required track deliverable
    └── extras/                  # tools/verify.py, metadata.schema.json, Dockerfile, requirements, ATTRIBUTION.md, verification_report.md
```

Rules: `renders/` holds exactly the ten official PNGs (no extra files there). `extras/` is additive. Final size target < 60 MB (textures ≤ 2K). Confirm the exact team-name string against the registration slide: convention is `CollegeName_TeamName`.

**Demo video:** one **100–110 s** video, so it satisfies both the track's "1–2 minute" line and the general "max 3 minutes" line. **Contact sheet:** 5×2 grid, each tile annotated with frame index, θ, (h,v), a clock-hand indicator, pupil-center crosshairs from `metadata.json`, and a ghost ring at the reset-pupil position.

---

## 13. Differentiators for the finals (what makes a Samsung jury remember us)

1. **"Don't trust us, run it."** The verification report and pixel-truth check turn claims into evidence.
2. **Ground truth that is provably exact.** Analytic projection, cross-checked against rendered pixels to sub-pixel, plus an optional refraction experiment showing we understand the cost of physical realism.
3. **Real anatomy.** Pivot at eyeball center, optical-axis/pupil-center definition, Listing's law, binocular vergence. Samsung builds gaze estimators; they will recognize optical-axis vs gaze-direction thinking.
4. **Grader-proof engineering.** Works headless, works as a library, works from any directory, works in Docker.
5. **Live-jury extras (stretch, not in the zip):**
   - **W1 Dataset mode:** `extras/generate_dataset.py` renders N random (h,v) frames with the same ground-truth schema, to show the point of the whole exercise (the synthetic gaze data gap). "10 graded frames, or 10,000 for training."
   - **W2 Live-aim mode:** in the Blender GUI, drag the `FixationTarget` empty and the eyes follow via muted-by-default aim constraints. A parity test proves the constraint solution equals the analytic one. (Great for a live demo; the headless wrapper never depends on constraints.)
   - **W3 Refraction ablation figure:** with/without refractive cornea, residual in px.
6. **Candid limitations slide**, which the submission template asks for anyway. Honest limits build trust.

**Pitch arc for the 100-second video:** (0–10 s) the data-gap problem and why 2D pupil sliding fails; (10–35 s) the rig: pivot at the eyeball center, fixation geometry diagram; (35–65 s) the ten clockwise frames with overlays; (65–85 s) the verification report scrolling to all-green; (85–100 s) scale-up: one command, 10,000 frames.

---

## 14. Ambiguity ledger and hedges

| # | Ambiguity | Our default | Hedge |
|---|---|---|---|
| A1 | `h>0` = image right or subject's right? | **Image right** (the only reading making the sweep clockwise in the renders) | Documented; both readings in `extra.conventions`; question to organizers |
| A2 | `L`/`R` anatomical or image-side? | Anatomical (`eye.L` = +X = image right) | `extra` has image-side aliases |
| A3 | Rotation units/type | Radians, Euler XYZ world-relative-to-primary | Quaternion and degrees in `extra` |
| A4 | `reset` = parallel primary or converged center? | Converged at the center target (physically what "fixate 35 cm" means) | `--parallel` flag; documented |
| A5 | `camera_matrix` = K or projection? | 3×3 intrinsics K | 4×4 extrinsics and 3×4 P in `extra` |
| A6 | JSON array vs object | Array of 10 | Documented; asked |
| A7 | Grader re-runs the wrapper or only inspects outputs? | Support both | Context-free wrapper; deterministic files |
| A8 | Blender version | Author in 4.5 LTS, test on 5.2 LTS | README states versions; Docker pins |
| A9 | Starter kit / harness provided? | Unknown | **Check the Google Form and email today** |

**Email to send today (`prism@samsung.com`, reference the team after registration):**
1. Is `h>0` image-right (viewer's right) or the subject's right? 2. Are `_L`/`_R` the subject's anatomical eyes or image-left/image-right? 3. Euler or quaternion for `eye_rotation_*`, and units? 4. Is `metadata.json` an array of 10 records? 5. Is there a starter kit or evaluator harness, and which Blender version will be used? 6. Are the 1–2 min track demo and the ≤3 min general video the same artifact? 7. Any CPU/RAM/runtime limit on rendering?
Replies are unlikely to arrive in time, so our defaults must stand alone. Send it anyway: it shows diligence if there's ever a dispute.

---

## 15. Risk register

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Convention mismatch with the grader (A1–A6) | Medium | High | Frozen contract, metadata carries aliases, organizers emailed, README explicit |
| R2 | Pupil shift judged "not visible" | Medium | Very high | 100 mm framing, light iris, annotated sheet, detector suite |
| R3 | AnatomEye eye mesh doesn't sit well in MPFB sockets (gaps, lash clipping) | Medium | Medium | Hard gate on Day 5; fallback to stock eyes + explicit pupil empty (Tier A) |
| R4 | MPFB eye bones oriented unexpectedly or named differently | Medium | Low | Build script measures geometry, never assumes names/orientation, asserts |
| R5 | Render too slow / grader time limit | Medium | Medium | CPU-only, draft/final presets, single-process sweep, measured and reported |
| R6 | Evaluator machine lacks matching Blender | Medium | Medium | `.blend` saved in 4.5, tested on 5.2, no add-on dependency, Dockerfile |
| R7 | Textures unpacked, scene opens pink | Low if checked | Very high | `pack_all`, V15 opens scene with a clean `BLENDER_USER_*` dir |
| R8 | Licensing (CC-BY assets, GPL code interplay) | Low | High | CC0-only assets, `ATTRIBUTION.md`, wrapper uses `bpy` so a GPL-compatible licence is the safe choice; ask organizers if IP terms matter |
| R9 | Over-engineering eats the 12-day window | **High** | High | Always keep a shippable ZIP; tiers P0 → P3; wow-features only after the freeze gate |
| R10 | Submission mistakes (name format, form, video link, late) | Medium | Fatal | Final checklist in the plan; submit 24 h early |

---

## 16. Known limitations (state them ourselves)

- Single static identity and lighting, as the brief requires; no head-pose, blink or expression randomization in the graded run.
- Cornea is non-refractive by design (ground-truth exactness over optical realism); effect quantified.
- Kappa angle (optical vs visual axis offset) modeled as 0, parameter provided.
- Listing's plane is not tilted with vergence (L2 neglected, effect < visible threshold, quantified).
- Pupil size fixed at 4 mm (parameterized).
- Determinism guaranteed for the same Blender build and machine; cross-machine tolerance reported.

---

## 17. Reference values (from the tested reference math)

- Vergence at center: 10.29°, so ±5.14° per eye.
- Pupil center at reset (px): L (735.18, 512.00), R (288.82, 512.00).
- Pupil shift at the 5 cm bound at 100 mm: ≈ 10.3–10.4 px.
- Sweep pupil shifts (px, relative to reset, L eye): k0 (0, −10.3), k1 (6.1, −8.4), k2 (9.9, −3.2), k3 (9.9, 3.2), k4 (6.1, 8.4), k5 (0, 10.3), k6 (−6.0, 8.2), k7 (−9.6, 3.1), k8 (−9.6, −3.1), k9 (−6.0, −8.2).
  (Image y is down, so negative y = pupil moves *up* in the picture.)

- Converged-eye yaw at reset: 0.0898 rad (5.14°) nasal; gaze pitch at reset: 0. Pupil-ellipse semi-axes ≈ 14.6 px; ellipse center vs projected center differs by ≈ 0.003 px at reset (perspective), so the two definitions of "pupil center" are interchangeable.

These are the numbers the verifier must reproduce from the real Blender scene to within sub-pixel tolerance.
