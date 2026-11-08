# Apollo

Synthetic binocular gaze pipeline for Samsung PRISM-XR Track 01.

Joining the team? Start with [TEAM_SETUP.md](TEAM_SETUP.md).

The earlier realism phase is preserved as the [v0.3.0-rc.1 prerelease](https://github.com/Eldo-John-Giby/Apollo/releases/tag/apollo-v0.3.0-rc.1).
See [the handoff](docs/PHASE_HANDOFF.md) for completed/deferred checks and preserved working files.

Standing project rule: do not create videos or presentations. Technical work and
still-image evidence continue. See [release versions](docs/RELEASES.md).

The completed CPU appearance upgrade is integrated into `main`; see [its execution record](docs/PHOTOREALISM_V2.md).
The `photorealism-v2` branch preserves its development history.
The packed development candidate and still-image evidence are in
[milestones/photorealism-v2-candidate](milestones/photorealism-v2-candidate/README.md).
Those development checkpoints are not qualified releases. The complete protected
competition release described below remains available unchanged.

The qualified upgrade is developed on `competition-upgrade`. The protected
`apollo-v0.1.0` development baseline remains unchanged. See the
[execution record](docs/UPGRADE_PROGRESS.md), [reproduction runbook](docs/UPGRADE_RUNBOOK.md)
and [verifier coverage](docs/VERIFIER_COVERAGE.md).

The selected scene has warm fiber-patterned irises, refitted lids/lashes and
32-sample rendering. Native Blender 4.5.15 qualification passes all V1–V17,
including the complete applicable Blender 5.2.3 suite. The 256-frame seeded
dataset, 25-pose visibility checks, actual UI operators, extracted-archive
regeneration and interrupted dataset resume pass. The 105-second narrated video
and editable ten-slide deck have been built and visually reviewed.
Full Linux V1–V17 qualification also passes, including its applicable 5.2 suite.
The [technical release](milestones/competition-upgrade-2026-11-07/README.md) contains
the complete reports, [demo](milestones/competition-upgrade-2026-11-07/apollo-demo.mp4),
[deck](milestones/competition-upgrade-2026-11-07/Apollo_Submission_ppt.pptx) and research corpus.
Use [delivery/apollo](delivery/apollo/README.md) for the conventional executable layout.
These measurements are local engineering checks, not official rubric scores.

The earlier development pipeline below builds the original radial appearance.
Use [the upgrade recipe](docs/UPGRADE_RUNBOOK.md) to rebuild the selected look.
`--quality final` in the older pipeline means 128 samples; the qualified upgrade
uses its separately measured 32-sample settings.

## Run the complete development pipeline

Install requirements.txt in an isolated Python 3.10+ environment. Set BLENDER_BIN
to Blender 4.5 LTS and BLENDER_SECONDARY_BIN to Blender 5.2 LTS.

```powershell
python tasks.py test
python tasks.py doctor
python tasks.py all
```

The pipeline creates a clearly labeled articulated development fixture, renders
ten clockwise frames, validates metadata/images, exports an annotated contact
sheet and GIF, and runs V1–V17 verification. Fixture outputs cannot be submitted.
The all command stops on failure or missing qualification evidence.

## Integrate the real character

```powershell
python tasks.py inspect --source assets/base_character.blend --folder out/production
python tasks.py all --production --mapping assets/character_mapping.json --quality final --team College_RegisteredTeam
```

Use the inspected stock-eye mesh names to fill the mapping example under docs/;
include verified attribution. The production builder preserves the textured face
and its original rig, normalizes the eye midpoint, hides stock eyes, and uses a
dedicated articulated eye rig. It rejects invalid scale, alignment, and placeholders.
Eye/socket fit, brows/lashes, skin appearance, and framing need visual review.

Read [the full runbook](docs/RUNBOOK.md) for setup, calibration, mapping, framing,
verification, Docker, packaging, and the human submission checklist.

## Commands

- test / doctor / sync: tests, environment diagnostics, embedded-core sync.
- inspect / scene / production-scene: character inventory or scene building.
- sweep / framing: official protocol or measured framing experiment.
- validate / sheet / prepare / demo: validate artifacts, contact sheet, candidate README/attribution, GIF/presentation outline.
- verify / bundle: measured reports and production ZIP with provenance checks.
- all / docker: ordered pipeline or container build.

Use --folder to select an artifact directory. Production defaults to out/production;
fixtures default to out/fixture. Bundle requires the actual --team name. Set
--quality final for 128 samples; draft uses 32. Wrapper commands are self-contained
and support importable move/reset/render/sweep/state/calibration functions.

## Geometry and guarantees

Meters; subject faces -Y, up +Z. Camera (0,-0.400,0); target
(0.05h,-0.350,0.05v). Anatomical L is image right. Positive h is image right,
positive v is image up. Pixels use a top-left origin; rotations are world-relative
XYZ Euler in radians. reset() converges on the centered target. Movement is
absolute and finite inputs are clamped to [-1,1].

Analytic pupil positions are checked against evaluated Blender transforms and
projection before records are accepted. Pupil ellipse annotations use a projected
conic. Sweep metadata is replaced atomically only after all frames succeed; stale
manifests are removed at regeneration start.

## Current validation evidence

79 Python tests pass on Windows and Linux. The exact selected scene SHA-256 is
`3fdc93632a84011cc78c3210e703ad0f6653fcef68375d21a741af76b951605d`.
Its independent audit covers 1009 actual deformed geometry poses and detects
14 injected faults. All five directions/reset pass. Official sweep blind/template
maximum errors are 0.175464/0.061253 px. The separate 256-image pixel check
has maximum error 0.217847 px; the 25-pose mask residual is at most 0.030619 px
with full visible/dark coverage. A real half-pupil obstruction and lighting-loss
render are rejected. These finite checks do not establish human naturalness,
universal detector robustness or downstream gaze-estimator accuracy.

The actual development ZIP regenerates all ten PNGs and metadata identically
from a clean configuration and different working directory. Completed and
interrupted 255-to-256 dataset resumes preserve all image and manifest bytes.
The scene rebuild produces an identical center PNG, without claiming identical
binary `.blend` saves. See [the original freeze](milestones/dev-freeze-2026-11-07/README.md)
for historical measurements; those are not substituted for new qualification.

The demo uses local synthesized narration and edited actual artifacts. It does
not represent real-time rendering speed. Team identity, final event filenames,
repository sharing and organizer uploads remain team-owned. No organizer
submission has been performed.
