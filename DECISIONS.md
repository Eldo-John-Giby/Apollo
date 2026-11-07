# Decisions and validation status

Competition-upgrade execution started on a separate branch. Frozen release and
its payload hashes remain untouched. Independent Rodrigues/pinhole reference
measures actual evaluated pupil triangles and fitted scleral spheres; 1009 poses
and fourteen injected defects pass/detect respectively. Geometry-guided pixel
oracle is separate from OpenCV detectors and explicitly not a visibility-mask
replacement. Nine 32-sample dataset anchors render and pass (max error 0.141464 px);
interrupted-after-eight resume matches PNGs/manifest byte-identically. Optional
sidebar matches API at nine poses and clean registration cycles; no graded
scene activation. New verifier provenance guards diagnostic/source changes and
rejects legacy cache reuse. 74 tests pass; fresh full qualification and visual
human review remain gates. See UPGRADE_PROGRESS.md for remaining work.

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

Primary correctness baseline achieved: V1–V15 and V17 PASS on Blender 4.5.15
with the draft production scene; V16 remains NOT RUN. Mask centroid residual
0.039657 px; minimum visible/dark pupil fraction 1.0; blind residual 0.170610 px;
template displacement error 0.039628 px. Two sweeps and clean-room regeneration
are byte-identical. 59 Python tests pass, including stationary-lid detector and
PNG metadata determinism regressions.
Corrections: tight circular pupil template avoids stationary lid bias; standalone
PNG output strips volatile text chunks without recompressing pixels; diagnostic
materials retain alpha and polygon material indices; diagnostic dithering is zero
so background noise cannot bias centroids. Visibility checks full-coverage pupil
interiors for darkness and independently checks integrated linear-light coverage
to retain detection of clipping, with the 98% requirement unchanged.
Mask-only reruns and evidence reuse require unchanged scene/wrapper/metadata/render
hashes; clean-room PASS is retained only for those same inputs. Original failed
mask report is retained under out/production/verification_before_fixes.

7 November visual-polish experiment: build/polish_scene.py creates an isolated
procedural radial iris material and planar UVs without changing eye vertices,
pupils, calibration or lighting. First dark variant rejected (cardinal pupil
residual 1.168 px). Revised green-hazel variant passes five-direction checks,
with maximum cardinal pupil error 0.159424 px and template displacement error
0.042945 px; reset byte-identical. Saved under out/polish-iris-clear with
comparison.png and visual_review.json. Not promoted; full sweep and correctness
verification still required for this material candidate. Verified production
baseline remains unchanged.

7 November: qualified and promoted radial-iris draft to out/production, preserving
the flat-eye verified baseline in out/verified-flat-20261107. V1–V15 and V17 PASS;
V16 NOT RUN. Sweep pupil error 0.199946 px, mask error 0.039657 px, template
error 0.042945 px, visibility 1.0. Two sweeps and standalone clean-room
regeneration are byte-identical. A source rebuild using --look radial reproduces
the center PNG exactly; production defaults to radial, with flat available.
Retained 100 mm lens after analytical brow/lash screening (brow margin 8.7%;
115 mm leaves 2.5%, 130 mm crops). No geometry/calibration/lighting changes.
Draft CPU sweep: mean 23.653 s/frame, maximum 25.70 s on i5-1135G7 (4 cores,
8 logical processors). This is a local baseline for M4, not an official limit.
59 tests pass. Final-quality and secondary-version qualification still pending.

7 November M4: official Blender 5.2.3 LTS Windows portable archive downloaded
and SHA-256 verified, build e13b728c6880. Secondary qualification succeeds;
primary report now has all V1–V17 PASS. Secondary directions, visibility,
repeat hashes and clean-room regeneration also pass. Retained nested reports
and version-specific PNG/metadata/mask evidence. tasks.py detects the pinned
portable runtime without changing global Blender/user configuration.
Qualified scene stays at 32 samples. Isolated center/up/down: 8 samples average
5.094 s (max pupil error 0.149 px); 16 samples 12.896 s (0.173 px). Mean center
grayscale difference from 32 samples: 1.997/255 and 1.332/255 respectively.
Preview profiles are not promoted or claimed fully verified. Docker info failed
with absent Linux engine pipe; automatic approval review blocked a command with
Desktop launch (reason: blocked by policy); no alternate launch attempted.
59 tests pass. Source documentation encoding normalized to UTF-8 and clean LF.

7 November M5 development freeze: user started Docker Desktop. Image build and
Linux doctor/60 tests/packed-scene center render pass (max pupil residual
0.078047 px). No full Linux V1–V17 claim. Downloaded asset ZIPs, caches, runtimes
and frozen archives are excluded from Docker context.
Compared 32 versus 128 samples at center: grayscale difference 0.768678/255,
detected pupil center difference <=0.082210 px, slightly smoother at 128.
Selected the qualified 32-sample artifacts for the development freeze based on
visual readability, accuracy and CPU cost. CLI final remains 128; it was not
renamed or silently treated as qualified. 128 render took 113.58 s concurrent
with Docker build; no controlled speedup claim.
Development-only archive uses the same fixture/stale/all-17 qualification gates
as packaging, without inventing a registered team. ZIP integrity and per-file
manifest pass; exact extracted archive reproduced ten PNGs and metadata
byte-identical from another working directory. Added versioned archive, reports,
comparison and checksums under milestones/dev-freeze-2026-11-07.

7 November competition upgrade closeout: retain the original freeze unchanged.
Select corrected warm-fiber B with reduced iris region and refitted lids/lashes;
reject the dark prototype rather than relax image thresholds. The exact scene
3fdc93632a84011cc78c3210e703ad0f6653fcef68375d21a741af76b951605d passes
all V1–V17 on Windows and Linux, each with the full applicable 5.2 suite.
Independent geometry covers 1009 poses and 14 injected faults. The separate
seed-0 dataset contains 256 actual images, with 25 mask-tested poses and rendered
occlusion/lighting faults. Completed and interrupted resume plus clean-CWD
archive reconstruction reproduce exact bytes. 79 tests pass on both platforms.

The 105-second demo uses actual artifacts and disclosed local synthesized
narration. The editable ten-slide deck and representative video frames were
visually reviewed; human naturalness preference and independent human usability
are not invented. Research images remain separate from the graded ten-frame ZIP.
Conventional execution layout is delivery/apollo; evidence and corpus are under
milestones/competition-upgrade-2026-11-07. Preserve mixed qualified Python/JSON
source bytes with Git -text; automatic line-ending conversion otherwise breaks
raw provenance hashes on checkout. Actual registered identity, final naming,
evaluator sharing and event uploads remain team-owned. No official score claimed.

## 8 November 2026 — User scope and release naming

Videos and presentations must not be created, regenerated or queued. The pending
realism media worker was stopped before authoring. Preserve historical artifacts,
and finish technical qualification, still images, datasets and executable archives.
The technical exporter no longer requires or copies decks/movies; numerical,
image, source-hash and replay gates remain unchanged.

Use uniform Apollo semantic-version tags and display names from docs/RELEASES.md.
The two existing tags were renamed atomically on GitHub while preserving their
original target commits. Historical archive paths and checksums remain unchanged.
