# GNM scoring improvement audit and execution plan

14 November 2026. Baseline: 49450ee, published rc.4 preserved.

The supplied evaluator slide 2 assigns texture 60, motion 20 and portability 20 points. It requires 5–10 face-and-eye sets and matched stills, three input modes and a playable Blender timeline. Team video/deck/public-access/submission tasks remain separate and pending. No numerical brownie allocation or render-time cap is stated.

## Evidence audit

- Existing receipt records five sets, 576 CPU frames, 84 tests and clean offline reproduction. This is baseline evidence, not candidate qualification.
- Visual inspection: low effective facial detail, smooth skin, weak brow contrast, soft and partly misplaced lip color, limited complexion diversity. Peak blink exposes a dark slit on the viewer-left eye and angular contact folds.
- Implementation: 2K source is a whole-body atlas; remapping cannot add genuine photographic detail. Skin pore bump uses generated coordinates and is absent from portable maps. Eye remapping uses nearest sampling and magnifies a small stock iris.
- Native topology, both corner UV arrays, upstream expression basis and strict verifiers must remain intact. Exact organizer model is unconfirmed. Human review is deferred.

## Prioritized implementation

1. Investigate CC0 higher-detail source skins; quantify source facial coverage. Compare sources and direct surface synthesis under matched cameras/lights. Fix alignment before cosmetic changes.
2. Export native-UV skin color plus justified roughness/height maps, with physical-scale seamless detail and explicit non-color bindings. Improve eye maps at their actual native iris footprint and retain distinct bilateral patterns. Review all five variants under front/three-quarter and neutral/oblique lights.
3. Diagnose blink rim and globe contact using native basis constraints; improve the fit without weakening tolerances. Validate rendered transition/closure/reopening anchors and upstream geometry.
4. Rebuild affected timelines and all final frames; verify fresh neutral wrapping in both layouts, packed resources, every frame receipt and recovery. Rehearse clean extraction, build a versioned archive, update anonymous review packet, commit and push a qualified prerelease.

A score prediction will be a subjective range tied to inspected delivered evidence, never an official score. No candidate improvement or qualification is claimed at this audit checkpoint.

## First implementation checkpoint

Native rim coupling removes the visible open slit in the matched frame-106 comparison. Coefficients remain within ±3 and the upstream clip installer passes its unchanged geometry and visibility checks. The smoothing sweep favors 1.0: full-closure maximum vertical rim gap is approximately 0.21 mm and neighboring-displacement p95 is approximately 0.71 mm. The 0.5 prototype closes more tightly but has higher local displacement variation. Candidate full qualification is pending. All 87 Python tests pass at this checkpoint.

Rejected skin prototypes include a direct portrait transfer with duplicate feature placement and a surrounding-skin replacement that created visible patches. A licensed head-only 4K scan transfer visibly retains stronger detail and is the next candidate; it is not yet qualified. The MakeHuman source and published rc.4 remain preserved.

## Scan candidate build

Use Blender 4.5.15 LTS and install the build dependencies with
`python -m pip install -r requirements-gnm-build.txt`. Generate the baseline
rose-brown variant manifest and prepare the pinned neutral template using
GNM_INTEGRATION.md. From the worktree root, run:

```powershell
python tools/submission_variants.py generate out/variants --polished-reference
& $env:BLENDER_BIN --offline-mode -b --factory-startup milestones/eye-expression-2026-11-11/scene.blend --python-exit-code 1 -P tools/gnm_skin_trial.py -- --gnm out/template/neutral.blend --variant out/variants/rose-brown/variant.json --out out/direct4k/raw.png --mouth-lift .014 --direct-albedo --size 4096
python tools/gnm_scan_transfer.py --blender $env:BLENDER_BIN --template out/template --fallback out/direct4k/raw.png --out out/scan4k
python tools/gnm_generate_textures.py --template out/template/template.npz --source out/scan4k --out out/score-textures
```

The scan transfer measured 99.309% raw scan coverage and 99.997% combined
projection coverage. The matched CC0 source covers 99,731 in-mask texels.
Remaining repair covers 503 in-mask texels with a maximum distance of
12.81 pixels in the 4K atlas. The five palettes share registered scan detail
and vary pigmentation and independent iris patterns. Source attribution,
asset checksums and derivative terms are in assets/gnm-scan. The source scan
contributes actual photographic detail. Relief, roughness, iris fibers and
vascular marks are authored surface detail.

The final fit reduced maximum full-closure rim gap from 1.24 mm on both
eyes to 0.212 mm on the left and 0.195 mm on the right. Neighboring
displacement jump at p95 decreased from roughly 0.73 to 0.71 mm.
This was measured at frame 107 with both blink weights at peak.
The current Python suite passed all 88 tests. Final render and archive
qualification are in progress.
