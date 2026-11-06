# End-to-end operation and human handoff

## Before character delivery

1. Install Blender 4.5 LTS and set BLENDER_BIN to the absolute executable path.
2. Install Blender 5.2 LTS separately and set BLENDER_SECONDARY_BIN for release verification.
3. Use a Python 3.10+ virtual environment and install requirements.txt.
4. Run `python tasks.py all` for the fixture pipeline. No character is required.

The all command runs tests, synchronizes core, builds the scene, sweeps, validates,
generates sheet/candidate docs/demo, and verifies. It stops with nonzero status on
any failure or missing qualification check. Fixture artifacts remain labeled and
cannot be packaged as a production submission.

Example PowerShell (replace the executable locations with actual installations):

```powershell
$env:BLENDER_BIN = 'C:\path\to\Blender4.5\blender.exe'
$env:BLENDER_SECONDARY_BIN = 'C:\path\to\Blender5.2\blender.exe'
python tasks.py all
```

## Character handoff

Save the textured MPFB character as assets/base_character.blend. It must face -Y,
use meter-scale geometry, have roughly 58–68 mm eye spacing, and retain textures.
Original rigging, brows, lashes, and skin are preserved; procedural eye meshes are
bound to a dedicated eye armature. Imported stock eyes are hidden from rendering.

Run:

```powershell
python tasks.py inspect --source assets/base_character.blend --folder out/production
```

Review out/production/inspect.json. Copy docs/character_mapping.example.json into
assets/character_mapping.json and replace the two stock-eye mesh identifiers and
asset attribution. L means the subject's anatomical left (world +X). Confirm the
orientation field only after checking the asset. If eye meshes contain asymmetrical
accessories, bounding-box centers need manual source correction before integration.

Build and run:

```powershell
python tasks.py all --production --mapping assets/character_mapping.json --quality final --team College_RegisteredTeam
```

Production uses out/production by default. Supply --folder to override. The team
name is required only for the final bundle step; without it, all produces verified
candidate artifacts and leaves the registration-specific ZIP for later.

## Framing and visual review

`python tasks.py framing --folder out/production` tries 85–135 mm, renders center,
right, and up for each focal length, and selects the largest lens meeting measured
eye-sphere margin and shift requirements. It saves the changed calibration and
framing_report.json. Brows/lashes and socket fit still require visual inspection;
the numeric margin is explicitly an eye-sphere measure, not a full-face audit.
Rerun sweep, validate, sheet, prepare, demo, and verify after any scene change.

## Verification

V1–V6: calibration, eye size/pivots, 1000 evaluated random poses, convergence,
shortest-arc torsion, and Blender/analytic projection agreement.
V7–V10: pupil-mask centroid, blind ellipse and template detectors, cardinal
movement, cross-axis limits, and byte-identical reset.
V11–V14: 200 call-order sequences, repeated sweep hashes, schema, and pupil
visibility for the sweep plus cardinal/reset frames.
V15: packed textures and clean-room regeneration from another working directory.
V16: independent 5.2 LTS checks; cross-version hashes are not required to match 4.5.
V17: annotation sanity, ellipse center offset, gaze angles, and rotation limits.

A verification run is deliberately expensive: multiple full sweeps, diagnostic
masks, clean-room regeneration, and secondary-version checks. Keep draft quality
for development and run final quality for the release candidate. Reports list
PASS, FAIL, or NOT RUN. No missing evidence is counted as a pass.

Packaging checks all seventeen statuses and exact hashes of the scene, wrapper,
metadata, and official renders, then creates and reopens/extracts the ZIP. Any
post-verification changes to those artifacts require re-verification. The ZIP
contains an explanatory README and attribution; the report records provenance.

## Docker and final human actions

The Dockerfile downloads pinned Blender 4.5.15 and installs the Python tools.
It has not been built in the current environment (Docker daemon unavailable).
`python tasks.py docker` builds it when Docker and network access are available.
Use a mounted workspace for outputs. Cross-version verification additionally
requires installing/mounting the secondary Blender executable in the container.

The generated sweep.gif and PRESENTATION.md are demo source materials. Record the
100–110 second final video, export the presentation to PPT/PDF with team details,
check public/shared links, and submit via the organizer form yourself. Registration,
email, uploads, and final submission are never performed automatically.
