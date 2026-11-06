# Gemini Deep Research Prompt — Existing Solution Reconnaissance for Samsung PRISM-XR Theme 01

## Mission

Act as an exceptionally thorough open-source intelligence researcher, GitHub code-search specialist, and computer-graphics engineering researcher.

**Your job is to find what has ALREADY BEEN BUILT that solves, approximates, or contains reusable pieces of Samsung PRISM-XR Hackathon 2026 — Theme 01: Synthetic Eye Movement & Virtual Camera Rendering.**

This is **not** an academic paper survey, and **not** a request to design a new implementation. I have a separate literature-research effort. This investigation must scour the general web for actual code, repositories, runnable demos, archived projects, hackathon entries, student projects, tutorials with complete code, engine samples, Blender scripts, 3D assets, and public solutions to related challenges.

### My underlying intention

I have very limited hands-on development and testing time. I plan to give your findings to Claude Code, which will inspect the actual source code and decide what is technically and legally reusable. I want to avoid reinventing components that someone has already implemented. Find complete solutions if they exist; otherwise find the smallest set of credible existing components that collectively cover the requirements. **Do not assume that similarity in a project title implies reusable functionality.** I want verifiable evidence, direct source links, runnable entry points, license details, and honest descriptions of what is missing.

The goal is legitimate reuse, adaptation, and learning—not plagiarism, misrepresenting another team's submission, or violating licenses or hackathon rules.

## 1. Source of truth: Samsung specification

I will attach a Markdown file containing the complete Theme 01 problem statement and the general hackathon rules. **Read that attachment first.** Extract the exact required inputs, outputs, interfaces, camera geometry, animation behavior, rendering constraints, metadata fields, evaluation criteria, and execution environment. Quote exact requirements where necessary and cite the attached specification by section.

For orientation, the challenge concerns a textured articulated face/eye rig, independently controllable eyeballs, deterministic `eyes.move(h, v)` and `eyes.reset()` controls, a fixed virtual camera approximately 35 cm in front of the eyes, 1024×1024 PNG rendering, a ten-frame clockwise sequence, and accurate JSON metadata including 2D pupil centers. **If the attachment contradicts this summary, follow the attachment.**

Create requirement IDs `R01`, `R02`, etc. from the actual specification. Keep official requirements separate from assumptions, suggestions, and unconfirmed details.

## 2. Search for direct and near-direct solutions first

Find any publicly accessible project that already implements one or more of the following:

- Fully procedural or scripted 3D eye gaze rendering.
- A face rig with independently rotatable eyes and a fixed virtual camera.
- `eyes.move(h,v)`-style horizontal/vertical gaze controls and reset behavior.
- Automated generation of eye images plus exact 2D pupil/iris coordinates.
- Synthetic gaze datasets whose generators or rendering pipelines are open source.
- Camera-calibrated 3D eye animation and synchronized pupil movement.
- Headless, deterministic rendering with image and JSON annotations.
- A clockwise gaze sweep with known angles and metadata.
- An end-to-end solution to a substantially equivalent assignment, challenge, benchmark, or hackathon.

Search exact phrases, alternative wording, code symbols, and distinctive combinations of requirements. Search for Samsung PRISM / PRISM-XR references and publicly released challenge materials, but do not assume previous solutions exist.

## 3. Search surfaces — investigate all

### Code hosting and software archives

GitHub, GitLab, Bitbucket, Hugging Face Spaces and repositories, Codeberg, SourceForge, Gists, archived repositories, software supplementary materials, and academic project code. Use GitHub repository search **and code search** where available. Examine README files, examples, demos, issues, releases, commit history, and actual relevant source files.

### Hackathons and student projects

Devpost, Unstop, Hackster, university capstone showcases, student GitHub organizations, project exhibitions, public coursework, coding competitions, computer-graphics assignments, game jams, XR/AR/VR competitions, and Samsung PRISM-related project pages. Search for prior entries solving similar gaze-animation, facial-rigging, synthetic-eye-data, or camera-calibration tasks. Clearly distinguish a confirmed solution from a merely related entry.

