# Apollo CPU appearance candidate

Completed appearance implementation and reviewed development handoff, 9 November
2026, on branch `photorealism-v2`. This is a development candidate, not a release.

The final pass reduces broad skin mottling, fills and aligns the eyebrows, varies
lash spacing/length, removes flat-shading bands from the sclera, and replaces the
smooth-looking hair mass with 10,000 baked strands, five fiber tones and 250
raised overlapping locks. The earlier adult-female anatomy, relaxed mouth,
fitted lids/tear tissue, brown iris atlas and compact bun remain baked and packed.
Eye mesh positions, physical pupils, bones/pivots, camera, fixation calibration,
public API and metadata contract are preserved.

## Open or run

Open `scene.blend` with Blender 4.5.15 LTS. No MPFB, MCP, network or simulation is
needed for playback. From this folder, using a **new** output directory:

```powershell
& $env:BLENDER_BIN -b --factory-startup scene.blend --python-exit-code 1 -P wrapper/eyes.py -- --out new-output
```

The included `renders/` are ten actual native 1024x1024, 32-sample Cycles CPU PNGs;
`metadata.json` is their matching official-format metadata. Only the contact sheet
adds review annotations. No graded frame was retouched or upscaled.

## Measured validation

| Check | Result |
| --- | --- |
| Unit tests | 80 passed |
| Independent geometry | 1009 poses, all 14 injected faults detected |
| Cardinal directions/reset | Pass; fresh eyes.reset() image byte-identical to center |
| Nine representative poses | Full pupil visibility; half-pupil occlusion fault detected |
| Nine-pose blind pupil error | Maximum 0.278 px (rounded upward) |
| Official ten-frame sweep | Metadata and image validation pass; maximum blind error 0.108 px (rounded upward) |
| CPU center/up/corner | 54.59/58.03/72.55 seconds |
| Peak OS process RSS | 1,507,520,512 bytes (1.40 GiB) |
| Visible evaluated polygons | 464,088 |
| Persistent data | Center/up PNGs identical with reuse disabled; retained enabled |

Timings are single local trials, not cross-machine guarantees. The direction
check reuses only matching scene/wrapper/worker/runtime/calibration/image-hash
cardinal renders from the same nine-pose run; reset is always actually rendered
after a corner move. A stale-scene reuse rejection was also exercised. No detector
threshold was relaxed.

## Review and evidence

`evidence/refinement-comparison/` compares this result against the previous v2
checkpoint. `evidence/comparisons/` compares it with the original prerelease.
Native eye crops and all nine poses were inspected, along with front and three-
quarter portraits, neutral-light and gray-material diagnostic stills. Live MCP
front/back/three-quarter inspection checked the scalp and bun. Review notes and
image hashes are in `evidence/review.json`; technical receipts, actual masks and
rendered poses are included alongside them. `manifest.json` binds every payload
file. Attribution and original licensed source textures are tracked in the repo.

The compatible licensed albedo is genuinely 2K, not 4K. Skin color is softened in
shader space; no extra photographic detail is invented. Efficient hair locks and
non-refractive eyes retain visible CG simplifications. This completes the scoped
CPU appearance implementation; photographic equivalence, industry-grade approval
and an official rubric score are not established by these engineering checks.

## Rebuild and qualification boundary

See `../../TEAM_SETUP.md` and `../../docs/PHOTOREALISM_V2.md`. The exact source
baseline remains at `../photorealism-v2-development/baseline/scene.blend`; the
prior checkpoint is preserved. Rebuilding needs MPFB; packed playback does not.
Source/config/assets and protected eye geometry are recorded in `build.json`.
The root recipe/config are authoritative; `appearance-config.json` is the exact
configuration snapshot for this scene.

No exhaustive Windows/Linux/secondary-version release qualification, expanded
research corpus, tag, release, video, presentation, organizer submission or
repository-sharing change was started. Release selection remains a separate step.

A fresh full recipe rebuild from the tracked baseline reproduced the protected
eye hashes, evaluated geometry and native center PNG exactly. The saved blend
container hash differs, so the evidence records both containers and binds the
actual identical PNG; it does not claim byte-identical blend serialization.
The tracked-baseline comparison was also rerun and all three sheets match the
local-baseline sheets byte for byte.
