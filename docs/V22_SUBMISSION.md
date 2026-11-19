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

PASS applies only to the scope stated in its row. PARTIAL means the cited
development evidence exists but the full requirement is not achieved. Generated audit
and release results live under `out/`; they are not source files in FILEMAP.
Engineering owns implementation and automated evidence. The user and independent
reviewers own visual acceptance; the team owns submission actions.

| Requirement | Owner | Acceptance | Evidence | State |
| --- | --- | --- | --- | --- |
| Preserve selected identity | Engineering | Hash check before every derived build; no source writes | selection receipt; `out/v22-audit/audit.json` | PASS for completed experimental derivations; ongoing build guard |
| Isolate integration | Engineering | Separate clean worktree; unrelated edits retained | branch above | PASS |
| Reproducible identity layer | Engineering | Native topology/order/UV unchanged; neutral matches selected evaluated surface | `out/v22-integrated-dense/*/expression.json`; `out/v22-review-pbr-512/*/appearance-check.json` | PASS for current development derivation; final frozen rebuild pending |
| Appearance inventory | Engineering | Geometry, keys, shader dependencies, textures and visible attachments inventoried | `out/v22-audit/audit.json` | PASS |
| Reference views | Engineering | Source-bound front/profile/three-quarter/eye stills inspected | selected source hashes; `out/v22-owner-identity-review`; reference records | PARTIAL: approved references authenticated; final matched view set pending |
| Native motion reference | Engineering | Pinned upstream evaluation; exact reference checks retained | `out/v22-native-dense-32`; saved PBR half-frame checks | PASS for development native evaluation and three saved scenes; final rebuild pending |
| Deformed identity | Engineering | Local surface transport; native eyes unaffected; neutral exact | `out/v22-review-pbr-512/*/half-frame-check.json` and appearance checks | PASS for three development scenes, 383 times each, native eye error zero |
| Attached groom/tears | Engineering | Roots and local orientation follow motion; no severe intersections | same half-frame checks; blink/reopening images | PARTIAL: numerical limits pass; independent collision/motion review pending |
| Five complete texture variants (60) | Engineering | Existing identifiers; coherent skin/lips/ears/eyes; base color, roughness, detail | `out/v22-variants-native-skin-v2/assembly.json`; source manifests and decoder reports | PARTIAL: five 4K/2K sets authored; corrected deep palette and final detail/human acceptance pending |
| UV portability (20) | Engineering | Automatic fresh-target wrapping of five variants in both layouts; seams/color spaces/dilation checked | `out/v22-corrected-five-wrap-evidence/layout-check.json` | PARTIAL: thirty current fresh-wrap cases pass layout agreement; final seam/detail acceptance pending |
| Texture-only result (60) | Engineering/reviewers | Convincing neutral and oblique-light appearance on fresh native target | judging stills and blinded review | Pending |
| Full v22 result (60) | Engineering/user | Identity retained with groom and geometry; sharp, consistent comparison settings | hero, details, contact sheets | Pending |
| Render convergence | Engineering | Lowest samples preserving eye/lip/skin/hair detail | `out/v22-three-pose-render-profile.json` and its analyses | PARTIAL: 512 passes default neutral, closure and reopened/upward pose; other variants/views/frozen build pending |
| Three motion modes (20) | Engineering | Left/right/generate-motion; 192 frames each at 24 fps; viewer-screen convention | `out/v22-review-pbr-512/*/expression.blend` | PARTIAL: three packed timelines checked; final 576 numbered PNGs pending |
| Kinematic checks (20) | Engineering | Binocular fixation, eye integrity, closure/reopening, smooth lids/expressions | three saved-scene half-frame checks; native interpolation receipts | PARTIAL: geometry/attachment checks pass at 383 times per mode; rendered full-motion and human gates pending |
| Image checks (20) | Engineering | Independent pupil/direction checks; peak occlusion and restored visibility | `out/v22-pbr-512-upward-reopening-check.json`; cardinal render queue | PARTIAL: upward gaze, closure and reopening pass; three other cardinal images pending |
| Exact reset | Engineering | Deterministic neutral reset and same-build reproduction | geometry/pixel/hash comparisons | Pending |
| Offline playback (20) | Engineering | Reopened packed scenes without paths, MCP, MPFB or GNM authoring environment | saved-scene resource checks; clean runtime rehearsal queue | PARTIAL: twenty-one packed images per current scene checked; clean runtime execution pending |
| Stable CLI (20) | Engineering | still/left/right/generate-motion; variant/layout/output/frame options retained | CLI tests and clean runs | Pending |
| Recovery (20) | Engineering | Resume, missing/corrupt repair, stale-cache rejection, invalid-input rejection | recovery tests on candidate | Pending |
| Cross-platform reproduction (20) | Engineering | Clean Windows/Linux extraction; spaces and different CWD; pinned Blender | reproducibility reports; platform tolerance stated separately | Pending |
| Independent review | User + 3–5 reviewers | >=95% cardinal accuracy; median >=4/5 each category; no severe defect shared by two reviewers | randomized blind sheets, responses, separate key | Pending |
| Final identity approval | User | Explicit approval of integrated hero as retaining v22 | `out/v22-owner-identity-review/identity-approval.json` | PASS for the reviewed integrated face and groom; final release gates remain separate |
| Freeze and full qualification | Engineering | Regenerate final deliverables after acceptance; bind source/scenes/maps/frames/tests | final manifest and all applicable tests | Pending |
| Package hygiene | Engineering | No credentials, personal paths, unlicensed or development artifacts | `out/v22-attribution-corrected-trial`; source/PNG policies; final archive scan | PARTIAL: pinned source notices and manifest linkage collected; final archive scan/inclusion pending |
| Judge documentation | Engineering | Verified setup, modes/variants, playback, evidence, compatibility, limitations | README, quickstart, submission audit | Pending |
| Release | Engineering | Checkpoint commits; push; uniform version/tag; promotion only after gates pass | release commit/assets/checksums | Pending |
| Submission handoff | Engineering/team | Exact repository/release/hashes/matrix and remaining checklist | handoff report | Pending |
| Public access and form | Team | Signed-out verification; form submission; confirmation retained | team confirmation | External |
| Video/PPT readiness | Team | Track externally; preserve existing artifacts | team status | External; excluded from engineering |

## Current execution

The current development candidate retains immutable v22 and separates native
motion from the transported identity layer. All three packed PBR timelines have
passed 383 integer/half-frame checks and eighteen-component neutral appearance
checks. The corrected five-set native matrix passes thirty fresh-wrap cases.
Default render convergence is verified at neutral, closure and reopening.

