# GNM portrait refinement — 16 November 2026

This is an isolated still-portrait refinement of the owner's supplied
`out/naturalness-review-v2/current-work.blend`, SHA-256
`c4daf292d1e5b6dc99777b10ae1fd16bd56b1b8489c1b1fc79668f359f472784`.
The source and qualified competition scenes remain preserved. This candidate
does not replace the production maps or qualified motion package.

## Appearance work

- An editable anatomy key refines cheek projection, jaw/chin definition,
  nasal wings and upper-lid framing; a second key adds subtle asymmetry.
  The original Basis remains available. No remeshing or UV changes.
- A warmer complexion retains the existing scan-derived pigment. Misplaced
  brow fibers are attenuated with nearby forehead pigment before adding
  anatomically fitted strands. Regional roughness separates forehead, nose,
  cheek and lips; fine relief remains physically small.
- A swept brown hairstyle replaces the pale, stiff preview groom. Scalp
  strands follow the actual surface, lift in uneven groups and taper at the
  tips. Short directional brows and restrained upper lashes frame the eyes.
- The original pupil and eye geometry are preserved. Delicate authored iris
  fibers and inner flecks augment the muted source maps, without claiming
  recovered photographic detail.
- Original-camera front evidence and separate neutral 85 mm studio views
  distinguish material/anatomy changes from lighting. Close-up evidence
  covers the eyes, skin and lips.

The static groom contains 48,000 scalp strands, 1,900 brow strands and 144
upper lashes. These are rendered at full density. It has no animation binding;
do not use it as a qualified motion groom.

## Reproduction

Use Blender 4.5.15 LTS and the repository's existing NumPy/Pillow/SciPy
dependencies. All paths below are relative to the repository root.

```powershell
python tools/gnm_portrait_maps.py --template out/template/template.npz --source out/naturalness-review-v2/maps --out out/portrait-maps
& 'C:/Program Files/Blender Foundation/Blender 4.5/blender.exe' --background --factory-startup out/naturalness-review-v2/current-work.blend --python-exit-code 1 --python tools/gnm_portrait_refine.py -- --maps out/portrait-maps --out out/portrait-review --size 1024 --samples 48
& 'C:/Program Files/Blender Foundation/Blender 4.5/blender.exe' --background --factory-startup out/portrait-review/portrait.blend --python-exit-code 1 --python tools/gnm_portrait_check.py -- --source out/naturalness-review-v2/current-work.blend --out out/portrait-review/reopened-check.json
```

`--finish-existing` resumes neutral studio reviews from a saved anatomy/groom
checkpoint. It does not rerun the sculpt or regenerate strand positions.
The final packed scene opens with the neutral frontal camera; the source
camera is retained as `GNM Camera`. The saved scene uses 1400 square pixels,
96 Cycles CPU samples and denoising; review stills use 64 samples. No beauty
retouching is applied.

## Evidence and limits

The milestone packet holds the editable packed scene, stills, comparison,
build/map receipts, reopened checks and checksums. The generic render delivery
gate is compared with the native source because the GNM model intentionally
combines independent skin, eye/cornea and internal mouth components.
Raw gate findings are retained rather than presented as an unconditional pass.

The reopened candidate passed the render delivery gate with no errors or
warnings. Source Basis, all 17,662 quads, both UV layouts and native eye
vertices match exactly. All five images are packed. Measured maximum scalp
and brow root offsets are 0.0801 mm and 0.0501 mm; all strand positions and
radii are finite. Anatomy refinement peaks at 2.428 mm, and asymmetry at
0.179 mm. These measurements verify asset integrity, not aesthetic ratings.

The existing Infinite Scan CC-BY-3.0 derivative and CC0 fallback attribution
continues to apply; see `assets/gnm-scan/ATTRIBUTION.md` and its retained license.
New fibers, iris variation and map refinements are authored synthesis.

This is an artistic candidate with technical still-image checks. Human
acceptance, photorealism, engine portability, motion deformation and organizer
scores are not established by these checks. No numeric beauty or competition
score is assigned.
