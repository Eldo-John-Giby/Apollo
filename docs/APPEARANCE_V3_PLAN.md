# Adult character appearance refinement plan

Started 11 November 2026 on appearance-v3, isolated from the active main workspace.
Estimated effort is 1-2 focused development days plus the final 7-9-hour stress run.

## Target

Develop a polished, approachable adult female character with natural eye
integration and restrained styling in the native evaluation view. Evaluate actual
images and preserve only changes that improve the result. CPU Cycles remains the
render path. The previous tested appearance is the source and comparison baseline.

## Stages and acceptance

1. Inspect facial landmarks, current materials and eye/socket contact. Preserve
   eye mesh vertices, pivots, eye bones, camera and fixation configuration.
2. Refine cheek/jaw transitions, lips and resting mouth corners. Test a modest
   upper-lid relaxation with a protected pupil-clearance region. Refit cosmetic
   attachments and inspect native upward/corner views. Reject any collision.
3. Introduce spatially restrained cheek/lip coloration, regional roughness and
   balanced skin detail. Improve iris reflectance using fixed physical lights.
   Avoid dark makeup connected to pupils and refractive image displacement.
4. Soften brow flow, hairline and pulled-back hair styling. Add sparse temple
   detail outside the eye region. Bake all geometry and pack all resources.
5. Inspect matched native center/cardinal/corner crops, front/three-quarter and
   neutral/clay stills. Benchmark CPU and process memory. Select the strongest
   consistent candidate. Aim for <=90 seconds per frame, <=4 GiB and <1M polygons.
6. Run unit tests, independent geometry, nine-pose RGB/masks, actual reset,
   official ten-frame sweep and metadata/image checks. Retain unchanged thresholds.
7. Freeze the selected scene and test sources. Complete the full 113-pose actual
   RGB/mask sweep and seeded 256-image corpus. Diagnose and fix failures. Review
   worst cases and retain all evidence with scene/source hashes.
8. Publish packed development assets, source recipe/config, comparison stills,
   tested conventional wrapper/layout and handoff instructions. Commit meaningful
   stages and push the branch. Release selection remains separately qualified.

## Boundaries

Read and comply with AGENTS.md. README changes require an explicit request.
Follow the standing media rules. New instructions belong in this plan and the
candidate HANDOFF.md. No new runtime addon, downloaded assets or simulation is
needed. Keep eyelids static for this implementation. Do not enlarge gaze offsets
or alter the physical pupil to increase apparent movement.

## Progress

Plan recorded. Inspecting the existing packed scene and starting an isolated
visible MCP workspace for artistic review.

User refinement priorities added during implementation: thicker, cleaner brows
and more realistic lips. The first prototype uses 1250 shaped brow hairs per
side, three brown fiber tones, soft inner growth and tapered tails. Lip work
adds sub-millimeter projection/volume, a restrained cupid bow and corner lift,
regional rose colouring, fine vertical shading detail and moderate roughness.
A 0.35 mm upper-lid relaxation is being previewed before visibility checks.
Initial exact V1/V2 preflight passed and protected eye mesh hashes match.

Second preview decision: brow density increased to 1500 hairs per side with a
4.5 mm root envelope, stronger lip volume/colour and shorter high-temple fibers.
The initial low temple wisps were rejected as skin marks. Final upper-lid
relaxation is 0.65 mm in the local weighted sculpt, with protected central pupil
clearance. Groom collections and source dependency receipts were completed.
Candidate-1 now undergoes native targeted checks before full stress testing.

Candidate-1 was rejected at the native benchmark: the larger lid reduction
caused blind pupil errors of 6.08 px upward and 9.30 px in the corner on one eye.
Candidate-2 retains only a 0.15 mm weighted upper-lid adjustment and the proven
iris reflectance. A mesh-distance lip-interior attribute now fades colour and
roughness at the actual vermilion boundary. All three native benchmark pupil
checks pass; measured center/up/corner times are 53.20/56.80/57.97 seconds.
A resumable full-suite runner now preserves the original start time, source
hashes and per-stage output hashes, addressing weaknesses found in the earlier
long-run launcher. Remaining stages continue serially.

The user added a later creative direction after this phase: leaner lower-face
proportions, more defined cheekbones/jaw/chin, fuller brows and refined lips,
with stronger dimensionality and a CPU ceiling. This follows the current phase
and will be compared against the completed candidate before selection.