The controller is rendering four cardinal images, then runs the independent
image gate, development runtime staging, Windows archive/recovery rehearsal and
five full/native judging pairs. A separate watcher schedules offline Linux
runtime execution after the Windows controller exits. Queued work is not a pass.
Owner identity approval has been received; the 3–5-person blind review remains pending. No final
freeze, complete PNG delivery, release qualification or submission handoff is
claimed. Historical rc.5 results remain separate from this candidate.

### Historical initial integration evidence (19 November)

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

The fresh master bake has started in `out/v22-master-4k` using the recipe files
from checkpoint `025a03c`. It is still a live process and is not a completed
texture set. Do not restart it merely because a bake stage has no new log lines;
check the actual Blender process and tool handle first. The continuation
snapshot is `out/v22-master-4k-job.json`, and its recorded PID is only a hint
until the process creation time and command are revalidated. All 103 Python
tests passed after the vertical-image and incomplete-bake guard additions.

### Master bake continuation and derivative input guards

The live master process was revalidated by its creation time and exact command.
Nine maps have been written: 4096-square skin and 2048-square eyes for color,
roughness and specular. The normal bake is still active; `complete` remains
false, so this is not a qualified master. Preserve this process and its frozen
bake recipes until it terminates.

Both the pigmentation-variant builder and the separate texture-only overlay
builder now use the same strict complete-manifest validator as runtime binding.
They reject unfinished masters before creating output directories, including
the interval after every map exists but before final source checks finish.

`gnm_v22_texture_check.py` independently decodes the delivered PNGs and checks
their actual RGB precision, dimensions, declared color spaces and tangent-normal
vectors. All twelve low-resolution prototype maps passed this inspection in
`out/v22-bake-prototype-6/decoded-map-check.json`; this does not qualify the
unfinished 4K master or prove appearance. Eleven targeted tests passed,
including actual low-bit-depth PNGs, wrong dimensions, inverted/short normals
and unfinished derivative inputs. The convergence renderer now permits
256/512/1024 samples if the unchanged convergence limits require higher
references; no delivery sample count has been selected.

The full Python suite subsequently passed: **107 tests**. The immutable v22
source still hashes to the recorded selection checksum. The existing bake
session `55117` and process creation time were revalidated after those checks;
normal baking remains live, so the master is still incomplete.

### Independent human review scorer

`tools/gnm_v22_review_gate.py` scores explicit returned responses; it does not
generate or invent reviewer feedback. Eleven targeted tests cover incomplete
answers, duplicate reviewers, wrong packets, a non-blind first pass, too few
reviewers, missing variant coverage, low category medians, repeated severe
defects and opposite-direction confusion. The full 107-test suite result above
predates these eleven new tests; no larger full-suite count is claimed here.

The frozen assessor key has `candidate_sha256`, a `directions` object mapping
anonymous case IDs to `left`/`right`/`up`/`down`, an `appearance` object and a
separate `motion` object.
Every candidate appearance case has `candidate: true`, its existing `variant`
identifier and `output: "full"` or `"texture_only"`. All ten combinations are
required. Reference cases have `candidate: false` and `reference: "rc5"` or
`"v22"`; both references are required. Keep this mapping out of reviewer packets.
The candidate digest must identify the frozen artifact manifest actually shown
to reviewers, and the eventual packet builder must authenticate the image and
playback assets against that manifest. The scorer alone cannot establish that
asset provenance or that reviewers are independent.

Generate a blank packet-bound response form with:

```powershell
python tools/gnm_v22_review_gate.py --key out/review/assessor-key.json --template --out out/review/responses.json
```

Returned forms must contain a distinct reviewer identifier, explicit
`independent_first_pass: true`, all cardinal answers (or `unclear`), integer
ratings from 1 to 5 for every category and case, and an explicit
`severe_defects` list. Categories are `skin`, `eyes`, `lips`, `ears`,
`brows_lashes` and `overall_realism`. Each motion case has its own integer
`motion_naturalness` rating, based on actual packed playback. The key's motion
cases have `candidate: true` and a `mode` of `left`, `right` or
`generate-motion`; all three candidate modes are required. Static reference
portraits and texture-only stills do not require invented motion ratings.
A defect entry has
`case`, `code` and explanatory `notes`; the tool lists the accepted codes.
Only reviewers can fill in these fields. An empty list means they explicitly
reported no severe defects; the generated template starts with null.

```powershell
python tools/gnm_v22_review_gate.py --key out/review/assessor-key.json --responses out/review/person-a.json out/review/person-b.json out/review/person-c.json --out out/review/scored.json
```

The scorer requires 3–5 distinct completed responses, at least 95% aggregate
cardinal accuracy, median ratings of at least 4 for every candidate case and
category, and no severe defect category identified by two reviewers. Repeated
opposite-direction answers also fail the gate. Reference ratings are reported
but cannot improve candidate medians. Its result covers the independent-review
gate only; the user's integrated-identity approval and technical qualification
remain separate. Actual final-packet preparation and collected feedback remain
pending while final appearance renders are unqualified.

The separate motion form and gate passed twelve targeted tests. Missing mode
coverage, blank motion scores, low motion medians and repeated severe defects
reported on actual motion cases fail the gate. No human responses have been
collected or inferred by these tests.

### Fresh-wrap comparison controls

The matched comparison tool now validates active maps and corneal shader graphs
after binding both the full character and fresh native target. It supports
`--angle` and `--oblique` while retaining the selected lighting as the default.
Comparisons fix CPU, seed, adaptive sampling, depth of field and motion blur,
and record camera, lights, exposure, target/template hashes and binding checks.
Source, map manifest, payloads and recipe files are checked again after renders.
The script compiles, but this changed Blender path has **not yet been executed**:
the existing master bake still occupies the single headless Blender slot. Its
creation time and command were revalidated, with CPU time continuing to rise.
The normal maps have not yet been written. WSL currently reports no running
distribution, so the earlier Linux qualification limitation remains unresolved.

### Selected appearance provenance inventory

`assets/v22-provenance.json` binds all nine selected packed image payloads to
the immutable scene hash, with dimensions and color spaces but no authoring
machine paths. It distinguishes the Infinite Scan CC-BY-3.0 skin/relief
derivatives, documented MakeHuman CC0 fallback, CC0 photographic iris sectors
and authored pigment, relief and masks. It retains the iris source's approximate
440-pixel photographed region; a 2K delivery atlas does not imply 2K photographic
detail. Native GNM geometry and the intentional identity/groom modifications
are recorded separately.

