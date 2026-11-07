# Realism visual preflight checkpoint

Development snapshot, not the fully qualified release or an organizer submission.
Open scene-preview.blend to inspect the new appearance in Blender. All textures
and cosmetic mesh geometry are packed. The registered delivery layout remains
separate; use the protected competition-qualified-2026-11-07 release until the
new complete qualification finishes.

This checkpoint passes 80 native tests, all five direction/reset checks, nine
anchor image/mask checks and the independent 1009-pose geometry audit. Repeated
sweeps, clean-room and full secondary/Linux qualification, the updated 256-image
corpus and expanded 113-pose visibility are not claimed complete here.

The selected profile uses 32 samples with denoising. All nine 32/64/128 sample
images were actually reviewed; the higher counts offered little visible gain
at the required resolution. Local means: about 75/141/271 s per frame. The older
scene averages about 27 s in a separate run. The new look costs more CPU time.

The visual ratings are an agent assessment, not independent human ratings or
competition points. Simplified non-refractive eyes and a static neutral head
remain limitations. Before/after images use matched poses and calibration.
Full-head portraits use separate presentation cameras and are not graded views.

Reproduce with build/realism_scene.py and build/realism_config.json as described
in docs/VISUAL_REALISM.md. No new qualified tag is associated with this snapshot.
