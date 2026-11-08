# Apollo competition technical release

This is an evidence-bound technical milestone, not an organizer submission.
The registered college/team identity and event upload links are team-owned.

Use the unpacked `delivery/apollo` directory for the conventional executable
layout, or extract `apollo-competition.zip`. Run `wrapper/eyes.py` directly in
Blender as described in its README. Optional controls and research tooling live
in the repository, outside the required wrapper path.

From the repository root (writes a separate replay, preserving shipped images):

```powershell
blender -b delivery/apollo/scene.blend --python-exit-code 1 -P delivery/apollo/wrapper/eyes.py -- --out out/replay
```

- [Unpacked executable delivery](../../delivery/apollo/README.md)
- [Ten-frame development ZIP](apollo-competition.zip)
- [Measured native report](verification_report.md) and [Linux report](linux-verification.json)
- [Contact sheet](contact_sheet.png), [105-second video](apollo-demo.mp4), [editable deck](Apollo_Submission_ppt.pptx)
- [Complete research manifest](dataset-256/dataset.json) and [image analysis](dataset-analysis.json)
- [Per-file checksums](MANIFEST.json)

Native 4.5 and secondary 5.2 qualification, full Linux qualification, the actual
256-frame dataset and 25-pose visibility checks are recorded in the attached
reports. Local project checks are not official competition scores. The complete
256-image research example is in `dataset-256/`; an additional ZIP is generated
under `out/upgrade/dataset-256.zip`. Keep its seeded manifest and images together.

The 105-second video uses actual artifacts with local synthesized narration.
The editable deck retains a technical-prototype identity if team details have
not been supplied. Human naturalness preference and independent human usability
ratings are not invented. See `docs/UPGRADE_RUNBOOK.md` for reproduction commands.