### Tutorials and developer communities

Blender Stack Exchange, Blender Artists, Blender documentation and add-ons, Stack Overflow, Unity forums and asset samples, Unreal Engine samples, Godot demos, OpenCV communities, graphics programming blogs, YouTube videos with downloadable code, technical walkthroughs, and personal project sites. Prefer complete working examples over text-only tutorials.

### 3D models and assets

MakeHuman, FLAME-related public resources, Blender-compatible facial rigs, eye-rig assets, permissively licensed character models, and procedural eye generators. Check whether assets are downloadable, legally reusable, textured, rigged, and capable of independent eye rotation. Note when a model requires registration or has research-only restrictions.

### Synthetic data and eye-tracking ecosystems

UnityEyes, SynthesEyes, gaze dataset generators, eye-tracking simulators, procedural face animation frameworks, and calibration toolkits. Find actual generator code or official downloadable assets rather than citing datasets alone.

## 4. Search laterally, not just by project name

Try combinations of terms such as:

- `blender python eye rig gaze render pupil center`
- `synthetic gaze generator github pupil coordinates`
- `3d eyeball rotation camera projection code`
- `headless blender gaze animation json annotations`
- `procedural eye movement 3d face rig github`
- `eyeball rig independent rotation python blender`
- `synthetic eye dataset generator source code`
- `camera calibrated pupil center ground truth rendering`
- `gaze direction to eye bone rotation quaternion`
- `blender eye tracking simulation dataset`
- `virtual camera eye model 2d iris center projection`
- `facial rig gaze control script github`
- `eye gaze animation hackathon project github`

Also search exact snippets and filenames from the attached problem statement, using exact-match search where possible. Search alternative languages and ecosystems when likely to uncover useful code. Follow links from projects to forks, predecessors, demos, and dependent repositories.

## 5. Required evidence for EACH candidate

Give each result a stable ID (`S001`, `S002`, ...). Record:

1. **Name and precise URL** (repository, demo, downloadable asset, or project page).
2. **Creator/maintainer** and last observable activity date, if verifiable.
3. **What actually exists:** source code, model, rig, scripts, weights, assets, executable, demo, or merely documentation.
4. **Evidence of functionality:** exact file paths, function/class names, command-line entry points, README sections, screenshots/videos, tests, or output samples. Link directly to relevant source files where possible.
5. **Requirements covered:** map to `R01` etc.; distinguish fully covered, partially covered, and unsupported.
6. **Reusable components:** describe the concrete code/assets/algorithms potentially reusable, without writing a new solution.
7. **Integration boundaries:** inputs, outputs, dependencies, supported formats, and what would need adaptation.
8. **CPU/headless feasibility:** documented CPU support, GUI requirements, runtime/compute information, and unknowns. Never infer a runtime benchmark without evidence.
9. **License and attribution:** exact SPDX/license if verifiable, license URL, commercial/research restrictions, redistribution obligations, and whether no license was found. A public GitHub repository is **not automatically open-source or reusable**.
10. **Availability and reproducibility:** links live? instructions complete? downloadable assets present? broken dependencies? archived/unmaintained? State what was actually verified.
11. **Missing functionality:** explicitly identify what it does not solve for Samsung Theme 01.
12. **Evidence confidence:** inspected source / inspected docs / demo only / third-party mention / unverified.

Do not claim you ran a repository unless you actually executed it. Do not invent code paths, licenses, performance numbers, compatibility, or URLs.

## 6. Classify results by degree of direct reuse

Organize discoveries into:

