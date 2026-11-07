# Competition upgrade — execution record

Branch: competition-upgrade. Protected fallback: dev-freeze-2026-11-07.
This record describes work completed so far, not completion of the whole upgrade.
Human input budget: approximately two hours/day; laptop CPU only. Registration
and event administration are outside this workstream.

## Locked direction

Rubric reliability plus a realistic technical demonstration, seeded dataset
generation and optional Blender-native controls. No ML accuracy claims, cloud
dependency or refractive cornea in the graded path. Engineering freeze target:
16 November, delivery-ready assets on 17 November. New features stay outside
the frozen wrapper/scene until their acceptance gates pass.

## A — Independent verification: first tranche implemented

- Separate Rodrigues rotation/projection reference imports no production math.
- Fits eye centers/radii from deformed scleral vertices and computes area-weighted
  pupil centroids from actual evaluated triangles; checks the entire pupil mesh.
- 1009 poses pass: nine anchors plus 1000 deterministic random inputs.
- Fourteen injected faults detected: reversed horizontal/vertical, disabled
  motion, scaled target bounds, swapped eye labels, camera distance/lens/rotation,
  unilateral eye failure, displaced pivot, bad annotation, displaced pupil mesh,
  missing texture reference and changed lighting.
- Independent geometry-guided connected-dark-surface check shares neither
  OpenCV detector. It rejects half-pupil occlusion and displaced pupils in tests.
  It is not blind detection and does not replace the full visibility-mask suite.
- New full verification reports bind verifier code and diagnostic files.
  Reuse rejects legacy reports without provenance, altered diagnostics and changed
  verifier versions. Input/source changes during a run invalidate the result.

Evidence: out/upgrade/audit/independent.json and run.log. New provenance changes
are unit tested; a full upgraded V1–V17 qualification still needs a fresh run.
Historical freeze reports are not silently upgraded.

## B — Visual comparisons: human review pending

The first comparison in out/upgrade/looks/comparison.png was rejected by the
user because differences were imperceptible. It is not evidence of visual improvement.
Replacement comparison: out/upgrade/looks-v2/comparison.png. B/C use a smaller
colored iris region (unchanged annulus/pupil geometry), distinct warm/cool iris
materials, reduced eye-opening targets and MPFB-refitted lashes; C also changes
constant key/fill lighting. Camera/target calibration and eye geometry remain
fixed. This comparison predates the dark-iris tracker rejection described below;
the corrected B center is out/upgrade/corrected-fibers/B/center.png.
This build experiment requires MPFB loaded; packed candidates render with
factory startup and need no addon. No candidate is promoted from a center image.
Human naturalness/pupil-clarity ratings select which candidate receives complete
direction, sweep, corner-visibility and new-verifier qualification. Further socket
remodelling remains untested. Keep the fallback if variants do not
improve naturalness without reducing clarity.

## C — Dataset generator: implemented, anchor smoke verified

```powershell
python tasks.py dataset --scene out/production/scene.blend --folder out/dataset --count 256 --seed 0
python tools/analyze_dataset.py out/dataset
```

Defaults: 256 frames, seed 0, 32 samples. First nine frames are the normalized
3x3 anchors; the remainder are seeded uniform square samples. Fixed identity,
camera, pupil size and lighting. The --samples 8 option is experimental.

Official ten-frame schema remains unchanged. Dataset manifest uses
apollo.dataset/1 with run signature and frames; random records have no invented
clockwise theta. Each image is hashed, progress is atomic, source/configuration
or completed-image changes reject resume. Outputs must be separate from source.

Nine 32-sample anchor frames have actually rendered. Independent pixel maximum:
0.141464 px. Interrupted-after-eight reconstruction matches all nine PNGs and
dataset.json byte-for-byte. Evidence: out/upgrade/dataset-smoke and
out/upgrade/audit/resume.json. Coverage plot and anchor sheet are generated.

Research reporting dependencies: pip install -r requirements-research.txt.
The actual 256-frame example, sixteen fixed random pixel/mask samples and full
corner visibility qualification remain outstanding. No dataset/ML performance
claim is made from the nine-frame smoke test.

## D — Live controls: implemented, interactive checks completed

