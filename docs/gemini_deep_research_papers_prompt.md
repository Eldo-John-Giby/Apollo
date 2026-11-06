# Gemini Deep Research Prompt — Samsung PRISM-XR 2026, Theme 1

## Role and mission

Act as a senior academic research librarian and computer graphics researcher specializing in ocular kinematics, 3D facial rigs, gaze synthesis, camera geometry, synthetic data, and reproducible rendering.

Conduct a **comprehensive, verifiable literature discovery** for **Samsung PRISM-XR Hackathon Challenge 2026 — Theme 1: Synthetic Eye Movement & Virtual Camera Rendering**.

Your job is **research discovery, not solution design**. A separate agent (Claude Code) will later inspect the papers, assess which ideas can be adapted, and decide on an implementation. Do not prematurely filter out papers for difficulty, age, GPU requirements, or apparent implementation convenience.

**Read the attached Theme 1 specification Markdown as the authoritative statement of competition requirements.** The summary below is context only. If the attachment differs, report the discrepancy and defer to the attached specification.

## Problem context

The task concerns a textured, articulated 3D face/eye rig; independent left/right eye rotation; deterministic horizontal and vertical gaze controls; a fixed virtual camera; 1024 × 1024 rendered PNGs; a ten-frame clockwise eye movement sequence; and per-frame metadata including gaze inputs, eye rotations, pupil centers in image coordinates, and camera parameters. The competition describes CPU-based execution. Exact APIs, angles, scoring, output format, and dependencies must be checked against the attached specification rather than inferred.

The core research question is:

> Which published methods could contribute geometric, anatomical, procedural, calibration, projection, rendering, or validation techniques to an accurate, deterministic, reproducible synthetic eye movement and virtual camera pipeline?

## Research scope

Search thoroughly across these areas, including foundational and recent publications through November 2026:

1. **Anatomical and parametric eyeball modeling:** eye shape, rotation centers, iris/pupil geometry, eye sockets, eyelids, corneal surfaces, binocular geometry, ocular kinematics.
2. **Procedural gaze animation:** gaze targets, horizontal/vertical input to rotations, independent versus coordinated eye movements, coordinate frames, quaternions, rotation matrices, inverse kinematics, saccades, fixation, and gaze trajectories.
3. **Facial rigs and 3D morphable models:** FLAME, MakeHuman, GNM and related systems, blendshapes, bone-based animation, eye articulation, retargeting, facial assets and their associated publications.
4. **Virtual camera calibration and projection:** pinhole cameras, intrinsics/extrinsics, fixed-camera geometry, coordinate transforms, 3D-to-2D pupil projection, perspective effects, pixel coordinate conventions, synthetic calibration.
5. **Pupil and iris localization:** analytic ground-truth pupil centers, visible versus geometric pupil center, synthetic annotations, eye segmentation, eyelid occlusion, image-based verification.
6. **Synthetic gaze datasets and generators:** UnityEyes, SynthesEyes, MPIIGaze, ETH-XGaze, GazeCapture, NVGaze, and related works. Separate dataset-generation methods from gaze-estimation methods.
7. **Rendering methods:** procedural rasterization, conventional/physically based rendering, eye appearance, corneal reflections, differentiable rendering, render/annotation consistency, deterministic and CPU-capable pipelines.
8. **Automated calibration, reproducibility, and validation:** geometric consistency tests, gaze direction verification, rendering determinism, metadata correctness, visual regression, calibration automation.
9. **Adjacent fields:** robotics, biomechanical eye models, simulation, photogrammetry, digital humans, medical eye tracking, synthetic-data annotation, and other transferable methods.

Search alternate terminology and conduct both backward and forward citation chaining. Look beyond highly cited or recent papers; obscure technical methods may be valuable.

## Sources and verification

Use Google Scholar, Semantic Scholar, arXiv, IEEE Xplore, ACM Digital Library, CVF Open Access, Eurographics, SIGGRAPH, university repositories, official author/project pages, and publisher pages where accessible. Use GitHub for associated code and assets. Secondary aggregators may aid discovery but should not be the sole verification source.

