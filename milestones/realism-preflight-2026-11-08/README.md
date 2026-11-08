# Realism visual preflight checkpoint

Development snapshot, not a qualified release or an organizer submission.
This replaces the earlier v9 snapshot after its full run exposed a render-seed
regression. The old snapshot remains in Git history; it was never promoted.
Use the protected `apollo-v0.2.0` release until the replacement is fully qualified.

Open scene-preview.blend to inspect the replacement appearance in Blender.
Textures and cosmetic geometry are packed. The renderer seed is 0; the separate
groom geometry seed remains 20261108. Scene SHA-256:
450bd7a7f03dff6c267e339eb8311912a6e8c375e5026bdfcdb51619bd3f8db5.

This snapshot passes 80 native tests, all five direction/reset checks, nine
anchor image/mask checks and the independent 1009-pose geometry audit, including
14 detected mutations. The exact V1/V2 preflight passes on native and Linux
Blender 4.5/5.2. Full V1-V17, repeated sweeps, clean-room replay, updated 256-image
corpus and expanded 113-pose visibility remain pending for this replacement.

Retain 32 denoised samples after inspecting all nine new 32/64/128 images.
Three-pose local means: about 63/126/269 seconds; these are measured examples,
not official benchmarks. The earlier scene averaged about 27 seconds in its
separate run. The appearance upgrade costs more CPU time.

The image-bound ratings are an agent assessment, not independent human ratings
or competition points. Simplified non-refractive eyes, texture mottling, a
stylized short groom and a static neutral expression remain limitations.
Before/after images use matched poses/calibration. Full-head portraits use
separate cameras and are not graded views. No videos or decks are created.

Reproduce using build/realism_scene.py and build/realism_config.json; see
/docs/VISUAL_REALISM.md for the replacement evidence path and qualification.
No qualified tag is associated with this development snapshot.
