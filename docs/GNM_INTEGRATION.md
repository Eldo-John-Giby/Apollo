# Public GNM Head v3 integration

This checkpoint targets Google Head v3 provisionally. The evaluator target is
unconfirmed. The verified MakeHuman fallback remains available as
apollo-v0.3.0-rc.2.

## Source pin

Use Blender 4.5.15 LTS and Python 3.12 for the upstream build environment.
The upstream source is google/GNM at
f84cdbdc86a34f55627526f137495f864e687679. The Head model comes from
google/gnm-v3 at revision c01e90d298d82301f9fd18f54806be751775cb7c. The
exporter downloads the pinned file if absent and verifies its SHA-256.
The source repository and model card declare Apache-2.0. The texture sources
are CC0 and credited in assets/photorealism-v2/ATTRIBUTION.md. Retain upstream
license and notices before redistributing a derived scene.

Install gnm/shape from that source revision into a Python 3.12 environment.
Example commands from the Apollo worktree:

```powershell
uv venv --python 3.12 out/gnm-env
uv pip install --python out/gnm-env/Scripts/python.exe ./out/google-gnm/gnm/shape
& out/gnm-env/Scripts/python.exe tools/gnm_template.py --model out/gnm_head.npz --out out/template
& $env:BLENDER_BIN -b --factory-startup --python-exit-code 1 -P tools/gnm_import.py -- --template out/template/template.npz --out out/template/neutral.blend
python tools/submission_variants.py generate out/variants --polished-reference
& $env:BLENDER_BIN -b --factory-startup milestones/eye-expression-2026-11-11/scene.blend --python-exit-code 1 -P tools/gnm_skin_trial.py -- --gnm out/template/neutral.blend --variant out/variants/rose-brown/variant.json --out out/raw/color.1001.png
New-Item -ItemType Directory out/trial -Force | Out-Null
python tools/gnm_skin_fill.py --template out/template/template.npz --bake out/raw/color.1001.png --out out/trial/color.1001.png
python tools/gnm_eye_maps.py --variant out/variants/rose-brown --out out/trial
foreach ($layout in 'udim','legacy') {
    & $env:BLENDER_BIN -b --factory-startup out/template/neutral.blend --python-exit-code 1 -P tools/gnm_texture_trial.py -- --maps out/trial --layout $layout --out "out/trial/$layout.png"
}
& out/gnm-env/Scripts/python.exe tools/gnm_gaze_trial.py --model out/gnm_head.npz --out out/gnm-gaze
```

## Evidence and remaining work

The neutral import preserved 17,821 vertices, 17,662 quads and both upstream
corner UV arrays exactly. The native evaluator produced bilateral pupil
movement in the expected directions for five gaze anchors. The front
renders using the two coordinate layouts differed by at most one 8-bit RGB
level. The trial samples separate images from the appropriate UDIM offsets.

The first aligned skin projection covered 65.4% of the rasterized skin UV
mask. Nearest-texel fill is for diagnosis. The maximum fill distance inside
the mask was 333 pixels at 2048 resolution, so this fails the texture
qualification gate. Fit regional correspondence before scaling to five
variants. Native blink fit, packed motion, full frame runs, archive and
publication remain pending.
