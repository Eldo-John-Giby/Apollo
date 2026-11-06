# Apollo development freeze — 7 November 2026

Git tag: `dev-freeze-2026-11-07`. This is a reproducible development milestone,
not an organizer submission. See [the freeze rationale](../../docs/DEVELOPMENT_FREEZE.md).

- `apollo-development.zip`: packed scene, standalone wrapper, ten PNGs, metadata,
  contact sheet, GIF, verification reports, attribution and per-file manifest.
- `verification_report.json` / `.md`: all V1–V17 PASS on the exact frozen inputs.
- `secondary_report.json`: Blender 5.2.3 measurements. Its own V16 is NOT RUN
  because the nested run does not recursively qualify a third runtime.
- `reconstruction_report.json`: all ten PNGs and metadata regenerated
  byte-identical from the extracted ZIP, from a different working directory.
- `docker_report.json`: image build, environment diagnostic, 60 tests and a
  packed-scene center render pass in Linux. Full Linux V1–V17 is not claimed.
- `quality_comparison.png` / `.json`: 32 versus 128 samples; the frozen scene
  retains the qualified 32-sample setting after visual and detector comparison.
- `SHA256.json`: SHA-256 and byte counts for the milestone files.

Extract the ZIP, enter `apollo-development`, then run with Blender 4.5.15:

```powershell
blender -b --factory-startup --python-exit-code 1 -P wrapper/eyes.py
```

No MPFB addon is required to render the packed scene. Do not add `--quality final`
when reproducing the freeze: that option means 128 samples, while this documented
development freeze uses 32. Archived MANIFEST.json verifies payload files before
experimentation. Back up the archive if you plan to overwrite extracted outputs.

Downloaded runtimes, original asset-pack ZIPs, caches and intermediate experiments
are excluded from Git. Their reproducible inputs and setup are documented in the
repository. The frozen character scene and its outputs are included in this ZIP.
