# v22 submission integration

Active branch: `codex/v22-submission-integration`, based on `9b02f41`.
The approved portrait remains immutable. The rc.5 fallback remains unchanged;
its test results do not qualify this candidate. The 60/20/20 rubric is the
authoritative target. No organizer grade is predicted.

## Inputs and boundaries

- The final hero is the approved v22 character, including its selected facial
  identity and groom. The user reconfirmed this after seeing the plain-target
  portability test. That unenhanced target is a separate evaluator compatibility
  output and must never be presented as the replacement final character.
- Selected scene: `milestones/gnm-portrait-final-2026-11-17/portrait_v22.blend`.
- SHA-256: `f648bbaff98edbb3254a386047a4909aa8bb20ba7e79c949985b0b43f8833cfd`.
- Selection receipt: `final-selection.json` in that directory. v23 is rejected.
- Runtime under audit: Blender 4.5.15 LTS. Skills targeting 5.2 require API checks.
- Target: public GNM Head v3, model SHA-256
  `61d78bbfb4ad8e0b38495804a4caef3214d3df00f8c3f68761e63b41ce3747eb`,
  pinned by `tools/gnm_template.py`. Organizer-specific compatibility is untested.
- On 19 November the user confirmed that the organizer supplied no asset or
  additional compatibility information, and that the deadline is 22 November
  midnight. Planning interprets this as the end of 22 November 2026 in
  Asia/Calcutta (23:59:59 IST); organizer timezone was not separately supplied.
- Public model licensing/provenance must be carried through qualification.
  Organizer acceptance of layouts, texture interpretation and redistribution
  remains an external uncertainty, not an engineering pass.
- README changes are explicitly authorized by the supplied execution plan.
  Videos and presentations remain excluded. Use still PNGs and Blender playback.

## Requirements to evidence

All locations below are planned unless explicitly marked PASS. Generated audit
and release results live under `out/`; they are not source files in FILEMAP.
Engineering owns implementation and automated evidence. The user and independent
reviewers own visual acceptance; the team owns submission actions.

