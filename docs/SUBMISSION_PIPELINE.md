# Track 01 submission pipeline

Use [the evaluation audit](PS_AUDIT.md) for the official checklist. This
pipeline currently uses the Apollo MPFB development rig. The evaluator GNM
mesh and UV layout are pending, so these artifacts cannot establish GNM
compatibility or final submission readiness.

## Run the development reference

Use Blender 4.5.15 LTS, the repository's Python requirements, and a CPU.
Run from the repository root. Set BLENDER_BIN to the executable.

```powershell
$scene = 'milestones/eye-expression-2026-11-11/scene.blend'
$work = 'out/submission-dev'
$variants = 'rose-brown', 'golden-hazel', 'olive-amber', 'neutral-deep', 'cool-grey'
python tools/submission_variants.py generate "$work/variants"
foreach ($variant in $variants) {
    & $env:BLENDER_BIN -b --factory-startup $scene --python-exit-code 1 `
        -P tools/submission_textures.py -- --variant "$work/variants/$variant/variant.json" `
        --out "$work/stills/$variant.png"
    if ($LASTEXITCODE -ne 0) { throw "Failed to render $variant" }
}
python tools/submission_variants.py sheet "$work/stills" --out "$work/contact-sheet.png"
foreach ($mode in 'left', 'right', 'generate-motion') {
    & $env:BLENDER_BIN -b --factory-startup $scene --python-exit-code 1 `
        -P tools/submission_motion.py -- --mode $mode `
        --variant "$work/variants/rose-brown/variant.json" --out "$work/$mode"
    if ($LASTEXITCODE -ne 0) { throw "Failed to build $mode" }
}
```

Use fresh output directories for variant generation and timeline builds. The
five palettes are development color studies derived from the licensed local
assets. Each manifest records map hashes, source hashes and attribution.
The local iris atlases reuse the Apollo iris shader's existing UV transform.
Review the variants under multiple lights and author further local detail
after transferring to the evaluator mesh.

Each mode saves a packed expression.blend with 192 frames at 24 fps. Add
`--preview-frame N` to render a selected frame or `--render` to produce
`frames/frame_0001.png` through `frames/frame_0192.png` in a new output
directory. The team can open the packed file and capture the same 8-second
animation at 24 fps, or encode the numbered frame sequence at 24 fps. The
three distinct clips must each be 15 seconds or less. The team also owns the
official template deck and submission.

## Integrate the evaluator head

1. Obtain the exact GNM head and UV version, material layout, and sharing
   terms from the PoC. Preserve an untouched copy for qualification. Work in
   a scratch scene that contains the source and the aligned target meshes.
2. Run `submission_textures.py -- --inventory` through Blender on the fresh
   target to get its object names, UV names, fingerprints, and material
   slots, along with mesh dimensions, armatures and shape keys. For each map, use `submission_bake.py -- --source SOURCE --target
   TARGET --uv UV_NAME --out MAP.png` in a disposable background process.
   The source must use Principled materials. This bakes base color through
   emission without lighting. Set `--cage` and `--distance` to suit the
   alignment and scale. Inspect for ray misses, seams and eye distortion.
   Bake separate eyes where the evaluator layout permits and adapt the
   binding if the supplied mesh uses a shared atlas. If both eyes share
   one material slot, reference the same packed eye atlas, slot and UV for
   both manifest roles. Conflicting entries are rejected before materials
   change.
3. Copy the manifest shape from a generated local variant. Set the target
   label, target object and UV names, material slot indices, UV fingerprints,
   map SHA-256 digests and source provenance. Omit `replace_image` and
   `replace_on_all_slots` for direct native UV assignment. Apply each set
   to a fresh evaluator mesh and render through the same judging camera and
   lighting. Inspect neutral and oblique closeups before scaling to the rest
   of the variants.
4. Map the target rig to Apollo's calibrated gaze controls. The current
   motion builder expects the Apollo eye bones and lid, lash and brow meshes.
   Fit the blink and brow deformations to the GNM mesh before saving the
   final scenes. Verify eyelid contact, visible directions, and expression
   playback on reopen. Review mid-blink, peak closure and reopening before
   rendering the full frame sequences.
5. Rehearse from a clean checkout, including license and asset access checks.
   Record the exact scene and map hashes and check the three frame counts.
   Put the runnable package, stills, timeline, documentation and team media
   on public GitHub. Keep the older sweep and metadata as supplementary
   evidence. If the evaluator asset cannot be shared, document its
   acquisition and import. The team verifies public access and submits the
   repository URL before the confirmed cutoff on 22 November.

## Development evidence

The first MPFB checkpoint used Blender 4.5.15 LTS on CPU. Five 1024 × 1024
stills rendered at 32 samples with the same camera and lights. The later
motion checkpoint was reopened and checked at the two peak-blink frames for
each mode. Camera rays to both evaluated pupil meshes were blocked at both
peaks. The pupils were visible before and after the blink. Projected pupil
positions also confirmed the expected left and right shifts. A human
reviewer should still judge the expression timing and the lid crease in
the preview frames.

Run these commands from the repository root after generating the original
development variants and all three updated timelines. The paths below are
examples. Choose unused output directories when rebuilding.

```powershell
$work = 'out/submission-dev'
$scene = 'milestones/eye-expression-2026-11-11/scene.blend'
& $env:BLENDER_BIN -b --factory-startup --python-exit-code 1 `
    -P tools/submission_motion_check.py -- --root $work
& $env:BLENDER_BIN -b --factory-startup $scene --python-exit-code 1 `
    -P tools/submission_uv_rehearsal.py -- `
    --variant "$work/variants/rose-brown/variant.json" --out "$work/uv" --size 1024
