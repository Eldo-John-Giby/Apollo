# Apollo

Synthetic binocular gaze pipeline for Samsung PRISM-XR Track 01.

Competition-upgrade work is isolated on `competition-upgrade`; see
[upgrade progress](docs/UPGRADE_PROGRESS.md) and [verifier coverage](docs/VERIFIER_COVERAGE.md).
The independent geometry audit, resumable dataset prototype and optional Blender
controls are implemented. Nine-frame dataset smoke and UI/API parity pass;
the complete 256-frame example and visual promotion are not yet qualified.

Current development scene uses procedural radial irises. All V1–V17 checks pass on Blender 4.5.15 with Blender 5.2.3 LTS secondary
qualification.
Artifacts and measured report are under out/production. Rebuild production with
`--look radial` (default); `--look flat` retains the original eye appearance.

See [the development roadmap](docs/ROADMAP.md) for current priorities and milestone gates.

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

60 Python tests pass. The polished 32-sample development candidate passes all
V1–V17 checks: calibration, 1000 evaluated poses, directions, pixel truth,
visibility, repeated hashes, clean-room regeneration and cross-version checks.
Primary Blender: 4.5.15 LTS; secondary: 5.2.3 LTS (official portable, checksum verified).
Reports and retained secondary evidence are under out/production/verification/.
The top-level measured report is out/production/verification_report.md.

Maximum sweep pupil error: 0.200 px; mask centroid error: 0.040 px; visibility:
100%. The isolated 8/16-sample benchmark averaged 5.094/12.896 s per frame for
center/up/down; these settings remain experimental. The qualified 32-sample
sweep averaged 23.653 s per frame. See docs/PERFORMANCE.md for scope and noise.

Docker image build, diagnostic, 60 tests and a packed-scene center render pass
in Linux; full Linux V1–V17 qualification is not claimed. M5 development freeze
is complete at 32 samples, selected after a 128-sample comparison. The exact ZIP,
reports and reconstruction evidence are in [the milestone](milestones/dev-freeze-2026-11-07/README.md).
See [the freeze rationale](docs/DEVELOPMENT_FREEZE.md) for settings and limits.
No organizer submissions or uploads are performed automatically.