- **A. Near-complete solutions:** substantially satisfy the full challenge contract.
- **B. Major building blocks:** implement a substantial subsystem such as gaze rigging, procedural rendering, pupil annotation, or camera projection.
- **C. Small reusable utilities:** focused functions/scripts for rotations, projection, metadata, headless rendering, validation, etc.
- **D. Assets and infrastructure:** textured eye/face rigs, renderers, datasets, example environments.
- **E. Analogous solutions:** different task, but a clearly transferable method or code pattern.
- **F. Leads needing verification:** promising but not sufficiently inspectable.

Do not force results into category A. A working demo with no accessible source should not be labeled a directly reusable implementation.

## 7. Cross-project synthesis — WITHOUT choosing an implementation

Construct a **component coverage matrix** showing which projects cover which official requirements. Identify combinations of existing projects that might cover the full problem, but do not select a final architecture or assert integration will be trivial.

For each plausible combination, note license compatibility concerns, language/framework mismatches, data format gaps, and unverified dependencies. Explicitly flag any essential requirement for which no credible public implementation was found.

Identify duplicate projects, forks, mirrors, abandoned successors, and cases where multiple repositories derive from the same upstream code. Avoid inflating the count with duplicates.

## 8. Search quality and stopping rules

Aim for **25–60 distinct, substantive candidates** if that many genuinely exist. Do not pad the catalog. Spend disproportionate effort on high-value, hard-to-find sources and working code. Continue exploring citation trails, repository topics, code imports, forks, related repositories, and linked demos until additional searching yields mostly duplicates or weak matches.

Document the major query families, platforms searched, search limitations, and areas where results were scarce. If a site blocks access or code search is unavailable, state that limitation. Do not silently substitute guesses.

Prefer primary sources: original repositories, official project pages, developer documentation, archived source snapshots. Treat Reddit, blog posts, and videos as discovery leads unless they link to verifiable artifacts.

## 9. Output format — make it useful to Claude Code

Produce a **self-contained Markdown report** with:

1. Executive reconnaissance summary (facts only, not a final solution recommendation).
2. Exact official requirement checklist from the attached Samsung specification.
3. Search methodology and coverage.
4. A table of all candidate projects with IDs, direct links, category, coverage, license, and evidence quality.
5. Detailed individual records for each substantive candidate.
6. Source-file index: `candidate ID → repository URL → relevant files/functions → role`.
7. Component-to-requirement coverage matrix.
8. Hackathon, coursework, and previous-solution discoveries (clearly distinguish confirmed vs suspected).
9. Open 3D assets and licensing matrix.
10. Possible cross-project combinations and unresolved integration issues.
11. Broken links, unavailable code, ambiguous licenses, and other blockers.
12. Remaining gaps and a bibliography/link inventory.

At the end, include a **Claude Code inspection handoff**: a concise ordered list of repositories/files worth opening first, with the reason each is worth inspection and the precise question Claude should answer about it. This is a reading priority, **not** a decision about what to implement.

Use stable IDs throughout. Link directly to source files rather than only repository homepages when possible. Make the report readable without the original conversation.

## 10. Non-negotiable rules

- **Do not implement or design the final solution.**
- **Do not produce a generic academic literature review.** Actual code and artifacts are the focus.
- **Do not equate stars, popularity, or a flashy demo with technical suitability.**
- **Do not misrepresent public availability as permission to copy.** Check licenses and attribution.
- **Do not present another hackathon team's submission as our own.** It may be studied or reused only within applicable rules.
- **Do not fabricate project links, functionality, file paths, or licenses.**
- **Do not omit partial solutions** merely because they are not end-to-end.
- **Do not hide uncertainty** when source inspection is impossible.
- **Do not assume a GPU, proprietary software, or cloud API is allowed.** Follow the attached specification and flag unknowns.
- **Do not decide the final stack or architecture.** Claude Code will independently assess actual usefulness.

**Success means discovering the maximum amount of verifiable, legally reusable existing engineering work so that Claude Code can build on proven components instead of starting from zero. Begin with the attached Samsung Theme 01 specification, then investigate the wider web systematically.**