All four pinned scan-source files, including the original license text, and
the original iris photograph match their existing source-receipt hashes. The
eight referenced attribution/source records also match committed Git bytes,
so those recorded hashes do not depend on a Windows line-ending conversion.
The final archive must retain the cited license/attribution documents and bind
this inventory to its exact baked maps. That archive linkage remains pending;
this inventory does not qualify unfinished textures or an unbuilt package.

### Preserve the selected sample count in runtime stills

The full-character `still` path previously forced 32 samples regardless of the
saved candidate preset. It now requests the saved scene sample count through
the internal Blender tool's `--scene-samples` option. The public CLI is unchanged;
legacy neutral-template archives retain their 32-sample still behavior and
explicit authoring sample overrides remain available. Existing authoring callers
without the new internal option retain their behavior.

Nine targeted PBR/CLI tests pass, including full-character selection with saved
samples and the legacy fallback with explicit 32 samples. The Python files
compile. Actual Blender execution of the new internal option remains pending
while the existing normal bake is live. Experimental integrated scenes still
inherit 1024 samples; final packaging must apply the measured delivery preset
before using this path. No sample count is qualified by this code change.
The full suite before this change passed 118 tests.

### Completed master, isolated normal artifact and Docker recovery

The 4K/2K master bake completed with exit code 0 and final source/recipe checks.
All twelve maps exist in `out/v22-master-4k`; preserve this raw bake unchanged.
The queued follow-up correctly stopped at independent map validation because
the skin normal atlas contained sixteen negative tangent-Z pixels. Both eye
normals passed. The skin normal p95 unit-length error was approximately
0.0000341, with the sixteen inverted pixels confined to four bilateral
mouth-corner faces (4724, 4726, 10720 and 10722).

An isolated 256-square crop retained the original shader, its source UV reads
and native geometry while uniformly scaling the target UVs to inspect the left
mouth corner. The full shader reproduced eight inverted pixels; disconnecting
its bump stack produced zero, with minimum tangent Z approximately 0.981.
Reports are `out/v22-master-normal-diagnosis.json` and
`out/v22-normal-crop/report.json`. This identifies a source-shading artifact
in that tested crop, rather than a transfer-only error. The immutable scene
was not saved or changed.

`gnm_v22_normal_repair.py` derives a separate copy using a 5x5 valid-neighbor
component median and unit normalization only at negative tangent-Z texels.
It rejects more than 64 affected pixels or an affected fraction over 0.00001;
these limits bound the permitted repair, not the independent validation gate.
The repaired copy in `out/v22-master-4k-repaired` changes exactly sixteen skin
normal pixels (approximately 0.0000954% of the atlas). Every other encoded
pixel and all eleven other map files are unchanged. The manifest records every
before/after pixel and both source hashes. Two targeted tests pass. All twelve
repaired maps pass the unchanged independent encoding/normal check; this does
not confer visual acceptance. Matched full-character and fresh-target stills
are now rendering in `out/v22-master-wrap-repaired-udim`.

After the user opened Docker Desktop, its Linux engine became responsive.
The existing Apollo base image was extended with the documented SciPy 1.15.3
build dependency, preserving NumPy 1.26.4 and OpenCV 4.5.5. A committed source-code
archive of `f13a3c0` was extracted inside the container under a path containing
spaces. All **118 tests passed** from a different working directory with
networking disabled. The log is `out/v22-linux-code-f13a3c0.log`. This qualifies
that source-code test run only: it excludes the two new normal-repair tests,
Blender runtime checks and the final delivery archive. Final clean-package
Windows/Linux reproduction remains pending.

The full current source checkpoint `4e67d64`, including the isolated repair,
subsequently passed **120 tests on Windows and Linux**. Windows emitted
`out/v22-code-4e67d64-windows.xml`; Linux again used a clean source archive,
a path containing spaces, a different working directory and no network, with
log `out/v22-linux-code-4e67d64.log`. This is source-code validation rather than
the final delivery-archive rehearsal.

The right mouth-corner control also reproduced inverted shader normals (seven
in its cropped bake) and zero with bump shading disconnected. Both sides were
tested without modifying source geometry or saving the selected scene. The
right report is `out/v22-normal-crop-right/report.json`.

The first 768-pixel full-character shader-conversion comparison completed and
was visually inspected. It retains the v22 face and groom. Descriptive native
crop mean RGB differences against its matched source were approximately
0.36 (eyes), 0.27 (skin), 0.65 (lips) and 0.56 (hair), with p95 at most two.
The comparison and graph-binding receipts are in
`out/v22-master-wrap-repaired-udim`. The fresh native result still has faint
brows and a flat scalp pigment region, so the separate texture-only visual
gate remains open. These observations do not replace independent acceptance.

### Judging determinism and five full-resolution sets

Repeating the source render in the initial layout comparisons varied by up to
three RGB levels. Disabling output dithering alone did not remove this
variation. Inspection identified the selected portrait's legacy `NOISE`
compositor texture, mixed at 0.02 by `Mix.001`, as another randomness source.
`gnm_v22_render_policy.py` now explicitly bypasses that grain branch for judging
while retaining the remaining portrait compositor, materials and geometry.
It also centralizes fixed CPU sampling, seed, denoising and disabled adaptive
sampling, depth/motion blur and dithering. The immutable studio scene is unchanged.
New matched comparisons are in progress under `out/v22-master-wrap-judging-*`;
pixel-repeatability is not yet claimed.

The bake export scene now disables output dithering for future builds and
records that choice. Existing raw/repaired masters are preserved with their
original recipe hashes. They must not be relabeled as outputs of the changed
baker; the required final freeze/regeneration remains pending.

All five full-resolution pigmentation derivatives were generated in
`out/v22-variants-4k-base`. Their original CLI identifiers are retained, and
the default copies the repaired master's map bytes exactly. Independent
decoded checks are running for all five; fresh wrapping, oblique-light
comparisons and visual acceptance are still required.

The grain-controlled judging comparisons completed with source images exactly
pixel-identical across independent loads. Default full-character layout images
differ at only 27 pixels, by at most one RGB level; the fresh native target
differs at 33 pixels, also by at most one level. All p95 differences are zero.
Receipts and image hashes are checked by
`out/v22-master-wrap-judging-layout-check.json`. This proves the tested default
set's fixed-light layout comparison, not all five sets or oblique views.
All five full-resolution sets have now passed decoded encoding/normal checks;
`out/v22-variants-4k-base/validation.json` also confirms byte-identical default
maps relative to the repaired master.

### Packed PBR development timelines and portability preflight

The four-profile neutral convergence run completed through 256 samples. Against
that reference, 128 still exceeds the unchanged eye/lip/hair limits (mean RGB
errors approximately 1.02/1.24/1.08 and p95 four); 32 and 64 also fail. Skin
passes. The comparison sheets were visually inspected, but no delivery sample
count is selected. Reports are in `out/v22-convergence-pbr-judging-analysis`.
A separate 512-sample reference is now rendering with the identical source,
maps, worker and judging policy, for a strict combined comparison later.

