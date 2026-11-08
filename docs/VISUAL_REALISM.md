# Visual realism implementation â€” 8 November 2026

Work branch: visual-realism. Protected fallback: apollo-v0.2.0.
The existing delivery and all released milestones remain unchanged.

## Current state

Implementation and early visual checks are in progress. No new scene is qualified.
The recipe builds separate anatomy, surface and finished checkpoints from the
released scene. MPFB is required only in the disposable build process for lid/lash
refitting. All new groom/lash/crease geometry is baked to meshes, so actual mask
occlusion includes it without changing the verifier. Rendering needs no addon.

```powershell
& $env:BLENDER_BIN -b delivery/apollo/scene.blend --python-exit-code 1 -P build/realism_scene.py -- --folder out/realism/checkpoint --stage finished
```

The builder refuses existing destinations. Physical pupil, iris and sclera
vertex positions are hashed before/after building. Shader-facing iris normals
may be corrected; pupil positions, eye centers, articulation, camera and metric
calibration are preserved. Build receipts bind source, recipe, configuration and
output scene. Recipe/config changes during building invalidate the receipt.

## Implemented appearance work

- Actual face/sphere intersection contours locate moist lid margins.
- Reduced MPFB eye-opening targets; small tear ducts and upper-lid creases.
- Tapered, seeded mesh eyelashes replace the stock lash cards in new candidates.
- Layered hazel shading, softened iris boundary and non-refractive wet response.
- Restrained peripheral scleral color variation.
- Skin subsurface response, fine bump and forehead/cheek roughness variation.
- Fixed soft key/fill illumination and seeded swept-back scalp strands.
- Configurable 32/64/128 sample experiments at center/up/corner.

Exploratory v1 groom was rejected as sparse and plug-like; v2 lighting was too
bright. v3 introduced denoising and darker irises. v4 exploratory geometry showed
lashes were too thin to survive denoising, prompting fuller tapered strands.
These are development comparisons, not promoted results or human ratings.

## Remaining acceptance gates

1. Matched full-frame/eye-region/cardinal/corner comparisons and documented agent
   visual assessment; require improvement in at least three categories without
   losing pupil readability. No independent human study is claimed.
2. Both unchanged direction detectors, exact reset and actual ten-frame preflight.
3. Controlled 32/64/128 comparisons; select the lowest acceptable noise level.
4. Expanded visibility: 81 grid poses plus 32 seeded random poses, real RGB and
   masks with actual occlusion. The stress manifest has a distinct schema.
5. Full independent geometry, native/secondary/Linux qualification, adversaries,
   repeated hashes and fresh-CWD reconstruction; regenerate the 256-image corpus.
6. Reviewed still-image evidence, exact archive/manifests and committed-byte checks,
   then tag/push only a passing final release. Event administration is separate.

```powershell
& $env:BLENDER_BIN -b --factory-startup out/realism/checkpoint/scene.blend --python-exit-code 1 -P tools/direction_smoke.py -- --folder out/realism/cardinals
python tools/direction_report.py out/realism/cardinals
& $env:BLENDER_BIN -b --factory-startup out/realism/checkpoint/scene.blend --python-exit-code 1 -P tools/benchmark_render.py -- --folder out/realism/samples --samples 32 64 128 --corner
& $env:BLENDER_BIN -b --factory-startup out/realism/checkpoint/scene.blend --python-exit-code 1 -P tools/realism_visibility.py -- --folder out/realism/stress-rgb --masks out/realism/stress-masks
python tools/analyze_visibility.py out/realism/stress-masks
```

## Current preflight and diagnostic findings

The darker v3 and v6 trials failed the unchanged ellipse detector in upward
image-left gaze: the pupil's dark component joined the lid shadow. Template
tracking still followed the correct pupil; it did not override the failed gate.
A soft frontal fill at (0.04, -0.22, -0.015) m separates both pupils correctly in
the actual upward render. v9 incorporates that fill, a restrained rear separation
light and the corrected front-edge lash fit. Full cardinals/reset and nine-anchor
RGB/mask checks are running before sample benchmarking. No threshold was relaxed.

The lid contour fitter must choose the front/exterior bisection bracket: averaging
a radius across an open edge can hit the rear socket wall and bury the lashes.
Strands are then fitted ahead of the actual skin surface along their length.
The early sparse groom, overbright lighting, and invisible-lash trials are not
promoted. Early exploratory build receipts are not release provenance.

The stress worker checkpoints nine anchors first, then the remaining 72 grid
poses and 32 random poses. It can reuse hash-checked, pose-matched images from
the complete corpus using --cache; scene, wrapper, runtime and sample signatures
must match. All 113 positions still receive actual occlusion-mask renders.
An extracted evidence archive can be analyzed with --dataset pointing to the
copied stress RGB folder, without rewriting the evidence JSON or its hashes.

The sample benchmark now binds scene/worker/wrapper bytes and marks completion
only after every requested profile finishes. Source changes during a benchmark
invalidate it. Clean-room qualification preserves stored scene settings rather
than forcing a 64-sample candidate to the old 32-sample draft setting. Dataset
CLI sampling now also supports 64 and 128; the public eye API is unchanged.

The release exporter has a distinct --profile realism gate: 113 stress poses,
explicit image-bound visual/sample reviews, actual benchmark evidence and an
unchanged selected center/up render. Old release gates retain their own profile.

## Completed v9 early gates

