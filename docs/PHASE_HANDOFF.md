# Visual realism phase handoff

For the current submission phase, use the [evaluation and submission
audit](PS_AUDIT.md) and [GNM runtime quickstart](GNM_QUICKSTART.md). The public
GNM Head v3 technical package passes clean offline qualification; its evidence
is under milestones/gnm-final-candidate. Organizer asset matching and the
deferred teammate visual review remain pending. The preview qualification
below applies to the earlier calibrated sweep and remains historical fallback
evidence; the separately released rc.2 MakeHuman package is also preserved.

This development phase is closed. Main integrates the competition and realism
work. Start new task branches from main; read TEAM_SETUP.md in the repository root.

Published prerelease: [Apollo v0.3.0-rc.1 — Visual Realism Preview](https://github.com/Eldo-John-Giby/Apollo/releases/tag/apollo-v0.3.0-rc.1).
It provides the reviewed packed scene, before/after image and setup guide.
apollo-v0.2.0 remains the fully qualified fallback. Full v0.3.0 is not qualified.

Completed for the reviewed candidate: 80 native tests, Windows V1–V17 including
applicable Blender 5.2 checks, official ten-frame image/schema checks,
direction/reset, nine-anchor visibility, independent 1009-pose geometry audit
with 14 detected mutations, and reviewed sample/construction comparisons.

The team stopped the exhaustive batch. Linux qualification is incomplete. The
replacement 256-image corpus, expanded 113-pose suite and final complete release
rehearsals are deferred. Qualification, finalizer and dedicated container were
stopped; automatic publication is disabled. Completed local evidence remains
under out/realism/seed-zero, which is intentionally ignored by Git.

The preview had local interactive Blender edits. They are preserved separately
under milestones/realism-working-copy-2026-11-08/scene.blend, without a validation
claim. The original reviewed snapshot and published prerelease remain unchanged.

Next phase: agree the next improvement, use representative renders and targeted
tests, and run full qualification only for a stable release candidate. Do not
create videos or presentations. Organizer submissions and sharing remain
team-owned. Use Apollo semantic version tags, with -rc.N for prereleases.
