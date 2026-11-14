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

## GNM technical candidate

Published prerelease apollo-v0.3.0-rc.3 targets
e16bfd7c39f9ede5c6f820da79074d03516d26fe.
Display name is Apollo v0.3.0-rc.3 — GNM Technical Candidate.

The release contains the 712,214,016-byte technical archive split into 29
numbered parts, a SHA-256 file, a reassembly script and the candidate receipt.
Every uploaded part matched its local size and digest. Download all parts
and reassemble-gnm.py into one directory, then run python reassemble-gnm.py.
The assembled archive must have SHA-256
83a1b5440b104e54a82dfb39d4e3a87e22b300ce8c6ee5017f83e2f0181ccd1a.

The archive includes five GNM face-and-eye texture sets, five matched stills,
three packed Blender timelines and 576 full-quality CPU frames. The clean
extraction rehearsal reproduced five outputs pixel-for-pixel. Evaluator
model matching is unconfirmed, and the technical receipt records the
remaining appearance limitations and deferred human review. Repository
access is required while Apollo is private.

## Refined GNM candidate

Published prerelease
[Apollo v0.3.0-rc.4 — Refined GNM Candidate](https://github.com/Eldo-John-Giby/Apollo/releases/tag/apollo-v0.3.0-rc.4)
targets f745a4c4ab3613db325640eead428d2005559ad2.

The primary download is apollo-gnm-v0.3.0-rc.4.zip, 725,843,567 bytes,
SHA-256 3195dfcb1e1bf8238df1a193d29507e714d0e31dea35058d3412e9e5b087cc79.
The same ZIP is available as 29 verified parts with a reassembly helper.
All 34 uploaded assets matched their local sizes and SHA-256 digests.

The archive contains 671 payload files: five native face-and-eye texture sets
with portable brow detail, five primary stills, matched side-light comparisons,
eye crops, three packed native-expression timelines and 576 full-quality CPU
frames. Clean offline rehearsal passed every-frame geometry and packed-map
checks, default and alternate-variant resume, and corrupt/missing-frame repair.
Five default image comparisons were exact; the alternate variant's UV layouts
differed by at most one RGB level. All 84 Python tests pass.

Receipts and publication verification are under milestones/gnm-final-candidate.
The evaluator asset match and deferred teammate visual review remain pending;
the release notes retain the known visual limitations. The MakeHuman rc.2 and
earlier GNM rc.3 downloads remain available. Public access and final event
submission remain team-owned while the repository is private.

## Detailed GNM candidate

Published prerelease [Apollo v0.3.0-rc.5 — Detailed GNM Candidate](https://github.com/Eldo-John-Giby/Apollo/releases/tag/apollo-v0.3.0-rc.5)
targets `4d61cae63f07582d2c97aa5505b0d41a16a79c8d`. All seven uploaded assets match their
local sizes and SHA-256 digests. Publication verification is recorded under
`milestones/gnm-score-final-candidate/publication.json`.

The technical ZIP is 1,173,058,697 bytes with SHA-256
`5f4c0e8b849da9f22f6de09b46207d0d95f7a791fc8209b06f3a5706b1a2ed6c`.
Its producer source is `8d8396d131ecc24ac55a2f0a2f0648a7103bff10`;
the release tag identifies the handoff with its final qualification evidence.
All 779 payload hashes and 52 committed producer files were verified.

The five variants use attributed 4K head-scan skin, portable roughness/16-bit
height and independently authored bilateral iris detail. Native lid-rim
coupling reduces full-closure gap from 1.24 mm to approximately 0.20 mm.
All 576 CPU frames, 88 tests, both UV layouts, packed relative resources,
clean-extraction reproduction and real interrupted-render recovery pass.
The anonymous teammate packet is prepared with blank responses. Exact
organizer compatibility and human approval remain unconfirmed. One scan
identity, authored detail, a thin closure crease and small repaired atlas
regions remain documented limitations. Earlier releases remain preserved.
