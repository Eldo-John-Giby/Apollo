# Track 01 evaluation and submission audit

Updated 12 November 2026 from the organizer emails supplied by the team,
the supplied Track 01 evaluation deck (`Evaluation_for_SyntheticEyes.pptx`) and
submission template (`official_ppt_template_supplied_by_judges.pptx`).
The forwarded evaluation email explicitly directs teams to generate all slide 2
outputs and describes natural human-like simulation as brownie credit. Slide 2
also puts realism in the scored rubric. Use this audit for final planning and
keep the launch specification as historical context. See the
[submission pipeline](SUBMISSION_PIPELINE.md) for development commands and
qualification steps once the evaluator asset arrives.

## Current evaluation

| Category | Points | What the deck emphasizes |
| --- | ---: | --- |
| Texture photorealism | 60 | High-frequency skin and iris detail, realistic colors and seamless application |
| Kinematic accuracy | 20 | Coordinated eye motion, realistic eyelid closure and smooth expressions |
| Code and UV portability | 20 | Direct texture application to the target head and automated execution |

The evaluation deck gives no CPU-only rule, GPU requirement or render-time cap.
Apollo's CPU timing gates are internal. The deck gives no numerical allocation
for brownie credit.

## Required outputs and Apollo readiness

| Slide 2 output | Apollo evidence and remaining work |
| --- | --- |
| 5–10 textured UV map sets covering face and eyes, with 5–10 rendered images using different textures | **Major gap.** Apollo's packed MPFB character and appearance milestones show skin and iris detail on their own mesh. Five local texture variants have matched renders and map receipts. Face and iris maps passed a transfer onto subdivided, triangulated MPFB targets with rotated UVs. Direct GNM wrapping is still unverified. Confirm the canonical mesh and UV layout, then round-trip one licensed face-and-eye set on it and inspect seams before scaling to five distinct sets and corresponding renders. |
| Python script to render using the generated textures | **Partial.** Existing Blender automation renders the packed Apollo scene. Verify that a clean checkout can load the target mesh, select each exported set and reproduce its still without the original project scene or local asset paths. |
| Python script accepting Left, Right and Generate Motion and rendering frames and video | **Partial.** The standalone wrapper supports deterministic binocular gaze, reset, single renders and the old ten-frame sweep. The new submission CLI builds all three named modes and writes PNG frames. Sampled timelines and a two-frame render passed on MPFB. All three MPFB draft frame sequences are available for review. Full-quality frames and target-rig integration are pending. |
| Three runtime-captured videos, one per input, each at most 15 seconds | **Pending team deliverable.** The historical sweep and general demo do not demonstrate three distinct runs under the new cap. |
| Blender file with an expression animated in the Timeline | **Partial.** Three MPFB timelines reopened at 24 fps with matching sampled poses. The revised local blink blocked both pupils at both sampled peak frames in all three modes. Fit and verify the final expression on the evaluator rig. |

Slide 1 recommends GNM initialization, scripted face shape and expression,
coordinated closure, UV transfer and distinct left/right iris maps. Slide 2
permits GNM or FLAME UVs in the texture guidance and says the textures will be
wrapped directly on GNM. Treat GNM compatibility as the conservative target
until the college PoC confirms the evaluator asset, accepted UV variants and
whether the 5–10 count means complete texture sets or individual maps. Confirm
whether the launch sweep, metadata and ZIP layout are still checked alongside
slide 2. Keep the qualified v0.2.0 package available as evidence for those older
outputs. Internal passes do not establish an organizer score.

## Submission logistics

| Milestone | Updated date |
| --- | --- |
| Final submission | 22 November 2026 |
| Top 12 announcement | 29 November 2026 |
| Final demo | 9 December 2026 |
| Final results | 12 December 2026 |

Use the final instructions email for dates. The evaluation deck's 28 October
date conflicts with that email. The email specifies no cutoff time for
22 November. Confirm the cutoff with the PoC.

The team must place the code, resources, documentation, demo, PPT, package and
README on **public GitHub** and submit its URL through the
[final submission form](https://forms.gle/86xENrtqhx988hBt8). Public access and
form submission remain unverified. Confirm any separate general demo requirement
with the PoC. The supplied template has nine slides covering team details,
problem, solution, architecture, track outputs, differentiation, demo/local
setup, brownie features and closing.

The standing project rule prohibits Codex from creating, editing, regenerating
or scheduling video and presentation artifacts. The organizer requirements
above remain team deliverables. Preserve the supplied decks and historical
media.
