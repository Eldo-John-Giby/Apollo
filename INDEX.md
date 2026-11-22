# Apollo Repository Index

Quick navigation index of all submission materials, documentation, runtime code, and verification reports for the **Samsung PRISM-XR Hackathon (Track 01)**.

---

## 1. Submission Deliverables & Formats (Root)

| File | Format | Responsibility / Role in Submission |
| :--- | :--- | :--- |
| [`LangAI3.0_AI_Disclosure.docx`](LangAI3.0_AI_Disclosure.docx) | Word Document | Official AI Usage Disclosure Form detailing team info, purpose, prompt logs, and human modifications. |
| [`Apollo_SamsungXR_Presentation.pptx`](Apollo_SamsungXR_Presentation.pptx) | PowerPoint | Comprehensive 14-slide Apollo presentation deck highlighting architecture, geometry, and evaluation results. |
| [`official_ppt_template_supplied_by_judges.pptx`](official_ppt_template_supplied_by_judges.pptx) | PowerPoint | Official 9-slide template supplied by Samsung PRISM-XR judges. |
| [`Evaluation_for_SyntheticEyes.pptx`](Evaluation_for_SyntheticEyes.pptx) | PowerPoint | Track 01 technical specifications, requirements blueprint, and 60/20/20 scoring rubric. |
| [`XR_Hackathon_2026_Consolidated_Slides_for_sharing_v1.pdf`](XR_Hackathon_2026_Consolidated_Slides_for_sharing_v1.pdf) | PDF Deck | Official launch-event slides covering event rules, timeline, deliverables, and guidelines. |
| [`README.md`](README.md) | Markdown | Primary project homepage containing project overview, visual gallery, rubric mapping, and reproduction instructions. |

---

## 2. Runtime Demonstrations & Videos

| File | Duration | Format | Description |
| :--- | :--- | :--- | :--- |
| [`videos/left.mp4`](videos/left.mp4) | 12s (288f) | H.264 MP4 | Coordinated eye movement towards viewer's Left with lid follow and blink. |
| [`videos/right.mp4`](videos/right.mp4) | 12s (288f) | H.264 MP4 | Coordinated eye movement towards viewer's Right with lid follow and blink. |
| [`videos/generate_motion.mp4`](videos/generate_motion.mp4) | 12s (288f) | H.264 MP4 | Multi-axis natural gaze sequence with micro-saccades, eyelid dynamics, and neutral reset. |

---

## 3. Judge Reproduction & Runbooks

| Document | Primary Focus |
| :--- | :--- |
| [`docs/V22_QUICKSTART.md`](docs/V22_QUICKSTART.md) | **Recommended for Judges**: Step-by-step setup, archive reassembly, and CLI rendering commands. |
| [`docs/RUNBOOK.md`](docs/RUNBOOK.md) | Operator reproduction steps, verification procedures, and Docker container instructions. |
| [`docs/PS_AUDIT.md`](docs/PS_AUDIT.md) | Comprehensive audit of deliverables against the 60/20/20 competition scoring rubric. |
| [`docs/V22_12_SECOND_DEMOS.md`](docs/V22_12_SECOND_DEMOS.md) | Frame-by-frame inventory and extension methodology for the 12-second motion demonstrations. |
| [`docs/RELEASES.md`](docs/RELEASES.md) | Versioning conventions, release tag history (`apollo-v0.3.0`), and SHA-256 archive digests. |

---

## 4. Source Code & CLI Entry Points

| Path | Responsibility |
| :--- | :--- |
| [`tools/gnm_run.py`](tools/gnm_run.py) | **Primary Judge CLI**: Headless renderer accepting `{still, left, right, generate-motion}` and `--variant`. |
| [`tools/reassemble_release.py`](tools/reassemble_release.py) | Standalone Python utility to verify and join multi-part release ZIP archives. |
| [`tasks.py`](tasks.py) | Portable project task CLI for testing, scene builds, frame sweeps, and qualification. |
| [`apollo_core/`](apollo_core/) | Pure Python/NumPy analytical geometry, 3D Rodrigues rotation, conic projection, and PNG chunk filtering. |
| [`tools/`](tools/) | Verification harnesses, grader simulators, independent geometric audits, and texture baking utilities. |
| [`tests/`](tests/) | Automated pytest test suite (175 tests validating kinematics, schema, and cross-platform integrity). |

---

## 5. Clean-Room Qualification Receipts

| Report | Result | Description |
| :--- | :--- | :--- |
| [`milestones/v22-12-second-demonstrations-2026-11-22/qualification/final-qualification-summary.json`](milestones/v22-12-second-demonstrations-2026-11-22/qualification/final-qualification-summary.json) | **Passed** | Comprehensive summary of clean Windows & Linux qualification. |
| [`milestones/v22-12-second-demonstrations-2026-11-22/qualification/windows-qualification.json`](milestones/v22-12-second-demonstrations-2026-11-22/qualification/windows-qualification.json) | **Passed** | Clean Windows extraction and runtime reproduction in path with spaces. |
| [`milestones/v22-12-second-demonstrations-2026-11-22/qualification/linux-qualification.json`](milestones/v22-12-second-demonstrations-2026-11-22/qualification/linux-qualification.json) | **Passed** | Headless Linux Docker container extraction and runtime reproduction. |
| [`milestones/v22-12-second-demonstrations-2026-11-22/qualification/cross-platform-comparison.json`](milestones/v22-12-second-demonstrations-2026-11-22/qualification/cross-platform-comparison.json) | **68.26 dB** | Cross-platform image PSNR comparison between Windows and Linux CPU path-tracing renders. |
