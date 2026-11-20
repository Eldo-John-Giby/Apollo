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
| Texture-only result (60) | Engineering/reviewers | Convincing neutral and oblique-light appearance on fresh native target | ten full/native fronts; twenty angle/oblique images; wrapping matrix; blinded packet | PARTIAL: all five native front/angle/oblique sets complete; deep-native sample/detail gap and independent acceptance pending |
| Full v22 result (60) | Engineering/user | Identity retained with groom and geometry; sharp, consistent comparison settings | fixed candidate judging collection; original receipts; owner approval | PARTIAL: identity approved; five full/native front and studio sets authenticated and reused; remaining sample optimization waived; independent acceptance and final archive qualification pending |
| Render convergence | Engineering | Samples preserving eye/lip/skin/hair detail; remaining optimization explicitly waived by user | motion profile; front measurements; stopped-by-owner record | PARTIAL: motion 512 passes three poses; full front 2048 passes default/deep/cool, native fronts pass four at 512 and deep at 1024; user selected conservative 2048 full/1024 native profiles and stopped olive/golden experiments without inferring measured convergence |
| Three motion modes (20) | Engineering | Left/right/generate-motion; 192 frames each at 24 fps; viewer-screen convention | `out/v22-review-pbr-512/*/expression.blend` | PARTIAL: three packed timelines checked; final 576 numbered PNGs pending |
| Kinematic checks (20) | Engineering | Binocular fixation, eye integrity, closure/reopening, smooth lids/expressions | three saved-scene half-frame checks; native interpolation receipts | PARTIAL: geometry/attachment checks pass at 383 times per mode; rendered full-motion and human gates pending |
| Image checks (20) | Engineering | Independent pupil/direction checks; peak occlusion and restored visibility | Generate Motion gate; `out/v22-{left,right}-full-detail-followup/followup.json`; preview checks | PARTIAL: full-detail Generate Motion cardinal/closure/reopening and both standalone Left/Right direction/closure/reopening pass; original preview failure retained; final rebuilt frames pending |
| Exact reset | Engineering | Deterministic neutral reset and same-build reproduction | mode recovery; pose sequences; complete-inventory verifier | PARTIAL: fresh Left neutral byte-identical; repeated held frames verified; complete final PNG reset inventory pending |
| Offline playback (20) | Engineering | Reopened packed scenes without paths, MCP, MPFB or GNM authoring environment | three reopened PNG playback checks; clean Windows/Linux runtime reports | PARTIAL: all three development playback scenes reopened; clean offline development archive renders pass both platforms; final archive pending |
| Stable CLI (20) | Engineering | still/left/right/generate-motion; variant/layout/output/frame options retained | source tests, extracted stills and runtime rehearsals | PARTIAL: contract retained; default Generate Motion and all five stills exercised; complete final-mode qualification pending |
| Recovery (20) | Engineering | Resume, missing/corrupt repair, stale-cache rejection, invalid-input rejection | Windows clean archive, other-mode recovery and alternate cache reports | PARTIAL: all three modes pass three-held-frame repair/stale/invalid-range checks; olive-amber legacy cache reuse/rejection passes; final archive pending |
| Cross-platform reproduction (20) | Engineering | Clean Windows/Linux extraction; spaces and different CWD; pinned Blender | both clean runtime reports; `out/v22-cross-platform-image-comparison.json` | PARTIAL: three held frames pass runtime on both; RGB max 5/255, mean 0.0096/255; no broader tolerance or final sequence pass claimed |
| Independent review | User + 3–5 reviewers | >=95% cardinal accuracy; median >=4/5 each category; no severe defect shared by two reviewers | authenticated randomized ZIP and separate private key | READY FOR REVIEW: packet integrity passes; zero actual response files received |
| Final identity approval | User | Explicit approval of integrated hero as retaining v22 | `out/v22-owner-identity-review/identity-approval.json` | PASS for the reviewed integrated face and groom; final release gates remain separate |
| Freeze and full qualification | Engineering | Regenerate final deliverables after acceptance; bind source/scenes/maps/frames/tests | final manifest and all applicable tests | Pending |
| Package hygiene | Engineering | No credentials, personal paths, unlicensed or development artifacts | pinned attribution; development text/binary scans; reopened UI probes | PARTIAL: attribution/text checks pass; original binary UI path identified and cleanup proven on native/character copies; final sanitized archive pending |
| Judge documentation | Engineering | Verified setup, modes/variants, playback, evidence, compatibility, limitations | README; `docs/V22_QUICKSTART.md`; submission audit | PARTIAL: v22 setup and scope corrected; final release locations and frozen evidence pending |
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

All four full-detail cardinal images and five full/native front pairs are
complete. The blinded packet contains 576 lower-cost timing PNGs and twelve
appearance cases. Default clean development runtime rendering passes on Windows
and Linux; final archive qualification remains separate. Alternate-cache and
additional Left/Right recovery rehearsals pass. Both full-detail Left/Right image gates,
twenty angle/oblique stills and native/character UI-cleanup probes are complete.
The higher front-reference batch is complete: deep native passes at 1024,
while hair rejects all five full fronts at 1024. The default 2048-vs-4096
comparison now passes all regions, as do deep and cool. The user subsequently
stopped further sample experiments and accepted conservative settings plus reuse
of verified unchanged inputs. The fixed technical build is now running in
`out/v22-fixed-technical-candidate`, with new packed scenes, reopened checks and
all 576 production-size PNGs at the measured 512-sample motion profile.
Queued work is not a pass.
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

### First packed-candidate cardinal image checked

The 1024px/512-sample frame-26 image completed from the saved PBR Generate
Motion scene. The independent image oracle detects screen-left pupil shifts
of approximately 9.09 and 6.16 pixels, with neutral iris-pattern correlations
0.914 and 0.835, above the unchanged 0.8 threshold. Closure and reopening remain
passing in the same invocation. Evidence:
`out/v22-pbr-512-left-blink-reopening-check.json`. The rendered image was inspected.

This is a completed-image pixel check, not yet the final source-bound four-image
batch receipt: the still worker writes that receipt after all requested frames
finish and its source/recipe rechecks pass. The renderer has moved on to frame
58. Right/down checks, the remaining requested up image, blind direction
readability and full-sequence qualification remain pending.

### PNG timing preview preparation

