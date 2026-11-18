# v22 submission integration

Active branch: `codex/v22-submission-integration`, based on `9b02f41`.
The approved portrait remains immutable. The rc.5 fallback remains unchanged;
its test results do not qualify this candidate. The 60/20/20 rubric is the
authoritative target. No organizer grade is predicted.

## Inputs and boundaries

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
| Preserve selected identity | Engineering | Hash check before every derived build; no source writes | selection receipt; `out/v22-audit/audit.json` | Source hash verified; audit running |
| Isolate integration | Engineering | Separate clean worktree; unrelated edits retained | branch above | PASS |
| Reproducible identity layer | Engineering | Native topology/order/UV unchanged; neutral matches selected evaluated surface | `out/v22-audit/identity.npz`; integration receipt | Pending |
| Appearance inventory | Engineering | Geometry, keys, shader dependencies, textures and visible attachments inventoried | `out/v22-audit/audit.json` | Running |
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
