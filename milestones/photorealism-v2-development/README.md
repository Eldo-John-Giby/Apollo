# Photorealism v2 development candidate

The CPU appearance implementation and targeted engineering checks are complete.
This is a reviewed development candidate, **not a qualified release or a claim
of photographic realism**. The main remaining visual gaps are smooth hair mass,
broad skin mottling, sparse brows and visibly synthetic eye shading.

Open `scene.blend` in Blender 4.5.15. All runtime meshes, materials and textures
are packed; MPFB and MCP are unnecessary for playback. The public wrapper is
`wrapper/eyes.py`. From this folder, with BLENDER_BIN pointing at Blender:

```powershell
& $env:BLENDER_BIN -b --factory-startup scene.blend --python-exit-code 1 -P wrapper/eyes.py -- --out new-output
```

Use a new output directory. This regenerates ten 1024x1024 clockwise PNGs and
metadata. The supplied `renders/`, `metadata.json` and `contact_sheet.png` are
actual outputs from this exact scene. Contact-sheet annotations are inspection
overlays only; the graded PNGs are unaltered native Blender renders.

The implementation adds baked adult-female anatomy and neutral mouth closure,
refitted orbital tissue, native 2K CC0 female skin with regional roughness and
micro-normal shading, textured brown irises, a pulled-back side-part bun,
individual brows and baked strands. Camera, eye meshes, pivots, fixation bounds,
API and metadata contract remain protected. Static lids and non-refractive eye
surfaces avoid new runtime dependencies and optical annotation displacement.

Evidence is in `evidence/`: geometry and fault injection, cardinal/reset report,
nine-pose image/mask checks, official-sweep image check, CPU benchmark, measured
process memory, matched baseline comparisons, portraits and neutral/clay views.
`baseline/scene.blend` is the exact clean source used by `build.json`; the older
reviewed prerelease and qualified fallback remain unchanged.

Measured checks: 80 unit tests; independent 1009 poses and 14 detected mutations;
all cardinal directions and byte-identical reset; nine fully visible pupil poses;
ten-frame metadata and image validation. The official sweep's maximum blind
pupil error is 0.111 px (rounded upward); nine-pose maximum is 0.276 px. CPU
center/up/corner took 55.28/62.77/63.52 seconds at 32 samples. Peak OS process RSS
across measured core stages was 1,428,791,296 bytes (1.33 GiB). Visible evaluated
geometry is 387,912 polygons. These are local engineering results, not official
rubric scores or cross-machine timing promises.

The first check-driver run stopped at an inspection-only diagnostic helper,
after all graded checks passed. Its original failure record is retained. The
helper was fixed to render non-calibrated portraits directly with absolute
paths; corrected diagnostic images and their hash receipt are included. No
passed graded evidence was relabelled as a release qualification.

Native skin is 2K rather than the planned 4K: the installed compatible CC0 set
has no genuine 4K detail. No upscaling, generative retouching or painted pupil
corrections were used. Stronger skin-map cleanup, less helmet-like hair and more
natural brows/eye integration remain necessary before claiming the original
industry-grade visual ambition is met. Review `evidence/comparisons/` at native
resolution rather than relying on this text.

Rebuilding anatomy requires MPFB and the versioned source recipe/config/assets;
see `../../docs/PHOTOREALISM_V2.md` and `../../TEAM_SETUP.md`. Full Windows/Linux
and secondary-version qualification, expanded pose suites and release publication
were intentionally not run. No videos or presentations were created.

Persistent-data off was measured separately for center/up: 60.66/66.48 seconds
versus 55.28/62.77 with reuse. Both PNGs are byte-identical. These are single
serial trials; persistent data remains enabled. See evidence/persistence in the
tracked development handoff.
