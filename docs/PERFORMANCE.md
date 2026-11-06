# Performance and compatibility evidence

Measured 7 November 2026 on an Intel Core i5-1135G7, four physical cores/eight
logical processors, Windows. Cycles CPU, 1024x1024, fixed seed, no denoising.
The qualified scene and its 32-sample settings remain unchanged.

| Samples | Scope | Mean frame time | Maximum pupil error |
| ---: | --- | ---: | ---: |
| 32 | Qualified ten-frame sweep | 23.653 s | 0.200 px |
| 16 | Isolated center/up/down benchmark | 12.896 s | 0.173 px |
| 8 | Isolated center/up/down benchmark | 5.094 s | 0.149 px |

The pose sets differ; these are practical timing observations, not a controlled
claim of a fixed speedup. The benchmark ran before secondary-version rendering.
Maximum 32-sample frame time was 25.70 s. The mean absolute grayscale difference
between benchmark center and the 32-sample center is 1.332/255 at 16 samples and
1.997/255 at 8 samples. Lower samples visibly increase grain, especially in crops.
The detector errors alone do not establish visual quality or full correctness.

Recommendation: retain 32 samples for the qualified candidate. Eight samples is
a promising iteration setting, not a qualified replacement; full directions,
visibility, repeatability and visual checks are needed before changing defaults.
The internal <=5 s draft aspiration is not met strictly by the 8-sample mean.
No organizer runtime limit is inferred from these measurements.

Reproduce the isolated benchmark (it does not save changes to scene.blend):

```powershell
& 'C:/Program Files/Blender Foundation/Blender 4.5/blender.exe' -b --factory-startup out/production/scene.blend --python-exit-code 1 -P tools/benchmark_render.py -- --folder out/performance
```

Raw timings and pose annotations: out/performance/benchmark.json.
Image measurements: out/performance/analysis.json.
Visual comparison: out/performance/comparison.png.

## Secondary runtime

Official Blender 5.2.3 LTS Windows x64 portable archive was downloaded from
https://download.blender.org/release/Blender5.2/ and checked against the official
SHA-256 manifest. Runtime prints 5.2.3 LTS, build e13b728c6880. Official release:
https://www.blender.org/releases/5-2/ .

The archive, manifest and extracted executable are under ignored out/runtimes/.
tasks.py detects that pinned local executable; BLENDER_SECONDARY_BIN overrides it.
Qualification results belong in out/production/verification_report.json and the
retained verification/secondary_report.json. Missing evidence is never a pass.

## Docker

docker info failed because the dockerDesktopLinuxEngine pipe was absent.
Automatic approval review blocked a command containing a Docker Desktop launch
with the reason "blocked by policy". No alternative launch was attempted.
The image build and container execution remain untested.

Qualification completed: primary V1–V17 PASS. Blender 5.2.3 passes its geometric,
direction, pixel, visibility, repeatability and clean-room checks. Its nested V16
is NOT RUN by design (no third runtime); the primary V16 is PASS. Secondary
reference PNGs, metadata and masks are retained in verification/secondary_reference/.

## Docker follow-up and freeze

The user started Docker Desktop on 7 November, superseding the earlier blocker.
Docker Engine 28.3.2 built apollo:dev-freeze; doctor and all 60 tests pass under
Python 3.11/Linux. The packed scene rendered through the standalone wrapper
under Linux Blender 4.5.15, with maximum center pupil error 0.079 px. The image ID
and measurements are in the versioned milestone's docker_report.json. This is
build/test/one-pose validation, not a complete Linux V1–V17 result.
M5 selected the 32-sample scene after comparing a 128-sample center render; see
DEVELOPMENT_FREEZE.md. The full native/secondary report is all-green and the
actual development ZIP was reconstructed byte-identical after extraction.
