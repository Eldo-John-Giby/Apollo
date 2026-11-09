# Photorealism v2 execution

Current handoff: [completed CPU appearance candidate](../milestones/photorealism-v2-candidate/README.md).
The chronology below records intermediate experiments; the measured status at
the end supersedes their pending-work statements. This is not a release.

Branch photorealism-v2; preserved baseline is apollo-v0.3.0-rc.1.
No release pipeline, videos or presentations are authorized for this phase.

Implemented: clean review recipe, named collections, hidden render-only helper
meshes in viewport, camera workspace, exact V1/V2 preflight, source/scene/recipe
hash receipts, preserved calibrated eye meshes. The viewport rectangles were
render-hidden stock eye/lash geometry left visible in the old workspace.

MCP connection was restored by opening an isolated review scene and starting the
installed addon server. Current visible scene is an adult female anatomy
EXPERIMENT, not an accepted finished candidate. Inspection found original macro
age 0.3 (child/adult blend) and gender 1; prototype uses age 0.5, gender 0, then
aligns paired orbital surface anchors to the protected original eye positions.
No eye vertices, eye centers or camera calibration are intentionally changed.

Baseline actual nine-pose RGB/mask capture is running under out/photorealism-v2.
Compatible young_asian_female skin is installed; its MHMAT explicitly declares
CC0 September 2020, Data Collection AB / Joel Palmius / Jonas Hauquier. No new
skin has been incorporated yet. Read assets/ATTRIBUTION.md for source ecosystem.

Remaining: validate/bake female anatomy and mouth closure, refit lid/brow/lash
attachments, adopt and document female skin/maps, refine eyes, construct the
pulled-back bun groom, lighting, CPU benchmarking and targeted final checks.
Do not describe this scaffold/prototype as completed photorealism.

## Anatomy, material and grooming implementation

The adult female morph is baked into evaluated geometry. The original orbital
contact zone is preserved and smoothly blended into the new face because the
first direct morph broke lid/sphere fitting. The existing contour fitter is
reused only for geometry, and new fitted cosmetics replace stale attachments.
A negative mouth-opening target closes the relaxed mouth before baking.

The new material uses the installed CC0 young_asian_female albedo at its honest
native 2K resolution, with separate procedural roughness/micro-normal and regional
lip response. The 4K target was not met by the available licensed pack; no fake
upscaled detail is claimed. Stock CC0 brown_eye atlas adds irregular iris detail
while keeping the physical pupil separate. Source asset files, original license
text and checksums are in assets/photorealism-v2.

The groom has a continuous temple/hairline transition, offset part, 8000 scalp
strands, 1100 fine hairline strands, compact bun with 360 fiber paths, and 1400
individual brows rooted using the original CC0 brow alpha map. Curves are baked
to mesh so the existing real-occlusion mask worker sees all grooming geometry.
The first hard-edged glossy cap was rejected after MCP inspection; subsequent
versions smooth and feather the transition and reduce gloss.

A dedicated JSON config separates groom seed from fixed renderer seed 0.
The builder preserves eye mesh vertex hashes and calibration, asserts a one-
million evaluated polygon ceiling, packs assets and runs unchanged V1/V2.
Candidate review/performance/direction/visibility gates are still pending.

Rebuild from the preserved prerelease scene in Blender 4.5 with MPFB enabled:

```powershell
& $env:BLENDER_BIN -b milestones/realism-preflight-2026-11-08/scene-preview.blend --python-exit-code 1 -P build/photorealism_scene.py -- --folder out/my-v2 --stage finished
```

Use a new folder. Baseline/anatomy/surface/finished stages are supported. Rendering
saved packed candidates requires no MPFB. Never invoke the release finalizer for
this development phase.

## Early image rejection and correction

The first stock-atlas iris passed center geometry but failed the unchanged blind
image detector in upward/corner gaze because dark iris/lid regions connected.
The check runner stopped immediately after its three-pose benchmark, before the
larger pose set. The replacement raises iris reflectance with a constant material
color lift and modestly strengthens the existing frontal fill. No pupil geometry,
image-space position, annotation or detector threshold was changed.

Replacement candidate is out/photorealism-v2/candidate-2. Exact scene preflight,
1009-pose independent geometry/14 mutations and all three benchmark pupil checks
pass. Targeted nine-pose/mask, direction/reset, official sweep, diagnostic stills
and visual acceptance are in progress under out/photorealism-v2/checks-2.
The target runner never runs the release verifier/finalizer or 256-image corpus.