A separate motion-only PNG preview is prepared to avoid depending on dense-groom
viewport speed for timing review. `out/v22_prepare_motion_preview.py` derives a
new scene from each checked 512-sample development timeline, requires its
192-frame/24-fps timing, and changes only sampling/resolution to 32 samples and
512px plus a relative output path. The original scene hash must remain unchanged.
`out/v22_render_motion_previews.py` renders and verifies all 192 PNGs per mode
with exact hold reuse, preserving per-frame receipts. It creates no encoded
video or presentation, and its images are explicitly excluded from skin/eye
appearance ratings and final 1024px delivery qualification.

The appearance controller, which has not started yet, now queues these previews
after its ten full/native stills and before packet assembly. Both new preview
helpers pass syntax compilation; actual preview rendering and playback packaging
remain pending. The live 512-sample cardinal batch was left unchanged.

### Anonymous PNG playback packaging

The packet builder now accepts an optional motion `preview` with `fps: 24`, a
hashed `playback` scene and exactly 192 ordered hashed PNG records. It validates
these before creating the output, then copies them to anonymous
`Mxx-preview/frames` directories alongside `playback.blend`. Nested payloads are
included in both the reviewer ZIP and assessor checksum inventory. Instructions
separate 512px/32-sample timing review from full-detail appearance ratings.
The image-sequence scene is generated from factory startup, with relative frame
paths; no video encoding is involved. Actual playback generation/reopening is
still pending and must be checked in Blender.

An end-to-end packaging regression covers all 192 frame payloads and playback
file inclusion, rejects incomplete/reversed sequences, and rejects a changed
frame before creating the packet directory. The complete Windows suite passes
**136 tests** (`out/v22-review-sequence-tests.xml`). These fixture tests validate
packaging behavior, not actual motion playback or human acceptance.

The clean offline Linux source attempt for `49652af` could not start because
the Docker Desktop Linux engine pipe was absent. Its log is
`out/v22-linux-code-49652af.log`; it contains no test pass. Docker Desktop was
launched hidden and its backend startup processes were confirmed, but engine
readiness is still pending. The existing Windows Blender cardinal process
remains live and was not restarted. Prior Linux source-test passes retain their
original commit scope; they do not qualify the new packet sequence code.

### Both horizontal cardinal images checked

Frame 58 completed and was visually inspected. The independent image oracle
finds rightward pupil shifts of approximately 9.22 and 6.40 pixels, with iris
pattern correlations 0.874 and 0.841. Together with frame 26, both horizontal
directions, closure and reopening pass the unchanged pixel checks in
`out/v22-pbr-512-horizontal-blink-check.json`. The batch's final source/recipe
receipt remains pending until all four frames finish. Frame 93 is now rendering.
Human direction readability and full-sequence validation remain separate gates.

The previously pending documentation push through `86e6ec5` completed
successfully. Docker readiness queries remain pending; the Windows renderer
continues independently and has not been restarted.

### Reviewer availability and playback round-trip preparation

The user confirmed they can arrange 3–5 independent reviewers when the blinded
packet is ready. This establishes reviewer availability, not completed reviews
or ratings. Packet delivery and returned responses remain pending.

The Docker backend logs report repeated engine ping timeouts. A bounded
`wsl --list --running` query also timed out after twenty seconds. No system or
Docker restart was performed, and the Windows cardinal render remains live.
Linux source/runtime checks remain pending; earlier passes retain their original
commit/artifact scope.

The queued PNG playback authoring helper now sets the strip's duration explicitly
to 192 frames. A separate Blender reopen worker requires one IMAGE strip, exactly
192 ordered elements, range 1–192 at 24 fps, relative `//frames/` paths and exact
agreement with every source PNG render-receipt hash. The preview controller runs
this worker after each save. Syntax compilation passes; actual playback creation,
round-trip checks and visual timing review have not run yet.

### Upward cardinal image and authorized backend recovery

Frame 93 completed and was inspected. Both pupils pass the upward-direction
image check: vertical shifts approximately -5.74/-7.45 pixels with iris-pattern
correlations 0.903/0.949. All three completed cardinal images pass together in
`out/v22-pbr-512-three-cardinal-check.json`. Frame 130 is now rendering. The final
batch receipt, downward check and independent human readability remain pending.

The user explicitly authorized restarting Docker and shutting down WSL,
including the disclosed impact on other sessions/containers. Docker Desktop
backend processes were stopped, `wsl --shutdown` returned exit code zero, and
Docker Desktop was relaunched hidden. Bounded engine probes still report startup
pending, so no Linux pass is claimed. Windows Blender PID 744 continued rendering
through this recovery and was not restarted. The queued PNG playback helpers
also now explicitly require a Standard/None display transform, zero exposure and
unit gamma to avoid adding another filmic transform to rendered PNGs; actual
playback round-trip execution remains pending.

### Cardinal gate, Linux source retry and partial Windows archive pass

All four 1024px/512-sample cardinal images completed. The final still-worker
receipt was checked against the current packed Generate Motion scene, each
worker/PNG-policy hash and every rendered image. The combined image oracle in
`out/v22-pbr-512-direction-and-blink-check.json` passes left/right/up/down,
peak closure and reopening. Downward pupil shifts are approximately 6.80/5.83
pixels, with iris correlations 0.815/0.914. The down image was visually inspected.
This does not replace independent human direction/readability review.

After the authorized restart, Docker engine 28.3.2 responded. The clean offline
source test for `49652af` was retried successfully: **136 tests pass**, logged in
`out/v22-linux-code-49652af-retry.log`. The failed first attempt remains retained.

The development runtime staged successfully. Its original Windows archive
rehearsal process later stopped during the first frame without a pass receipt;
process inventory and its missing execution handle confirmed it was no longer
live. Recovery session `38969` verified the existing ZIP manifest, rehashed all
archive/extracted payloads, and resumed without recreating the checked scenes.
The recovery helper now supports this existing authenticated extraction.

`out/v22 clean archive rehearsal/rehearsal.json` now records a completed partial
Windows pass: three held frames rendered from outside the extracted project
in space-containing paths, exact corrupt/missing-frame repair, valid frame-1
hash/mtime preservation, stale-receipt rejection and invalid-range rejection.
The saved receipt is linked to the runtime manifest and ZIP hash. This covers
three held frames on the development archive, not the final full delivery.
The controller advanced to full/native appearance renders, then will produce
timing previews and the blind packet; Linux runtime and alternate-cache checks
follow serially. Those later stages are not yet passed.

### Appearance review progress after pause/resume

On resuming the goal, the appearance controller and its Blender child were
confirmed live. Rose-brown and golden-hazel completed both full-character and
fresh native front renders at 1024px/512 samples. Their receipts were checked
against the extracted runtime character hash, current per-variant map-manifest
hashes, actual image hashes and identical pinned Blender build `5afeabba6097`.
The partial evidence summary is `out/v22-completed-appearance-pairs.json`.
Both full-character images were inspected and retain the approved face/groom.
This is development inspection, not independent visual acceptance.