`gnm_v22_prepare.py` checks the source integration scene/geometry receipts,
selected appearance audit and complete PBR manifest, applies the explicit
judging preset, packs images and asserts unchanged head geometry, polygon
regions and both UV layouts. It records all recipe/input hashes. The trial's
256 samples are a development setting, **not a selected delivery preset**.
The reopened verifier and whole-character checker now accept the intentional
PBR head conversion through independent shader/payload validation while
retaining native/derived geometry checks and exact groom checks.

The first cache test exposed Blender dropping the replaced portrait's unused
image datablocks on a later save. Original selected images now have explicit
retention; alternate caches retire only replaced, unused PBR materials/images
and update their active manifest stamp. The failed v2 alternate cache remains
unqualified. The v3 development scene retains all nine original payloads plus
twelve active PBR images across repeated saves.

`out/v22-packed-pbr-trial-v3/whole-character-check.json` passes all eighteen
visible components, with maximum neutral deviation approximately 0.06 microns.
The olive-amber alternate in the legacy UV layout passes reopened native,
derived, attachment, eye and packed-resource checks at frames 1, 107 and 112;
it retains 21 images, and a second cache invocation verifies the same artifact.
These are targeted checks, not all-frame qualification or a rendered alternate
motion acceptance. The old material path remains available for legacy archives.

Docker's installed Blender was directly verified as 4.5.15 LTS, build
`5afeabba6097`. The v3 default packed scene passes the same three-frame reopened
checks in a network-disabled Linux container without the authoring v22 scene
or authoring output directories mounted. Only the scene, maps, reference data,
checker code and evidence destination were supplied. The report is
`out/v22-packed-pbr-trial-v3/linux/reopened-check.json`. This is a development
portability preflight; final clean delivery-archive reproduction is still pending.

The separate native-target groom projection/rasterization completed. Its trial
in `out/v22-native-groom-review` improves brow definition but still shows an
unconvincingly flat scalp region, so it is **not visually accepted**. All twelve
full-character map files remain unchanged by that separate trial. Further
texture-only scalp refinement is needed before five-set visual qualification.

### PNG metadata and higher-sample control

Inspection found source filenames, dates and render timings embedded in rendered
PNG metadata. Pixel-identical source comparisons were therefore not byte-identical.
`apollo_core/png.py` removes PNG text, EXIF and time chunks after validating their
checksums, while preserving compressed image data and color-management chunks.
Four targeted tests pass, including actual 16-bit RGB channels, corrupt-input
rejection and preservation of PNG image-data bytes. Applying it in memory to
the independently rendered source controls produces byte-identical PNG data;
the existing experimental images and their receipts were not modified.

New still/frame outputs and future bake exports now use this policy before
hashing. Frame receipts include renderer and PNG-policy hashes, so old receipt
directories are rejected rather than mixing output policies. Both technical
bundle builders include the new pure-Python helper. The active convergence
worker and its original rendering helper remain unchanged until its experiment
finishes; final judging output integration will use the same metadata policy.

The 512-sample reference completed. Relative to it, 256 samples pass eyes and
skin but still fail lips (mean RGB approximately 1.125) and hair (p95 four).
The analysis is `out/v22-convergence-pbr-to-512/analysis.json`; no count is
selected. A repeated 32-sample control in one process gave identical pixels
and identical canonicalized PNG bytes, with lens jitter explicitly false.
This rules out an additional repeatability error in the tested setup.
A 1024-sample reference is now running with the identical worker and policy.

After the metadata policy changes, the complete Windows Python suite passed
**125 tests**, with JUnit evidence in `out/v22-png-policy-tests.xml`. This does
not update the earlier Linux unit-suite count or qualify the new rendering
hooks without an actual subsequent Blender render. The pure metadata helper
was also checked against real source-control PNGs: stripping metadata in memory
gave byte-identical results while leaving the original files untouched.

### Texture-only scalp restoration trial

The flat native scalp comes from underpainting intended to sit beneath the
separate v22 groom. The historical groom receipt identifies the uncapped input
atlas with SHA-256 `04f57d1256e6f5239ccd665dcaab09465c2f38fce3988628cc6b36cd3dd8d2b8`;
the retained rc.5 cool-grey atlas matches those exact bytes. The brow rasterizer
now supports `--brows-only`, generating a separate 4K overlay with 27,807 covered
texels rather than projecting scalp strands onto the bare native mesh.

A development restoration in `out/v22-native-bare-scalp-trial` uses that verified
uncapped photographic scalp, calibrated to the current forehead in linear RGB.
Its world-space scalp coverage excludes native ears and restores approximately
3.72 million scalp/padding texels. The twelve full-character maps are unchanged.
The experimental recipe and exact inputs are recorded by
`out/v22_restore_native_scalp.py` and the trial manifest. It is not yet rendered
or visually accepted: the single Blender slot remains occupied by the live
1024-sample reference. Do not use this trial as the master for the existing
variant generator; its scalp restoration is not yet part of that authoring path.

The 1024-sample reference and queued scalp preview completed. Against 1024,
**512 is the lowest tested setting passing all four neutral crops**: eye/lip/
skin/hair mean RGB errors are approximately 0.80/0.95/0.32/0.89, all p95 values
at most three, with retained detail ratios within 0.9–1.1. The comparison sheet
was visually inspected without visible denoising smearing. The source-bound
development selection is `out/v22-neutral-render-profile.json`; it qualifies
frame 1 only, not a final delivery preset or untested poses/variants.

The restored scalp preview was rendered and inspected in
`out/v22-native-bare-scalp-review`. It removes the flat painted-cap effect and
retains brow definition; independent human acceptance and all five native sets
remain pending. The full v22 character is unchanged. The comparison tool now
canonicalizes its PNGs before hashing, and the actual rendered preview contains
no authoring paths or timing metadata (only display-density information).

The clean Linux source archive at `03447c9` passed all **125 tests**, including
the PNG policy, with networking disabled and execution outside its extraction
directory. See `out/v22-linux-code-03447c9.log`. The current comparison-tool
metadata hook was subsequently verified by the queued Blender render.

### Reproducible native scalp authoring

The prototype is now implemented in `tools/gnm_v22_scalp.py` and exposed by
`gnm_v22_texture_only.py --uncapped <verified atlas> --template <pinned template>`.
Both inputs are required together, and restoration requires a brow-only overlay.
The atlas has the historical pinned hash above. Template and recipe dependencies
are checked before and after processing. Each variant calibrates the licensed
uncapped scalp to its own forehead in linear RGB; only the separate native color
map is restored. Full-character maps remain byte-identical to their input set.

