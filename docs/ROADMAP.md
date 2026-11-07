# Apollo development roadmap

Updated 7 November 2026. Objective: maximize the documented 100-point rubric
through visible correctness, reliable automation and reproducible evidence.
This is the current execution roadmap; IMPLEMENTATION_PLAN.md remains the
original design/reference plan. We are developing locally, not submitting now.

## Score targets and current evidence

The rubric below comes from the supplied slide transcription in
problem_statement.md, section 2.8. No points are claimed as awarded.

| Category | Weight | Evidence already available | Remaining proof |
| --- | ---: | --- | --- |
| Direction pass/fail | 40 | Actual cardinal/reset checks, two detectors, exact reset, reviewed sequence | Organizer evaluation; human naturalness preference unmeasured |
| Calibration | 20 | Full scene audit; 1009 independent deformed-geometry poses; 25 mask-tested dataset poses | Organizer-specific measurement method remains unspecified |
| Automation | 20 | Standalone wrapper; 79 tests; repeated hashes; clean-CWD archive reconstruction; dataset resume | Native/Linux primary and full applicable secondary suites pass; organizer timing criteria unspecified |
| Sequence and metadata | 20 | Ten 1024x1024 PNGs; clockwise inputs; schema/projection/pixel checks; artifact hashes | Technical release and checksums complete; organizer evaluation remains external |

V1–V17, detector tolerances, the 60 MiB budget and render-time targets are our
engineering checks, not additional official scoring categories. The official
transcription says all five direction checks must pass; exact scoring deductions
and evaluator implementation are unknown. Research/spec guesses are not rules.

## Execution order and gates

### M0 — Working development baseline: achieved

- Packed textured MPFB character, default rig, brows/lashes and mapped stock eyes.
- Dedicated replacement eye rig, true 3D rotation and binocular target fixation.
- Ten draft production renders, metadata, contact sheet and GIF.
- Initial geometry and blind-detector evidence; baseline pushed as c3a5086.
- Full verification remains unproven. Keep this baseline available for rollback.

### M1 — Prove all five directions: achieved on the draft character

Measured 6 November: both detectors pass all four cardinal directions; reset
PNG is byte-identical to baseline. Maximum cross-axis error 0.089 px; template
displacement/annotation residual below 0.04 px. Enlarged comparison reviewed.
Evidence: out/production/verification/direction_report.md and directions.png.
Fixed stationary-lid template bias and variable PNG text metadata; scene unchanged.

1. Render a center baseline and Left, Right, Up, Down, Reset through the public API.
2. Measure both eyes using blind ellipse fitting and template displacement.
3. Inspect full images and eye crops for direction, lid/lash interference,
   socket gaps, pupil clipping and readable motion at normal viewing size.
4. Verify reset reproduces the baseline PNG exactly on this Blender build.
5. Save a labeled five-direction comparison with measurements and failures.

Gate: all five visually correct; both detectors agree; cardinal displacement
at least 8 px, cross-axis movement below 0.5 px, template error below 1.5 px.
These are internal margins. A visible direction failure blocks all polish work.
If the verifier fails, inspect images and geometry before changing the test.

### M2 — Establish the complete correctness baseline: in progress

Measured: V1–V15 and V17 PASS; V16 NOT RUN (secondary runtime not configured).
Maximum mask centroid residual 0.039657 px; visible/dark pupil fraction 1.0.
Two repeated sweeps and standalone clean-room regeneration match byte-for-byte.
Evidence: out/production/verification_report.md and verification_report.json.

1. Run full primary-Blender verification on the current draft candidate.
2. Audit metric units, camera at 40 cm, fixation plane at 35 cm, +/-5 cm bounds,
   physical pivots, static lighting and exactly ten 1024x1024 PNGs.
3. Run 1000 evaluated poses, projection parity, 200 call-order sequences,
   two repeated sweeps, annotation checks and texture-resource checks.
4. Render unoccluded and occluded pupil masks; compare projections to pixels.
5. Regenerate from an isolated directory with no MPFB/addon dependency.
6. Triage every failure as scene, wrapper, annotation, detector, verifier or
   environment; fix the underlying cause and retain failure evidence.

Gate: V1–V15 and V17 PASS on the primary Blender; V16 explicitly pending if no
supported secondary runtime is installed. Pixel-mask residual below 0.5 px
(aim below 0.2), blind residual below 1 px, visible/dark pupil fraction at least
98%, repeated sweeps and clean-room regeneration byte-identical on the same build.
No status is silently promoted from NOT RUN to PASS.

### M3 — Improve visual clarity without breaking geometry

7 November: radial iris candidate created in out/polish-iris-clear. Five-direction
checks pass; maximum cardinal pupil error 0.159424 px, template displacement
error 0.042945 px, reset byte-identical. First darker variant rejected at
1.168 px pupil error. Comparison: out/polish-iris-clear/comparison.png.
Qualified and promoted 7 November: V1–V15 and V17 PASS; V16 NOT RUN.
Current scene/renders/report: out/production. Flat-eye baseline preserved in
out/verified-flat-20261107. Full sweep blind error 0.200 px, mask error 0.040 px,
visibility 100%; repeats and clean-room outputs byte-identical.
Kept 100 mm framing: measured brow margin 8.7%, versus 2.5% at 115 mm and
cropping at 130 mm. Source rebuild center render matches the candidate exactly.