| Requirement | Owner | Acceptance | Evidence | State |
| --- | --- | --- | --- | --- |
| Preserve selected identity | Engineering | Hash check before every derived build; no source writes | selection receipt; `out/v22-audit/audit.json` | PASS for completed experimental derivations; ongoing build guard |
| Isolate integration | Engineering | Separate clean worktree; unrelated edits retained | branch above | PASS |
| Reproducible identity layer | Engineering | Native topology/order/UV unchanged; neutral matches selected evaluated surface | `out/v22-audit/identity.npz`; integration receipt | Pending |
| Appearance inventory | Engineering | Geometry, keys, shader dependencies, textures and visible attachments inventoried | `out/v22-audit/audit.json` | PASS |
| Reference views | Engineering | Source-bound front/profile/three-quarter/eye stills inspected | `out/v22-audit/*.png` and hashes | Running |
| Native motion reference | Engineering | Pinned upstream evaluation; exact reference checks retained | native clips and reference verification | Pending |
| Deformed identity | Engineering | Local surface transport; native eyes unaffected; neutral exact | derived motion checks | Pending |
| Attached groom/tears | Engineering | Roots and local orientation follow motion; no severe intersections | attachment manifest, all-frame and transition checks, crops | Pending |
| Five complete texture variants (60) | Engineering | Existing identifiers; coherent skin/lips/ears/eyes; base color, roughness, detail | texture manifests, source licenses and hashes | Pending |
| UV portability (20) | Engineering | Automatic fresh-target wrapping of five variants in both layouts; seams/color spaces/dilation checked | fresh wrapping receipts and comparisons | Pending |
| Texture-only result (60) | Engineering/reviewers | Convincing neutral and oblique-light appearance on fresh native target | judging stills and blinded review | Pending |
| Full v22 result (60) | Engineering/user | Identity retained with groom and geometry; sharp, consistent comparison settings | hero, details, contact sheets | Pending |
| Render convergence | Engineering | Lowest samples preserving eye/lip/skin/hair detail | sample comparisons and selected presets | Pending |
| Three motion modes (20) | Engineering | Left/right/generate-motion; 192 frames each at 24 fps; viewer-screen convention | packed timelines and 576 numbered PNGs | Pending |
| Kinematic checks (20) | Engineering | Binocular fixation, eye integrity, closure/reopening, smooth lids/expressions | all-frame checks and intermediate transition samples | Pending |
| Image checks (20) | Engineering | Independent pupil/direction checks; peak occlusion and restored visibility | image oracle reports | Pending |
| Exact reset | Engineering | Deterministic neutral reset and same-build reproduction | geometry/pixel/hash comparisons | Pending |
| Offline playback (20) | Engineering | Reopened packed scenes without paths, MCP, MPFB or GNM authoring environment | offline audit and clean extraction receipts | Pending |
| Stable CLI (20) | Engineering | still/left/right/generate-motion; variant/layout/output/frame options retained | CLI tests and clean runs | Pending |
| Recovery (20) | Engineering | Resume, missing/corrupt repair, stale-cache rejection, invalid-input rejection | recovery tests on candidate | Pending |
| Cross-platform reproduction (20) | Engineering | Clean Windows/Linux extraction; spaces and different CWD; pinned Blender | reproducibility reports; platform tolerance stated separately | Pending |
| Independent review | User + 3–5 reviewers | >=95% cardinal accuracy; median >=4/5 each category; no severe defect shared by two reviewers | randomized blind sheets, responses, separate key | Pending |
| Final identity approval | User | Explicit approval of integrated hero as retaining v22 | review decision | Pending |
| Freeze and full qualification | Engineering | Regenerate final deliverables after acceptance; bind source/scenes/maps/frames/tests | final manifest and all applicable tests | Pending |
| Package hygiene | Engineering | No credentials, personal paths, unlicensed or development artifacts | archive scan and licenses | Pending |
| Judge documentation | Engineering | Verified setup, modes/variants, playback, evidence, compatibility, limitations | README, quickstart, submission audit | Pending |
| Release | Engineering | Checkpoint commits; push; uniform version/tag; promotion only after gates pass | release commit/assets/checksums | Pending |
| Submission handoff | Engineering/team | Exact repository/release/hashes/matrix and remaining checklist | handoff report | Pending |
| Public access and form | Team | Signed-out verification; form submission; confirmation retained | team confirmation | External |
| Video/PPT readiness | Team | Track externally; preserve existing artifacts | team status | External; excluded from engineering |

## Current execution

The integration starts by extracting the evaluated selected identity, without
removing or reinterpreting its shape keys. Native motion and derived appearance
will have separate measurements. The existing installer rejection must remain
the default for arbitrary keyed scenes; any integration path must explicitly
authenticate v22 and record its derivation.

No visual, motion, texture portability, clean-machine or release gate has passed
for this integrated candidate yet. Historical rc.5 qualification and still-only
v22 checks remain separate evidence.

### Initial integration evidence (19 November)

- All 92 Python tests passed, including two new numerical regressions. These do
  not replace the Blender and visual checks.
- `out/v22-audit` inventories the selected scene: 17,821 vertices, the exact
  native basis, both original UV layouts, nine packed texture images, a keyed
  appearance layer, static curves and keyed tear-corner meshes. Skin is 4K;
  both irises are 2K. There are additional procedural color/specular/normal
  dependencies, so the packed image files alone do not reproduce the look.
- Source-derived reference views were rendered and inspected. The first
  `front.png` used the saved angled beauty camera; it must be relabeled
  `saved-camera.png` and a true frontal view generated before reference freeze.
- The native 35 cm binocular fixation shifts the neutral pupils about 1.15 mm
  relative to the selected still. The non-eye neutral surface remains exact.
  Keep the selected still separate; inspect the intentional motion convergence.
- Trial 3 reopens with native/derived errors below `1e-12` m and exactly native
  eye vertices at seven stress frames. Sixteen groom/tear objects use packed
  Geometry Nodes anchors; no Python handler or authoring add-on is required.
  Pupil occlusion/reopening and the unchanged 0.005 screen-direction threshold
  pass using the rc.5 frontal motion camera prescription (115 mm, 0.58 m).
- These checks do **not** accept Trial 3: its closed-eye still showed upright
  lashes. Rim orientation measurements subsequently found a nearly 128-degree
  change. A tip correction and stable proximal orientation patches are being
  tested, while retaining the original roots and neutral strand shapes.
