# v22 release qualification and handoff

This checklist preserves the agreed final scope. It is not a release approval.
Use the evidence matrix in [V22_SUBMISSION.md](V22_SUBMISSION.md) for current
results. The original portrait and rc.5 fallback remain unchanged.

## Acceptance before final freeze

- [x] Owner explicitly approved the integrated v22 face and groom.
- [ ] Receive 3–5 independent response files for the authenticated blinded packet.
- [ ] Score actual responses with `tools/gnm_v22_review_gate.py`; require >=95%
  aggregate cardinal accuracy, every required median >=4/5, no systematic
  direction confusion and no unresolved severe defect shared by two reviewers.
- [x] Resolve the technical Left-mode full-detail pupil diagnostic; the
  source-bound `out/v22-left-full-detail-followup/followup.json` passes neutral,
  extreme gaze, closure and reopening at 1024 pixels / 512 samples.
- [ ] Complete the equivalent Right-mode full-detail check and inspect lid
  contact, lashes, tears and the complete motion modes. The Left diagnostic
  does not establish acceptance of complete playback or the final rebuild.
- [ ] Inspect full/native angle, oblique and native-pixel detail evidence for
  all five sets. Numerical UV agreement does not prove convincing appearance.

## Frozen technical rebuild

- [ ] Record exact source revision, immutable portrait, pinned GNM/template,
  map recipes, pigment choices, render policy and Blender build in one manifest.
- [ ] Regenerate the baked master with the current canonical PNG policy;
  preserve raw outputs and any separately audited normal repair.
- [ ] Regenerate all five complete 4K skin/2K eye sets, including native-only
  scalp/brow maps and attribution linkage. Verify dimensions, 16-bit detail,
  color spaces, normals, seams and dilation.
- [ ] Rebuild all three packed timelines from those exact inputs; check native
  topology/order/UVs, zero eye corrections, all frames and transition samples,
  groom anchors, local orientations and neutral appearance preservation.
- [ ] Render all 576 final-quality PNGs at the selected converged preset and
  verify every receipt/hash, ordered range and Generate Motion's exact neutral
  reset with `tools/gnm_v22_delivery_frames.py`. Left/Right retain their ending
  direction holds; repeated-pose determinism is checked in every mode.
- [ ] Verify five-set fresh wrapping on both layouts; retain front, angle,
  oblique and eye/skin/ear/lip details plus a labeled contact sheet.
- [ ] Exercise representative alternate-variant motion, cache verification,
  interruption/resume, corrupt/missing repair, stale receipts and invalid input.

## Exact final archive

- [ ] Include full hero, native template, all textures, three packed scenes,
  576 final PNGs, runner dependency closure, licenses, pinned source records,
  documentation, per-file checksums and source-bound validation evidence.
- [ ] Keep rejected experiments, private review keys, response identities,
  credentials, author-machine paths and development caches out of the archive.
- [ ] Run the standalone file verifier from clean extraction; test actual public
  commands on Windows and Linux offline, outside the project and in paths with
  spaces. Require exact same-platform reproduction; document cross-platform
  image differences with their tested scope and explicit acceptance policy.
- [ ] Re-run all applicable tests on the exact final source. No historical
  fallback result may qualify the v22 candidate.
- [ ] Update setup instructions and requirements matrix to the exact package,
  commands, evidence locations, supported model/UV boundary and limitations.
- [ ] Commit/push, reconcile integration and submission branches, and record the
  exact release commit without changing unrelated worktrees.
- [ ] Publish a candidate only when its status is accurate; promote after all
  gates pass. Use `apollo-vMAJOR.MINOR.PATCH` and
  `Apollo vMAJOR.MINOR.PATCH — Short Descriptive Name`. Check remote versions
  before selecting the next tag. Retain the archive SHA-256 alongside assets.

## Team-owned submission

Engineering hands over the repository URL, exact commit/tag, downloadable
assets, checksums, requirements matrix and explicit remaining external items.
The team verifies public and signed-out access, completes the official form and
preserves submission confirmation. Video and presentation work is external;
no new video or presentation is required for this technical archive.

The user specified 22 November midnight. Planning uses the end of 22 November
2026, Asia/Calcutta; the organizer's timezone was not supplied. No organizer
model was provided, so compatibility is limited to the pinned public GNM Head
v3 and its tested layouts. Preserve the submitted commit/archive/confirmation;
subsequent fixes require a new version and a deliberate resubmission decision.
