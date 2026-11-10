# Direction readability iteration

Ambuj reported that isolated horizontal images made one eye appear straight,
left could resemble up, and down was hard to distinguish from looking forward.
He recognized up/down in the comparison sheet. Reset matched baseline.
The initial procedure did not keep baseline alongside every test image.

Implemented five shuffled, neutrally named review pairs. Every pair retains
native 1024x1024 RGB pixels with baseline at left and pose at right, equal scale,
fixed alignment and a consistent header. A separate assessor folder contains the
answer mapping and matched eye crops. A response table records uncertainty,
confidence and eye-specific comments for three independent observers. RUN_TEST.md
specifies the baseline-relative procedure and image-space directions.

A disposable native three-pose comparison raised fill energy from 0.24 to 0.36.
The matched eye crops brighten slightly, with little clear improvement in gaze
readability. The experiment was rejected after assistant visual review. The
rendered source scene hash remained unchanged. Stronger-fill images are retained
locally under out/direction-readability/fill-comparison. The assessor folder
includes its comparison and recipe receipt.

The reviewed horizontal positions have different absolute eye angles because
both eyes converge on the same target 35 cm away. The baseline-relative shift is
about 10 pixels in both eyes. Downward movement is about 8.1 degrees and 10.3
pixels at the full specified target displacement. Increasing those angles would
require changing the fixation constraints. The source candidate is retained for
the baseline-paired human review. Current technical accuracy results remain
applicable to that identical scene. Improved human recognition remains unmeasured.

Verification checked all five pairs pixel-for-pixel against their native source
frames, answer-key completeness, reset identity and the 15-row blank response
sheet. Source image hashes were validated against the tracked candidate manifest.
The renderer, wrapper and appearance recipe are unchanged by this iteration.
