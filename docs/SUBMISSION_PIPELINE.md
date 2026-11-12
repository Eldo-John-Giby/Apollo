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
   slots. For each map, use `submission_bake.py -- --source SOURCE --target
   TARGET --uv UV_NAME --out MAP.png` in a disposable background process.
   The source must use Principled materials. This bakes base color through
   emission without lighting. Set `--cage` and `--distance` to suit the
   alignment and scale. Inspect for ray misses, seams and eye distortion.
   Bake separate eyes where the evaluator layout permits and adapt the
   binding if the supplied mesh uses a shared atlas.
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

The MPFB checkpoint uses Blender 4.5.15 LTS on CPU. Five 1024 × 1024
stills rendered with the same calibrated camera and 32 samples. A 256-pixel
emission bake onto a duplicate iris exercised the bake path. All three packed
timelines reopened with frames 1–192 at 24 fps. Five sampled frames per mode
matched the requested target and blink weights, and eye rotations matched
across two builds. Preview renders confirmed lateral motion and showed a
small gap at peak blink even after adjustment. The eyelid fit needs another
pass on the evaluator mesh. Full frame sequences, independent visual review
and GNM qualification remain pending.
