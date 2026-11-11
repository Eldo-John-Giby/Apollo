# Natural adult appearance handoff

The first requested makeover is complete on appearance-v3. This candidate has
thicker shaped brows (1500 hairs per side), fuller contoured lips with a blended
vermilion boundary, regional lip colour/roughness, fine vertical surface detail,
soft cheek/jaw shaping, a minimal tested lid adjustment and refined temple hair.

Open scene.blend with Blender 4.5.15 LTS. Runtime meshes/textures are packed.
The wrapper, ten native renders and official metadata are included. From this
folder, run Blender with -b --factory-startup scene.blend --python-exit-code 1
-P wrapper/eyes.py -- --out NEW_DIRECTORY. Rebuild from the original v2 candidate
with build/appearance_v3.py and build/appearance_v3_config.json from the repo.
No MPFB installation is required by this packed-scene refinement recipe.

82 unit tests, independent 1009-pose geometry with 14 faults, exact reset/cardinal
checks, official ten-frame images/metadata, nine real visibility masks, native
CPU benchmarking and all 113 stress poses plus 256 fresh corpus images pass.
Center/up/corner benchmark timings are 53.20/56.80/57.97 seconds. Peak targeted
process RSS is 1,530,953,728 bytes. Minimum full-suite pupil visibility is
99.826%, blind maximum is 0.316136 px and independent corpus pixel maximum is
0.153842 px (upper-rounded). Thresholds remain unchanged. Check the JSON evidence
for exact values and scene/source identities.

The larger lid reduction was rejected because it joined an iris to lid shadow
in the image detector. Earlier failure evidence remains in local outputs.
The accepted build uses a smaller tested adjustment. The technical passes and
assistant visual review are recorded separately from human aesthetic/readability
judgments. Visible CG simplifications remain in the 2K skin, efficient grooming
and non-refractive eyes.

Evidence includes matched portrait/eye comparisons, neutral/clay diagnostics,
actual masks and full-suite measurements. Raw stress renders remain locally
archived with their SHA-256 and per-file manifest in evidence/review.json and
evidence/stress/raw-manifest.json. The full binary archive is local. The packed
candidate and selected raw evidence are versioned in this folder.

The next user-requested creative sculpting pass follows this completed baseline.
Cross-platform release qualification remains a separate release-selection step.