Aim for **40–80 genuinely relevant publications**, if supported by the evidence. Do not pad the catalog. Verify titles, authors, years, venues, DOI/arXiv IDs, and URLs. Never invent papers, code repositories, or numerical results. If full text is unavailable, explicitly mark conclusions as abstract-only or secondary-source-based.

## Required record for every paper

Assign stable IDs `P001`, `P002`, etc. Provide:

- **Exact title, authors, year, venue, DOI/arXiv identifier**.
- **Official paper URL**, open-access PDF URL if available, official project page and code repository if available.
- **Classification:** foundational, methodological, empirical, survey, or technical report; primary and secondary topic clusters.
- **Research problem:** what the authors actually investigated.
- **Core contribution:** precise algorithm, geometry, mathematical model, rendering method, or system insight; avoid generic summaries.
- **Technical details:** equations, coordinate transformations, calibration methods, optimization objectives, rotation conventions, camera models, annotation procedures, and evaluation protocols. Give section/page/equation numbers when verified.
- **Relevance mapping** to the following requirements:
  - R1: Textured articulated face rig
  - R2: Independent eye rotation
  - R3: Deterministic horizontal/vertical gaze control
  - R4: Fixed virtual camera and projection geometry
  - R5: Accurate 2D pupil-center ground truth
  - R6: Clockwise ten-frame sequence
  - R7: Per-frame metadata
  - R8: Visual direction correctness
  - R9: Automated reproducibility
  - R10: Computational efficiency
- **Transferable ideas for later inspection:** describe specific ideas without proposing a final implementation.
- **Dependencies and limitations:** only documented hardware, assets, datasets, licenses, training requirements, and known constraints; mark unknowns.
- **Evidence level:** full-paper verified / abstract verified / official documentation / secondary source only.
- **Citations supporting the claims** with direct URLs and page/section references where possible.

Distinguish what the paper proves from your interpretation of possible transferability.

## Synthesis deliverables

### 1. Master paper catalog

A comprehensive Markdown table:

| ID | Paper | Year | Core contribution | Requirements mapped | Official paper link | Code available? | Evidence level |
|---|---|---|---|---|---|---|---|

### 2. Detailed paper records

Use the required per-paper schema above. Maintain stable IDs and working links.

### 3. Research clusters and citation relationships

For each technical cluster, identify foundational work, major improvements, competing approaches, documented limitations, and unresolved research questions. Describe meaningful paper-to-paper relationships, distinguishing confirmed citations from inferred conceptual similarities.

### 4. Open-source artifact inventory

List associated repositories, datasets, pretrained models, assets, and reproducible research artifacts. Include official URL, related paper IDs, purpose, verified license, languages/frameworks, artifact type, and evidence of maintenance where available. Do not claim a repository runs without testing.

### 5. Research gaps

Assess the literature's coverage of exact projected pupil coordinates, deterministic gaze control, independent eye articulation, fixed-camera calibration, ten-frame sequence correctness, CPU execution, and cross-machine reproducibility. Distinguish actual literature gaps from insufficient search coverage.

### 6. Consolidated bibliography

Provide a clean, machine-readable Markdown bibliography with one consistently formatted entry per paper, using the same IDs as the report. Include DOI, arXiv, PDF, and code URLs when verified.

### 7. Search transparency

Summarize search queries, databases, date coverage, citation-chaining approach, inclusion/exclusion criteria, and important access limitations. State where further investigation would be necessary.

## Strict boundaries

- **Do not design the solution, choose a tech stack, or write code.**
- **Do not rank papers by ease of implementation or subjective usefulness.** Claude will do that later.
- Do not dismiss relevant work because it needs a GPU, a proprietary tool, or substantial computation; document the constraint instead.
- Do not prefer neural methods over analytical geometry, or recent papers over foundational ones.
- Do not conflate gaze estimation with gaze generation, eyeball centers with pupil centers, or projected centers with image-detected centers.
- Do not invent unsupported technical details, evaluation metrics, references, or licenses.
- Avoid filler explanations and generic background; maximize actionable research evidence.

**Final output:** a self-contained, source-verified research corpus that another AI agent can independently evaluate for transferable ideas relevant to Samsung PRISM-XR Theme 1. Begin the research now.