- Trial 4 measures groom roots within 0.177 mm of the skin through frames
  103–112, but its initial orientation issue still requires the proximal-patch
  fix and a new visual review. These partial results are not all-frame gates.
- A four-substep native clip failed the additional continuous interpolation
  comparison (43.3 micrometres maximum position error between packed samples).
  A denser evaluation is in progress; the 1 micrometre threshold is unchanged.

Next: inspect the corrected blink, qualify integer and intermediate frames,
finish authenticated frontal references, and test the UV bake on a fresh native
target. Texture variants, human review, clean-machine qualification, packaging
and release remain pending.

Trial 5 retains the roots while choosing the nearest proximal orientation patch
with a maximum sampled step below 30 degrees. Upper strands also have an explicit
70-degree, root-preserving blink articulation, with the native one-frame right
lid delay. The closed-eye render was inspected and no longer has the upright
spikes. Reopened checks through frames 103–112 pass, including the unchanged
camera gate. This remains a coarse visual trial, not final motion acceptance.

The 32-substep native reference has 6,113 sample times and 1,186 unique poses.
Direct upstream evaluations at interval midpoints differ from packed linear
interpolation by at most `7.450580596923828e-7` m, passing the unchanged `1e-6` m
threshold. Receipt: `out/v22-native-dense-32/generate-motion.json`. The integrated
dense scene is not yet built or qualified. The builder authenticates the receipt
and rejects dense clips that failed this gate.

The authenticated frontal reference is now `out/v22-audit/front.png`; the original
angled camera image is `saved-camera.png`. Profile, three-quarter and eye-detail
images are also recorded in the regenerated audit. All have been inspected.

The low-resolution bake/wrapping prototype now produces twelve 16-bit maps:
base color, roughness, specular and tangent normal for skin and both eyes. Its
manifest also preserves the selected subsurface method and corneal shader
recipe. Empty eye maps and opaque default target corneas were caught and fixed
before further qualification. Material slots must be replaced in place: clearing
the slot list silently resets polygon regions. The bake now asserts region
preservation before every channel pass.

`out/v22-wrap-prototype-4` contains matched source/full-baked/fresh-native stills.
The full prototype looks close at this resolution; fresh-target eyes now display
with the selected corneal recipe. The unenhanced target retains its native eye
openings and has no groom or appearance geometry. Its faint portable brows and
flat scalp remain visual limitations to address or explicitly review. No
texture-only realism gate has passed. A 4K skin / 2K eye bake is running.

Normal serialization was checked independently through OpenCV: no inverted blue
channel pixels in covered regions and 95th-percentile unit-length error below
`3.6e-5` on the prototype. This does not establish final-resolution quality or
seam continuity. Five prototype variant sets are also generated, with the default
maps copied byte-for-byte; palette review and final-resolution generation remain
pending.

### Resumed motion qualification

Work was paused at the user's request after the plain-target test caused
confusion. The active 4K normal bake was stopped, leaving an incomplete map set
that must not be packaged. The original v22 copies were rehashed and still
matched the selection receipt. On resume, motion of the full approved character
is the immediate priority. The prototype overlay files remain isolated work;
they are not selected appearance changes.

The dense Generate Motion trial is saved at
`out/v22-integrated-dense/generate-motion/expression.blend`. It contains the
selected full-character materials, 16 surface-attached groom/tear objects,
ordinary packed shape-key animation and a separate native-motion reference.
An offline all-integer-frame audit is running. The source audit at
`out/v22-audit-current/audit.json` adds a path-independent shader recipe signature
and exact packed-image hashes; reopening must match both. All 92 Python tests
passed again. These are development checks, not final release acceptance.

The dense scene subsequently passed the offline 192-integer-frame audit at
`out/v22-integrated-dense/generate-motion/integer-check.json`. Maximum native
error was `3.64e-12` m; derived error was `1.82e-12` m; native eye error was zero.
The head shader signature and all nine packed texture payloads match v22. The
maximum root-to-skin distance was 0.1771 mm, and the upper-lash orientation step
stayed below 28.43 degrees per frame. Geometry-based camera checks passed closure
and reopening. These checks cover integer samples only; dense intermediate
playback checks and rendered collision/image checks are still required.

