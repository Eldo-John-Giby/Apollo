# Verification coverage audit

The frozen V1–V17 report is historical evidence for its exact inputs. All checks
passing is not proof of perfection or a competition-score estimate.

| Check | What the original check establishes | Remaining boundary / upgrade |
| --- | --- | --- |
| V1 | Configured camera/target/units, resolution and static animation audit | Independent camera transform and observed lighting signature added; arbitrary shader animation still needs adversarial review |
| V2 | Scleral radius/pivot/spacing consistency | Independent least-squares sphere fitting now measures deformed geometry |
| V3–V4 | Wrapper-offset axis and convergence at 1000 poses | Shared stored offsets weakened independence; new oracle measures pupil triangles directly |
| V5 | Shortest-arc torsion check | Does not establish full binocular physiological realism or validate L2/kappa modelling |
| V6 | Blender projection agrees with wrapper annotations | New separate fixed-convention pinhole/Rodrigues reference avoids production math imports |
| V7 | Unoccluded pixel-mask centroids within tolerance | Does not prove pupil visibility; diagnostic dithering/coverage require explicit handling |
| V8 | Ellipse detection on current appearance | Threshold/area priors are tuned to this scene, not universal detector robustness |
| V9 | Template displacement from an ellipse-initialized baseline | Shares initialization with V8; not fully independent. Separate geometry-guided pixel oracle added |
| V10 | Measured cardinals and exact reset | Human visibility/naturalness review and corners remain separate |
| V11 | 200 deterministic call-order sequences | Finite sample, not proof for every possible interaction |
| V12 | Exact repeated PNG/metadata hashes on one build/machine | Variable PNG text is intentionally stripped; cross-machine identity is not promised |
| V13 | Strict ten-frame protocol and analytic consistency | Production math is shared; independent annotation check now available; dataset uses its own protocol |
| V14 | Mask coverage and dark interior at sweep/cardinals | Does not establish natural socket/lash appearance or all square corners |
| V15 | Packed-resource audit and isolated-CWD regeneration | Same host; Docker freeze evidence was tests plus one pose, not full Linux qualification |
| V16 | Selected geometric/pixel/determinism checks on 5.2 | Nested report covers more, but original gate only requires V1–V7/V12; extend policy before broader claims |
| V17 | Annotation bounds and analytic agreement | Not independent physiological validation |

New report provenance includes scene/wrapper/render/metadata hashes, verifier
sources and raw diagnostic hashes. Legacy cache reuse is rejected; source/input
changes during qualification fail rather than creating a fresh-looking PASS.
Packaging now enforces the same verifier/evidence bindings. The corrected upgrade now passes a fresh native full run. The new V16 gate requires every
secondary check except recursive V16 itself; the older gate policy above remains
an accurate description of the protected historical report.

The corrected candidate also passes 25 actual pose masks, a rendered half-pupil
occlusion rejection and a rendered loss-of-illumination rejection. The separate
256-image corpus passes its independent pixel check. Actual extracted-archive
regeneration and completed/interrupted dataset resume pass. Full Linux qualification and its complete applicable secondary suite also pass. See UPGRADE_PROGRESS.md
for the selected scene hash and final evidence locations.

Broader detector robustness and human naturalness are not established by these
finite tests. Packaging tests cover changed diagnostics, missing frames, stale
inputs, fixtures, archive layout and manifest integrity. No existing threshold
was relaxed.