Pigmentation must be generated before native restoration. The variant generator
rejects a restored native master rather than silently discarding its restoration.
The targeted calibration and manifest/variant suite passes 12 tests. Five-set
authoring is running under `out/v22-variants-native-skin`; its visual/layout
qualification remains pending. The frame-107 convergence experiment continues
with its frozen worker and repaired master, independently of this host authoring.

The independent texture decoder now also checks the three optional native maps:
4K 16-bit RGBA brow overlay, 4K 16-bit RGB restored color and roughness, and their
declared color spaces. Its malformed-alpha regression passes. The complete
Windows suite passes **129 tests**, recorded in
`out/v22-scalp-and-encoding-tests.xml`. This is source-level evidence; it does
not count as fresh-target visual acceptance or final archive qualification.

### Five-set fresh-wrap matrix gate

`gnm_v22_wrap_check.py` requires thirty actual fresh-target trials, arranged as
`<source>/<variant>/<udim|legacy>/<front|angle|oblique>/comparison.json`.
Front and angle use neutral judging light; oblique uses the front camera with
directional light. Both layouts must have identical camera, lights, sampling,
render policy and source recipes. The gate checks current map and image hashes,
fresh native bindings and source/template identities, then requires at most one
RGB level difference between layouts. It rejects missing/stale cases and changed
comparison conditions; it does not award visual acceptance. Targeted adversaries
cover changed lighting, image payloads, case labels and excessive pixel error.

The default and golden-hazel native sets have passed the expanded decoder with
all fifteen maps. The remaining authoring/checks and thirty-render matrix are
still pending; the Blender slot remains occupied by frame-107 convergence.

All five native sets subsequently completed. Each passed the expanded independent
decoder (fifteen maps per set), recorded in `out/v22-native-{default,golden,olive,
deep,cool}-decoded-check.json`. A second cross-set manifest/payload check confirms
all sixty full-character map files remain unchanged; see
`out/v22-native-five-set-summary.json`. The scripted default restoration is
byte-identical to the previously inspected prototype color map. These results
do not qualify unrendered variants or replace human review.

The complete Windows suite passed **131 tests** with the new matrix gate
(`out/v22-wrap-matrix-tests.xml`). Testing against an older real receipt exposed
missing comparison fields; the checker now rejects these explicitly, with a
targeted regression, rather than accepting incomplete historical evidence.

Frame 107 at 512 samples completed and was visually inspected. Both irises are
covered at closure. Lash clusters remain visible on closed lids and need review
alongside reopening, rather than assuming image quality from geometry checks.
The matching 1024-sample reference is still rendering; no new motion-wide sample
preset or convergence pass is claimed.

The thirty-render native matrix is queued in execution session `66927`, waiting
on the original blink process handle (PID 12012, creation UTC
2026-11-19 11:25:04.941785). The serial controller
`out/v22_native_matrix_driver.py` checks both completed reference hashes before
starting, rejects any competing Blender process, freezes input/worker hashes
and records each case under `out/v22-native-five-wrap-matrix`. It uses 768px,
32-sample development comparisons, not a final detail-qualified preset. A failed
render or changed input stops the matrix without counting remaining cases.

New wrap receipts identify the actual Blender version/build. The matrix checker
requires the same build and judging conditions across both layouts and all five
variants. The queued matrix is not yet evidence of completed rendering.

The baked PBR 512-sample frame-107 closure now passes the independent image-only
gate against the matching neutral image: both pupils are detected in neutral
and neither remains detectable at closure. Evidence:
`out/v22-pbr-512-closure-image-check.json`. This covers this closure frame only;
reopening, directional poses and full final sequences remain separate gates.

Committed source `1fe7428` passes **131 tests on Linux** with networking disabled,
two CPUs and 3 GiB, clean extraction to `/tmp/clean path/Apollo`, and execution
from `/tmp`. See `out/v22-linux-code-1fe7428.log` and its hash-bound JSON receipt.
The 378,611-byte archive includes the code and test dependencies listed in that
receipt. A full historical source-asset archive was first attempted, but stopped
explicitly after observed slow bind-mount extraction; it has no qualification
result. Its log remains `out/v22-linux-full-source-extraction-attempt.log`.
Neither source test substitutes for final Windows/Linux delivery-archive tests.

Integer pose sequences currently contain 13 unique poses for Left, 13 for Right,
and 39 for Generate Motion. This supports planning exact hold reuse while still
delivering all 576 numbered PNGs; none of those final sequence renders is counted
as complete from this metadata alone.

### Blink convergence and review packet construction

Frame 107 completed at both 512 and 1024 samples. The unchanged thresholds pass
for 512: eye/lip/skin/hair mean absolute RGB errors are approximately
0.809/0.947/0.341/0.869, with p95 values 3/3/1/3 and detail ratios within
0.977–1.001. The comparison sheet was inspected without obvious additional
smearing at 512. Evidence is under
`out/v22-convergence-pbr-blink-107-analysis`. This adds peak closure to the
neutral-frame evidence; extreme gaze and reopening still require checks.

The thirty-case fresh-wrap controller started after the original process exited
successfully. The first front/default/UDIM case completed. Matrix completion,
layout agreement and visual acceptance remain pending.

`tools/gnm_v22_review_packet.py` now builds randomized review packets from an
explicit JSON source specification. Appearance entries carry `candidate`,
`variant`/`output` or `reference`, and an `images` list of `{file,sha256}`.
Direction entries carry `expected`, `neutral` and `judgment` image records.
Motion entries carry `candidate`, `mode` and a `scene` record. Paths resolve
relative to the specification. All five full/native pairs, rc.5/v22 references,
four cardinal directions and three motion modes are mandatory. The complete
source specification is hashed into the candidate identity.

The reviewer ZIP includes anonymous sheets, metadata-free full-resolution views,
anonymously named packed-scene copies and blank scorer-compatible responses.
The assessor key stays outside the ZIP. Instructions disclose that Blender
internals can reveal a mode, request independent first-pass review and do not
present viewport shading as rendered appearance evidence. Input hashes are
rechecked after construction. The packet builder authenticates selected input
bytes; it does not itself qualify Blender playback or invent human approval.
No actual new candidate review packet or responses have yet been produced.

The packet builder's end-to-end packaging test confirms the assessor key is
excluded from the reviewer ZIP, the response fields remain unset, full-size
anonymous image copies and all three scene slots are included, and every shipped
payload matches the assessor hashes. Changed payloads and missing variant scope
are rejected. The complete Windows suite passes **133 tests** in
`out/v22-review-packet-tests.xml`; this packaging fixture does not establish
real-scene playback or supply any human ratings.

