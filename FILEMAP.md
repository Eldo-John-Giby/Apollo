# Repository File Map

Navigation index. Inspect implementation before changing it.

## Status and flow

Apollo implements synthetic binocular gaze for Samsung PRISM-XR Track 01.
The GNM submission path is qualified on pinned public Head v3: five texture
sets, three packed timelines, 576 frames and clean offline reproduction.
The detailed candidate adds 4K scan-derived skin, portable surface maps,
improved native lid contact and qualified interruption recovery. Its exact
receipt is under `milestones/gnm-score-final-candidate`.
Start with `docs/GNM_QUICKSTART.md`; build details are in `docs/GNM_INTEGRATION.md`.
The evaluator asset match and deferred human review remain pending.
The protected radial-iris development freeze remains available. The competition
upgrade adds a qualified warm-iris/lid/lash look, independent geometry audits,
a complete seeded 256-image dataset, optional controls and evidence media.
The protected competition-qualified release passes native/Linux V1Ã¢â‚¬â€œV17 and all
applicable secondary checks, with 79 tests on both platforms. The CPU adult-female appearance candidate is integrated into main;
qualification of that earlier appearance candidate remains deferred. Generated temporary
artifacts belong under out/ and are not listed here.

Flow: character inspection/mapping or fixture Ã¢â€ â€™ calibrated scene Ã¢â€ â€™ standalone eye
wrapper Ã¢â€ â€™ PNGs/metadata Ã¢â€ â€™ image validation/contact sheet Ã¢â€ â€™ V1Ã¢â‚¬â€œV17 Ã¢â€ â€™ production ZIP.

## Requirements and research

Phase closure and next-work boundaries: `docs/PHASE_HANDOFF.md`. The realism
preview is published as apollo-v0.3.0-rc.1; exhaustive qualification is deferred.

| File | Responsibility |
| --- | --- |
| `TEAM_SETUP.md` | Teammate onboarding, pinned tools, packed-scene workflow, MPFB assets, daily checks, collaboration and release boundaries. |
| `AGENTS.md` | Navigation, standing no-video/no-presentation rule, release naming and checkpoint commits. |
| `docs/problem_statement.md` | Screenshot-transcribed requirements, rubric, deliverables, unresolved organizer questions. |
| `docs/SOLUTION_TECHNICAL.md` | Proposed geometry, conventions, API, verification checks, risks, and limitations. |
| `docs/IMPLEMENTATION_PLAN.md` | Original phased plan and embedded reference math/tests; numbered companion references mean the unnumbered files here. |
| `docs/ROADMAP.md` | Current rubric-driven milestones, evidence gates, priorities and deferred scope; use for next development steps. |
| `docs/gemini_deep_research_web.md` | Prompt for reusable-code/asset research, not findings. |
| `docs/gemini_deep_research_papers_prompt.md` | Prompt for academic literature discovery, not findings. |
| `docs/Synthetic Gaze Reconnaissance Plan.docx` | Component research report; independently verify reuse/license claims. |
| `docs/Synthetic Gaze Literature Discovery.docx` | Literature report; independently verify cited claims. |
| `docs/Module 6 Congestion Control.ppt` | Unrelated/undetermined presentation, not used by the pipeline. |
| `docs/RUNBOOK.md` | Operator setup, fixture workflow, character handoff, framing, verification, Docker and submission steps. |
| `docs/PERFORMANCE.md` | Measured sample-count timing/noise tradeoffs, secondary-runtime provenance and Docker limitations. |
| `docs/DEVELOPMENT_FREEZE.md` | Chosen freeze quality, rubric evidence, archive reproduction and explicit validation limits. |
| `docs/PS_AUDIT.md` | Requirement-by-requirement technical coverage and remaining event/submission deliverables against the user's consolidated specification. |
| `docs/SUBMISSION_PIPELINE.md` | CPU commands, evaluator mesh integration, and qualification handoff for the final outputs. |
| `docs/UPGRADE_PROGRESS.md`, `docs/VERIFIER_COVERAGE.md` | Upgrade execution gates, measured prototype status and verifier independence/coverage limitations. |
| `docs/UPGRADE_RUNBOOK.md` | Reproduction commands for upgraded looks, independent/dataset adversaries, controls, Linux qualification, deck/video and archive rehearsals. |
| `docs/RELEASES.md` | Uniform release/tag names, historical version mapping and promotion policy. |
| `docs/PHOTOREALISM_V2.md` | V2 construction, appearance review, measured CPU checks, deviations and development handoff. |
| `docs/VISUAL_REALISM.md` | Current appearance work, rejected prototypes, reproducible checkpoints and remaining visual/technical gates. |
| `docs/CHARACTER_POLISH.md` | Adult-face refinement plan, matched still review, CPU checks and release boundary. |
| `docs/character_mapping.example.json` | Explicit stock-eye identifiers, orientation confirmation and attribution template. |

