# Apollo development freeze — 7 November 2026

This milestone freezes the textured radial-iris character and its verified
development pipeline. It is not an organizer submission or a claim of awarded
rubric points. Video, presentation and organizer delivery remain separate work.

## Selected settings

Cycles CPU, 1024x1024 RGB PNG, 32 samples, fixed seed, no denoising; 100 mm
horizontal-fit camera at 40 cm; fixation at 35 cm with +/-5 cm target bounds.
Both eyes rotate about physical centers and converge on the shared target.

The 32-sample setting was selected after direct comparison with a 128-sample
center render. The higher-sample image is slightly smoother; mean grayscale
difference is 0.769/255 and detected pupil centers differ by at most 0.083 px.
Direction readability is unchanged in the reviewed comparison. The already
qualified 32-sample setting balances appearance, annotation accuracy and CPU
cost. This is a documented development-quality choice, not an assertion that
the two images are identical. CLI `--quality final` still means 128 samples;
only its comparison pose was tested. Render the frozen scene without that
override to reproduce its qualified 32-sample artifacts.

The 128-sample comparison took 113.58 s with a concurrent Docker build; that is
not a controlled timing benchmark. The earlier isolated 32-sample sweep averaged
23.653 s/frame. See PERFORMANCE.md for benchmark scope and preview experiments.

## Rubric evidence

| Rubric category | Evidence |
| --- | --- |
| Calibration (20) | Metric scene audit; 1000 evaluated poses; independent projection; pixel-mask residual 0.040 px |
| Automation (20) | Absolute API; 200 call-order sequences; repeated sweep hashes; standalone clean-room regeneration; Blender 4.5.15/5.2.3 |
| Directions (40) | Both eyes pass Left/Right/Up/Down; Reset byte-identical; two blind detectors; 100% measured pupil visibility |
| Sequence/metadata (20) | Exactly ten clockwise 1024x1024 PNGs; calibrated schema/annotations; maximum blind pupil error 0.200 px |

All V1–V17 checks pass for the exact archived scene/wrapper/metadata/render
hashes. These are internal engineering checks supporting the documented rubric.
The Python suite has 60 passing tests, including stale-archive rejection and
manifest integrity. Docker build, doctor, 60 tests and one packed-scene Linux pose pass. All ten
PNGs and metadata regenerate byte-identical after archive extraction from a
different working directory. Measurements are recorded with the milestone.

## Reproducible artifact

The versioned archive and evidence are in `milestones/dev-freeze-2026-11-07/`.
Extract `apollo-development.zip`, then run from any working directory:

```powershell
blender -b --factory-startup --python-exit-code 1 -P /absolute/path/apollo-development/wrapper/eyes.py
```

Use the pinned Blender 4.5.15 build for exact native PNG/metadata hash comparison.
The archive includes packed textures and needs no MPFB addon. MANIFEST.json
contains SHA-256 hashes for every payload file. Reports bind the calibrated
scene, wrapper, metadata and official renders. Editing those requires verification.

Rebuild the scene from source with `python tasks.py production-scene --mapping
assets/character_mapping.json --look radial`. The standalone material helper is
shared by the builder and comparison workflow. Source builds require Python
requirements plus Blender; character recreation additionally needs MPFB/assets.

The archive is produced by `tools/freeze_candidate.py`; its qualification checks
are shared with the submission-bundle tool. No registered team name is invented
and no submission archive or organizer upload is performed by this milestone.

## Limits

- One static character, fixed lighting and fixed pupil size.
- Simplified non-refractive eyes; zero optical/visual axis offset.
- Exact reproducibility is scoped to the same Blender build and machine;
  secondary-version checks use their own reference images.
- Reduced 8/16-sample profiles are benchmarks, not qualified replacements.
- Docker evidence is scoped to the commands actually run, not a claim that the
  complete Windows hash qualification suite passed inside Linux.