The actual new default front pair completed with maximum absolute RGB difference
one, p95 zero, and nineteen changed pixels at 768px. Evidence is
`out/v22-native-default-front-layout-check.json`. The UDIM front image was
visually inspected and retains the restored scalp/brows. The other twenty-eight
matrix cases remain pending at this checkpoint; no broad five-set UV pass is
claimed from the single pair.

The default's three front/angle/oblique pairs subsequently completed: maximum
absolute RGB difference one in each pair, p95 zero, with 19/28/30 changed pixels
respectively. See `out/v22-native-default-completed-view-checks.json`. Its angle
UDIM image was inspected; no flat scalp cap or obvious gross wrapping break is
visible at this development scale. Other variants are now rendering.

Source `fb731e9` passes **133 tests on clean offline Linux** in the same pinned
qualification image, with code-only extraction into a path containing spaces
and execution from `/tmp`. Evidence: `out/v22-linux-code-fb731e9.log`.

Execution session `9771` waits on the verified matrix-controller process handle
(PID 15804, creation UTC 2026-11-19 12:27:19.7662813). Only a successful completed
matrix gate permits the next single Blender experiment: frame 112 at 512/1024
samples, followed by its independent convergence analysis. This reopened-lid,
upward-gaze pose has not yet rendered and supplies no acceptance evidence yet.
Its frozen source scene, repaired maps, worker and judging policy are unchanged.

### Packed PBR review preparation queue

The still-review worker now supports `--maps` and `--layout`: authenticated
original-shader inputs receive the explicit full-character PBR binding; saved
PBR inputs must already validate their packed bindings. The worker applies the
shared judging policy, strips variable/private PNG metadata before hashing and
records source, audit, map, recipe and Blender-build identities. Inputs/recipes
are rechecked after rendering. The source scene is never saved. Syntax checks
and the existing **133-test** Windows suite pass; actual new Blender execution
is queued and must pass before claiming this worker qualified.

Session `61748` waits on the exact reopened-experiment controller handle (PID
16260, creation UTC 2026-11-19 12:32:53.3739879). After that controller exits,
`out/v22_prepare_review_driver.py` requires successful matrix evidence and
512-sample passes for neutral, closure and reopening before packing all three
development timelines under `out/v22-review-pbr-512`. It runs reopened checks at
all 383 integer/half-frame times and whole-character neutral appearance checks
for each saved file. Four 1024px/512-sample cardinal stills follow on the saved
Generate Motion candidate. Every Blender subprocess is serial and its exit is
checked. No queued stage is counted as completed evidence. Final visual
acceptance, frozen regeneration and release gates remain outstanding.

### Development runtime staging

`gnm_v22_stage.py` stages the explicit runtime Python dependency closure, five
complete sets, three packed scenes, the default character and fresh native
template. It requires current scene-bound preparation, all 383 integer/half-frame
checks, the current verifier recipes, eighteen-component appearance evidence and
matching map manifests/selected identities. Every copied payload is rehashed.
Its manifest labels the output as a development rehearsal, excluding any claim
about final sequences, licenses, human approval or release completeness.

The queued prepare driver now uses the default set containing native-only extras,
after checking that every full-character map still matches the convergence master.
Thus full-character and texture-only runtime bindings share one manifest without
changing the active full-character maps. Targeted tests reject altered scenes and
narrow motion evidence, and launch the copied public CLI with isolated Python path
handling from outside its project. The complete Windows suite passes **135 tests**
(`out/v22-runtime-stage-tests.xml`). Actual Blender runtime rehearsals are pending.

Session `60776` waits on the verified review controller (PID 23852, creation UTC
2026-11-19 12:37:53.3309469). After completed packed checks/cardinal renders, it
runs the independent four-direction/closure/reopening image gate and stages only
on success, into `out/v22 runtime rehearsal`. A failure stops without counting
the stage as complete. The new stage directory does not replace prior trials or
the qualified fallback.

Source `1a73e00` subsequently passes **135 tests on clean offline Linux** under
the same pinned image, resource limits, space-containing extraction path and
outside-project CWD. Evidence: `out/v22-linux-code-1a73e00.log`.
The first four native variants completed all three UV pairs: twelve pair checks
pass with maximum RGB difference one; see
`out/v22-native-completed-pairs-check.json`. Cool-grey remains in progress, and
the final matrix-wide authentication gate has not yet run.

### Completed native matrix and neutral-deep color trial

All thirty native fresh-wrap renders completed, and the matrix-wide checker
passed all fifteen variant/view UV pairs with maximum absolute RGB difference
one. It authenticated current maps, targets, workers, image payloads, Blender
build and shared judging conditions. Evidence:
`out/v22-native-five-wrap-matrix/layout-check.json`. This proves the stated
development wrapping/layout scope, not final image-detail or human acceptance.
Frame-112 convergence began serially after the matrix process exited.

The five-way front/detail sheet in `out/v22-native-front-review` was inspected.
It exposed excessive orange saturation in neutral-deep. That variant remains
visually unaccepted despite its successful technical UV checks. The original
sets and all default v22 maps are preserved.

An isolated neutral-deep pigment trial uses broader, less channel-separated
darkening: authored attenuation coefficients `(0.98,1.0,1.08)` replace the prior
deep-palette `(0.54,0.94,1.35)`. Other palettes retain their coefficients. The
authoring CLI can select `--variants neutral-deep` for an isolated output; its
default still builds all five. `out/v22-neutral-deep-pigment-v2` changes only
skin base color, preserving all eleven other map files. The covered-atlas median
red/blue ratio falls from approximately 5.75 to 2.32; this measures color change,
not realism. Hash/statistical evidence is
`out/v22-neutral-deep-pigment-v2-check.json`.

The separate native restoration trial is being generated under
`out/v22-neutral-deep-native-v2`. A matched 768px/32-sample front preview is added
to the queued review-preparation driver after frame-112 convergence and before
packing. It must be visually inspected before choosing or regenerating revised
five-set delivery inputs. No corrected render or acceptance is claimed yet.

The Windows suite remains **135 passing tests** after the isolated palette and
authoring-selection changes (`out/v22-neutral-deep-trial-tests.xml`). These
source checks do not substitute for the queued corrected-color Blender preview.

### Retained source licenses and texture linkage