## Development-candidate handoff, 9 November 2026

The packed candidate, exact baseline build input, wrapper, ten native frames,
metadata, contact sheet and selected evidence are tracked under
`milestones/photorealism-v2-development`. Its README is the teammate entry point.
Source/config/asset receipts identify the build; the packed scene SHA-256 is
`34b1e13554c789baa522d32445972a91cafef2b7e9c366c8d5c13f73072db752`.

| Area | Actual result |
| --- | --- |
| P0 | Named collections, clean camera workspace, helper visibility fixed, nine matched baseline RGB/mask poses captured. |
| P1 | Baked adult-female macro/anatomy and closed relaxed mouth; orbital contact zone preserved; gray/front and actual portraits inspected. |
| P2 | Licensed native 2K skin, roughness/micro-normal/SSS, textured iris and tear/lid integration implemented. Broad mottling and synthetic shading remain visual gaps. |
| P3 | Baked side-part pulled-back hair/bun, 8000 scalp strands, hairline fibers, 1400 brows, fitted lashes. Front/three-quarter and MCP rear views inspected; smooth cap and sparse brows remain visible. |
| P4 | Fixed lighting and CPU budget pass on this laptop; 387,912 visible evaluated polygons, 32 fixed samples, no DOF/refraction/lid simulation. |
| P5 | Packed development handoff, exact source baseline, recipes/assets/licenses and scene-bound targeted reports. No release qualification or photographic-quality certification. |

Targeted results: V1/V2 pass; independent 1009 poses and all 14 geometry mutations
pass; four cardinal directions and byte-identical reset pass; nine-pose RGB and
actual masks pass, with minimum pupil visibility 1.0 and injected half-pupil
occlusion detected. Maximum blind error is 0.276 px for nine poses and 0.111 px
(rounded upward) for the ten-frame official sweep. Official metadata/image
validation passes. All 80 unit tests pass. No detector threshold was relaxed.

Center/up/corner CPU measurements at 32 samples are 55.28/62.77/63.52 seconds.
OS peak process RSS across measured core stages is 1,428,791,296 bytes (1.33 GiB),
not Blender's internal memory display. Both budgets meet the local targets;
these measurements do not promise identical performance on teammates' CPUs.

The check driver completed all graded checks and portraits, then correctly
stopped when the diagnostic helper tried to call the calibrated API after
moving the camera. The helper now renders inspection portraits directly and
resolves output paths absolutely. Corrected neutral/clay outputs are rerun
separately; the original failure log remains available. The source scene and
passed graded artifacts were not changed to bypass that error.

The actual front, three-quarter, gray and neutral-light stills plus the official
sheet and matched eye/pose crops were inspected. The anatomy/mouth and gaze
integration improve on the baseline; no obvious representative-pose socket
collisions or pupil obstruction were observed. Appearance remains synthetic.
Native 2K skin, broad mottling, smooth cap-like hair, sparse brows and non-
refractive eye shading limit the industry-grade ambition. This handoff closes
the implementation/checkpoint work; it does not claim all aspirational visual
acceptance criteria have been achieved or assign official scores.

To reproduce from the exact cleaned baseline (MPFB required for build only):

```powershell
& $env:BLENDER_BIN -b milestones/photorealism-v2-development/baseline/scene.blend --python-exit-code 1 -P build/photorealism_scene.py -- --folder out/rebuilt-v2 --stage finished
```

For matched comparisons on a fresh clone, create the nine baseline poses first:

```powershell
& $env:BLENDER_BIN -b --factory-startup milestones/photorealism-v2-development/baseline/scene.blend --python-exit-code 1 -P tools/realism_visibility.py -- --folder out/photorealism-v2/baseline-poses --masks out/photorealism-v2/baseline-masks --limit 9
```

Then run the bounded check command in TEAM_SETUP.md, review actual stills and
commit changed evidence with the changed scene. Any later release selection
needs its separately scheduled Windows/Linux and secondary-version qualification.
The qualified fallback and reviewed prerelease were preserved. No new release,
videos, presentations, submission or sharing changes are part of this handoff.

Persistent-data off was measured separately for center/up: 60.66/66.48 seconds
versus 55.28/62.77 with reuse. Both PNGs are byte-identical. These are single
serial trials; persistent data remains enabled. See evidence/persistence in the
tracked development handoff.


## Final appearance refinement