python tools/submission_variants.py generate "$work/polish" --polished-reference
& $env:BLENDER_BIN -b --factory-startup $scene --python-exit-code 1 `
    -P tools/submission_textures.py -- --variant "$work/polish/rose-brown/variant.json" `
    --out "$work/oblique.png" --oblique-light
```

The UV rehearsal rotates the face and both iris UV layouts by 180 degrees
on the local rig. It bakes in both layouts, compares covered texels, then
reopens the source and applies the transferred maps to fresh objects with
the new UVs. At 1024 pixels all three maps exceeded 99.98% coverage overlap,
and the largest mean absolute color error was below 0.00029. The rehearsal
tests the transfer and manifest workflow with a controlled layout change.
A different head topology and the evaluator's eye material layout still
require the official GNM asset.

Use the same camera for all five variants under the calibrated lights and repeat
with `--oblique-light` for a side-key comparison. Use
`--polished-reference` to generate only rose-brown for a quick bake rehearsal.
Add `--changed-geometry` to the UV rehearsal to subdivide, triangulate, and offset
the face and iris targets before baking. This changes connectivity and surface
position, with related geometry and UV islands. The 1024-pixel rehearsal
used extended padding and a short projection cage. The face target changed
from 53,512 to 428,096 polygons and each iris changed from 128 to 1,024.
All three maps exceeded 99.997% coverage overlap, and the largest mean
absolute color error was 0.000473. The rebound scene rendered after the maps
were assigned to fresh target objects. The evaluator mesh may differ in
facial proportions and seams and still requires its own validation. Use `--draft` alongside
`--render` for a 25% resolution, four-sample motion review. Omit `--draft`
for the team capture. The motion scene is saved at the original resolution
and sample count in both cases.

The MPFB review handoff contains 192 draft PNGs for each mode. It renders
each unique pose and reuses the resulting PNG during identical holds.
The numbered sequence stays at 24 fps. Rebuild full-quality frames with
the normal render command for team capture. Review the unlabeled direction
sheet before opening the separate answer key, then record any expression or
eyelid issues by mode and frame number.


## Full-quality CPU fallback

Generate the five variants and both matched still sets under `$textures`
using the commands above. Write calibrated-light renders to `$textures/neutral`
and side-key renders to `$textures/oblique` with `--oblique-light`. Render
from saved timelines built by the current motion tool. The same render command can
be rerun after an interruption. It binds the output to the exact saved scene
and Blender build, validates PNG dimensions and chunk checksums, and replaces
missing or corrupt frames. Use the same flags on resume. The verifier requires
all 192 numbered PNGs for a mode.

```powershell
$motion = 'out/submission-fallback'
$textures = 'out/submission-score'
$seams = "$motion/seams"
$scene = 'milestones/eye-expression-2026-11-11/scene.blend'
foreach ($mode in 'left', 'right', 'generate-motion') {
    & $env:BLENDER_BIN -b --factory-startup $scene --python-exit-code 1 `
        -P tools/submission_motion.py -- --mode $mode `
        --variant "$textures/variants/rose-brown/variant.json" --out "$motion/$mode"
    if ($LASTEXITCODE -ne 0) { throw "Timeline build failed: $mode" }
    & $env:BLENDER_BIN -b --factory-startup "$motion/$mode/expression.blend" `
        --python-exit-code 1 -P tools/submission_render.py -- `
        --out "$motion/$mode/frames" --reuse-holds
    if ($LASTEXITCODE -ne 0) { throw "Render failed: $mode" }
}
& $env:BLENDER_BIN -b --factory-startup --python-exit-code 1 `
    -P tools/submission_motion_check.py -- --root $motion `
    --variant "$textures/variants/rose-brown/variant.json"
& $env:BLENDER_BIN -b --factory-startup $scene --python-exit-code 1 `
    -P tools/submission_seams.py -- --out $seams `
    --variant "$textures/variants/rose-brown/variant.json"
python tools/submission_bundle.py --motion $motion --textures $textures `
    --seams $seams --out "$motion/apollo-mpfb-fallback.zip"
```

After building a timeline, rerun only its render command to resume.
`--first` and `--last` can render a subset for inspection. Pass `--verify-only`
with the original flags to check all 192 frames. Use `--reuse-holds` only on
unedited timelines from Apollo's static reference scene. It reuses the full
resolution render for the exact same gaze and blink pose with fixed render
seed and motion blur off. Each frame still has its own numbered PNG and
receipt. Omit the flag and use a fresh output folder for custom timelines
with extra animation or any frame-dependent shading.

The seam rehearsal cuts originally continuous UV edges, packs the two
regions into separate atlas areas, and compares baked colors at matching
polygon sample positions. It rebinds the maps on a fresh scene, verifies the
target UV fingerprints, and renders a still. The local run added 217 face
seam edges and two per iris. All 53,768 expected polygon color samples
remained covered. Mean absolute color error was at most 0.00202 on a 0–1
scale. It is a local stress test.
Evaluator geometry and licenses still depend on the organizer asset.


The 13 November fallback checkpoint verified 576 PNGs and the archive
manifest, then extracted the ZIP into a fresh directory. It reproduced
one rose-brown still and Left frames 21–22 pixel-for-pixel, with hold reuse
disabled during reproduction. The [fallback receipt](../milestones/submission-fallback-rehearsal-2026-11-13/fallback-receipt.json)
records the archive checksum, frame receipts, and reproduction results.
The ZIP remains a local technical fallback for team review and media capture.