Olive-amber's full render completed and its native render is now running. The
remaining pairs, PNG timing previews, blind packet, Linux runtime and alternate
cache rehearsal remain pending. Background jobs were inspected rather than
restarted on resume; no completed render was discarded.

Olive-amber's completed full/native pair was subsequently inspected and passed
the same receipt checks. `out/v22_check_completed_appearance.py` now additionally
compares every map input recorded by each completed full render with the actual
extracted runtime map files, including the PBR manifest and optional native
maps. It requires the saved character hash, output image hashes, 1024px/512
settings and pinned Blender build. The refreshed partial summary reports three
completed authenticated pairs. This audit does not count absent variants or
award human acceptance. Neutral-deep's corrected full-character render is live.

Neutral-deep's corrected full-character 1024px/512-sample render subsequently
completed and was inspected. The previous excessive orange cast is reduced;
face and groom remain present. Its native counterpart is currently rendering,
so the fourth completed pair is not yet counted. Independent review remains
required before selecting this trial for final frozen regeneration.

The pending Linux runtime helper now creates a uniquely named, network-disabled
container and copies the complete development ZIP into it with `docker cp`.
Before extraction the container verifies the archive against the streamed host
SHA-256. This avoids slow random ZIP reads over the Windows bind mount while
preserving the complete archive scope. Only the evidence output directory is
bind-mounted. Container command exit status is checked explicitly, and a finally
block removes only this named rehearsal container. Syntax compilation passes;
the actual Linux runtime run remains queued, not qualified.

Neutral-deep's native render completed and was inspected. The fourth full/native
pair passed the exact runtime-map, character, image/settings and build audit;
`out/v22-completed-appearance-pairs.json` now lists four pairs. Cool-grey's full
render is currently live. The corrected deep palette remains a review candidate,
not independently accepted for final frozen delivery.

The not-yet-started motion-preview controller now first invokes
`out/v22_appearance_contact_sheets.py` after all ten judging images complete.
It requires the source receipt image hashes and 1024px dimensions, then creates
separate five-variant full/native overview sheets and native-pixel eye, skin,
lip and ear crops, with a source/output hash receipt. Overview resizing is
explicit; crop files retain source pixel scale. Syntax compilation passes;
the sheets/crops have not been generated yet and imply no review approval.

### All ten appearance renders completed; playback recovery

All five full/native 1024px/512-sample front pairs completed and passed the
exact image/runtime-map/build audit. `out/v22-completed-appearance-pairs.json`
now records five pairs. Both five-variant overview sheets and native-pixel
detail crops were generated in `out/v22-five-set-contact-sheets`, with hashed
source/output records. The full-character overview was inspected. These are
review inputs, not independent human acceptance.

The Left motion preview rendered and verified all 192 PNGs. Its playback save
failed because the headless Blender area still exposed `SpaceView3D` immediately
after changing the area's type. The helper now looks for an actual sequencer
space before assigning preview mode. The corrected playback saved and reopened
successfully: `out/v22-motion-review-previews/left/playback-check.json` confirms
192 ordered hashed frames at 24 fps, relative paths and the required display
settings. This structural pass does not replace visual timing review.

The stopped controller was not restarted wholesale. Session `28745` resumes
motion previews, checking existing preview scene/source hashes and letting the
renderer retain valid PNGs. It then queues Linux runtime and alternate-cache
checks. Packet assembly remains pending after the remaining previews; the
earlier appearance controller exited before writing its final review packet.

### Independent review packet ready; runtime rehearsal live

All three timing previews now contain 192 verified PNGs and passed reopened
relative-path playback checks. The blinded packet is available at
`out/v22-independent-review-packet/apollo-v22-independent-review.zip`.
Its separate `integrity-check.json` verifies 618 payloads, 576 preview frames,
12 appearance cases, four cardinal cases and three motion cases. ZIP SHA-256:
`9902410c57c552a19fd9cbd853f806d78c8f3b1c0a5050e78d645cc44ee303e9`.
Only the public ZIP is intended for reviewers; `assessor-key.json` stays private.
Actual independent responses received: zero. Identity approval remains separate.

The previews use 512px/32 samples for timing, while appearance/cardinal images
use 1024px/512 samples. The ancillary Right preview pupil diagnostic passes.
Left's screen-right iris correlation is 0.7508, below the unchanged 0.8
threshold, so `out/v22-left-timing-preview-image-check.json` remains failed.
Both pupils are visible on inspection, but this does not override the failed
diagnostic. A full-detail Left-mode extreme/reopening follow-up remains pending;
the passing Generate Motion cardinal check does not cover its larger amplitude.

The network-disabled Linux clean-archive rehearsal container is confirmed live
and rendering its first frame with the pinned runtime. No Linux runtime pass
or alternate-cache pass is claimed yet. Final frozen regeneration, 576
final-quality delivery PNGs, independent acceptance and final release/archive
qualification remain incomplete.

### Non-review continuation and Linux measurements

At the user's request, continue all work independent of human review while they
sleep. The review gate remains pending, and the agreed post-acceptance final
freeze is retained. No videos or presentations are created.

`out/v22 Linux runtime rehearsal/rehearsal.json` now records a successful
network-disabled, clean-extraction development runtime run with pinned image
`sha256:beb58a3d91e8169f6df8c989da2703f1c0fbfcc45bdcdf1d21c6c8c6f205619b`.
It verifies the same archive SHA-256 as Windows and three held neutral frames.
`out/v22-cross-platform-image-comparison.json` authenticates both receipts and
matching scene/build/render settings: max RGB-channel difference 5, mean
0.009595870971679688, p95 and p99 zero (8-bit channels). Bytes differ across
platforms. These measurements do not establish a new tolerance or waive exact
same-platform reproduction. Full-sequence qualification remains pending.

The alternate olive-amber/legacy cache rehearsal is rendering. The generated
`out/v22_nonreview_followup.py` waits on that actual live prerequisite, then
renders Left frames 1, 26, 103 and 108 at full detail using the production
receipt/resume/hold-reuse path. The original failed low-cost diagnostic remains
unchanged. `out/v22_nonreview_angles.py` subsequently queues twenty 1024px/
512-sample full/native angle and oblique-light stills across all five sets.
These jobs run serially and guard against simultaneous host/container Blender.
Their pending outputs are not visual acceptance or final frozen regeneration.