`out/v22-main-character-review` is rendering the full approved character's
portrait and motion-camera views at neutral, closed blink and reopening. Its
neutral portrait has been inspected and retains v22's selected face and groom.
This review does not change the selected scene or confer user acceptance.

The six portrait/motion-camera neutral, closure and reopening stills have now
rendered. The neutral and closed portrait images were inspected; the earlier
upright lash defect is absent and the full character is retained. The still
receipt binds source scene, shader identity, cameras, settings and image hashes.

The existing general-purpose image detector selected nostrils in this new
framing. `gnm_v22_image_check.py` therefore uses fixed eye regions of the frontal
motion image, without geometry or projected pupil predictions, and confirms
dark candidates against the neutral pupil/iris image patch. A 0.8 normalized
correlation is an internal detector threshold, not an organizer rule. The closure
image contained a dark lash clump (correlation 0.541), which is recorded and
rejected as a pupil; reopened iris matches were 0.877 and 0.962. Actual neutral,
closure and reopening checks pass in `out/v22-main-character-review/pupil-blink.json`.
Three adversarial tests verify nostril rejection, shifted pupil tracking, closed
lash lines and rejection of deliberately exposed unilateral pupils. Horizontal
direction images of this dense scene are not yet rendered or checked.

An offline 383-sample integer/half-frame audit is running against the same
dense scene, with explicit 0.25 mm root-distance and 30 degrees/frame orientation
rate limits. This is additional evidence; it must not be described as passed
until its final report says so. The 32-substep native interpolation receipt does
not by itself prove derived-character playback between integer frames.

The integer/half-frame audit completed successfully:
`out/v22-integrated-dense/generate-motion/half-frame-check.json` checks 383
sample times across the full clip, including closure/reopening and reset.
Maximum native error is `3.64e-12` m, derived error `1.82e-12` m, eye error zero,
root distance 0.1771 mm and orientation rate 28.99 degrees/frame. The final report
has no attachment-limit errors. This is stronger playback evidence than the
integer-only report, but does not replace independent visual review, all required
PNG sequences, cross-platform qualification or the final frozen rebuild.

Both dedicated Left and Right dense timelines have also been built and reopened
offline. Each passes 383 integer/half-frame samples with native eyes unchanged,
selected head shaders and texture payloads intact, maximum root distance
0.1771 mm and maximum orientation rate 28.65 degrees/frame. Their evidence is
under `out/v22-integrated-dense/{left,right}/half-frame-check.json`. The original
v22 file remains byte-identical. These are experimental full-character scenes;
they are not promoted release assets.

The rendered Generate Motion direction check in
`out/v22-main-direction-review/image-check.json` passes both binocular directions:
left shifts are -4.57/-4.80 px, right shifts +4.32/+2.62 px at 640 px image width.
All neutral, closure, reopening and direction stills have been inspected and
collated in `out/v22-main-character-review/full-character-sheet.png`. This is a
labeled development sheet, not the blind independent review packet. The user
has been asked to judge whether this integrated full character retains v22;
no response or acceptance has yet been recorded.

The runtime now recognizes complete manifest-bound PBR sets, including both eye
normal/specular maps and the corneal recipe. Corrupt/incomplete maps fail before
rendering; cache identities include all map bytes, manifests and binder code.
`still` prefers `model/character.blend` when provided, retaining the neutral-model
fallback for existing archives. No public command flag or variant identifier
changed. The full-character PBR still path preserves v22 lighting and uses its
frontal 85 mm judging framing; texture-only targets retain their separate rig.

All 101 Python tests passed, including complete-set corruption, missing skin
normal, cache-recipe changes and full-character/legacy CLI selection tests.
A development-only standalone trial in `out/v22 runtime trial` contains copied
runner files, packed full-character scenes and low-resolution prototype PBR
sets. Running its existing `still` command from outside the repository produced
a 1024 px image with a source/map-bound receipt, proving full-character selection
and paths-with-spaces operation. The generic lighting initially over-brightened
the hair, so a second render is checking preservation of v22's lighting. This
trial is not a release archive, final-resolution map set or clean-machine
qualification. Cached PBR motion rendering still needs an actual runtime test.