Scene SHA-256: 13a29bdfe9430ebac5aca13219dbb28856b438dce35647fbd459676aa8d17966.
All five cardinal/reset checks pass with both detectors; reset is byte-identical.
Maximum template/annotation error: 0.063294 px. All nine anchor images pass:
maximum blind error 0.230891 px, template error 0.093563 px. Actual masks show
full visible/dark coverage, maximum centroid residual 0.026708 px, and reject a
real half-pupil obstruction. All 80 native unit tests pass. The serial 32/64/128
sample comparison is running. Complete native/secondary/Linux qualification,
113-pose coverage and the final corpus remain gated. Videos and presentations
are excluded by the standing user rule recorded in AGENTS.md.

## Sample selection and reproducibility

All nine 32/64/128 sample images were reviewed, including center, up and corner.
Retain 32 samples: local means are about 75, 141 and 271 seconds respectively.
Mean luma difference between 32 and the 128-sample reference is about 0.382/255
for the full image and 0.182/255 for the forehead region. These are differences,
not objective naturalness scores. All nine sample images pass the independent
guided pupil check (maximum 0.190832 px). Selected center/up/corner PNGs match
the built checkpoint and early checks byte-for-byte. The matched sheets and both
portrait views have been inspected. Scene/image-bound agent review receipts
record modest improvements and explicit limitations, without human-study claims.

The fresh baseline averages about 27 seconds per frame in a separate serial run.
The new appearance costs more CPU time; no rendering-speed improvement is claimed.

For reproduction, build a separate finished checkpoint, select its saved sample
settings, copy the exact scene to out/realism/candidate, retain attribution, then
run the standard sweep/validate/sheet/prepare/verify commands from UPGRADE_RUNBOOK.
Do not pass a draft/final override when testing a stored 64-sample scene. Generate
its separate dataset with tasks.py dataset --scene ... --folder ... --count 256
--seed 0 --samples matching the saved scene. Analyze all images, then run the full
realism_visibility worker with --cache pointing to that validated corpus.

Final staging command (only after complete reviews and passing reports):

```powershell
python tools/export_upgrade.py out/realism/seed-zero --out milestones/apollo-v0.3.0 --delivery delivery/realism --profile realism --version v0.3.0
```

This preserves the older executable delivery. The new profile also includes the
113-pose RGB/mask evidence, matched comparisons, portraits and sample evidence.
Manifest, ZIP and committed Git blob checks precede tagging. Event administration,
registered team filenames and sharing remain team-owned.

## User scope update — 8 November 2026

Do not create or regenerate videos or presentations. The queued media worker
was stopped before authoring. Technical qualification, still-image review,
datasets, archive rehearsals and release packaging continue. Export no longer
requires or ships newly authored decks or movies. Historical artifacts remain
unchanged. Release names and the version mapping are in [RELEASES.md](RELEASES.md).

The new release archive uses `apollo-v0.3.0.zip`. After staging, run
`python tools/check_release.py milestones/apollo-v0.3.0 --delivery delivery/realism --revision :`
and repeat against HEAD after committing. This verifies actual Git bytes rather
than assuming local working-file hashes survive checkout/staging unchanged.

For the already-running local qualification batch, `python tools/finish_realism.py
--publish` waits for actual passing evidence and completed construction renders,
then exports, checks staged/committed Git bytes, commits, tags and pushes. It
stops on failed evidence or a changed checkout. Its status is recorded under
`out/realism/finish-status.json`. It never creates videos or presentations.

## Render-seed regression and replacement candidate

The v9 full run failed V1 on native and secondary Blender. The appearance
builder accidentally assigned its geometry/groom seed (20261108) to Cycles;
the unchanged verifier requires the renderer seed to remain 0. All other native
checks passed, including directions, visibility and extracted-archive replay.
V9 is not qualified. Its earlier image/sample reviews describe that rejected
checkpoint and cannot qualify the replacement candidate.

The builder now keeps the grooming seed separate and uses render seed 0. Before
rendering the center image it executes tools/scene_preflight.py, which extracts
and runs the exact existing V1/V2 verifier functions without duplicating or
relaxing their rules. The old v9 scene fails this quick check at the seed
assertion; the replacement passes both checks. Full V1–V17 is still required.

Replacement evidence is isolated under out/realism/seed-zero. The original
failed evidence stays under out/realism. All replacement sample renders, review
bindings, qualification, datasets and archive rehearsals must be regenerated;
old image hashes and ratings must not be relabelled as replacement evidence.
Use tools/finish_realism.py --out out/realism/seed-zero --publish only after the
replacement reviews exist and its qualification/checkpoint workers are running.

## Replacement early evidence

The render-seed-zero replacement scene SHA-256 is
450bd7a7f03dff6c267e339eb8311912a6e8c375e5026bdfcdb51619bd3f8db5.
Exact V1/V2 configuration preflight, all five direction/reset checks, nine-anchor
blind/template image checks and actual mask checks pass. Reset is byte-identical;
maximum direction template error is 0.074464 px. Nine-anchor blind error is at
most 0.215781 px; all nine masks retain full visible/dark pupil coverage and
reject the real half-pupil obstruction. All 80 native unit tests pass.

All nine new 32/64/128 renders were individually inspected. Retain 32 samples:
three-pose means are about 63, 126 and 269 seconds. The 32-to-128 luma difference
is about 0.383/255 overall and 0.186/255 in the documented forehead ROI. The
independent guided pupil check passes all nine (maximum error 0.194831 px).
These are engineering measurements, not naturalness scores. New scene/image-
bound reviews cover the three matched sheets, all nine eye rows and both new
portrait views. No old v9 review was relabelled as replacement evidence.

Review cumulative anatomy/surface/finished construction stills before starting
the long qualification batch. Intermediate stages remain unqualified. Final
export also requires an image-bound construction review. Videos and decks stay
excluded; only passing technical evidence may receive apollo-v0.3.0.