## Entry points and core

| File | Responsibility |
| --- | --- |
| `tasks.py` | Portable CLI orchestrating test, inspection, scene build, sweep, framing, validation, sheet, prepare, demo, verify, bundle, Docker and separate seeded dataset generation. |
| `wrapper/eyes.py` | Standalone Blender API/CLI; embedded NumPy core; absolute pose, evaluated geometry/projection checks, atomic metadata output. |
| `apollo_core/core.py` | Finite inputs/config, fixation, shortest-arc rotation, camera projection, exact pupil conic, sweep and annotations. |
| `apollo_core/metadata.py` | Structural/semantic protocol checks and optional analytic checks against a supplied calibration. |
| `metadata.schema.json` | Ten-frame JSON Schema; mathematical consistency is enforced by Python validation. |
| `check_core.py` | Direct reference assertion runner; normal task tests use pytest. |
| `pyproject.toml`, `requirements.txt` | Pytest configuration and pinned Python tool dependencies. |
| `Makefile`, `Dockerfile`, `.dockerignore` | Task aliases and pinned Blender/Linux container build (built and tested locally). |
| `README.md`, `DECISIONS.md` | Current usage/evidence and recorded implementation decisions/remaining validation. |
| `.gitignore`, `.dockerignore`, `.gitattributes` | Exclude caches/downloads from source and containers; preserve exact milestone payload bytes for checksums. |

## Scene construction

| File | Responsibility |
| --- | --- |
| `build/fixture_scene.py` | Procedural face proxy, open scleral shells, iris/pupil meshes skinned to dedicated eye bones, camera/light calibration; explicitly marks fixture. |
| `build/inspect_character.py` | Read-only source rig/mesh/material/image inventory for explicit mapping. |
| `build/build_scene.py` | Load mapped source face, preserve spacing, integrate eye rig and selected flat/radial look, pack textures and save candidate. |
| `build/polish_scene.py` | Build an isolated radial-iris material candidate, preserve calibration/pupil geometry, and render five-direction comparison evidence. |
| `build/finalize_mpfb_character.py` | Create/finalize the MPFB character in an MPFB-enabled Blender: CC0 assets, split stock eyes, uniform 63 mm spacing, packed source and mapping. |
| `assets/character_mapping.json`, `assets/ATTRIBUTION.md` | Actual source-eye mapping and selected character asset provenance. |

`assets/base_character.blend` and its completed mapping are now present.
Integration requires -Y facing, meter scale, aligned anatomical eyes,
58Ã¢â‚¬â€œ68 mm center spacing, actual stock-eye mesh names, and attribution.

## Verification and artifacts

