# Photorealism v2 execution

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