`docs/V22_QUICKSTART.md` now describes the current full character, 4K/2K PBR
maps, packed preset, offline runtime and honest compatibility/reproduction
boundaries. README links to it, as explicitly authorized by the supplied plan.
The older quickstart is labeled as the earlier release's instructions.

The new `tools/gnm_v22_bundle.py` assembles an explicitly unqualified development
archive from the authenticated runtime and matching attribution. It refuses
changed inputs, missing notices and colliding destinations; binds all payloads
and source revision; and never promotes a release. The standalone standard-library
`tools/gnm_bundle_verify.py` verifies extracted hashes and optionally rejects
extra files. Targeted tests cover tampering, traversal, Windows-reserved names,
case collisions, missing files, license mismatch, override attempts and isolated
execution: eighteen pass. The earlier full run passed 148 tests before the last
six targeted cases were added; a fresh full run is in progress.

The development bundle's public cardinal report changes only local image paths
to packaged relative image paths and records the original report SHA-256. Image
hashes and numerical results are retained; the raw report is unchanged. The
generated public evidence snapshot is explicitly scoped to development, retains
all pending gates, and excludes private review keys and responses.

The full Windows source suite subsequently passed 154 tests
(`out/v22-bundle-source-tests-final.xml`). Development archive assembly completed:
`out/v22-development-archive/apollo-v22-unqualified-development.zip`,
2,702,298,567 bytes, 203 hashed payloads, SHA-256
`8d7cfc139f78bf5c21888382fd288c8b53b8eb9b534aef038674cf574200e0c1`.
Its manifest explicitly records `release_ready=false` and source `5ab5f19`.
Clean extraction, bundled-verifier execution and hygiene inspection of this
new archive remain pending. This is a development checkpoint, not the final
post-acceptance archive. The builder's unit-test API now also accepts explicit
source identity so isolated code ZIP tests need no Git metadata; the CLI still
records the actual checkout identity. Eighteen targeted cases pass after that
small portability adjustment.

The new development archive passed clean extraction and its bundled standalone
verifier in isolated Python: all 203 payloads match, with no extra files.
`out/v22-development-archive/check.json` records no personal absolute paths,
credential-token patterns or private-key patterns in packaged text, and no
excluded private/development filenames. This text scan does not claim a separate
binary-format audit; packed Blender resource paths retain their source-bound
checks. The archive remains explicitly unqualified.

Fresh offline Linux source tests at `fdfdde9` pass all 154 cases in 45.83 seconds:
`out/v22-linux-source-fdfdde9-retry/result.json` and `tests.xml`. The first
code-only ZIP accidentally omitted the metadata schema and baseline build
dependencies: thirteen tests failed with missing source files. That attempt is
retained, and the corrected retry includes the prior tested source closure plus
the new files. No application or test expectation was changed to obtain the pass.

`docs/V22_RELEASE_CHECKLIST.md` now preserves the acceptance-before-freeze order,
complete final rebuild/archive scope, exact release naming and team-owned public
access/form handoff. Generated `out/v22_remaining_mode_recovery.py` waits for the
angle job and then exercises three held frames, corrupt/missing repair, stale
receipts and invalid ranges for Left and Right; it also compares a fresh Left
neutral with the full-detail follow-up. These additional checks remain queued.

The olive-amber/legacy alternate-cache rehearsal subsequently passed:
`out/v22 alternate cache rehearsal/rehearsal.json`. All three held frames and
the cached scene retained their hashes/mtimes on reuse; the deliberately stale
scene-hash receipt was rejected and restored. Source scene bytes remained
unchanged. The serial Left full-detail follow-up is now confirmed live,
rendering its neutral frame at 1024px/512 samples; angle and further recovery
jobs are waiting on their actual live prerequisites.

### Binary hygiene follow-up: saved file-browser location

The decompressed ASCII marker scan in
`out/v22-development-archive/blend-path-marker-scan.json` found one personal-path
marker per unique Blender payload. A direct SDNA/block inspection locates the
same value in `FileSelectParams.dir`, at offset 96 of that UI structure. It is
a saved file-browser directory, not an image/library/runtime dependency. The
development archive remains unchanged; its text hygiene pass did not cover
this binary UI field. The final binary hygiene requirement is not yet passed.

`gnm_portable.clear_file_browser_paths()` now resets saved browser directories
and filenames before future prepared-timeline/cache saves; native import calls
the same helper. It edits no scene or texture data. Sixteen targeted UI/PBR/cache
tests pass, including empty/no-active UI handling. Native Blender 4.5.15 save/
reopen validation is queued, not claimed complete: generated workers will save
derived native/full-character copies, compare mesh/material/packed-image
snapshots and verify reopened UI params. Raw v22 and current evidence are
preserved. The waiting angle coordinator was intentionally replaced to insert
this new prerequisite before its render batch; the active Left render was not
restarted. Additional recovery still waits on the live angle coordinator.

All 156 Windows source tests pass after the UI-only cleanup change
(`out/v22-ui-cleanup-source-tests.xml`). This test result does not claim that
the queued native save/reopen probes have run or that old scenes were sanitized.

Fresh clean offline Linux source extraction at `092f9c3` also passes the updated
suite: `out/v22-linux-source-092f9c3-retry/result.json` and `tests.xml` bind the
source ZIP, pinned container image and successful exit. Native Blender probes
remain queued behind the still-running full-detail Left renders; this source
test pass does not substitute for those save/reopen checks.