| File | Responsibility |
| --- | --- |
| `tools/sync_core.py` | Embed core math in wrapper or check drift; strips the source future import for embedding. |
| `tools/validate_metadata.py` | JSON Schema/semantic checks and exactly ten 1024Ãƒâ€”1024 PNG validation. |
| `tools/grader_sim.py` | Image-only ellipse pupil detector, weighted mask centroid, subpixel template-displacement detector. |
| `tools/reference_geometry.py`, `tools/independent_audit.py` | Independent Rodrigues/projection oracle, deformed mesh measurements and disposable Blender defect injection. |
| `tools/pixel_oracle.py` | Geometry-guided dark-surface pixel check independent of OpenCV detectors; not a visibility-mask replacement. |
| `tools/visibility_audit.py`, `tools/analyze_visibility.py` | Dataset corner/random occlusion masks, independent mask centroids and rendered half-pupil fault detection. |
| `tools/lighting_adversary.py` | Disposable rendered lighting-loss fault, requiring lighting signature and pupil-pixel rejection. |
| `tools/dataset_protocol.py`, `tools/generate_dataset.py`, `tools/analyze_dataset.py` | Separate seeded/resumable dataset protocol, Blender generation, independent image checks and coverage artifacts. |
| `tools/submission_variants.py`, `tools/submission_bake.py`, `tools/submission_textures.py` | Generate MPFB development palettes, bake base color to aligned target UVs, and validate and render texture manifests. |
| `tools/submission_motion.py` | Build packed 24 fps expression timelines for Left, Right and Generate Motion, with optional PNG frame rendering. |
| `tools/submission_motion_check.py`, `tools/submission_uv_rehearsal.py` | Validate saved timeline gaze and pupil coverage, and rehearse color transfer onto a changed local UV layout. |
| `tools/submission_render.py`, `tools/submission_bundle.py` | Resume CPU timeline PNG rendering with frame receipts and verify the fallback ZIP. |
| `tools/submission_seams.py` | Repack split local UVs and check face/iris color transfer before rebinding on a fresh scene. |
| `tools/gnm_template.py`, `tools/gnm_import.py` | Verify the pinned Google model and import its original topology and native UV layouts into Blender. |
| `tools/gnm_skin_trial.py`, `tools/gnm_skin_fill.py`, `tools/gnm_eye_maps.py` | GNM color-transfer build with measured projection coverage and native eye tiles. |
| `tools/gnm_texture_trial.py` | Fresh-template and timeline texture application, CPU inspection renders and scene/map/build-bound still receipts. |
| `tools/gnm_skin_detail.py` | Bake reproducible authored brow fibers into the native skin atlas using surface-to-UV correspondence, with source and output hash receipts. |
| `tools/gnm_surface_maps.py`, `tools/gnm_eye_detail.py` | Author native-UV skin pigment, physical-scale relief/roughness and distinct bilateral iris/sclera maps with reproducible provenance. |
| `tools/gnm_materials.py` | Shared portable skin surface-map bindings for still and cached motion scenes. |
| `tools/gnm_natural_maps.py`, `tools/gnm_natural_trial.py` | Experimental owner-review skin/brow/iris maps and optional short-hair preview; isolated from the qualified runtime and not visually accepted. |
| `tools/gnm_portrait_maps.py`, `tools/gnm_portrait_refine.py` | Isolated still-portrait complexion maps, reversible anatomy keys, fitted brow/lash fibers, swept scalp groom and matched/neutral multi-angle reviews; not a motion-qualified replacement. |
| `tools/gnm_portrait_check.py`, `docs/GNM_PORTRAIT_REFINEMENT.md` | Reopened source/candidate geometry, UV, packed-resource and groom checks; portrait evidence, reproduction and qualification limits. |
| `tools/gnm_peak_maps.py`, `tools/gnm_peak_realism.py`, `docs/GNM_PEAK_REALISM.md` | Further portrait trials: linear scan relief, 16-bit pores, ocular optics, fitted lid/tear anatomy, vellus and strand variation; micro-skin diagnostics and review status. |
| `tools/gnm_groom_finish.py` | Restore uncapped ear complexion and blend scalp pigment and short fibers at the nape and front hairline. |
| `tools/gnm_expression_still.py` | Test an asymmetric mouth and cheek pose on the packed portrait and fit facial vellus to that pose. |
| `tools/gnm_stubble_still.py` | Compare two densities of surface-fitted cheek and chin stubble under the same portrait lighting. |
| `tools/gnm_feedback_still.py` | Apply portrait review notes with a defined jaw, matte skin, lip and lid creases, fuller brows, visible lashes and a lower, less uniform groom. |
| `tools/gnm_crown_study.py` | Test a shorter side-parted crown, varying strand absorption and an irregular tapered hairline; render matched views of the fuller-brow portrait. |
| `tools/gnm_lash_study.py` | Compare upper-lash splay and silhouette in matched eye crops and a full front portrait. |
| `tools/gnm_ocular_study.py` | Test inner-corner sclera color and softer corneal reflections using matched eye crops. |
| `tools/gnm_complexion_study.py` | Test localized cheek and lower-lid complexion, skin mottling and regional roughness in the isolated portrait. |
| `tools/gnm_realism_overhaul.py` | Build versioned geometry, skin, eye, hair and light passes on the packed haired portrait, with fixed-camera and beauty renders. |
| `tools/gnm_realism_compositor.py` | Install the beauty compositor on the editable portrait and preview it on the saved render. |
| `tools/gnm_portrait_review.py` | Refine front hair density, right eye aperture, corneal reflections and ear texture on the packaged v08 portrait. |
| `tools/gnm_upper_face_review.py`, `tools/gnm_sclera_vessels.py` | Refine forehead complexion, scleral capillaries and tear-corner tissue on v12, with a packed vessel mask and review crop. |
| `tools/gnm_soft_face_review.py`, `tools/gnm_face_depth_review.py` | Continue the latest haired portrait with softer jaw settings, denser upper/lower lashes, tear tissue and reversible anatomical depth, with matched still reviews. |
| `tools/gnm_eye_finish.py`, `assets/gnm-eye-photo/source.json`, `assets/gnm-eye-photo/ATTRIBUTION.md` | CC0 photographic iris-sector reconstruction, source provenance and fitted lash/lower-waterline refinement trials. |
| `tools/gnm_gaze_readability.py` | Evaluate native horizontal-target amplitude alternatives for review without changing production timing or face geometry. |
| `docs/GNM_NATURALNESS_REVIEW.md` | Owner/teammate feedback, prototype state, known failures and handoff for the next appearance workflow. |
| `tools/gnm_portable.py` | Preserve packed image bytes while replacing authoring filenames with relative paths before timeline delivery and variant caching. |
| `tools/gnm_scan_transfer.py`, `tools/gnm_generate_textures.py` | Checksum-verified attributed scan registration, emission transfer, measured CC0 fallback and five complete native texture sets. |
| `assets/gnm-scan/source.json`, `assets/gnm-scan/ATTRIBUTION.md` | Pinned scan asset URLs/checksums, CC-BY-3.0 source license and derivative attribution. |
| `docs/SCORE_IMPROVEMENT.md` | Current 60/20/20 audit, prioritized implementation and candidate qualification record. |
| `tools/gnm_gaze_trial.py`, `tools/gnm_blink.py`, `tools/gnm_timeline_trial.py` | Evaluate native gaze anchors and clip geometry using upstream NumPy, then install and check the Blender timeline. |
| `tools/gnm_blink_polish.py` | Build an isolated blink appearance review with matched animated upper lashes, slightly wider open lids, and localized matte skin. |
| `apollo_core/submission_timing.py` | Shared deterministic motion timing for the MakeHuman and GNM submission paths. |
| `tools/gnm_bundle.py`, `tools/gnm_verify.py`, `tools/gnm_rehearse.py` | Verify reopened GNM timelines and package the technical archive from authenticated frame and texture outputs. |
| `tools/gnm_run.py`, `tools/gnm_motion_variant.py` | Run stills or motion with any texture variant and UV layout; pack hash-bound variant timelines for resumable rendering. |
| `tools/gnm_review.py` | Prepare anonymous, receipt-bound direction and five-variant appearance comparisons with a separate assessor key for deferred teammate review. |
| `tools/gnm_comparison.py` | Authenticate the published baseline archive and candidate still receipts, then create matched front/side panels and native eye/skin crops for every variant. |
| `docs/GNM_INTEGRATION.md` | Pinned GNM setup, trial results and qualification status. |
| `docs/GNM_QUICKSTART.md` | Extracted GNM package setup, runtime commands, output locations and capture inputs. |
| `tools/live_controls.py` | Optional Blender sidebar invoking the public wrapper; never required or automatically enabled in graded scenes. |
| `tools/ui_rehearsal.py` | Real Blender panel operators: pose-render/API byte parity and official sweep output validation. |
| `build/upgrade_looks.py` | Distinct iris-region/shading/light candidates and MPFB lid/lash refit; preserves pupil/eye geometry and calibration, requires MPFB for building only. |
| `build/photorealism_scene.py`, `build/photorealism_config.json` | Separate v2 adult female bake, preserved orbital contact, licensed skin/iris materials and baked bun/brow groom; source/config/asset receipts and protected-eye checks. |
| `build/portrait_refinement.py`, `docs/PORTRAIT_REFINEMENT.md` | Packed-v2 portrait refinement: cheek contour, feathered satin lips, fuller fitted brows and temple fibers; isolated build and targeted acceptance plan. |
| `tools/portrait_checkpoint.py` | Gate targeted portrait evidence and package a development scene with matched portrait stills and a hash manifest. |
| `build/eye_expression.py` | Build skin microdetail, iris reflections and gaze-driven eyelid shape keys from a packed appearance scene. |
| `build/complexion_polish.py` | Refine nose and jaw proportions and add procedural freckles and rose lipstick over the eye-expression scene. |
| `build/brow_fill.py` | Pack a feathered pigment mask beneath the existing eyebrow fibers to fill visible gaps. |
| `build/skin_realism.py` | Add procedural pore relief, subtle complexion variation and varying sheen to the packed portrait. |
| `build/character_polish.py` | Source-bound v2 appearance pass with lower-face contour, feathered lip shading and a replacement brow groom. |
| `assets/photorealism-v2/ATTRIBUTION.md` | Native skin/eye texture provenance, licensing and checksums. |
| `build/realism_scene.py`, `build/realism_config.json` | Isolated anatomy/surface/groom checkpoints with seeded baked strands, actual lid/sphere contour fitting, preserved eye meshes and source-bound build receipts. |
| `tools/realism_visibility.py` | Resumable 81-grid + 32-random RGB stress poses and real occlusion masks; separate from official and research protocols. |
| `tools/realism_hero.py` | Separate front/three-quarter presentation portraits; preserves the saved calibrated scene and writes no graded metadata. |
| `tools/realism_comparison.py` | Hash-checked, pose/calibration-matched baseline/candidate sheets and native eye crops; leaves visual ratings to explicit review. |
| `tools/direction_report.py` | Five-direction measurements, reset comparison and enlarged visual comparison from checkpointed verification renders. |
| `tools/direction_review.py` | Scene/hash-checked shuffled center-reference pairs, human response sheet and separate assessor key for direction readability. |
| `tools/direction_smoke.py` | Actual baseline/cardinal/reset image gate; optional hash-bound pose reuse with a fresh eyes.reset() render. |
| `tools/early_image_gate.py` | Early blind/template checks on the actual sweep or checkpointed dataset using independent projections and unchanged thresholds. |
| `tools/photorealism_checks.py` | Targeted v2 geometry, CPU/RSS benchmark, 9-pose visibility, directions, official sweep, still diagnostics and comparisons; never releases. |
| `tools/photorealism_persistence.py` | Serial persistent-data-off timing and exact image comparison against a matching baseline benchmark. |
| `tools/photorealism_diagnostics.py` | Disposable neutral-light and clay portrait renders without modifying saved scene or graded metadata. |
| `tools/scene_preflight.py` | Run the existing verifier V1/V2 functions without renders; scene/source-bound early failure report, never full qualification. |
| `tools/blender_verify.py` | Blender evidence worker with progress checkpoints: calibration/metrics, random evaluated poses, repeated sweeps, direction images, isolated/occluded masks, packed resource audit; hash-guarded mask-only reruns. |
| `tools/verify.py` | V1Ã¢â‚¬â€œV17 coordinator, pixel/direction/visibility checks, clean-room/secondary subprocesses, evidence-bound JSON/Markdown reports and hash-guarded evidence reuse. |
| `tools/framing_sweep.py` | 85Ã¢â‚¬â€œ135 mm experiments and eye-sphere margin/shift selection; brows/lashes still need visual review. |
| `tools/benchmark_render.py` | Isolated Configurable 8Ã¢â‚¬â€œ128-sample center/up/down or corner timings and pose records; leaves the source scene and qualified settings unchanged. |
| `tools/contact_sheet.py` | 5Ãƒâ€”2 annotated sheet, crosshairs, reset rings, direction clocks, fixture label. |
| `tools/prepare_candidate.py` | Candidate-specific README and fixture attribution; production attribution must already exist. |
| `tools/demo.py` | Labeled sweep GIF and presentation/recording outline; not a final narrated video. |
| `tools/build_presentation.mjs`, `tools/build_demo_video.py` | Editable Artifact Tool evidence deck and 105-second actual-artifact demonstration with local synthesized narration. |
| `requirements-research.txt`, `requirements-media.txt` | Optional measured dataset plots and demo-video authoring dependencies. |
| `tools/make_bundle.py` | Reject fixtures, stale evidence and incomplete reports; stage ZIP, size/integrity/extraction checks. |
| `tools/freeze_candidate.py` | Development-only archive using shared qualification gates; per-file manifest, ZIP integrity and extraction checks. |
| `tools/release_rehearsal.py` | Actual ZIP regeneration from clean config/different CWD; complete and interrupted 255Ã¢â€ â€™256 dataset resume reproduction. |
| `tools/finish_realism.py` | Wait for existing qualification/checkpoints, gate technical export, verify Git bytes and optionally commit/tag/push; never authors media. |
| `tools/check_release.py` | Verify release manifests, ZIP integrity and source/payload hashes against staged or committed Git blobs. |
| `tools/export_upgrade.py` | Gate technical milestones, executable delivery, still-image evidence and complete research-dataset ZIP; excludes videos/decks. |

