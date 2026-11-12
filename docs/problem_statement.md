# Samsung PRISM-XR Hackathon Challenge 2026 — Theme 1 / Track 01

> Source: screenshots of the launch-event PowerPoint, presented 5 November 2026. This document transcribes and organizes visible information; it is **not** the original slide deck. Unreadable or unconfirmed details are identified rather than invented.

> **Final evaluation update (12 November 2026):** See [the current submission audit](PS_AUDIT.md) for the 60/20/20 rubric, GNM/FLAME UV and motion outputs, public GitHub requirement and revised schedule. The launch rubric and technical format below are retained for reference while the team confirms how they carry forward.

## 1. Event overview

- **Event:** Samsung PRISM-XR Team — XR Hackathon Challenge 2026
- **Launch:** 5 November 2026, 3:00 PM (as shown in meeting title)
- **Organizers:** XR Team and PRISM Team, Samsung R&D Institute India, Bangalore
- **Format:** Select a track, register a team, build a working prototype, and submit code, presentation and a demo video.
- **Team size:** Up to **4 members**, from a **single college**.
- **Team name convention:** `CollegeName_TeamName` (shown in the registration slide).
- **Theme restriction:** One theme/submission per team.
- **Finalists:** Top **15 teams** present live to a Samsung R&D jury.
- **Query email:** `prism@samsung.com`
- **Registration URL shown:** https://forms.gle/2h5t4zMXaoyJFd rj8 (spacing/characters should be verified against the slide before use; screenshot is not fully clear).

### Event dates

| Date (2026) | Milestone |
|---|---|
| 5 November | Launch; team registration opens |
| 8 November | Registration closes (registration slide says 11:59 PM) |
| 22 November | Final submission (cutoff time unspecified in the updated email) |
| 29 November | Top 12 teams announced |
| 9 December | Final demo |
| 12 December | Final results |

*The dates were marked tentative / subject to minor changes on the closing slide.*

### General registration requirements

- Register through the Google Form.
- Supply team name and per-member name, email, phone, year and branch.
- One theme per team.
- Final submission link is shared **only with teams that completed registration**.

### General final submission requirements

