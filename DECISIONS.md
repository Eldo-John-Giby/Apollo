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