Run tools/live_controls.py in Blender's Text Editor with a calibrated scene open.
Apollo sidebar: normalized sliders, cardinal/reset buttons, distances, current
pose render and sweep into a separate demo folder. Controls invoke the existing
wrapper. No handlers, gaze constraints or alternate articulation algorithm.

Background Blender test passes API/UI parity at all nine anchors and clean
unregister/re-register cycles. Evidence: out/upgrade/audit/ui.json. The agent
clicked all five cardinal/reset buttons in the actual Blender sidebar and
rendered a pose using its render button. The existing dirty scene was preserved;
its original pose and render settings were restored without saving. Evidence:
out/upgrade/ui/sidebar.jpg and live-panel.png. A separate operator rehearsal
checks pose-render byte parity and the real sweep operator; its result is only
accepted when out/upgrade/ui/operator-rehearsal/report.json passes.
This optional UI is not enabled in the graded scene or required by the wrapper.

## Active complete-run gates

The original dark-hazel B prototype was rejected by the image-only direction
tracker: its iris joined the pupil into a dark region larger than the allowed
reference patch. Geometry/visibility passing did not override that failure.
Its 41 completed dataset frames and partial qualification are preserved under
out/upgrade/rejected-dark-iris, with rejection.json and the failed direction log.
The original fallback remains unchanged. Detector thresholds were not relaxed.

The corrected B raises iris reflectance while retaining its fiber pattern,
reduced colored region and refitted lashes. Two path bounces, one diffuse/glossy
bounce and persistent render data are used in the new candidate; those settings
must pass fresh qualification. Earlier 0.058/255 optimization comparison data
belongs to the rejected dark prototype, not the corrected candidate. Human
naturalness preference is not fabricated.

The rejected prototype passed all nine dataset anchor mask tests: full visibility,
maximum independent mask-centroid error 0.030619 px. An actual injected half-pupil
obstruction measured 0.499356 coverage and was rejected. Evidence:
out/upgrade/rejected-dark-iris/corner-visibility/report.json. The 25-pose extension also passed:
nine anchors plus sixteen fixed seeded random poses, minimum visible/dark fraction
1.0, maximum mask-centroid error 0.030619 px and the same obstructed-pupil rejection.
Evidence: out/upgrade/rejected-dark-iris/dataset-visibility/report.json. A rendered loss-of-illumination
fault was rejected by both the lighting signature and the pixel oracle; see
out/upgrade/rejected-dark-iris/lighting-adversary/report.json.

These mask/lighting results belong to that prototype and are not transferred
to the corrected scene. Corrected B passes the real five-direction/reset check:
reset byte-identical, maximum template/projection error 0.050578 px. Evidence:
out/upgrade/corrected-fibers-smoke/verification/direction_report.json. Builder
and factory-startup center PNGs also match byte-for-byte before enabling the
render cache. The new full sweep receives early blind/template checks before
long jobs. The count-256 dataset is intentionally interrupted after its first
nine completed anchors, checked with actual pixels/masks, then resumed.

Fresh corrected-scene 256-frame, seed-0, 32-sample generation and complete
native/secondary/Linux qualification are gated on those preflights. No pending
result is a pass. The editable evidence deck has passed structural/layout/font
and import checks, and PowerPoint exported all ten preview slides. Final claims
are rebuilt from final reports. The 105-second demo builder requires completed
passing evidence before export; its local synthesized narration passes timing.
Team identity is requested separately and never invented.

## Remaining gates and order

1. Complete the verifier coverage review, image/lighting adversarial cases and
   fresh full qualification under new provenance; retain old failure evidence.
2. Review visual candidates; qualify the selected look before adoption.
3. Validate the actual 256-frame dataset and live interaction, not just smoke tests.
4. Prepare the 100–110 second demo and required deck, with claims linked to
   measured evidence and honest limitations; human review before final export.
5. Run unfamiliar-user/different-CWD/container/extracted-archive rehearsals;
   bind the final reports and tag only the exact passing artifacts.

Priority on schedule slip: correctness/delivery, visual clarity, dataset, controls,
extra polish. No new features after 15 November. Dataset generation and visual
experiments do not run as competing performance benchmarks.
