# GNM technical submission quickstart

Use the tested Blender **4.5.15 LTS** build. The packed scenes render with
Cycles CPU; no GPU, MPFB add-on or Google model installation is needed for
runtime. Python 3.10 or newer launches the bundled runner.

Download and extract the technical ZIP from the selected Apollo prerelease.
For a split release, download every numbered part and the supplied
reassemble-gnm.py, then run `python reassemble-gnm.py` before extraction.
Keep the extracted directory structure intact. Run these commands there:

```powershell
$blenderPath = 'C:/Program Files/Blender Foundation/Blender 4.5/blender.exe'
python tools/gnm_run.py still --variant rose-brown --blender $blenderPath --out renders/rose-brown.png
python tools/gnm_run.py left --blender $blenderPath --out renders/left --first 1 --last 3
python tools/gnm_run.py right --blender $blenderPath --out renders/right --first 1 --last 3
python tools/gnm_run.py generate-motion --blender $blenderPath --out renders/generate-motion --first 1 --last 3
```

Remove `--first` and `--last` to render all 192 frames. Repeating the same
command resumes and repairs missing or corrupt frames. Use a separate output
directory for each mode, variant and layout. All runner invocations enable
Blender offline mode. Non-default motion variants pack a local scene cache
under their output directory, with a hash receipt checked on resume.

Available variants are rose-brown, golden-hazel, olive-amber, neutral-deep and
cool-grey. Both still and motion commands accept `--variant` and
`--layout udim|legacy`. Left and Right refer to the viewer's screen.

| Included output | Location and settings |
| --- | --- |
| Five judging stills and a labeled contact sheet | `stills/` |
| Five face-and-eye color sets | `textures/<variant>/`, 4K skin 1001, 1K anatomical left eye interior 1002, 1K anatomical right eye interior 1004; optional 4K roughness and 16-bit height for the detailed candidate |
| Three packed, playable timelines | `timelines/<mode>/expression.blend`, frames 1–192 at 24 fps |
| Three complete numbered PNG sequences | `timelines/<mode>/frames/`, 1024 × 1024, 32 Cycles CPU samples, 8 seconds per sequence |
| Eye details, UV-layout comparisons and blink sheet | `evidence/` |
| Per-file checksums and render settings | `manifest.json` and each frame directory's `render-receipt.json` |
| Native template, original topology and both UV layouts | `model/` |
| Model license and texture provenance | `licenses/` and the included attribution documents under `assets/` |

Open a packed timeline and play frames 1–192 to inspect the animation.
For media capture, use the three included PNG sequences and the 24 fps frame
rate above. Video creation and the official presentation remain team work.

The tested target is pinned public Google GNM Head v3. Organizer confirmation
of the evaluator's exact mesh and UVs remains outstanding. The scan candidate
uses sRGB color for tiles 1001, 1002 and 1004. Apply the optional skin roughness
and 16-bit height images as Non-Color data on tile 1001. Use height as bump
with a 0.09 mm distance and 0.65 strength. Corneal reflections come from the
separate native corneal material. See SCORE_IMPROVEMENT.md for evidence and
the separately released MakeHuman fallback for the alternate target.

For source acquisition, texture rebuilding and clean-extraction qualification,
see [GNM integration](GNM_INTEGRATION.md). The technical package's license
and attribution files must remain with redistributed assets.

The detailed candidate's packed timelines store relative image and output
paths. Alternate-variant caches preserve packed image bytes and use relative
filenames as well. The verifier checks both image paths and packed-file paths;
runtime rendering does not require the author's development directories.