The pinned local Google GNM checkout was independently confirmed at Git revision
`f84cdbdc86a34f55627526f137495f864e687679`, with a clean tracked LICENSE file.
The existing qualified-package copy matches its checked-out bytes. Git's license
blob differs only in LF versus Windows CRLF; `assets/gnm/LICENSE.txt` now retains
the exact upstream Git blob, SHA-256
`ba12fffb7f905c67daa3e0d9656e8638d3a0d0eee70862ec17da7db429be19f0`.
Git attributes preserve those bytes. `assets/gnm/source.json` records source/model
revisions, checksums and modifications. The v22 inventory now pins both records;
the prior eight source-record hashes are unchanged.

`gnm_v22_attribution.py` collects all pinned source records, retains upstream
license/notices, and writes component attribution with explicit photographic
resolution limits and five texture-manifest hashes. The actual development
bundle is `out/v22-attribution-development-v2`; its previous first output is
superseded because source JSON line endings were normalized before the final
development collection. No map or scene was changed by this work.

Independent checks rehashed every collected file, resolved the generated local
links, confirmed exact GNM license bytes and rechecked all five manifest hashes.
The complete Windows source suite remains **135 passing tests** in
`out/v22-attribution-tests.xml`. This establishes retained source documentation
and development manifest linkage; the final frozen maps and release archive
still require a regenerated attribution bundle and archive-inclusion check.

### Interrupted job recovery and corrected-color preview

The original frame-112 process and all waiting controllers were confirmed absent
from the process inventory; their execution handles were unavailable. The log
ends at 497/512 and no completed render receipt exists. This attempt is not
qualified. Its directory/log are preserved with the `-interrupted` suffix.
The frozen worker, judging policy and raw source scene hashes were checked
against the preceding experiment before restarting the unfinished run.

Recovery session `14560` first rendered the isolated neutral-deep v2 front
preview in `out/v22-neutral-deep-v2-review`. The image was inspected: its color
is more balanced brown, with the earlier excessive orange reduced. This is a
development assessment, not human acceptance or final-detail qualification.
The original five-set matrix remains valid for its original inputs; it does not
qualify the revised palette. Six corrected-palette view/layout renders are now
part of the queued prepare driver, followed by pair comparisons.

The recovery then restarted frame 112 with the same frozen inputs and will run
its analysis and review-preparation driver serially. The old waiting sessions
`9771`, `61748` and `60776` are no longer live. Their image gate and runtime-stage
continuation are now performed directly by the prepare driver after successful
packed checks and cardinal renders. Queued results remain pending.

All ten source records in the updated provenance inventory were independently
rehash-checked against committed Git blobs, including exact upstream license
bytes. The working tree was clean before this recovery documentation change.

### Actual runtime recovery rehearsal queued

The queued prepare driver now invokes
`out/v22_windows_runtime_rehearsal.py` after successful staging. It builds a
development ZIP from the runtime manifest, checks each source payload, extracts
into a path containing spaces, and rehashes every extracted file. It invokes the
copied public CLI from a separate outside-project CWD, rendering frames 1–3 with
the saved 512-sample preset. It then corrupts frame 2 and removes frame 3, resumes,
and requires exact restored hashes plus unchanged frame-1 modification time.
Negative invocations must reject a changed sample receipt and frame range
193–194 without altering valid images. Each subprocess exit is checked.

Both controller scripts pass syntax compilation. This is prepared, pending
execution, and covers three held frames on the development runtime only. It
does not replace full 576-frame rendering/recovery, alternate-cache checks or
final Windows/Linux archive qualification. The recovered frame-112 renderer is
confirmed live as PID 17212 (creation UTC 2026-11-19 13:42:46.4742995), with
advancing sample output; no second Blender process was launched.

### Baked reopening visibility and owner identity review

The recovered 512-sample frame 112 completed. Independent image checks detect
both pupils after reopening and neither at peak frame-107 closure; neutral iris
template correlations after reopening are approximately 0.848 and 0.940, above
the unchanged 0.8 threshold. The reopened image was also visually inspected.
Evidence: `out/v22-pbr-512-closure-reopening-image-check.json`. The 1024 reference
continues, so this visibility pass does not yet establish reopening convergence.

`out/v22-owner-identity-review` contains a hash-bound comparison of the exact
approved v22 portrait and the integrated neutral/closed/reopened PBR images.
The approved reference checksum matches `final-selection.json`. Lighting and
framing differ between the original portrait and motion judging camera; this
sheet is for identity review, not pixel equivalence. The user was asked whether
the integrated face and groom retain the approved identity. Approval remains
unset pending their explicit reply. This is separate from independent blind
review and final submission acceptance.

### Corrected five-set development assembly

`out/v22-variants-native-skin-v2` is a separate completed trial assembly. Its
rose-brown, golden-hazel, olive-amber and cool-grey sets are byte-identical to
their original native sets, including manifests. Only neutral-deep is drawn
from the isolated corrected/restored trial. Every copied map and manifest was
rehashed against its source, all fifteen-map manifests were validated, and all
source manifests were rechecked after copying. Evidence: its `assembly.json`.
Original map directories remain preserved.

The pending prepare driver now validates all five assembled sets and explicitly
checks that the default manifest is unchanged. It stages this corrected trial
only after the queued six corrected-color renders and their three layout-pair
checks pass, alongside the packed scene and image gates. This does not select
the palette as visually accepted or freeze it for final delivery. Attribution
is being regenerated against the assembled trial manifests rather than reusing
the prior neutral-deep hash. Owner identity approval remains pending.

### Five-set appearance render queue

The prepare driver now continues after the clean Windows runtime rehearsal with
`out/v22_render_review_appearance.py`. It invokes the public `still` command
from the extracted development runtime for each full-character variant, keeping
the saved 512-sample preset. Each result must be 1024px, bound to the extracted
character scene, and match its image receipt. Five native-only 1024px/512-sample
front renders follow serially using the corresponding extracted texture sets,
fresh native target and pinned template. Both output types retain source-bound
receipts under `out/v22-five-set-appearance-review`.

These ten stills are queued, not completed. Their fixed development sample
setting is not a claim that every variant/view has independently passed final
detail convergence. The controller scripts pass syntax compilation. This work
prepares actual appearance inputs for the blinded review packet without
inferring ratings, selecting the revised palette, or approving the final release.

### Completed reopening convergence

The recovered frame-112 experiment completed successfully. All four 512-sample
crops pass against 1024 samples under the unchanged limits: mean absolute RGB
errors for eyes/lips/skin/hair are approximately 0.783/0.946/0.316/0.877, with p95
3/3/1/3 and detail ratios 0.998/1.001/0.987/0.971. The comparison sheet was
inspected without obvious added smearing at the lower count. Evidence:
`out/v22-convergence-pbr-reopened-112-analysis`.

