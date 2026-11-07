# Competition upgrade operator guide

The protected development fallback is `dev-freeze-2026-11-07`. Upgrade work lives
on `competition-upgrade`. Read the execution record for actual completed gates;
this guide describes commands, not a claim that every output already exists.

## Native prerequisites

Install the pinned tools with `python -m pip install -r requirements.txt`.
Set `BLENDER_BIN` to Blender 4.5 LTS and `BLENDER_SECONDARY_BIN` to the separately
installed Blender 5.2 LTS executable. `python tasks.py doctor` reports discovery.
Rendering a packed scene does not require MPFB. Building the character/look does.

For the selected look, use a disposable Blender process with MPFB enabled:

```powershell
& $env:BLENDER_BIN -b out/production/scene.blend --python-exit-code 1 -P build/upgrade_looks.py -- --folder out/rebuilt-look --variant B --optimized
```

The builder changes iris materials, lid targets and lash fit, and sets two total
path bounces with one diffuse/glossy bounce. It never changes physical pupil
size, eye centers, fixation/camera distances or the gaze solver. Use a separate
output directory. Do not rebuild over a qualified scene.

## Qualification

```powershell
python -m pytest -q
python tasks.py sweep --folder out/upgrade/candidate --quality draft
python tasks.py validate --folder out/upgrade/candidate
python tasks.py sheet --folder out/upgrade/candidate
python tasks.py prepare --folder out/upgrade/candidate
python tasks.py verify --folder out/upgrade/candidate
```

All V1–V17 checks must pass, including the full applicable secondary-runtime
suite. Source or input changes during the run invalidate it. Evidence reuse and
packaging reject missing/changed provenance. Historical reports are not upgraded
by relabelling them. Do not edit verifier sources during a running qualification.

## Dataset and adversarial checks

Install `requirements-research.txt` for coverage plots. Keep dataset output
separate from the source scene. Repeat the exact generation command to resume.

```powershell
python tasks.py dataset --scene out/upgrade/candidate/scene.blend --folder out/upgrade/dataset-256 --count 256 --seed 0
python tools/analyze_dataset.py out/upgrade/dataset-256
& $env:BLENDER_BIN -b --factory-startup out/upgrade/candidate/scene.blend --python-exit-code 1 -P tools/visibility_audit.py -- --dataset out/upgrade/dataset-256 --folder out/upgrade/dataset-visibility --count 25
python tools/analyze_visibility.py out/upgrade/dataset-visibility
& $env:BLENDER_BIN -b --factory-startup out/upgrade/candidate/scene.blend --python-exit-code 1 -P tools/lighting_adversary.py -- --folder out/upgrade/lighting-adversary
```

The first 25 visibility poses contain nine square anchors and sixteen seeded
random poses. A real half-pupil occluder must fail. The lighting adversary renders
a loss-of-illumination fault and requires both signature and pixel rejection.
These finite checks do not establish universal robustness or ML accuracy.
The official ten-frame schema stays unchanged; research data uses its own
`apollo.dataset/1` manifest. Images are hashed; progress is atomic.

## Optional Blender controls

Open a calibrated scene. Run `tools/live_controls.py` in Blender's Text Editor.
The Apollo sidebar provides normalized sliders, cardinal/reset buttons, pose
render and official sweep. Use a separate output folder. This optional panel is
not enabled or needed in the evaluator's `.blend` file.

```powershell
& $env:BLENDER_BIN -b --factory-startup out/upgrade/candidate/scene.blend --python-exit-code 1 -P tools/ui_rehearsal.py -- --folder out/upgrade/ui/operator-rehearsal
python tools/validate_metadata.py out/upgrade/ui/operator-rehearsal/sweep
```

The rehearsal invokes actual Blender operators and compares the pose render to
the public API byte-for-byte. Interactive tests supplement this; an automated
rehearsal is never described as an independent human usability study.

## Linux

`python tasks.py docker` builds the current source. Mount the repository read-only
and a separate writable output directory for runs. The default Dockerfile supplies
the primary Blender runtime. A full cross-version Linux run additionally needs
the official Linux Blender 5.2 LTS distribution, extracted to a separate path;
pass it as `--secondary` to `tools/verify.py`. With no secondary runtime, V16 is
NOT RUN and the report cannot be called a full pass. Never substitute the Windows
secondary executable inside Linux.

## Presentation and demo

The deck uses `tools/build_presentation.mjs` and `@oai/artifact-tool` in Node.
It is editable, uses actual scene images, and reads measured JSON reports.
Supply `out/upgrade/identity.json` with `team` and `members` only when known;
otherwise it is explicitly a technical prototype, with no invented identity.
Render every slide, inspect it, and run the presentation package/layout checks.
The exact event filename depends on the registered college/team name.

Install `requirements-media.txt`, then:

```powershell
python tools/build_demo_video.py out/upgrade --out out/upgrade/video
```

The video builder requires passing native, dataset and visibility evidence.
It creates a 105-second edited demonstration with local Windows SAPI synthesized
narration. It does not imply real-time render speed or a human speaker's voice.
Inspect decoded frames, actual duration and the audio stream before delivery.

## Freeze and extraction rehearsal

```powershell
python tools/freeze_candidate.py out/upgrade/candidate --out out/upgrade/apollo-competition.zip
python tools/release_rehearsal.py --blender $env:BLENDER_BIN --archive out/upgrade/apollo-competition.zip --dataset out/upgrade/dataset-256 --scene out/upgrade/candidate/scene.blend --out out/upgrade/release-rehearsal.json
```

The rehearsal regenerates the actual extracted archive from another working
directory with fresh user configuration. It also tests a completed 256-frame
resume and a real interrupted 255→256 reconstruction. PNGs and manifests must
match. Preserve the original fallback unchanged. Tag exact passing inputs only.

Registration, organizer forms, team identity and public upload links remain
team-owned. No local verifier result is an official competition score.
