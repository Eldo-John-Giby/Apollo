# Character appearance refinement

The source is the packed adult-female scene in
`milestones/photorealism-v2-candidate/scene.blend`. The November 10 stress run
remains evidence for that specific scene. This pass creates a separate packed
development candidate from the same calibrated rig.

## Plan and implementation

1. Sculpt the lower face with a localized cheek hollow, a gentler lower cheek
   taper and a slight asymmetric lift at the mouth corners. Preserve the upper
   face, lid fit and eye meshes. Review front and three-quarter stills for
   unintended pinching or a forced expression.
2. Replace the sparse brow outline with a fuller arch and tapered tail. Vary
   the fiber direction, thickness and brown tone. Reproject all fibers onto
   the face and replace the existing groom at the same strand and polygon counts.
3. Keep the existing lip albedo as the base. Feather rose pigment inward from
   the shared lip/skin boundary and use directional microfolds and a satin
   highlight to give the lips more relief using the packed skin atlas and face mesh.
4. Review matched portraits and calibrated pose crops. Verify the exact
   saved scene with V1/V2, the independent geometry audit, 32-sample CPU
   benchmark, nine RGB and pupil-mask poses, a fresh reset render and the
   official ten-frame sweep. Use the existing 120 s/frame and 4 GiB RSS
   limits and keep the saved Cycles profile.

Use the bounded checks during appearance iteration. For a final release on
the new scene, regenerate the required expanded stress and release evidence
against its own hash. The older 113-pose and 256-image evidence remains tied
to the original v2 candidate.

## Reproduce

Run from the repository root with the pinned native Blender in
`$env:BLENDER_BIN`. MPFB is unnecessary for this pass.

```powershell
& $env:BLENDER_BIN -b --factory-startup milestones/photorealism-v2-candidate/scene.blend --python-exit-code 1 -P build/character_polish.py -- --folder out/character-polish/rebuild
python tools/photorealism_checks.py --scene out/character-polish/rebuild/scene.blend --out out/character-polish/rebuild-checks --baseline milestones/photorealism-v2-candidate/evidence/poses --blender $env:BLENDER_BIN
python tasks.py test
```

The build receipt binds the original packed scene, recipe and saved scene.
The reloaded scene is used for all bounded checks. The existing portrait
worker keeps the portrait camera edits in memory and renders only stills.

## Result

The packed scene, matched portraits and exact-scene evidence are in
[`milestones/character-polish-2026-11-11`](../milestones/character-polish-2026-11-11/).
The front portrait shows fuller brow bodies with visible individual fibers
and a stronger rose tone across the lips. The three-quarter portrait shows
the change in cheek depth more clearly than the front. Fine lip folds are
subtle at portrait scale. The clay render shows a continuous lower-face
surface and a small mouth-corner lift. The calibrated view still puts the
eyes at the center of the image and crops most of the mouth.

| Check | Measured result |
| --- | --- |
| CPU at 1024 × 1024, 32 samples | 64.42 s center, 66.47 s up, 85.20 s corner |
| Peak measured Blender RSS | 1.41 GiB |
| Visible evaluated geometry | 464,088 polygons, 2,100 brow strands |
| Independent geometry | 1,009 poses passed, 14 injected faults detected |
| Nine RGB and pupil-mask poses | 100% minimum visible dark coverage, 0.2774 px maximum blind error |
| Direction and reset | Passed, byte-identical center after corner-to-reset |
| Official sweep | All ten frames passed metadata and image checks, 0.1071 px maximum blind error |
| Python suite | 82 passed |

The center/up/corner measurements are single native Blender 4.5.15 CPU runs.
The development evidence summary binds the packed scene and delivered stills
by SHA-256.
