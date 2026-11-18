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