1. Work on a copy of the measured baseline. Compare candidate looks side by side.
2. Choose framing for clear motion, visible brows/lashes and sufficient margins.
   Pre-screen lens choices analytically, then render a small shortlist. The
   existing full framing command costs 33 renders and measures eye bounds only.
3. Improve flat iris appearance with restrained procedural color/texture detail;
   retain a clear pupil boundary and calibrated pupil plane/radius.
4. Tune sclera shading, socket fit and skin/light balance while keeping lighting
   identical across poses. Avoid highlights over pupils and excessive eye opening.
5. Review center, all cardinal directions and the clockwise sweep after changes.

Gate: appearance improves on side-by-side review, M1 still passes, pupils remain
visible and detection/annotation margins do not regress. Rerun affected checks
after each change and full verification after selecting the final look.
Do not change camera distance or target bounds to exaggerate movement.

### M4 — Reproducibility and performance: completed for the development milestone

7 November: V16 PASS on checksum-verified portable Blender 5.2.3 LTS.
Primary report now passes all seventeen checks. Secondary directions, masks,
repeated hashes and clean-room regeneration also pass. Evidence retained under
out/production/verification/secondary_report.json and secondary_reference/.
Eight/16-sample center/up/down benchmarks average 5.094/12.896 s, compared
with the qualified 32-sample sweep at 23.653 s. Preview settings not promoted.
Docker was initially unavailable. User started Desktop; image build, doctor,
60 tests and a Linux packed-scene center render now pass. Full Linux V1–V17
qualification is not claimed.
See PERFORMANCE.md for measured scope, noise and reproduction details.

1. Record actual scene load, per-frame and sweep times, hardware, samples and memory.
2. Profile the expensive part before optimizing. Compare lower-cost materials,
   geometry and sample settings using direction and annotation checks.
3. Test a secondary Blender version that actually exists and is supported.
   The planned 5.2 LTS exists and 5.2.3 has now been tested.
4. Build/test Docker when its daemon is available. Document observed limitations.
5. Resolve internal release-policy conflicts explicitly: the original plan allows
   dropping secondary-version testing, but current packaging requires all V1–V17.
   Keep the gate unchanged unless a deliberate documented decision is made.

Gate: reproducible standalone regeneration, actual timing table, no hidden addon
or absolute-path dependency, compatibility results accurately recorded.
Original performance aspirations (draft <=5 s/frame, final <=30 s/frame on eight
cores) are stretch targets, not verified organizer limits or current achievements.

### M5 — Freeze a polished, evidenced development candidate: achieved

7 November freeze selects the qualified 32-sample scene after a 128-sample
center comparison (mean grayscale difference 0.769/255; pupil-center difference
0.083 px). All V1–V17 remain PASS for those exact artifacts. The development ZIP
passes manifest/integrity/extraction checks; all ten PNGs and metadata reproduce
byte-identical from a different working directory. 60 tests pass. Versioned ZIP,
reports and checksums are in milestones/dev-freeze-2026-11-07/.

1. Produce final-quality renders using settings justified by visual comparison.
2. Run the complete required verification against those exact artifacts.
3. Regenerate contact sheet, GIF, README and a concise rubric-to-evidence table.
4. Test local archive/extraction and reconstruction when the candidate is ready.
5. Commit/tag a reproducible milestone; preserve measurements and artifact hashes.

Gate: selected look, complete evidence, documented limitations and reproducibility.
Recording a final video, exporting slides, publishing links and organizer
submission are later activities, performed when requested.

## Scope and tracking rules

- Finish M1 and M2 before optional features. M3 changes require revalidation.
- No dataset expansion, live aiming, refraction or eye-system replacement unless
  it solves a measured rubric problem or all core milestones are secure.
- Never trade direction/visibility/calibration for appearance or speed.
- Do not equate tests passing with a predicted competition score.
- Each work session reports milestone, change, evidence, remaining failure and
  next action. Update this roadmap when a gate is actually achieved.
- Establish a scorecard after M2: PASS / FAIL / NOT RUN, artifact path, measurement,
  runtime version and hashes. Keep historical evidence separate from current runs.
- Organizer ambiguities (runtime/version, JSON expectations, naming and limits)
  remain unresolved until confirmed from supplied official material or organizers.

M0–M5 remain protected in the original development freeze. The subsequent
competition upgrade implements independent verification, a qualified appearance,
the complete 256-image research corpus, Blender controls, and reviewed video/deck.
Archive regeneration and interrupted resume pass. Full Linux qualification and technical release export pass. The exact release
is preserved under milestones/competition-upgrade-2026-11-07 with conventional
execution layout under delivery/apollo. See
[the execution record](UPGRADE_PROGRESS.md) and [reproduction commands](UPGRADE_RUNBOOK.md).
Organizer submission remains outside the technical workstream.
