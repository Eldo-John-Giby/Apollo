# Competition upgrade — execution record

Branch: `competition-upgrade`. Protected fallback: `apollo-v0.1.0`.
Technical gates A–F are complete. The evidence-bound release is staged under
`milestones/competition-upgrade-2026-11-07` with executable `delivery/apollo`. Registration and event administration are outside
this workstream. No official score or independent human preference is claimed.

## A — Independent verification: complete

The separate NumPy Rodrigues/pinhole reference imports no production math. It
fits physical eye centers/radii from deformed scleral vertices and measures
area-weighted pupil centroids and full pupil surfaces on 1009 poses (nine anchors
plus 1000 seeded random inputs). Fourteen injected faults are detected, covering
motion, unilateral failure, bounds, labels, pivots, camera, annotations, pupil
mesh, missing texture and lighting. The geometry-guided connected-dark-surface
oracle is independent of both OpenCV trackers; it is not blind detection or a
substitute for visibility masks.

All native V1–V17 checks pass on Blender 4.5.15, including every applicable
Blender 5.2.3 secondary check. Source/artifact/diagnostic hashes bind reports;
changed inputs or verifier sources invalidate reuse and packaging. Missing
results stay NOT RUN. No detector threshold or qualification gate was relaxed.
79 tests pass on Windows and Linux. The complete Linux V1–V17 run also passes, including its applicable 5.2 suite.

## B — Appearance and selected candidate: technically qualified

The first comparison was rejected by the user because its variants looked the
same. The replacement changes the colored iris radius/material, lid opening and
MPFB-refitted lashes. A dark-hazel prototype then failed the unchanged image-only
direction tracker because its iris merged with the dark pupil. Its partial run
and 41 dataset frames are retained under `out/upgrade/rejected-dark-iris`.
Neither geometry success nor failed-prototype masks were accepted as a release.

Corrected B raises iris reflectance while preserving the fiber pattern, pupil
geometry, physical centers and calibration. It uses 32 samples, two path bounces,
one diffuse/glossy bounce and persistent render data. Scene SHA-256:
`3fdc93632a84011cc78c3210e703ad0f6653fcef68375d21a741af76b951605d`.

The corrected real cardinal/reset check passes, reset PNGs are byte-identical,
and maximum template/projection error is 0.050578 px. The ten-frame sweep's blind
and template maxima are 0.175464 and 0.061253 px. All native qualification checks
pass on these exact bytes. Rebuilding from the protected frozen source with the
MPFB recipe produces an identical center PNG; binary `.blend` identity is not
claimed. Human naturalness/preference ratings remain unmeasured.

## C — Separate research dataset: complete

Actual seed-0, 32-sample generation contains 256 rendered poses: nine normalized
square anchors plus 247 seeded random inputs. Manifest `apollo.dataset/1` keeps
camera, lighting, identity and pupil size fixed. Source/config/runtime signatures,
per-image hashes and atomic progress protect resume. Random records do not invent
a clockwise theta, and the official ten-frame metadata schema is unchanged.

All 256 images pass independent geometry-guided pixel checks, maximum residual
0.217847 px. Coverage and spatial anchor plots are generated. All 25 visibility
poses (nine anchors plus sixteen seeded random inputs) have full visible/dark
coverage; maximum mask-centroid residual is 0.030619 px. A real half-pupil fault
measures 0.499356 coverage and is rejected. A rendered lighting-loss fault is
rejected by both signature and image checks. Reports bind the corrected scene,
evidence JSON, mask PNGs and analyzer source.

Completed 256-frame resume changes no bytes. A real 255-to-256 interrupted run
reconstructs every PNG and the manifest identically. These are finite geometric
and image checks, not an ML benchmark or a diverse-identity dataset.

## D — Blender controls: complete

The optional Apollo sidebar calls the public wrapper for normalized sliders,
Left/Right/Up/Down/Reset, pose render and official sweep. All five buttons and
pose rendering were exercised in live Blender while preserving the unsaved user
scene and restoring its pose/render settings. The final candidate operator
rehearsal produces an API-identical pose PNG and valid ten-frame sweep; cleanup
passes. The panel is not installed or required in the evaluator scene.

## E — Evidence presentation and demonstration: complete

The editable ten-slide deck uses actual scene images and measured reports.
Package, layout, font and import checks pass. PowerPoint exported every slide;
all ten final slides were individually visually inspected. The 105.05-second
1280×720/24-fps video fully decodes (2520 frames); measured narration level is
-21.8 dB. Thirteen representative frames were reviewed, including directions,
reset, sequence, dataset, controls and limitations. Direction utterances are
separately generated and padded to five seconds each. Local Windows SAPI
synthesized narration and edited-artifact timing are explicitly disclosed.
Team/member names are not invented. No independent human usability study or
real-time render-speed demonstration is claimed.

## F — Reproduction and release: complete

The actual `apollo-competition.zip` passes extraction and regenerates all ten
PNGs and metadata identically with fresh configuration from a different CWD.
Archive SHA-256:
`2c3031176adbe5758155914a9291f6073905e37a6ef6e4ff91284d01db1ff09e`.
The earlier development freeze remains byte-for-byte protected.

The first Linux retry exposed a project-relative provenance-path requirement;
its failed evidence is retained under `out/upgrade/rejected-external-mount`.
Qualification was restarted under writable `/workspace/out/upgrade`. A slow
Windows-mounted runtime extraction was replaced by copying and extracting the
same runtime archive on the container filesystem. Geometry preflight and all
79 Linux tests pass. Full primary/secondary Linux qualification passes all seventeen outer checks;
all sixteen applicable nested checks pass. Recursive nested V16 remains NOT RUN
by design; no missing check is relabelled.

`tools/export_upgrade.py` has validated and exported the conventional
`delivery/apollo` layout, development ZIP, full separate 256-image corpus,
deck/video and hashed evidence archives. Final manifests, ZIP CRCs and Git blob hashes are checked before tagging.
Release tag: `apollo-v0.2.0`. No new feature work is needed for this
release. College/team filenames, evaluator access and organizer forms remain
team-owned.
