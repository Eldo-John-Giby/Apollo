# Apollo release versions

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
