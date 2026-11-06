# Decisions and validation status

- Fixture-first implementation selected by the user. Fixture scenes/metadata are explicitly labeled and rejected by submission packaging.
- Preserve measured production IPD (58–68 mm); fixture defaults to 63 mm. Horizontal sensor fit fixes square-camera calibration.
- A separate dedicated armature articulates procedural replacement eyes while preserving imported facial mesh and original rig. Explicit mesh mapping avoids guessing bone/mesh names.
- Non-refractive eye surfaces favor analytic/render alignment. Iris annulus and pupil disc share the calibrated depth; open scleral front avoids burying pupils in opaque geometry.
- Core rejects nonfinite gaze/configuration values; projected pupil annotations use an exact conic.
- Wrapper embeds synchronized core and cross-checks evaluated pupil transforms and Blender projection. Records include calibration, render samples, pose/lighting hashes and runtime version.
- Failed sweep regeneration invalidates stale metadata and commits replacement JSON atomically after complete success.
- V1–V17 source is implemented, including clean-room/secondary subprocesses. Missing evidence never counts as PASS. Packaging checks report status and bound artifact hashes.
- Framing optimization measures full eye-sphere bounds; brows/lashes/socket fit require visual inspection. No automated metric is represented as a full visual-quality guarantee.
- 51 pytest tests pass (Python 3.10.7, NumPy 1.26.4); pytest importlib collection avoids restricted-parent traversal.
- Blender unavailable in checked locations; official download failed with WinError 10013 socket access denial. Docker client exists but Docker daemon is unavailable. Blender and Docker execution remain unverified, and no final scene/renders/ZIP are claimed ready.
- Human inputs still required: textured character, explicit mapping, asset attribution, registered team name, final visual review, narrated video/presentation export and organizer submission.
- Dataset mode, live aiming and refraction experiments stay deferred until a verified candidate exists.


Final local validation: 51 tests passed; 23 Python files parsed successfully.
The actual `tasks.py all` command passed tests/sync and stopped at scene creation
with exit code 2 because Blender is unavailable. An explicit verify run generated
an INCOMPLETE/FAILED report under out/fixture with no synthetic PASS claims.
Docker execution was attempted and failed because no daemon pipe is available.

Runtime handoff: resolved the Start Menu shortcut to the launcher and verified the
actual C:\Program Files\Blender Foundation\Blender 4.5\blender.exe (4.5.15 LTS).
Fixture builds successfully. Initial render revealed overexposed metric-scale
lighting; reduced area-light powers and disabled procedural material specular.
Corrected Up-pose image renders successfully; image-only pupil residuals are
0.0973 px (L) and 0.0877 px (R). Full sweep validation is in progress.
Background jobs now use factory startup to avoid loading user add-ons and writing
to their restricted log/cache directories. The task runner detects the standard
Windows Blender 4.5 installation and exports it to child tasks automatically.

First complete fixture sweep now succeeds on Blender 4.5.15 LTS. Ten PNGs and
metadata pass protocol/JSON Schema/image validation; contact sheet, candidate docs
and labeled GIF generated. Blind pupil detection versus analytic metadata across
all twenty eye/frame pairs has maximum residual 0.116304 px. This is initial render
validation, not completion of V1–V17, production integration, or cross-version tests.
MPFB 2.0.18 is installed in the user's Blender extensions. Character handoff remains
pending. Factory-startup background jobs avoid modifying user add-on state.

Production character milestone (6 November 2026): created MPFB adult neutral male
with default 163-bone rig, young_asian_male skin, eyebrow001 and eyelashes01.
Selected asset MHCLO/MHMAT headers explicitly declare CC0. Split stock eye pair
into StockEye.L/R and uniformly scaled the hierarchy to measured 62.999994 mm
spacing. Saved packed assets/base_character.blend, mapping and attribution;
production integration succeeds. Initial 100 random evaluated poses: maximum
axis vector error 2.216e-7; fixation ray error 1.117e-7 m. All four packed textures
load correctly. Draft production sweep started; full V1–V17 remains pending.
Packed-image audit now requests pixels before has_data, because freshly opened
packed images are loaded lazily and otherwise give a false missing-texture failure.

Initial production sweep exposed lash interference at upward gaze. Increased
symmetric eye-opening targets from 0.35 to 0.65 and refitted brows/lashes.
Regenerated all ten draft production frames: metadata/schema/image validation
passes; blind detector maximum residual is 0.170610 px across all twenty pupils.
Contact sheet, GIF and candidate documents regenerated. Corrected production
scene is loaded in live Blender at reset. Full V1–V17 remains pending; these
initial checks do not qualify the scene for submission packaging. Python tests:
51 passed; character finalizer and verifier compile successfully.
