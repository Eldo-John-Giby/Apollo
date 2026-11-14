# Track 01 evaluation and submission audit

Updated 15 November 2026 from the organizer emails supplied by the team,
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
| 5–10 textured UV map sets covering face and eyes, with 5–10 rendered images using different textures | Five sets on pinned public Google GNM Head v3, each with 4096-pixel scan-derived skin color, roughness and 16-bit height, two distinct 1024-pixel eye maps and a matched 1024-pixel judging still. All five have neutral/oblique front and three-quarter views, close eyes and authenticated rc.4 comparisons. Both UV layouts agree within one RGB level; clean-extraction still reproduction is exact. Evaluator model match is unconfirmed. |
| Python script to render using generated textures | tools/gnm_run.py selects the variant and UV layout for stills and motion. A clean extraction reproduced the rose-brown judging still and both layout comparison stills pixel-for-pixel. Golden-hazel motion agreed between layouts within one RGB level, with cached-scene resume preserving valid frames. |
| Left, Right and Generate Motion input modes | All three packed GNM timelines have 192 full-quality PNGs at 24 fps and 32 CPU samples. Resume repaired missing and corrupt frames. A real interrupted render resumed through frame 26, preserving the valid first frame. Extracted CLI outputs and the recovered segment reproduce exactly. |
| Three runtime-captured videos, each at most 15 seconds | Team deliverable outside the current technical-project objective. |
| Blender Timeline expression | All three packed timelines reopen offline with every evaluated pose within one micrometer of the reference clip, original topology/UVs and packed maps intact, and zero absolute image paths. Fresh upstream NumPy evaluation matches all 576 saved poses exactly. Native lid follow, brow response and asymmetric blink remain. Full-closure gap decreased from 1.24 mm to approximately 0.20 mm; a thin contact crease remains. |

The technical archive and clean-extraction evidence are recorded in
[the detailed GNM candidate receipt](../milestones/gnm-score-final-candidate/receipt.json).
The archive contains 779 authenticated payload files and all 576 full-quality
frames. Clean extraction, offline resource checks, alternate-variant resume,
corrupt/missing-frame repair, real interruption recovery and all 88 Python tests pass. The known visual
limitations and deferred teammate review are recorded in the receipt.
Use [the GNM quickstart](GNM_QUICKSTART.md) for runtime commands and the exact
capture inputs. The earlier rc.3 evidence remains preserved under
milestones/gnm-technical-candidate.
The qualified detailed archive is prepared for `apollo-v0.3.0-rc.5`; publication
is recorded separately in its milestone directory. The published
[Apollo v0.3.0-rc.4](https://github.com/Eldo-John-Giby/Apollo/releases/tag/apollo-v0.3.0-rc.4)
and its verified downloads remain preserved.

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
form submission remain unverified. The repository is currently private; the
team must make the final GitHub resources public and verify signed-out access.
Confirm any separate general demo requirement
with the PoC. The supplied template has nine slides covering team details,
problem, solution, architecture, track outputs, differentiation, demo/local
setup, brownie features and closing.

The standing project rule prohibits Codex from creating, editing, regenerating
or scheduling video and presentation artifacts. The organizer requirements
above remain team deliverables. Preserve the supplied decks and historical
media.