The final instructions email requires public GitHub and submission through the [final form](https://forms.gle/86xENrtqhx988hBt8). The list below records the launch instructions. See the [current audit](PS_AUDIT.md) for the updated output checklist.

The general submission slide lists:

1. Required deliverable for the selected theme (see Track 01 specifics below).
2. Working prototype code in a public or shared GitHub repository.
3. `README` with reproducible setup instructions, Docker files and other requirements where applicable.
4. Demo video, **maximum 3 minutes** (YouTube or Drive link).
5. Presentation (PPT or PDF) named according to the prescribed team-name convention.
6. One submission per team via the Google Form.

Presentation topics shown:

- Theme ID, project title and team details.
- Problem statement in your own words.
- Solution and architecture diagram.
- Tools and technology stack.
- Innovation highlights, results and limitations.

**Warning on slide:** Teams not following submission guidelines may be directly disqualified.

### Benefits and awards

- **Certificates:** Every shortlisted team receives a participation certificate; winners receive a merit certificate.
- **Prizes:** Top teams share prizes worth **₹1.0 lakh** (slide displays `₹1.0 L`). Exact distribution not shown.
- **PRISM worklet:** Winning teams get an opportunity to work in a PRISM worklet with a Samsung mentor; based on mentor availability, students and problem statement.
- **Samsung R&D internship:** Two-month summer internship for selected students. Slide notes selected students **may have to appear for a MAGIC coding test**; not a guaranteed internship for all participants or winners.

---

## 2. Track 01 — Synthetic Eye Movement & Virtual Camera Rendering

### 2.1 Objective and motivation

Build a **textured, articulated face/eye rig** that supports controlled, synchronized eye movements and reproducible virtual-camera rendering. The challenge centers on realistic, anatomically plausible eyeball motion and eye-pupil positioning in a fixed camera scene, with structured metadata to verify each frame.

The problem slide identifies a **synthetic gaze data gap**: training robust XR gaze estimators requires massive, ground-truth-annotated gaze datasets, but capturing real human eye movement across extreme gaze angles is slow, costly and restricted by strict privacy regulations.

Two motivation/realism themes on the slide:

- **Anatomical & kinetic realism:** 2D planar pupil translation looks unnatural; realistic eyes simulate true 3D spherical eyeball rotation around physical centers.
- **Rigid metric calibration:** 2D planar pupil translation lacks a natural realistic gaze simulation; accurate gaze depends on 3D spherical eyeball rotation around physical centers.

### 2.2 Challenge abstract (visible slide text, organized)

- Build a **textured, articulatable face model in Blender**.
- Provide a **Python wrapper** that rotates both eyeballs about their centers.
- Pupils move **Left / Right / Up / Down** with a center reset.
- Capture standardized **1024 × 1024** renders from a camera fixed **40 cm ahead**.
- Evaluate **5 directional pass/fail checks (100 pts)** in a **10-day rapid prototyping sprint** (as described on the challenge slide).

> The screenshots mention Blender as part of the challenge abstract. The exact permitted Blender version, renderer, dependency policy and CPU time limit are **not visible** in the supplied slides.

### 2.3 Key specifications

| Requirement | Specification from slide |
|---|---|
| Model | Textured, articulatable face rig; MakeHuman / GNM / FLAME with left/right eye bones (wording varies slightly between slides) |
| Fixation target | **35 cm forward** from eye midpoint; motion bounds **±5 cm** |
| Render camera | Locked **40 cm forward**, facing the face |
| Render output | **1024 × 1024 PNG** |
| Movement API | Deterministic Python controls `eyes.move(h, v)` and `eyes.reset()` |
| Movement sweep | Synchronous pupil articulation, **10 clockwise renders**, at `0k` through `2πk/10` for `k = 0…9` |
| Metadata | Per-frame ground-truth JSON containing inputs and 2D pupil centers |
| Directions tested | Left, Right, Up, Down, Reset/Center |
| Lighting | Constant lighting for rendered frames |

The clockwise sweep is described on the submission slide as `θₖ = 2πk/10 (k = 0…9), h = sin θₖ, v = cos θₖ, starting top`.

### 2.4 Required deliverables

1. **Complete Blender scene** with textured mesh, eye bones and materials.
2. **Python wrapper** and `README` explaining setup and execution.
3. **10 clockwise renders** (PNG), with per-frame JSON metadata.
4. **Contact sheet** or a **1–2 minute demo video** of the wrapper in action (track-specific deliverable).
5. **Submission ZIP** with the specified directory layout.

**Note:** The general hackathon slide separately requests a demo video of up to **3 minutes**. To avoid ambiguity, prepare a short demo satisfying both the track-specific 1–2 minute recommendation and the general maximum of 3 minutes.

### 2.5 Submission bundle layout

The slide calls for a single `team_name.zip` containing approximately:

```text
team_name.zip
└── team_name/
    ├── scene.blend
    │   # textured mesh, eye bones, materials
    ├── wrapper/
    │   └── eyes.py
    │       # eyes.move(h,v), eyes.reset(), eyes.render()
    ├── renders/
    │   └── [10 clockwise PNG frames]
    ├── metadata.json
    │   # per-frame inputs, rotations, pupil centers
    └── README.md
        # setup and run instructions
```

The slide's file tree is illustrative; use the official starter kit or submission instructions if they provide stricter names.

### 2.6 Per-frame metadata

A visible example on the metadata slide has this **approximate schema** (illustrative values and placeholder arrays, not a validated submission):

```json
{
  "frame": 3,
  "theta": 1.8849,
  "input": { "h": 0.951, "v": -0.309 },
  "eye_rotation_L": [0, 0, 0],
  "eye_rotation_R": [0, 0, 0],
  "pupil_center_2D_L": [0, 0],
  "pupil_center_2D_R": [0, 0],
  "camera_matrix": []
}
```

- Inputs are **normalized to [-1, +1]**.
- Eye rotations are represented in **3D world frame**.
- The slide describes **2D pupil centers projected at 40 cm**.
- The screenshot shows `metadata.json — one record per render`, but does not clearly establish whether the final file is a JSON array or another enclosing structure. Verify against the actual slide/starter kit.

### 2.7 Scene calibration constraints

- Fixation target **35 cm** forward from eye midpoint, with motion bounds of **±5 cm**.
- Render camera locked **40 cm** forward, facing the face.
- Output **1024 × 1024 PNG** under constant lighting.
- Clockwise sampling: `θₖ = 2πk/10`, `h = sin θₖ`, `v = cos θₖ`, starting at top.
- Demo: contact sheet or 1–2 minute video of wrapper in action.
- Open assets mentioned: **MakeHuman / MPFB (CC0), GNM Head Editor, Textured FLAME**. **Check each asset's actual license and suitability** before using; the screenshot does not establish universal license terms for all assets.

### 2.8 Launch evaluation — 100 points

| Category | Weight | Detail |
|---|---:|---|
| **Execution & Efficiency** | **40** | Calibration **20**; Automation **20** |
| **Quality & Movement** | **60** | Direction pass/fail **40**; Sequence & metadata **20** |
| **Total** | **100** | |

**Direction check (pass/fail):** Pupil shift must be visibly correct versus center for **Left, Right, Up, Down and Reset**. The slide states **all five directions must pass**.

---

## 3. Outstanding information to verify

- Exact registration URL (small screenshot text is not fully reliable).
- Whether the organizer provides a starter Blender rig or evaluator harness.
- Required Blender version, allowed packages and asset licensing.
- Runtime, RAM and CPU limits.
- Exact JSON schema and coordinate convention for 3D rotations and pupil centers.
- Whether evaluator expects fixed file names and directory paths beyond the illustrated bundle.
- Whether 1–2 minute track demo and general up-to-3-minute video are separate artifacts or can be the same.
- Whether there are updated dates or instructions after the launch presentation.

## 4. Source slide map

- **Slide 4:** Track 01 problem statement and motivation.
- **Slide 5:** Track 01 challenge blueprint, deliverables and 100-point evaluation.
- **Slide 6:** Track 01 submission bundle and scene calibration constraints.
- **Slide 7:** Track 01 per-frame metadata and direction pass/fail check.
- **Slide 23:** Overall event timeline.
- **Slide 24:** Registration, team rules, final submission requirements and presentation contents.
- **Slide 25:** Certificates, prizes, PRISM worklet and Samsung R&D internship.
- **Slide 26:** Registration information, contact and key dates.

*Compiled from user-provided screenshots, 6 November 2026.*
