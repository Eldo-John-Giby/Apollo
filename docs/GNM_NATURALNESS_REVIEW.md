# Naturalness review handoff — 16 November 2026

Stopped at the owner's request after the current preview finished. No new
release was built. The published rc.5 package and its qualification remain
unchanged; its appearance has not received human approval.

## Human feedback

The owner reviewed A01 and requested natural-looking skin, a less glassy eye
without the conspicuous iris pattern, shorter/tidier brows and head hair.
The owner did not supply numeric ratings and did not know how to assess a
texture seam. These must remain unrated, rather than inferred as a pass.

A teammate reported C01, C02 and A01 only. They requested clearer bilateral
gaze, some natural-coloured hair and a natural middle skin tone. Their C01/C02
direction headings are reversed against the hidden screen-space key, so
coordinate confusion is possible. Their confidence ratings and motion review
were not supplied. Keep this report separate from the owner's observations.

The existing camera checks measure both pupils moving: Left is -9.066/-9.314
pixels, Right is +9.310/+9.070 pixels in the 1024-pixel output. A stuck eye is
not established. Readability still warrants human comparison. Do not bend the
face sideways to imitate eye movement.

## Isolated experiment

- `tools/gnm_natural_maps.py`: source-map brow cleanup, shorter authored fibers,
  a darker skin gain, muted stock-atlas iris detail, roughness and scalp pigment.
- `tools/gnm_natural_trial.py`: restrained skin/corneal shading and 50,000 short
  hair strands on a separate object. Original head vertex positions remain
  unchanged by the groom. This is a static appearance experiment, not a
  qualified animated groom.
- `tools/gnm_gaze_readability.py`: seven upstream-native poses at baseline,
  1.5x and 2x horizontal fixation-target amplitude. These alternatives were
  evaluated but not rendered or accepted; production controls are unchanged.

The finished preview is `out/naturalness-review-v2/front.png` with its
`.render.json`. It used 1024 pixels, 32 Cycles CPU samples and the original
front camera/lighting. Maps and recipes are in that directory. A copy of the
preview and trial receipts is preserved in the matching review milestone.

## Known failures in this preview

The rendered hair is too light and stiff. The brow replacement is too faint
and leaves visible residual fibers near the lids. The skin is still fair in
the rendered lighting. The revised eye needs close-up and oblique review.
This preview is not accepted and must not replace the qualified maps, scenes
or receipts. Do not propagate it to all five sets or rebuild 576 frames yet.

The next workflow should address these visible failures, show a single
matched preview for owner review, and only then consider full propagation and
qualification. The earlier 82–90 estimate was provisional and is not validated
by the received human feedback. No new score is asserted here.

Original response sessions remain under `out/human-review-2026-11-15-owner`
and `out/human-review-2026-11-16-teammate`. No numeric responses were invented.