The UI cleanup now scrubs the full RNA-reported fixed buffers before writing
the final anonymous directory and empty filename. Inspection of Blender's
[4.5 RNA setter generator](https://raw.githubusercontent.com/blender/blender/blender-v4.5-release/source/blender/makesrna/intern/makesrna.cc)
and [string-copy implementation](https://raw.githubusercontent.com/blender/blender/blender-v4.5-release/source/blender/blenlib/intern/string.cc)
shows that a short assignment alone leaves bytes beyond the new terminator.
A regression model reproduces that residual-byte behavior and requires the
entire buffers to contain only anonymous filler/terminators after cleanup;
unknown capacities are rejected. All 158 Windows source tests pass
(`out/v22-ui-buffer-source-tests.xml`). Native validation is still pending.

Generated `out/v22_check_ui_probe_buffers.py` is waiting on the actual native
save/reopen probes. It independently reads typed SDNA `FileSelectParams`
directory/filename arrays from the resulting copies and checks the complete
buffers, including trailing bytes. This is stronger than checking only the
visible RNA strings, but it is not yet a pass. The Left full-detail neutral
render completed and was visually inspected; frame 26 is now rendering. Original
preview diagnostic failure remains unchanged pending this full-detail check.

The complete 158-test suite also passes in clean offline Linux extraction at
`59c6e30`: `out/v22-linux-source-59c6e30-retry/result.json` and `tests.xml`.
The stronger cleanup has source-test coverage on both platforms; native saved
buffer inspection and final sanitized archive qualification remain pending.

### Five-set front still sample/detail coverage queued

The current 512-sample evidence does not yet qualify every variant/output/view.
`tools/gnm_v22_still_convergence.py` now compares authenticated full/native front
judging pairs at native pixel scale, using the existing mean/p95/detail-ratio
limits. It requires identical source, map, worker, build and camera/policy
receipts except the sample count and output image identity; altered images,
changed targets/cameras and angle/oblique views are rejected. Eye, skin, lip
and ear crops are measured for both outputs, with an additional hair crop for
the full character. Crops are explicitly front-camera-specific. Measurements
do not grant independent appearance acceptance or broader motion convergence.

Generated `out/v22_judging_still_references.py` waits on the existing mode-
recovery job, then serially renders ten 1024-sample references against the
completed 512-sample full/native fronts, prioritizing the deep/cool variants.
No reference has rendered yet. Its waiting coordinator was deliberately
replaced to load the final checker only when prerequisites finish; no active
Blender render was interrupted. This is development quality qualification,
not post-acceptance frozen regeneration or final PNG delivery. Higher-quality
references are not assumed stable before the measurements and visual checks.

All 166 Windows source tests pass with the new still checker
(`out/v22-still-convergence-source-tests.xml`). The eight additional tests
exercise matching full/native pairs, receipt/image tampering, source/camera
mismatch, incorrect sample order, non-front views and an actual above-limit
pixel change. They validate the checker, not the unrendered reference pairs.

Clean offline Linux source extraction at `084bc58` also passes all 166 tests
(`out/v22-linux-source-084bc58-retry/result.json` and `tests.xml`). The generated
`out/v22_left_early_direction_check.py` watches the actual live Left render for
the receipt-verified frame 26 and then runs the unchanged image oracle against
its own full-detail neutral. This partial early check excludes closure/reopening
and does not replace the full follow-up report. Frame 26 is still rendering.

The early Left full-detail direction check subsequently passed:
`out/v22-left-full-detail-followup/direction-only-image-check.json`. At 1024px/
512 samples, both pupils move screen-left by 5.9908 and 7.2536 pixels; neutral-
reference iris correlations are 0.8784 and 0.8287. The existing 0.8 threshold
and checker recipe are unchanged. The completed extreme render was visually
inspected. This is a pass for the neutral/extreme pair only: frame 103 closure
is now rendering, reopening remains pending, and human direction/naturalness
acceptance remains separate. The original 512px timing-preview failure is kept
as evidence of its limited diagnostic reliability; it has not been relabeled.

### Complete default PNG inventory verifier prepared

`tools/gnm_v22_delivery_frames.py` now verifies exactly 192 recorded/present
1024px PNGs per default mode, matching scene/geometry/preparation hashes, selected
sample/build/render-policy receipts, canonical metadata-free PNGs and actual
decoding. Reuse references must point to the same authenticated pose ID and
same image bytes; every repeated pose must be byte-identical. It reads dense
pose-array headers without loading the full tensors. It is a file/receipt/hold
inventory, not a replacement for native geometry/resource or visual gates.

The real control implementation and pose NPZs confirm that Left/Right end in
their direction holds (`sequence` IDs 0 to 160), while Generate Motion returns
to neutral (0 to 0). The verifier enforces return-to-neutral for Generate Motion
and preserves the existing Left/Right contract. It does not alter animation to
fit the check. The release checklist now states that scope explicitly.

The real partial Left output was copied into a separate preflight directory
and correctly rejected as incomplete: `out/v22-delivery-partial-preflight/preflight.json`
records two completed frames and the 192-frame requirement. This is rejection
evidence, not a 576-frame pass. The immutable source, live render and current
review packet were not modified. Nine targeted inventory cases cover completeness,
tampering, stale settings, private PNG metadata, wrong-pose reuse, geometry
changes, Generate Motion reset and isolated CLI import. No final frame inventory
exists yet; final frozen rendering remains after visual acceptance.

The final inventory implementation passes all 175 Windows source tests
(`out/v22-delivery-inventory-final-source-tests.xml`). Actual dense pose-array
headers were inspected as well: Left/Right each contain 385 poses over 17,821
vertices; Generate Motion contains 1,186. The inventory reads just their headers
and the 192-index sequences, avoiding full tensor allocation. This development
test pass is not a complete delivery-inventory or final release pass.

### Completed overnight technical checks and remaining sample gap

All 175 tests pass in clean offline Linux source extraction at `2e1c777`
(`out/v22-linux-source-2e1c777-retry/tests.xml` and `result.json`).

The standalone Left full-detail image gate passes neutral, extreme, peak closure
and reopening: `out/v22-left-full-detail-followup/followup.json`. Neither pupil
is detected at closure; both reappear with the existing >=0.8 iris-correlation
requirement. The closure image was inspected. No detector tolerance or identity
was changed. The earlier low-cost preview failure remains preserved.

Both native and full-character UI-cleanup copies passed Blender 4.5.15 save/
reopen with matching mesh/material/packed-image snapshots and unchanged source
files. `out/v22-ui-cleanup-native-probes/serialized-buffer-check.json` also passes
typed SDNA inspection of the entire 1090-byte directory and 256-byte filename
arrays, including their tails. This proves the cleanup on those copies; original
development scenes/ZIPs are unchanged and are not retroactively sanitized.

All twenty 1024px/512-sample full/native angle/oblique images completed.
`out/v22-angle-output-audit/audit.json` independently rechecks their source,
maps, current worker recipes, build/settings and image hashes. Four five-variant
overview sheets were inspected. These remain development visual evidence;
independent acceptance, view-specific convergence and frozen qualification remain.

`out/v22-other-mode-recovery/recovery.json` passes Left and Right three-held-
frame repair, valid-frame preservation, stale-receipt and invalid-range rejection.
Left's fresh neutral PNG matches the prior independent render byte-for-byte
(`6fed64f64b6004b7bf0118b38fcaba183ba5edd1ecaeec9efdb2707a51470933`).
Together with the earlier Generate Motion rehearsal, all three development modes
have these scoped checks. Final all-frame/archive recovery is still separate.

Ten 512-vs-1024 front still comparisons completed. Four native variants pass.
All five full-character hair crops fail the unchanged mean <=1/p95 <=3 RGB
limits (mean approximately 1.20–1.26, p95 4); deep full/native skin detail ratios
also fail (approximately 0.876/0.808, minimum 0.90). The default full and deep
native comparison sheets were inspected. These failures are retained and the
512 front profile is not declared sufficient. Generated
`out/v22_higher_judging_references.py` is rendering six 2048-sample references
to test the corresponding 1024-sample candidates, starting with the default
full character. This does not invalidate the separately tested 512-sample
close-up motion framing or qualify untested views.

Generated `out/v22_right_full_detail_followup.py` waits on that live higher-
reference job, then checks the standalone Right extreme/closure/reopening at
1024px/512 samples. It seeds only previously receipt-verified neutral held frames
to avoid rerendering them. These Right outputs are pending, not accepted.

### First higher-sample result

The rose-brown full front 1024-vs-2048 comparison completed. Eyes, skin, lips
and ear pass; hair still fails the unchanged limits: mean absolute RGB
1.0471918512288572, p95 4, detail ratio 0.97197163313687. The result is retained
in out/v22-front-sample-references-2048/rose-brown/full/sample-analysis/analysis.json.
Neither the 1024 front profile nor the 2048 reference is declared converged.
The remaining five higher-reference cases continue in the live serial job.

The default 1024-vs-2048 comparison sheet was inspected. Generated
`out/v22_default_hair_reference_4096.py` now waits on the actual live Right
follow-up coordinator, then renders one 4096-sample default full front and
compares the existing 2048 candidate with the unchanged limits. It is queued,
not rendered or converged; other variants/views remain separate. Existing
reference renders and failed results are preserved, and no second Blender
process is launched while the current job is active.

The deep full-character 1024-vs-2048 comparison also completed. Skin detail
now passes (ratio 0.9778283751331677), as do eyes, lips and ear. Hair remains
failed: mean absolute RGB 1.100593402485749, p95 4, detail ratio
0.9695259772286299. The whole still is therefore not declared converged.
Its report is under `out/v22-front-sample-references-2048/neutral-deep/full/sample-analysis`.
The deep native-target reference is now rendering in the same serial job.

The deep native 1024-vs-2048 front comparison subsequently passed all four
regions: skin detail ratio 0.9412077459824904, mean RGB 0.8384345608161964,
p95 2; eyes, lips and ear also meet the unchanged limits. Thus all five native
front variants now have a passing measured candidate (512 samples for four,
1024 for deep), with visual inspection and frozen qualification still separate.
The report is in `out/v22-front-sample-references-2048/neutral-deep/native/sample-analysis`.
Full-character hair convergence remains unresolved; remaining references continue.

The deep native 1024-vs-2048 crop comparison sheet was inspected after its
numerical pass. Eyes, skin, lips and ear retain comparable structure; this
inspection does not replace the independent appearance ratings. The release
checklist now records the already-completed Left full-detail diagnostic
separately from the queued Right diagnostic and complete-playback acceptance.

The cool-grey full front 1024-vs-2048 measurement completed and its native-pixel
comparison sheet was inspected. Eyes, skin, lips and ear pass. Hair still fails:
mean absolute RGB 1.0442855807868423, p95 4, detail ratio 0.9722276981772878.
The unchanged limits therefore reject the whole 1024-sample front profile.
Evidence: `out/v22-front-sample-references-2048/cool-grey/full/sample-analysis`;
analysis SHA-256 `6961432579ccd6dd252b8f0255c5e8caea97237d379cf382810f1a4e4ace6cb2`.
The serial controller advanced to olive-amber; no final still preset is frozen.

A capacity observation at `out/v22-capacity-observation.json` records roughly
11 GiB free on the only mounted data volume. Existing evidence is preserved.
Recheck capacity before final rebuild, archive creation and clean extraction;
the observation does not establish that all final stages fit simultaneously.

Generated coordinator `out/v22_remaining_hair_references_4096.py` is queued
behind the default 2048-vs-4096 result. It verifies that report's analysis hash
and proceeds only if the default 2048 candidate passes; otherwise it records
a stop for diagnosis. It then measures the remaining full-front variants that
failed at 1024, one Blender process at a time, against 4096-sample references.
Prior reports and renders are retained, receipts are compared by the existing
strict checker, and less than 1 GiB free stops further rendering. This is a
queued measurement, not a qualified preset or completed output. Other views,
motion and independent visual acceptance remain separate gates.

The six-case 2048-reference batch completed. Olive-amber and golden-hazel
comparison sheets were inspected and their report hashes verified. Both pass
eyes, skin, lips and ear; hair still fails (olive mean RGB 1.0580366320904588,
golden 1.0531305485468647; both p95 4). All five full fronts therefore fail at
1024 samples solely on hair. No 2048 front is declared converged before its
higher-reference comparison.

The standalone Right full-detail gate also completed and its source-bound
report/receipt hashes were verified. Both irises move right by 10.9403 and
6.4077 pixels, with correlations 0.894004 and 0.818275 above the unchanged 0.8
minimum. Peak closure exposes neither pupil; reopening restores the exact held
extreme image. The extreme and closure images were inspected. Evidence:
`out/v22-right-full-detail-followup/followup.json`, image-check SHA-256
`b631c9d6a2c806e6d48f510c729f75531593f728cd05a545c37b9e8438bf25d0`.
Both dedicated direction diagnostics now pass; complete final playback,
independent ratings and frozen regeneration remain separate requirements.

The default full-front 2048-vs-4096 measurement passed all five regions and
its comparison sheet was inspected. Hair now meets the unchanged limits:
mean RGB 0.8960798056256425, p95 3, detail ratio 0.965385194554782. Eyes, skin,
lips and ear also pass. Evidence: `out/v22-default-front-reference-4096/result.json`;
analysis SHA-256 `cd0c70227d326ef51a315bdec8901082419596d880975d9f9dce1ae2d3f71338`.
This selects a measured 2048 candidate for this default full-front workload
only. It does not qualify other variants/views, change the 512 motion profile,
freeze final inputs or replace independent acceptance. The waiting coordinator
advanced to neutral-deep's 4096 reference; three further full variants follow.

Both dedicated direction evidence sets were independently reauthenticated
against their current scenes, receipts and actual PNG bytes in
`out/v22-direction-evidence-current-audit.json` (four Left entries, six Right).
An unused development extraction was also reverified: 203 payload files pass
the standalone verifier. A subsequent removal command was rejected by
automatic approval review as "blocked by policy"; no extraction files were
removed. Keep that directory and the original archive, and recheck capacity
before final packaging. No alternative deletion method was attempted.

The neutral-deep full-front 2048-vs-4096 comparison passed all five regions.
Its analysis hash was verified and the native-pixel comparison sheet inspected.
Hair mean RGB is 0.9511634426689094, p95 3, detail ratio 0.9597031847189664;
skin detail ratio is 1.0112397870406984. The unchanged limits therefore accept
this development front workload at 2048 samples. Evidence:
`out/v22-remaining-front-references-4096/neutral-deep/sample-analysis/analysis.json`,
SHA-256 `46862ae785c3a5f1cab42b3c11a82dcd9dde4ba9e87fe391f08ed28c838083eb`.
Two of five full fronts now have passing measured candidates; cool-grey is
rendering next, followed by olive-amber and golden-hazel. This remains a front
sample measurement, without all-view, human-review or final frozen qualification.

On resuming the goal after the user pause, the serial controller was still
running. Cool-grey's 2048-vs-4096 full-front comparison had completed and passes
all five regions. Its analysis hash was verified and comparison sheet inspected.
Hair mean RGB is 0.8940379403794038, p95 3, detail ratio 0.9651044709081344.
Evidence: `out/v22-remaining-front-references-4096/cool-grey/sample-analysis/analysis.json`,
SHA-256 `3bb479ab4afec12afad0cd3e268eb4033fa09cd323c647e330158f85012ce4fe`.
Three of five full-front candidates now pass at 2048 samples. Olive-amber is
actively rendering its reference; golden-hazel follows. Existing failed lower
sample reports remain preserved, and no final or independent acceptance is inferred.

### User-approved faster execution (21 November)

The user asked what could be skipped and explicitly said "do it" to stopping
further sample-count experiments, reusing verified unchanged outputs, avoiding
redundant tests and omitting extra comparison sheets/cosmetic polish. The
controller and its actual olive-amber render were identified by command line
and stopped; completed measurements were preserved. The partial original
progress report remains unchanged, with the stop recorded separately in
`out/v22-remaining-front-references-4096/stopped-by-owner.json`.

The selected conservative still profiles are 2048 samples for the full front
and 1024 for native fronts. Full-front convergence is measured on default,
deep and cool; olive/golden remain unmeasured at 2048. This distinction is
explicit, and independent appearance acceptance still covers all five sets.
The motion profile remains the separately measured 512 samples at 1024 pixels.

The fixed technical candidate builds before review completes and remains
unqualified until all release gates pass. Its generated coordinator is
`out/v22_fixed_technical_candidate.py`; `input-freeze.json` records exact map,
geometry, portrait, source-revision and Python recipe hashes. It reuses the
existing 75 validated texture maps and their original bake/repair evidence,
rather than rebaking solely for newer PNG serialization. Each new scene gets
current preparation, 383-time geometry/resource and eighteen-component
appearance checks, including the current UI-path cleanup. The production
renderer then writes all 192 frames per mode, reusing exact repeated poses
with receipts, followed by the complete 576-frame inventory. Final clean
Windows/Linux archive qualification, independent responses and release
promotion remain required. A review-driven change requires rebuilding and
rechecking affected outputs; none of these selected inputs is silently final.

The fixed technical build has completed all three new packed scenes. Each
reopened geometry/resource report passes at 383 integer/half-frame times with
zero errors, and each whole-character appearance report passes all eighteen
components. Scene hashes are Left
`afb2c2926b891ba18277a4fd52d8d6a93e8600c61c89f6741ac22a34d6f67c9b`,
Right `c39c35111f2a80f66746e47c535bc7676e5d96263a6ca0e5b94d301e392ead1c`,
and Generate Motion `1624eb5745558f53117ae644dd4ca0dedb0e0fa96500246e85961dcc1bf70aca`.
Reports are under `out/v22-fixed-technical-candidate/timelines/<mode>`.
The bounded-memory decompressed marker scan now finds zero personal-path
markers in all three actual scene payloads; its complete report is
`out/v22-fixed-technical-candidate/blend-path-marker-scan.json`. This resolves
the known file-browser path issue for these scene hashes, without substituting
for final archive hygiene. Full 192-frame production-size Left rendering has
started, with Right and Generate Motion following serially. The internal
input-freeze record contains authoring input locations and must receive a
public path mapping before any release archive includes its provenance.

The public input provenance derivation is complete at
`out/v22-fixed-technical-candidate/input-provenance-public.json`. It preserves
all 93 input dependency hashes under path-free identifiers and binds the
private freeze by SHA-256; it also retains the source commit, Python recipe
hashes and selected render profiles. The public record hashes to
`45cc1e39a720da4d3c32dac36d2a7b5010e71ba06d4b5254ef067285d37bfaa5`.
`input-provenance-derivation.json` verifies the one-to-one hash preservation and
absence of local-path markers. Dependency identities are explicitly separate
from the final archive inventory: external authoring inputs are not falsely
described as packaged runtime files. Keep the original private freeze out of
the public archive. This provenance step makes no release-readiness claim.

The user-approved reuse collection is complete in
`out/v22-fixed-technical-candidate/judging`: thirty authenticated images
(five full fronts at 2048, five native fronts at 1024, and twenty existing
full/native angle/oblique views at their recorded 512 samples), plus the
existing overview/detail sheets. All 108 collected files retain their exact
bytes and original receipts; no stills or sheets were rerendered. The collection
report `judging-assets.json` hashes to
`d9527f57a8047ec4ecd80fc4bbda88cf868ffb7e20a1b9e6e8942f68c3b8de07`.
The preparation comparison confirms identical native source, integration,
geometry, map, render-policy and appearance-retention fields. Only the scene
file hash and recognized file-browser cleanup recipe differ. Original still
source hashes remain intact rather than being rebound to the new scene hash.
The retained native-target cleanup probe and current map manifest hashes bind
the texture-only evidence. Existing 512-sample overviews keep that provenance;
they are not relabeled as crops from the higher-sample primary fronts.

The fixed Left sequence has reached 99 saved frames. New neutral and extreme
Left images are byte-identical to the earlier passing diagnostic images;
`same-platform-left-gaze-regression.json` records the two exact comparisons
and prior image-check hash. This supports reusing those pixel results without
rerunning an unchanged-input image test. New closure/reopening images,
complete sequence inventory and final archive checks remain pending.


### Optional Kaggle GPU handoff — 21 November 2026

The CPU fixed-candidate driver remains live and its tracked Python recipes are
unchanged. Kaggle is an optional acceleration route; no GPU result or speedup
has yet been measured. No Kaggle credentials or connected tool were available.
The official service documents an MCP endpoint at https://www.kaggle.com/mcp.

`out/v22-kaggle-handoff/apollo-v22-kaggle-input.zip` contains the three exact
fixed-candidate packed scenes, the minimal PNG/timing dependencies, retained
component licenses, a file-hash manifest and a separate experimental CUDA
renderer. Archive size: 971,518,743 bytes; SHA-256:
`fcd05e8085899d229ed6cb718d82289a42a5d587109f63a1952d64707c5998cb`.
All 20 payload files were reread from the ZIP and authenticated. The three
scene hashes match the fixed CPU candidate; no scene was modified or saved.

The adjacent `apollo-v22-kaggle.ipynb` is prepared for a private Kaggle notebook
with GPU and Internet enabled and the ZIP attached through a private dataset.
It verifies inputs and the official Linux Blender 4.5.15 download checksum,
then benchmarks one 1024px/512-sample Left neutral frame. Full rendering is
explicitly disabled by default pending that benchmark and output inspection.
The experimental worker requires build `5afeabba6097`, selects CUDA devices,
disables CPU selection, rejects missing CUDA devices and records GPU/backend/
device identities in its own receipts. Outputs use separate GPU directories;
they cannot be substituted into the CPU inventory or claimed as CPU results.

The generated builder is `out/prepare_kaggle_handoff.py`. Python compilation,
notebook-cell compilation, ZIP integrity and file hashes passed. This is not
evidence of CUDA execution, convergence, image acceptance or final archive
qualification. An actual account-authorized Kaggle run and local validation of
its downloaded images/receipts remain necessary before adopting GPU outputs.
No upload, account change or cloud execution was performed.

The fixed-candidate archive base preflight now authenticates 238 proposed
payload files (2,706,812,961 bytes before frames). This includes the current
12-file runtime closure, cleaned native target, pinned template, three checked
scenes, five complete map sets, matching retained licenses, 108 reused judging
assets and selected public provenance/evidence. The report is
`out/v22-fixed-technical-candidate/archive-preflight/base-inputs.json`.
The direct inventory avoids staging another multi-GB copy. Its bounded text
scan found zero recorded personal-path markers; this is not a complete
credential or final ZIP hygiene scan. The adjacent `PRIVATE-input-locations.json`
is local assembly bookkeeping and must never enter a release archive.
Complete PNGs, finalized package documentation/status and clean extracted
Windows/Linux tests remain pending; no archive or release is claimed ready.

Agent inspection of four retained full/native angle/oblique overview sheets
covered all five variants, with additional default-eye and deep-skin crops.
`judging-agent-inspection.json` binds those eight actual images. Framing and
variant tissue/eye color remain consistent; the full character retains groom
and the native target intentionally demonstrates texture-only wrapping.
No obvious atlas discontinuity appeared at overview scale. Skin crops remain
soft and these resized/512-sample sheets do not establish native-pixel detail
or independent photorealism acceptance. Actual reviewer ratings and complete
motion inspection remain separate gates. No new renders or sheets were made.

A direct technical-candidate assembler is prepared at
`out/v22_assemble_fixed_candidate.py`. It requires the completed fixed driver
state and matching delivery-inventory hash, reruns the full 576-frame verifier,
checks frozen tracked Python hashes, authenticates every preflight input and
streams a new ZIP without a redundant staging copy. It preserves separate
pending independent-acceptance/clean-archive statuses and always leaves
`release_ready` false. It rejects an existing destination and insufficient
space, hashes each streamed payload and checks ZIP integrity. This assembler
has not yet produced a complete archive: the real incomplete candidate was
rejected as expected before any ZIP write; the recorded check is
`archive-preflight/assembler-incomplete-check.json`.

Left frame 100 is saved (SHA-256
`b4c88784cc94da8023cc9ae4bb962d175b7a7ac43da0532df74e8673f2d0ff1a`)
and was visually inspected at 1024 pixels. It shows the expected partial
blink with retained iris structure, brows and upper/lower lashes; this one
image does not establish full closure, complete motion acceptance or a
release gate. The existing owned renderer continued into frame 101 without
restart. No tracked Python recipe or fixed scene was changed.

The retained visual inspection now covers all forty native-pixel front crops
(five variants, full/native targets, eyes/skin/lips/ear) plus the four angle and
oblique overview sheets. `judging-agent-inspection.json` records all 44 image
hashes. The crop receipt explicitly identifies native-pixel crops from the
original 512-sample fronts; only the overview sheets are downscaled. These
crops are not relabeled as extracts of the later higher-sample primary fronts.
Iris structure and lip microfolds remain visible across variants; skin detail
is soft, particularly in deep-variant shading. Front ear crops show a narrow
outer-ear view and do not independently prove inner-bowl appearance. No broad
photorealism acceptance or complete seam audit is claimed from these images.
Independent human ratings and complete motion acceptance remain pending.

The Kaggle notebook now accepts either a ZIP input or Kaggle's unpacked dataset
layout. Its local syntax/archive checks still pass with the same input archive
hash. Windows Computer Use could not confidently identify the browser URL and
stopped under its safety policy, so no browser authentication, upload or GPU
session was attempted. The CPU fixed-candidate render continues separately.

The proposed 238-file archive base passed a bounded-memory known-credential
pattern scan, including decompressed Blender payloads. The report is
`archive-preflight/base-credential-pattern-scan.json`; it binds every scanned
file hash and the exact preflight inventory. Rules cover classic/fine-grained
GitHub tokens, OpenAI project keys, AWS access-key identifiers and private-key
armor. No matched contents are printed. A separate synthetic positive check
verified detection, including a token spanning the 4 MiB read boundary.
No real secret was used in that check; its fixture is explicitly excluded from
the proposed archive input mapping. The direct assembler now requires current,
clean base-scan evidence and includes the report plus the positive-check result.
This does not prove absence of all credential formats and does not cover future
frame receipts or final ZIP additions; complete archive hygiene remains open.

The fixed Left closure checkpoint is now authenticated. Fresh frame 102 and
its identical-pose hold at frame 103 both hash to
`cf323bb15c852b6762511506b330d5505e427ff1241e3f5ce809b66b0e67ebcf`,
exactly matching the previous passing full-detail closure diagnostic's frame
103. The current scene hash and current/prior frame receipts were checked;
the prior image-check report itself was authenticated and records no pupil
in either eye at closure. The new binding is
`out/v22-fixed-technical-candidate/same-platform-left-closure-regression.json`.
The actual image was visually inspected with both eyes covered. The renderer
continued into reopening frame 104 without restart. This reuses an unchanged
pixel result, not a relabeled historical scene receipt. Reopening, the complete
576-frame inventory and independent motion acceptance remain pending.
