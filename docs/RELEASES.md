# Apollo release versions

Published preview: `apollo-v0.3.0-rc.1` — Apollo v0.3.0-rc.1 — Visual Realism Preview.
The suffix `-rc.N` marks a prerelease. Full v0.3.0 qualification is deferred;
see PHASE_HANDOFF.md for completed and remaining checks.

Use tags `apollo-vMAJOR.MINOR.PATCH` and display names
`Apollo vMAJOR.MINOR.PATCH — Short Descriptive Name`.
Increment minor for a qualified capability or appearance milestone and patch
for fixes to an existing release. Use major for incompatible public API changes.
Development snapshots are commits, not qualified release tags.

| Version | Display name | Commit | Previous tag |
| --- | --- | --- | --- |
| `apollo-v0.1.0` | Apollo v0.1.0 — Development Baseline | `c9833302689f6e01bca901c50f3e9c1de6b6a564` | `dev-freeze-2026-11-07` |
| `apollo-v0.2.0` | Apollo v0.2.0 — Competition Baseline | `b59f61b29f30ac038e157dd3eda6b69f17946049` | `competition-qualified-2026-11-07` |
| `apollo-v0.3.0` (reserved) | Apollo v0.3.0 — Visual Realism | Not tagged until all technical gates pass | — |

At the naming audit on 8 November 2026, GitHub had no Release objects; the two
existing releases were annotated Git tags. Their replacement tags point to the
same commits. Historical milestone directories, payloads and checksum manifests
retain their original names and bytes so evidence remains verifiable. Old names
inside historical archives are historical references, not additional versions.

New technical releases include the executable layout, calibrated renders,
metadata, still-image evidence, test/qualification reports and checksums.
Do not create videos or presentations; see the standing rule in AGENTS.md.
Event identity, registration and organizer uploads remain team-owned.


## CPU appearance integration, 9 November 2026

The completed photorealism-v2 work through `7dbbb07` is integrated into main.
The packed adult-female candidate and targeted evidence are under
`milestones/photorealism-v2-candidate`. Its 80 unit tests, local geometry/image
checks and exact center-render rebuild evidence do not replace full cross-
platform release qualification. No new tag or Release object was created for
this source integration. The published v0.3.0-rc.1 preview and protected v0.2.0
qualified fallback remain unchanged; v0.3.0 stays reserved until its gates pass.