The next revision attenuates the licensed albedo's broad color variation in the
material (without editing or inventing texture detail), improves brow density
and growth direction, and breaks uniform lash spacing. Flat-shaded sclera faces
were the cause of visible ring bands: smooth normals now remove those bands
without changing any protected vertex. Hair now has five strand tones, a
flow-coordinate micro-normal, 10,000 visible strands and 250 raised overlapping
locks that survive native-resolution denoising. Geometry remains below 500,000
visible polygons. Matching graded/front/three-quarter 512 px Cycles previews
were inspected before native-resolution checks began.

The bounded check runner can reuse its own matching nine-pose RGB cardinal
images for the direction gate, checking scene/wrapper/worker/runtime/calibration
and each image hash. Reset is always freshly rendered after an actual corner
move and eyes.reset(). This avoids five duplicate CPU renders without reusing
any evidence from the previous appearance or relaxing image thresholds.
Native-resolution checks are currently running for the frozen refinement.


## Final CPU appearance handoff

The refined candidate is now `milestones/photorealism-v2-candidate/scene.blend`,
SHA-256 `8acd0df98cd2581f54bf83901d56c669795c5eef14e853a378bcb18e6bf71c4d`.
The earlier development checkpoint and exact baseline remain intact. The final
recipe has 10,000 scalp strands, 250 overlapping hair locks, five strand tones,
2100 brows, irregular tapered lashes, softened UV-aligned skin color and smooth
sclera normals. It contains 464,088 visible evaluated polygons. No protected eye
vertex changed. Skin remains native 2K; this is an explicit asset limitation.

All 15 bounded check stages completed successfully on this exact scene, including
both diagnostic images. All 80 unit tests passed. The independent 1009-pose audit
and 14 injected faults pass. The nine representative pose RGB/mask reports pass:
maximum blind error 0.278 px (rounded upward), minimum visible pupil fraction 1.0.
A real corner-to-reset render is byte-identical to center. The official ten-frame
sweep passes metadata and blind/template checks; maximum blind error 0.108 px
(rounded upward). Native center/up/corner timings are 54.59/58.03/72.55 seconds;
peak measured process RSS is 1,507,520,512 bytes (1.40 GiB). Persistent-data-off
center/up measurements are 56.52/61.97 seconds, with byte-identical PNGs. Reuse
remains enabled; these single trials do not establish statistical speed gains.

The final native center, upward/corner images, all-pose/eye crop comparison,
official sheet, front/three-quarter portraits and neutral/clay images were
inspected. Hair now has readable locks rather than a smooth cap, broad color
mottling is reduced and brows are fuller. Non-refractive eye shading and efficient
hair geometry retain CG simplifications; no photographic equivalence or official
score is claimed. Manual review is recorded against the actual image hashes.
The scoped construction, iteration, targeted testing and development handoff are
complete; full release qualification remains intentionally deferred.

The check runner now supports `--baseline` and automatically uses the tracked
baseline poses when local generated poses are absent. This permits fresh-clone
checks without first rerendering the old baseline. Its direction reuse validates
scene/wrapper/worker/runtime/calibration and image hashes, and always freshly
renders eyes.reset(); a stale-scene negative check confirms rejection.

Current packed-scene playback from the repository root:

```powershell
& $env:BLENDER_BIN -b --factory-startup milestones/photorealism-v2-candidate/scene.blend --python-exit-code 1 -P wrapper/eyes.py -- --out out/my-v2-sweep
```

No MPFB or MCP is needed for playback. All release/media/submission boundaries
in the original plan and AGENTS.md remain in force.

A fresh full recipe rebuild from the tracked baseline reproduced the protected
eye hashes, evaluated geometry and native center PNG exactly. The saved blend
container hash differs, so the evidence records both containers and binds the
actual identical PNG; it does not claim byte-identical blend serialization.
The tracked-baseline comparison was also rerun and all three sheets match the
local-baseline sheets byte for byte.


## Expanded CPU stress evidence, 10 November 2026

The full 113-pose RGB/actual-mask suite and fresh seeded 256-image corpus pass
on the final candidate. Minimum pupil visibility is 99.826%, maximum mask
centroid residual is 0.044821 px and independent corpus pixel error is 0.153842 px
(upper-rounded). Blind/template maxima are 0.277359/0.137939 px. All 82 current
unit tests pass after a bounded checkpoint-file retry fix. See
[the full stress report](../milestones/appearance-stress-2026-11-10/README.md)
for scene/source bindings, interruption recovery, reviewed worst cases and local
raw archive identity. Native expanded stress evidence is complete.