## Tests and relationships

- `tests/test_core.py`: original eleven geometry assertions from the implementation plan.
- `tests/test_protocol.py`: invalid inputs/config/metadata, exact conic boundary, embedded core and standalone import parity.
- `tests/test_artifacts.py`: image/sheet validation and production packaging gates.
- `tests/test_verification.py`: blind detector/template synthetic accuracy, centroid coordinates and missing-runtime report behavior.
- `tests/test_realism_visibility.py`: deterministic 113-pose square-boundary coverage.
- Core is authoritative; regenerate wrapper embedding with `python tasks.py sync` after core edits.
- Reports bind scene, wrapper, metadata and render hashes. Regenerate/reverify after changing these artifacts.
- `all` orders tests Ã¢â€ â€™ sync Ã¢â€ â€™ scene Ã¢â€ â€™ sweep Ã¢â€ â€™ validate Ã¢â€ â€™ sheet Ã¢â€ â€™ prepare Ã¢â€ â€™ demo Ã¢â€ â€™ verify Ã¢â€ â€™ optional production bundle.
- Missing evidence is NOT RUN or FAIL; all seventeen checks are required for production packaging.
- Calibration defaults: meters, -Y forward, +Z up, anatomical L at +X, camera 40 cm, target 35 cm, bounds Ã‚Â±5 cm, clockwise ten-frame sweep.
- Deliberate deviations from original documents: preserve measured production IPD instead of forcing 63 mm; horizontal sensor fit; simplified non-refractive procedural eyes; visual review remains necessary.

Update affected entries when important source files or responsibilities change;
exclude generated outputs, dependencies, caches and build artifacts.



