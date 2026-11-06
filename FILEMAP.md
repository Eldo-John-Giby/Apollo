# Repository File Map

Navigation index verified 6 November 2026. Inspect implementation before changing it.

## Status and flow

GazeForge implements synthetic binocular gaze for Samsung PRISM-XR Track 01.
Source exists for the complete fixture/production pipeline. Blender 4.5.15 LTS is now installed and ten-frame fixture rendering and artifact validation now pass; full V1–V17 verification remains pending. Docker execution remains unavailable.
The textured character asset is still a human handoff. Fixture results cannot be
packaged as production. Generated artifacts belong under out/ and are not listed.

Flow: character inspection/mapping or fixture → calibrated scene → standalone eye
wrapper → PNGs/metadata → image validation/contact sheet → V1–V17 → production ZIP.

## Requirements and research

| File | Responsibility |
| --- | --- |
| `AGENTS.md` | Repository navigation and file-map maintenance rules. |
| `docs/problem_statement.md` | Screenshot-transcribed requirements, rubric, deliverables, unresolved organizer questions. |
| `docs/SOLUTION_TECHNICAL.md` | Proposed geometry, conventions, API, verification checks, risks, and limitations. |
| `docs/IMPLEMENTATION_PLAN.md` | Original phased plan and embedded reference math/tests; numbered companion references mean the unnumbered files here. |
| `docs/gemini_deep_research_web.md` | Prompt for reusable-code/asset research, not findings. |
| `docs/gemini_deep_research_papers_prompt.md` | Prompt for academic literature discovery, not findings. |
| `docs/Synthetic Gaze Reconnaissance Plan.docx` | Component research report; independently verify reuse/license claims. |
| `docs/Synthetic Gaze Literature Discovery.docx` | Literature report; independently verify cited claims. |
| `docs/Module 6 Congestion Control.ppt` | Unrelated/undetermined presentation, not used by the pipeline. |
| `docs/RUNBOOK.md` | Operator setup, fixture workflow, character handoff, framing, verification, Docker and submission steps. |
| `docs/character_mapping.example.json` | Explicit stock-eye identifiers, orientation confirmation and attribution template. |

## Entry points and core

| File | Responsibility |
| --- | --- |
| `tasks.py` | Portable CLI orchestrating test, inspection, scene build, sweep, framing, validation, sheet, prepare, demo, verify, bundle, all and Docker. |
| `wrapper/eyes.py` | Standalone Blender API/CLI; embedded NumPy core; absolute pose, evaluated geometry/projection checks, atomic metadata output. |
| `gazeforge_core/core.py` | Finite inputs/config, fixation, shortest-arc rotation, camera projection, exact pupil conic, sweep and annotations. |
| `gazeforge_core/metadata.py` | Structural/semantic protocol checks and optional analytic checks against a supplied calibration. |
| `metadata.schema.json` | Ten-frame JSON Schema; mathematical consistency is enforced by Python validation. |
| `check_core.py` | Direct reference assertion runner; normal task tests use pytest. |
| `pyproject.toml`, `requirements.txt` | Pytest configuration and pinned Python tool dependencies. |
| `Makefile`, `Dockerfile`, `.dockerignore` | Task aliases and pinned Blender/Linux container build (not executed in current environment). |
| `README.md`, `DECISIONS.md` | Current usage/evidence and recorded implementation decisions/remaining validation. |

## Scene construction

| File | Responsibility |
| --- | --- |
| `build/fixture_scene.py` | Procedural face proxy, open scleral shells, iris/pupil meshes skinned to dedicated eye bones, camera/light calibration; explicitly marks fixture. |
| `build/inspect_character.py` | Read-only source rig/mesh/material/image inventory for explicit mapping. |
| `build/build_scene.py` | Load mapped source face, preserve measured spacing, hide stock eyes, integrate dedicated procedural eye rig, pack textures and save candidate. |

The human-provided `assets/base_character.blend` and completed mapping are not
present yet. Integration requires -Y facing, meter scale, aligned anatomical eyes,
58–68 mm center spacing, actual stock-eye mesh names, and attribution.

## Verification and artifacts

| File | Responsibility |
| --- | --- |
| `tools/sync_core.py` | Embed core math in wrapper or check drift; strips the source future import for embedding. |
| `tools/validate_metadata.py` | JSON Schema/semantic checks and exactly ten 1024×1024 PNG validation. |
| `tools/grader_sim.py` | Image-only ellipse pupil detector, weighted mask centroid, subpixel template-displacement detector. |
| `tools/blender_verify.py` | Blender evidence worker: calibration/metrics, random evaluated poses, repeated sweeps, direction images, isolated/occluded masks, packed resource audit. |
| `tools/verify.py` | V1–V17 coordinator, pixel/direction/visibility checks, clean-room/secondary subprocesses, evidence-bound JSON/Markdown reports. |
| `tools/framing_sweep.py` | 85–135 mm experiments and eye-sphere margin/shift selection; brows/lashes still need visual review. |
| `tools/contact_sheet.py` | 5×2 annotated sheet, crosshairs, reset rings, direction clocks, fixture label. |
| `tools/prepare_candidate.py` | Candidate-specific README and fixture attribution; production attribution must already exist. |
| `tools/demo.py` | Labeled sweep GIF and presentation/recording outline; not a final narrated video. |
| `tools/make_bundle.py` | Reject fixtures, stale evidence and incomplete reports; stage ZIP, size/integrity/extraction checks. |

## Tests and relationships

- `tests/test_core.py`: original eleven geometry assertions from the implementation plan.
- `tests/test_protocol.py`: invalid inputs/config/metadata, exact conic boundary, embedded core and standalone import parity.
- `tests/test_artifacts.py`: image/sheet validation and production packaging gates.
- `tests/test_verification.py`: blind detector/template synthetic accuracy, centroid coordinates and missing-runtime report behavior.
- Core is authoritative; regenerate wrapper embedding with `python tasks.py sync` after core edits.
- Reports bind scene, wrapper, metadata and render hashes. Regenerate/reverify after changing these artifacts.
- `all` orders tests → sync → scene → sweep → validate → sheet → prepare → demo → verify → optional production bundle.
- Missing evidence is NOT RUN or FAIL; all seventeen checks are required for production packaging.
- Calibration defaults: meters, -Y forward, +Z up, anatomical L at +X, camera 40 cm, target 35 cm, bounds ±5 cm, clockwise ten-frame sweep.
- Deliberate deviations from original documents: preserve measured production IPD instead of forcing 63 mm; horizontal sensor fit; simplified non-refractive procedural eyes; visual review remains necessary.

Update affected entries when important source files or responsibilities change;
exclude generated outputs, dependencies, caches and build artifacts.



