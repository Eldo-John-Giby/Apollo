# Apollo

Synthetic binocular gaze pipeline for Samsung PRISM-XR Track 01.

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

51 pytest tests pass in the current Python 3.10.7 / NumPy 1.26.4 environment.
Coverage includes reference geometry, invalid inputs/metadata, exact conic boundary,
standalone core synchronization, image artifacts, contact sheet, detector subpixel
accuracy on synthetic images, and missing-runtime/report behavior.

Blender 4.5.15 LTS is now installed at C:\Program Files\Blender Foundation\Blender 4.5\blender.exe. Earlier, the environment denied network
socket access for downloading it. The Docker executable exists, but its daemon
is unavailable. The fixture builder and a single-pose render now run successfully; the Dockerfile has
not been executed here. The ten-frame fixture sweep, metadata validation, contact sheet
and GIF now succeed; a textured production scene also builds. Full V1–V17
verification and a submission ZIP remain pending. Tests use synthetic images, not Blender
renders. Missing runtime reports explicitly remain NOT RUN/FAIL.

The MPFB textured assets/base_character.blend and character_mapping.json now exist.
The production scene builds and an initial 100-pose check passes. Ten draft
production frames validate; maximum blind pupil-detector residual is 0.171 px
across all twenty pupils. Contact sheet and GIF are in out/production.
Full V1–V17 production verification remains pending.
There are no automatic
emails, publication, uploads, or organizer submissions. Optional dataset/live-aim/
refraction experiments are deferred until a verified submission candidate exists.