`out/v22-three-pose-render-profile.json` binds the three completed analysis files
and their authenticated source receipts for frames 1, 107 and 112. It records
512 as a development judging profile and explicitly does not mark a final
delivery preset or qualify untested variants/poses. The prepare controller
advanced to the corrected neutral-deep view/layout renders; no additional
Blender process was launched in parallel. Identity approval remains pending.

### Corrected five-set wrap gate completed

All six corrected neutral-deep renders completed. Front, angle and oblique
layout pairs each differ by at most one RGB level (p95 zero), with 27/29/35
changed pixels respectively. Angle and oblique images were inspected: the
earlier orange cast is reduced. These development-scale views still do not
establish final-detail quality or human acceptance.

`out/v22-corrected-five-wrap-evidence` consolidates the four unchanged variants'
original receipts/images with the corrected neutral-deep receipts/images.
The full matrix checker passed all thirty cases against
`out/v22-variants-native-skin-v2`, rechecking current manifest/image/recipe hashes,
target/template identity, Blender build and matching judging conditions. Its
`layout-check.json` is the corrected five-set development UV evidence. The
original matrix is retained separately and is not relabeled.

The saved Left PBR timeline was prepared at 512 samples with geometry/UV
preservation assertions passing. Its reopened integer/half-frame verification
is currently running; no completed Left motion pass is claimed yet. The right
and Generate Motion checks, cardinal stills and runtime rehearsals follow
serially under the same live controller.

The Left saved PBR scene subsequently passed all 383 integer/half-frame checks
and its eighteen-component whole-character neutral appearance check.
`out/v22-review-pbr-512/left/half-frame-check.json` reports no errors, and
`appearance-check.json` records the separate neutral comparison. Right-scene
preparation has started. These results validate the saved development PBR Left
timeline; they do not qualify unrendered full sequences or other modes yet.

The saved Right PBR timeline also passed all 383 integer/half-frame geometry,
attachment and resource checks and its eighteen-component neutral appearance
check (`out/v22-review-pbr-512/right`). Generate Motion preparation has started.

An actual partial Linux ZIP rehearsal is queued in session `44176`, waiting on
the verified live review controller PID 15840, whose command runs
`out/v22_prepare_review_driver.py`. After the Windows sequence exits, the watcher
requires its successful clean-archive rehearsal report, then invokes
`out/v22_linux_runtime_rehearsal.py`. The Linux script uses the immutable local
qualification-image ID with networking disabled, four CPUs and 6 GiB. Only the
development ZIP and an evidence output directory are mounted; it extracts to
`/tmp/clean path/Apollo`, rechecks all manifest payloads, and invokes the extracted
public CLI from `/tmp` for three held frames. It checks output receipt hashes
and records the image/archive identities. Syntax compilation passes, but this
rehearsal has not executed yet. Full sequence, alternate variant, cross-platform
image comparison and final archive qualification remain separate requirements.

### Three saved PBR timelines checked and review references authenticated

Generate Motion passed all 383 integer/half-frame checks: maximum native error
approximately `3.64e-12 m`, derived error `1.82e-12 m`, eye error zero, twenty-one
packed image resources and no attachment-limit errors. Its whole-character
neutral check also passed for eighteen visible components. All three newly
packed development PBR timelines now have these completed saved-scene checks.
The controller advanced to four 1024px/512-sample cardinal review renders.
This does not establish completion of their final 576-frame PNG delivery.

The rc.5 reference ZIP was rehashed against its committed candidate receipt:
`5f4c0e8b849da9f22f6de09b46207d0d95f7a791fc8209b06f3a5706b1a2ed6c`.
The rose-brown judging image was read from that authenticated ZIP and matched
its embedded render receipt. The selected v22 reference image also matched
`final-selection.json`. Both are retained in `out/v22-review-references` with
their provenance record. Their camera/light/sample differences are disclosed;
they are visual references, not a matched pixel-improvement experiment.

After the remaining appearance renders, their controller now writes an explicit
hash-bound review specification and invokes the repository packet builder for
ten full/native variant cases, the two references, four cardinal cases and three
packed motion scenes. The planned output is `out/v22-independent-review-packet`.
Response fields remain blank, and the answer key is kept outside its reviewer
ZIP. Syntax compilation passes. Packet creation and human review remain pending.

### Alternate-cache rehearsal coverage added

The release-checklist audit identified that the queued runtime checks covered
the default variant but not a new alternate motion cache. After its Linux run
returns and the container has exited, the not-yet-started Linux controller now
invokes `out/v22_alternate_cache_rehearsal.py` serially on Windows. It uses the
extracted public CLI for olive-amber/legacy Generate Motion frames 1–3, then
requires cache reuse without rewriting the cached scene or valid images. It
temporarily changes the cache receipt's scene hash, requires rejection, restores
the original receipt bytes in a finally block, and checks that the source scene
and all valid frames are unchanged. This avoids relying solely on a unit test
or the older development cache.

Both helper scripts pass syntax compilation. The actual alternate-cache run is
pending behind the existing review/Windows/Linux sequence. Its scope is three
held frames; final alternate blink/gaze samples and final release validation
remain outstanding. No second Blender process was started during this audit.

### Corrected-set encoding coverage and explicit identity approval

The corrected neutral-deep native set independently passed all fifteen map
encoding checks, including restored color, roughness and the 16-bit RGBA brow
overlay. `out/v22-corrected-five-set-encoding.json` links this report and the four
unchanged sets' decoder reports to their exact current manifests/payload hashes.
All seventy-five corrected trial map files have decoder evidence. This covers
data integrity, precision, dimensions and normals, not final visual acceptance.

The user explicitly answered the comparison question: **“Yes, keep this v22
identity.”** The owner face/groom identity gate is therefore passed for the
reviewed character. `out/v22-owner-identity-review/identity-approval.json` records
the response and binds it to the original review manifest, comparison sheet and
four authenticated source images; those hashes were rechecked before recording.
The approved v22 source remains unchanged. Independent visual/motion ratings,
final frozen regeneration, full PNG sequences and archive qualification remain
outstanding and are not implied by this identity approval.

### Branch handoff preflight

A successful fresh `git fetch origin` confirmed that the submission branch at
`49450ee` and main at `5b85e82` are ancestors of the integration branch. At
integration checkpoint `b72a8be`, neither remote branch had a commit missing from
the integration history; integration was 119 commits ahead of submission and
150 ahead of main. Exact full commit IDs/counts are retained in
`out/v22-branch-reconciliation-preflight.json`. This checks ancestry without
touching other worktrees or branch pointers. Final reconciliation must recheck
remote state after qualification, then identify the exact released commit to
the team; the preflight is not a merge, release or submission handoff.
