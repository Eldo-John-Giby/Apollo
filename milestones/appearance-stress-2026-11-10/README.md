# Full CPU appearance stress evaluation

Completed on 10 November 2026 IST using isolated commit fda66c7 and Blender
4.5.15 LTS. The exact tested scene is the packed CPU appearance candidate,
SHA-256 8acd0df98cd2581f54bf83901d56c669795c5eef14e853a378bcb18e6bf71c4d.
All RGB images were freshly rendered at 1024x1024, 32 fixed samples on CPU.

| Measurement | Result |
| --- | --- |
| Grid/random stress poses | 113/113 pass |
| Minimum visible dark pupil fraction | 0.9982608695652174 |
| Maximum actual-mask centroid residual | 0.04482052848528855 px |
| Injected half-pupil obstruction | Detected, measured fraction 0.49935601022212484 |
| Stress blind pupil error | Maximum 0.27735891861172496 px |
| Stress template error | Maximum 0.1379384871446995 px |
| Seeded corpus | 256/256 pass |
| Independent corpus pixel error | Maximum 0.15384109313465757 px |
| Corpus blind pupil error | Maximum 0.27735891861172496 px |
| Corpus template error | Maximum 0.1379384871446995 px |
| Current workspace tests after checkpoint fix | 82 passed in 10.72 seconds |

Automated completion took 1.96 hours wall time, including monitoring gaps
and recovery. Selected worst-visibility and worst-pixel-error images, anchor
overview and coverage plot were visually inspected. No obvious new pupil
obstruction or socket collision appeared in those reviewed images.

## Recoveries

The launcher initially omitted --progress for the stress manifest. It was
corrected and analysis resumed using the completed RGB/mask evidence. During
corpus checkpoint 151, Windows denied atomic replacement of progress.json.
Generation resumed from the valid 150-frame checkpoint and rerendered that
uncommitted frame. The frozen renderer/source hashes stayed constant. Both
failure records and original/corrected launcher files are included.

The main workspace now retries transient checkpoint PermissionError with bounded
backoff. Regression tests exercise successful retry and persistent failure while
preserving the previous checkpoint. This fix was tested separately from the
frozen run. Every image was analyzed under the frozen test source versions.

## Evidence locations

This folder contains reports, complete per-frame metadata, raw-file hashes,
selected native review images and the reviewed contact sheet. All 609 raw evidence
files are retained locally under out/full-test-20261109, with a ZIP at
out/full-test-20261109/apollo-appearance-stress-evidence.zip. Its size is
376,474,808 bytes and SHA-256 is
e8646d49e8c410f04b7f290de2b8cdc9cbdd0c59dc79eb2e401e79d83c7571bd.
The ZIP passed integrity checking. The large raw archive is local; the tracked
raw-evidence-manifest.json permits verification of its complete extracted files.

The reported results cover the requested native CPU appearance stress suites.
Cross-platform release qualification and independent teammate/human testing are
separate outstanding activities. Existing scene/style limitations are documented
in the candidate handoff. Reviewer scope and inspected stills are in review.json.
