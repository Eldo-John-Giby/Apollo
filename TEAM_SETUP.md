# Teammate setup and development

Start here when joining Apollo (Samsung XR Track 01). Commands below use Windows
PowerShell from the repository root. Read AGENTS.md and FILEMAP.md before editing.
Older runbooks contain historical workflows; this guide identifies the current
starting point. Do not create videos or presentations, including through agents.

## 1. Get the repository

Ask the repo owner for GitHub collaborator access first; the repository is private.
Install Git and authenticate with your own GitHub account (Git Credential Manager
or GitHub CLI). Never share tokens or copy another teammate's credentials.

```powershell
git clone --branch visual-realism https://github.com/Eldo-John-Giby/Apollo.git
cd Apollo
git switch -c teammate/your-name-your-task
```

Current development branch: visual-realism. Qualified fallback: apollo-v0.2.0.
apollo-v0.3.0 is reserved for the realism candidate until its full qualification
passes; check docs/RELEASES.md and remote tags for its actual availability.
The clone includes packed scenes and the source character. out/ is ignored and
is NOT downloaded by Git. Do not assume another teammate's out/ paths exist.

## 2. Install Python tools

Use Python 3.10 or 3.11 for these pinned dependencies; avoid assuming the newest
Python is compatible with the pinned OpenCV/NumPy wheels. Python here runs tests
and orchestration. Blender uses its own bundled Python for bpy scripts.

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python tasks.py test
python tools/sync_core.py --check
```

If Python 3.11 is installed instead, use py -3.11 in the first command. If
PowerShell blocks activation, use .\.venv\Scripts\python.exe in place of python;
there is no need to change machine-wide execution policy. Select this virtual
environment as the interpreter in PyCharm/VS Code/your coding agent.
For research corpus analysis/plots, additionally run:

```powershell
python -m pip install -r requirements-research.txt
```

requirements-media.txt is not needed for current work. Do not run media builders.

## 3. Install Blender and configure paths

The tested primary runtime is Blender 4.5.15 LTS. Install it separately from
Blender 5.2.3 LTS, the secondary release-check runtime. Primary Blender is enough
for normal editing/rendering; install secondary when doing cross-version checks.
Set actual executable paths for YOUR machine, not paths copied from Eldo's PC.

```powershell
$env:BLENDER_BIN = 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
# Only if secondary Blender is installed at this location:
$env:BLENDER_SECONDARY_BIN = 'C:\Tools\Blender-5.2.3\blender.exe'
python tasks.py doctor
```

These variables apply to the current shell; set them again in new terminals or
configure them in your IDE's run environment. doctor can report a missing
secondary runtime/Docker during normal development; that does not prevent
primary rendering, but full release qualification requires its prerequisites.
Do not change the stored sample count with --quality final: that older preset
means 128 samples. The current realism candidate uses measured 32-sample settings.

## 4. Open the current face, without rebuilding it

The reviewed DEVELOPMENT snapshot is checked into Git at:

milestones/realism-preflight-2026-11-08/scene-preview.blend

Open it through Blender's File > Open. Save As into a new out/ folder before
editing; preserve the checked-in snapshot and qualified fallback artifacts.
This snapshot is not a qualified delivery. Its companion README and SHA256.json
record its scope. If a newer qualified delivery/realism/scene.blend exists after
a release, use its README and release tag to identify that version.

Packed scenes already include textures and baked cosmetic geometry. You do NOT
need MPFB, asset ZIP installation, Docker, or a running Blender MCP just to open
or render them. A GUI Blender window is not required for background rendering.

Render one center image (writes only to your own output location):

```powershell
New-Item -ItemType Directory -Force out/my-work | Out-Null
& $env:BLENDER_BIN -b --factory-startup milestones/realism-preflight-2026-11-08/scene-preview.blend --python-exit-code 1 -P wrapper/eyes.py -- --h 0 --v 0 --out out/my-work/center.png
```

Generate the official ten-frame clockwise sweep and validate it:

```powershell
& $env:BLENDER_BIN -b --factory-startup milestones/realism-preflight-2026-11-08/scene-preview.blend --python-exit-code 1 -P wrapper/eyes.py -- --out out/my-sweep
python tools/validate_metadata.py out/my-sweep
python tools/contact_sheet.py --help
```

A frame takes roughly a minute on the current development laptop; your hardware
will differ. Ten-frame sweeps and full qualification are substantially longer.
Always use separate output folders. The wrapper replaces output metadata during
regeneration, so do not point it at tracked release directories.

## 5. Editing Blender scenes and rebuilding the appearance

For ordinary scene editing, use the packed development scene above and save your
variant under out/. For rebuilding the appearance recipe, install MPFB 2.0.18
into Blender 4.5 and enable it. Get the official project/asset sources linked in
assets/ATTRIBUTION.md. The original setup used these CC0 packs:

- makehuman_system_assets_cc0.zip
- skins02_cc0.zip
- eyebrows01_cc0.zip
- eyelashes01_cc0.zip

Install MPFB as the add-on/extension supported by that Blender installation;
install asset packs through MPFB's asset/library installation UI. Asset pack ZIPs
are not themselves Blender add-ons. They are ignored by Git and must be obtained
separately if you rebuild. assets/base_character.blend, character_mapping.json
and ATTRIBUTION.md are already versioned; do not regenerate the base character
unless your task specifically requires it. Rendering exported scenes needs no MPFB.

Rebuild the current finished appearance into a NEW folder (MPFB must be enabled
in your normal Blender user configuration, so no --factory-startup here):

```powershell
& $env:BLENDER_BIN -b delivery/apollo/scene.blend --python-exit-code 1 -P build/realism_scene.py -- --folder out/my-realism --stage finished
```

The recipe/config are build/realism_scene.py and build/realism_config.json.
It runs the exact V1/V2 scene preflight before the center render. Groom geometry
uses seed 20261108; the renderer must keep seed 0. Do not merge those seeds.
Anatomy/surface stages are construction checkpoints, not independently qualified
releases. See docs/VISUAL_REALISM.md for the actual reviewed candidate and limits.

## 6. Daily development: keep feedback small

- Python/math changes: run relevant tests; run all unit tests before pushing.
- Core math lives in apollo_core/core.py. After changing it, run python tasks.py
  sync, then python tools/sync_core.py --check so wrapper/eyes.py stays standalone.
- Scene/material changes: render center, cardinal directions and corners in your
  own folder. Check pupil visibility, socket fit and lighting before bulk renders.
- Wrapper/calibration/randomness changes: rerun the affected geometry, direction
  and repeatability checks. Old reports do not qualify changed artifacts.
- Run full qualification/research/export only for an agreed stable candidate.

Quick cardinal/reset checks for a saved candidate:

```powershell
& $env:BLENDER_BIN -b --factory-startup out/my-realism/scene.blend --python-exit-code 1 -P tools/scene_preflight.py -- --out out/my-realism/scene-preflight.json
& $env:BLENDER_BIN -b --factory-startup out/my-realism/scene.blend --python-exit-code 1 -P tools/direction_smoke.py -- --folder out/my-directions
python tools/direction_report.py out/my-directions
```

Do not use tasks.py all as an onboarding smoke test. It runs the older fixture/
demo pipeline, includes generated media, and triggers expensive verification.
Do not run tools/finish_realism.py merely to develop: it is a release finalizer
for existing evidence and --publish can commit, tag and push.

Keep camera at 40 cm, target forward component at 35 cm, bounds at +/-5 cm,
1024x1024 PNG, static lighting, true eye-center rotations, public move/reset/render
API and the official metadata contract intact unless explicitly changing scope.
Positive h is image right; positive v is image up. See docs/problem_statement.md.

## 7. Work with coding agents and teammates

Give your agent this starting instruction:

> Read AGENTS.md, FILEMAP.md and TEAM_SETUP.md. Work on my task branch. Use the
> checked-in packed scene; do not assume out/ exists. Do not regenerate the base
> character, run a release pipeline, alter qualification thresholds, overwrite
> qualified artifacts, or create videos/presentations. Run appropriate quick
> checks, update FILEMAP.md for important responsibility changes, and commit
> completed work. Ask before expanding beyond the assigned task.

Commit source/config/docs and intentionally reviewed assets. Do not commit .venv,
caches, downloaded Blender runtimes, asset ZIPs or temporary renders under out/.
Never overwrite delivery/apollo or historical milestone checksums for experiments.

```powershell
git status
git add path/to/changed-file
git commit -m "Describe the completed change"
git push -u origin HEAD
```

Coordinate with the release owner before merging work into visual-realism while
qualification is running: source changes can invalidate evidence and the waiting
finalizer deliberately stops if its starting checkout/commit changes. Prefer
separate clones/worktrees and task branches. Do not run concurrent release jobs
on the same machine/output directories. Commit meaningful checkpoints regularly.

## 8. Docker and release work (optional for daily development)

Install/start Docker Desktop with Linux containers if doing Linux qualification.
The Dockerfile pins Blender 4.5.15 and Python dependencies. From repository root:

```powershell
python tasks.py docker
```

That builds the image; it does not by itself execute the complete Linux release
suite. Read docs/UPGRADE_RUNBOOK.md for Linux/container operations. Windows Blender
executables cannot serve as the Linux secondary runtime: install the Linux build
of Blender 5.2.3 separately in the qualification container/environment.
Full release checks cover V1-V17, secondary Blender, independent geometry,
visibility, archive replay and the research corpus. Missing checks are not passes.
Use apollo-vMAJOR.MINOR.PATCH tags and the naming in docs/RELEASES.md.
Do not run registration, submission forms or change repository sharing yourself.

## 9. Troubleshooting and where to read next

| Symptom | Action |
| --- | --- |
| Cannot clone | Confirm collaborator access and authenticate your own GitHub account. |
| bpy cannot be imported in normal Python | Run Blender scripts through Blender's executable; pip installing bpy is not the setup workflow. |
| Blender unavailable | Correct BLENDER_BIN and run tasks.py doctor in the same terminal. |
| pip wheel/dependency failures | Confirm Python 3.10/3.11, use a fresh venv and install the pinned requirements. |
| Textures/assets appear missing | Use the packed scene first; consult ATTRIBUTION.md if rebuilding asset libraries. |
| MPFB operator/module missing during build | Enable compatible MPFB in the Blender 4.5 user configuration used by the build. |
| out/ path missing | Normal on a fresh clone. Use tracked snapshots/deliveries and generate your own outputs. |
| Evidence/manifest mismatch | Preserve the original artifacts and regenerate evidence for the changed candidate; never edit hashes to force a pass. |
| Finalizer says checkout changed | Coordinate with release owner; commit legitimate changes, then deliberately restart finalization against the new clean HEAD. |

Read FILEMAP.md for navigation, docs/VISUAL_REALISM.md for current appearance work,
docs/RELEASES.md for versions, docs/UPGRADE_RUNBOOK.md for advanced qualification,
and docs/PS_AUDIT.md for requirement coverage. Historical statements in older
runbooks do not override AGENTS.md or the current no-video/no-presentation rule.

## Photorealism v2 development branch

The completed appearance work is integrated into main; photorealism-v2 preserves
its development history. See docs/PHOTOREALISM_V2.md.
Build with build/photorealism_scene.py and its separate photorealism_config.json;
use a new output folder and a Blender 4.5 configuration with MPFB enabled.
Skin/eye asset sources and license/checksum files are versioned under
assets/photorealism-v2. Saved packed scenes need no MPFB for playback.

Targeted development checks (approximately tens of minutes on the current CPU,
not a release run):

```powershell
python tools/photorealism_checks.py --scene out/my-v2/scene.blend --out out/my-v2-checks
```

The runner uses the local baseline poses when available and automatically falls
back to the tracked `milestones/photorealism-v2-development/baseline/poses` on a
fresh clone. An explicit `--baseline PATH` selects another matching pose set;
a missing baseline fails before expensive rendering.
It never runs full Windows/Linux qualification, generates the 256-image research
corpus, publishes tags, or creates videos/decks. Inspect the output stills before
accepting the candidate. CLI output and status.json report failures explicitly.

Open `milestones/photorealism-v2-candidate/scene.blend` for the packed v2
development candidate. Its README records measured checks and limitations.
To regenerate the official sweep from the repository root:

```powershell
& $env:BLENDER_BIN -b --factory-startup milestones/photorealism-v2-candidate/scene.blend --python-exit-code 1 -P wrapper/eyes.py -- --out out/teammate-v2
```

No MPFB or Blender MCP is needed for this packed-scene playback. MCP is useful
for interactive artistic iteration; MPFB is required only when rebuilding anatomy.
