# Apollo v0.3.0 runtime setup

Apollo's stable v0.3.0 submission combines the approved v22 face and groom,
five complete texture sets and three gaze timelines. A separate texture-only
output demonstrates application to the unchanged native target. The native
target is not the replacement hero character.

Stable release `apollo-v0.3.0` includes the final technical archive and a separate
12-second demonstration supplement. The exact archives passed clean extraction,
file verification and Windows/Linux offline runtime checks; see
`milestones/v22-12-second-demonstrations-2026-11-22/qualification/final-qualification-summary.json`.
Independent human review and organizer-model compatibility remain outstanding.
Download all submission ZIP parts, `release-assets.json` and
`reassemble_release.py` into one directory, then run `python reassemble_release.py`.
Extract the resulting ZIP. The demonstration supplement can be extracted separately.

## First render from an extracted v22 runtime

Use Python 3.10 or newer and Blender 4.5.15 LTS, build `5afeabba6097`.
The launcher needs only Python's standard library. Blender supplies its own
Python and numerical runtime. No MCP connection, authoring add-on, MPFB or
separate GNM installation is needed. Keep the extracted directory intact.

The source checkout is not an extracted runtime: the runner expects `model/`,
`textures/` and `timelines/` alongside `tools/`. Download the stable v0.3.0 archive from GitHub Releases. From the extracted runtime directory on Windows:

```powershell
$blenderPath = 'C:/Program Files/Blender Foundation/Blender 4.5/blender.exe'
python tools/gnm_run.py still --blender $blenderPath --out renders/hero.png
python tools/gnm_run.py generate-motion --blender $blenderPath --out renders/motion --first 1 --last 3
```

These paths were exercised from the clean extracted submission archive,
including spaces in directory names and execution outside the project.
The still command selects the full packed character when
`model/character.blend` is present. Motion uses the saved preset: currently
1024 × 1024, 512 Cycles CPU samples. A unique pose can take tens of minutes
on the test laptop; the runner reuses verified identical holds.

Linux example, using the absolute installed Blender executable:

```bash
python3 tools/gnm_run.py generate-motion --blender /opt/blender/blender --out 'renders/motion with spaces' --first 1 --last 3
```

The final clean Linux qualification verified all 831 packaged payloads and
exercised three held neutral frames in an offline container. The Windows
qualification also exercised repair and input rejection. This is the recorded
runtime scope, rather than exhaustive cross-platform rendering of every frame.

## Modes, variants and recovery

```powershell
python tools/gnm_run.py left --blender $blenderPath --out renders/left --first 1 --last 3
python tools/gnm_run.py right --blender $blenderPath --out renders/right --first 1 --last 3
python tools/gnm_run.py generate-motion --variant olive-amber --layout legacy --blender $blenderPath --out renders/olive-legacy --first 1 --last 3
python tools/gnm_run.py still --variant cool-grey --layout udim --blender $blenderPath --out renders/cool-grey.png
```

Remove both frame limits to render all 192 frames. Left and Right use the
viewer's screen convention. The variants are `rose-brown` (approved default,
blue-grey eyes), `golden-hazel`, `olive-amber`, `neutral-deep` and `cool-grey`.
Both `udim` and `legacy` layouts are supported on the pinned target.

Keep separate output directories for different modes, variants and layouts.
Repeating a motion command preserves verified frames and repairs missing or
corrupt PNGs. Non-default variants/layouts create a packed local cache in the
output's `scene/` directory. Stale or mismatched receipts are rejected; use a
fresh output directory after changing inputs or settings. Do not edit receipts
to bypass checks. All launcher invocations enable Blender offline mode.

## Files and playback

| Runtime path | Purpose |
| --- | --- |
| `model/character.blend` | Full v22-derived character for still rendering |
| `model/neutral.blend`, `model/template.npz` | Unchanged native target and topology/UV reference |
| `textures/<variant>/` | Complete maps and hashed PBR manifest |
| `timelines/<mode>/expression.blend` | Packed 192-frame, 24 fps animation |
| `runtime-manifest.json` | Runtime file hashes and preset provenance |
| `tools/gnm_run.py` | Offline command-line entry point |

Open `expression.blend` in Blender and play frames 1–192 at 24 fps. It contains
ordinary packed Blender data. Rendered material view is necessary for appearance
inspection. The separate independent-review packet includes relative-path PNG
playback scenes. Its 512px/32-sample PNGs are timing previews; appearance/cardinal
stills use 1024px/512 samples. The previews are not final delivery sequences.

## Compatibility, maps and provenance

The tested target is public Google GNM Head v3, model SHA-256
`61d78bbfb4ad8e0b38495804a4caef3214d3df00f8c3f68761e63b41ce3747eb`.
The organizer supplied no model; an undisclosed evaluator asset is untested.

The new sets use 4K skin and 2K left/right eye maps. Base color is sRGB;
roughness, specular and tangent-space normal maps are Non-Color data. Follow
the PBR manifest and binding recipe rather than the older rc.5 height-map recipe.
Separate native scalp/brow color maps support texture-only wrapping. Full
character rendering retains its selected groom. The development UV matrix
covers five sets, two layouts and three lighting/views (thirty cases).

Skin sources include attributed InfiniteScan material and CC0 MakeHuman
fallback; eye detail includes a CC0 photographic iris-sector reconstruction.
The reconstructed iris source has approximately 440px region coverage; 2K
output size does not imply 2K photographic detail. Preserve the pinned model
license, scan license, source records and attribution with redistributed assets.

Windows and Linux neutral rehearsal images are not byte-identical: maximum
RGB-channel difference 5/255, mean 0.0096/255, 99th percentile zero. These
measurements cover three identical held frames; they do not establish an
accepted motion tolerance. Exact same-platform reproduction remains required.
Final archive integrity and hygiene checks passed in the retained qualification
reports. Independent human appearance and motion review remains outstanding.
