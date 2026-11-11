# Adult avatar portrait refinement

## Plan and acceptance

1. Preserve the packed v2 source and its calibrated eye geometry, rig, camera,
   lighting, wrapper and renderer settings. Build a separate candidate without
   MPFB or downloads.
2. Refine lower cheek and jaw contours, feather lip pigment into the existing
   atlas, add directional lip microfolds and restrained satin highlights, replace
   sparse brows with fuller tapered fibers, and add lightweight temple locks.
3. Inspect front and three-quarter stills before expensive checks. Compare against
   v2 using the same camera and lighting. Reject cosmetic changes that obstruct
   pupils or exceed 500,000 visible evaluated polygons.
4. Run existing V1/V2 preflight, independent geometry/fault audit, CPU/RSS checks,
   nine-anchor RGB and actual visibility masks, direction/reset, official sweep,
   metadata and image detectors. Keep existing thresholds (120 s/frame, 4 GiB).
5. Preserve the candidate, reproducible recipe, bound evidence and comparisons as
   a development checkpoint. Full cross-platform release qualification and the
   exhaustive dataset are separate; old scene-bound evidence is not transferable.

The original source is `milestones/photorealism-v2-candidate/scene.blend` and is
never overwritten. `build/portrait_refinement.py` checks its exact SHA-256 before
editing. The existing unfinished `build/character_polish.py` is preserved.

Eevee is not substituted for the CPU Cycles pipeline: the established scene and
verifier require that renderer. This work concerns CPU offline rendering, not a
claim that full-quality frames render at interactive rates.

## Reproduction

```powershell
& $env:BLENDER_BIN -b --factory-startup milestones/photorealism-v2-candidate/scene.blend --python-exit-code 1 -P build/portrait_refinement.py -- --folder out/portrait-refinement/rebuilt
python tools/photorealism_checks.py --scene out/portrait-refinement/rebuilt/scene.blend --out out/portrait-refinement/rebuilt-checks --baseline milestones/photorealism-v2-candidate/evidence/poses
python tools/portrait_checkpoint.py --candidate out/portrait-refinement/rebuilt --checks out/portrait-refinement/rebuilt-checks --out out/portrait-refinement/rebuilt-checkpoint
```

Use fresh output directories. Rendered images, benchmark results and masks must
bind to the new scene; do not copy old evidence into the new check folder.
The packager requires passing source-bound checks and unchanged build inputs.
It creates matched front/three-quarter stills, a packed scene, evidence, attribution
and a hash manifest. It does not promote a release or award a visual-quality score.

If a process stops specifically during `anchors`, the check command accepts
`--resume-anchors` with the same output folder. It rejects a different scene or
stage, repeats preflight/geometry/timing, and lets the existing visibility worker
validate and resume the saved image hashes. Two regression checks cover stale
scene and incorrect-stage rejection.

## Iteration notes

The first temple-lock prototype floated away from the face in three-quarter
view and was rejected. The second fits every fiber to the face surface, blends
its root into the existing hairstyle and varies tip lengths. It has 483,288
visible evaluated polygons (v2: 464,088), 2,100 thicker brow fibers and 320 new
temple fibers. Cheek/jaw changes affect 4,775 vertices with maximum displacement
4.294 mm; the edited region starts below z=-24 mm, clear of the eye sockets.

The first targeted run passed preflight and the 1,009-pose/14-fault geometry
audit but failed the unchanged CPU gate during another concurrent Blender job:
142.765 / 154.532 / 155.391 seconds for center/up/corner. Those measurements are
retained in `out/portrait-refinement/checks`. They are not passing performance
evidence. A separate run waits for the pre-existing render batch to finish.

All 82 unit tests passed. Git checkpoint creation was attempted, but the session
cannot create `.git/index.lock`; commit and push remain blocked by filesystem
permissions. No README, video or presentation edits are part of this work.

## Skin, iris and expression follow-up

The organizer's email prioritizes realistic skin, eye textures and eye expressions.
`build/eye_expression.py` builds on the tested character-polish milestone. It
adds stronger skin microrelief, softer roughness variation around the nose and
forehead, and a curved reflection layer over the packed iris texture. Upper and
lower lid shape keys respond to the existing fixation target, including matching
motion in the lash, wet margin and crease meshes. The build checks weights at
down, center and up and verifies that pupil meshes and calibration are preserved.

```powershell
& $env:BLENDER_BIN -b --factory-startup milestones/character-polish-2026-11-11/scene.blend --python-exit-code 1 -P build/eye_expression.py -- --out out/eye-expression/rebuilt/scene.blend
python tools/photorealism_checks.py --scene out/eye-expression/rebuilt/scene.blend --out out/eye-expression/rebuilt-checks --blender $env:BLENDER_BIN
```

The reloaded prototype passed scene preflight and 1,024-pixel renders at center,
up and down. These eight-sample trial images retained 100% measured visible dark
pupil coverage. Maximum blind and template errors were 0.172 px and 0.122 px
respectively, rounded upward. The comparison pairs these trials with the original
character-polish renders at the same gaze and calibration. Sample counts differ.
The exact scene, comparison and reports are in
`milestones/eye-expression-2026-11-11`. The full CPU, reset and sweep checks remain
necessary before using this candidate as the submission build.