The second standalone still completed and was inspected. It uses the full
character, the selected lighting and a frontal 85 mm camera, at 1024 px and 32
samples. The scene hash in `renders/v22-lighting.render.json` matches the staged
full-character file. Its material maps are still low-resolution prototypes, so
the softened detail must not be treated as the final visual result. The focused
PBR/legacy/image regression set passed all 13 checks after this lighting change.

Next engineering work: choose render samples through convergence evidence;
finish the interrupted 4K/2K texture set and qualify all five variants in both
UV layouts; run an actual alternate-variant cached-motion render; produce the
complete PNG sequences; prepare and collect independent review; freeze/rebuild,
reproduce and package the accepted result. No new release or submission has
been created. README/quickstart updates must describe the finally verified
package, not these development staging directories.

### Whole-character preservation and render convergence

`out/v22-integrated-dense/generate-motion/whole-character-check.json` now compares
all 18 visible geometry components directly with a fresh append of immutable
v22. Material recipes, additional hair/material modes, transforms and groom
radii match. Maximum neutral point error is `5.96e-8` m; native eyes are excluded
from this neutral identity comparison because their intentional shared fixation
is separately checked against the upstream motion reference. The checker leaves
both files unchanged. This is technical identity evidence; user acceptance is
still pending.

The 1024 px fixed-seed, nonadaptive 32/64-sample comparison is complete in
`out/v22-convergence-32-64`. Source scene, camera, exposure, denoising and lighting
are held constant. The predeclared internal stability limits are mean absolute
RGB difference <=1, 95th percentile <=3 and high-frequency detail ratio within
0.90–1.10. These are render-convergence criteria, not organizer scoring rules.
At 32 versus 64 samples, skin passes (mean 0.46, p95 1); eyes (1.40, 6), lips
(1.68, 5) and hair (1.34, 5) fail. The native crop sheet was inspected. No delivery
sample count is selected from this failed comparison. A 128-sample reference is
rendering, after which the existing 64-sample image can be reused only if the
worker, source and complete render policy match exactly.

The image checker now supports vertical gaze as well as horizontal gaze. An
adversarial test rejects reversed vertical labels; the vertical images of the
candidate still need rendering and inspection before that check can pass.

The interrupted 4K set has nine valid, source-bound maps but no normal maps.
It remains incomplete. The baker now captures all recipe hashes and writes a
completion marker only after its final source/recipe guards pass. Runtime
validation rejects a new bake marked incomplete even if all map files happen
to exist. A fresh complete 4K/2K set will be generated with this provenance.

Linux qualification is not available yet: Ubuntu startup failed twice with
`Wsl/Service/CreateInstance/CreateVm/ERROR_TIMEOUT`, including after a successful
idle `wsl --shutdown`. The running-distribution list was empty before recovery.
Docker Desktop was started hidden, but its engine query did not return; that
read-only query was stopped. No distributions were deleted or converted, and no
Windows restart was performed. Windows rendering continues. Historical Linux
results are not evidence for this candidate, and the Linux gate remains pending.

The 128-sample original-shader reference is complete. The 64-versus-128 crop
comparison also misses the unchanged limits in eyes, lips and hair, so neither
32 nor 64 is accepted as a delivery setting on this evidence. These references
remain useful for appearance comparison. Final sample selection must also be
tested on the portable appearance actually delivered; the convergence worker
can now bind and independently validate an explicit PBR set while retaining the
full v22 geometry and groom.

Rendered vertical checks completed in `out/v22-vertical-review/image-check.json`:
upward pupil shifts are -4.23/-5.27 px and downward shifts +3.31/+3.43 px at
640 px image width. The up/down stills were inspected. All four cardinal image
checks, closure and reopening now pass on this development scene; this is not
the 3–5-person blind accuracy gate.

`gnm_v22_materials.validate` checks active map payloads, color spaces, UV offsets,
tangent normal strength, selected constant shader inputs/modes and the complete
corneal recipe. An actual Blender test accepted the twelve-map prototype and
rejected four injected defects: sRGB normals, wrong normal UVs, altered skin IOR
and altered corneal roughness. The selected source scene was unchanged. The
test report is `out/v22-pbr-graph-check.json`. A fresh complete 4K/2K master bake
is next; the baker's recipe files must remain fixed throughout that job.
