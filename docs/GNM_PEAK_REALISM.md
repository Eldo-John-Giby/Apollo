# Continuing realism development

Owner instruction: push the existing face toward maximum realism and keep
improving it. This work continues after the first portrait checkpoint; the
goal is not considered achieved by passing an asset-integrity check.

## Confirmed defect and repair

The first portrait's `height.1001.png` was constant white. The authoring code
divided a 16-bit source PNG by 255, then clipped and saved it at 8-bit
precision. Thus its purported pore-relief layer contributed no variation.
`read_data_image()` now normalizes by stored precision and keeps height
outputs at 16 bits. Regression cases cover representative 16-bit relief
values and 8-bit roughness. This defect was in the isolated portrait recipe;
the supplied source scene and qualified submission were preserved.

## Further trials

`tools/gnm_peak_realism.py` builds from the packed first portrait, not from
the qualified runtime. Trials add refractive corneas with a transparent-shadow
approximation, fitted water menisci, small moist inner-corner tissue,
subtle bilateral ocular texture variation, regional lip roughness, individual
hair absorption/roughness variation, and 10,000 fine facial vellus fibers.
The optional orbital-anatomy shape key fits folds to the actual lid opening.
The native Basis, topology, UV layouts and eye vertices remain available.

`tools/gnm_peak_maps.py` transfers the existing registered Infinite Scan
relief as linear, non-color 16-bit data. Only a high-pass component is blended
over the synthetic pore field; donor macro anatomy is not transferred.
Source attribution remains CC-BY-3.0 with the project's existing CC0 sources.
The ocular capillaries are authored synthesis.

The new checker option `--require-relief` verifies the *reopened active image*
has 16-bit PNG payload, Non-Color interpretation and nonzero relief variance.
It also checks all visible mesh additions through the render delivery gate.
This guards against a correct source PNG being left unbound in the scene.

## Review discipline

Compare neutral front, close-up and three-quarter renders with the first
portrait, then inspect a smaller grazing key. Do not use softness, depth of
field or a flattering light alone as proof of improved anatomy or detail.
Early trials remain under `out/peak-realism-v1` through `v4`. The v4 trial
was rejected by the attachment gate: vellus sampled on alternate quad
diagonals could float above the evaluated surface. The builder now projects
each root onto the same BVH surface used by the checker. Its rejected packet
is preserved under `out/peak-realism-v4-rejected-checkpoint`.

Remaining visual concerns include the overall uniformity of the eye whites,
the controlled hairstyle's cap-like nape, the balance between lip sheen and
skin roughness, and the amount of physically visible pore detail. A separate
optional micro-skin layer adds physical-scale pore normals independently of
the atlas texel density. V5 tests that layer and the repaired vellus; it is
not accepted merely because it exists in the code. It needs a macro review
and a reopened attachment check before promotion.

The groom is static. Motion deformation, engine export and organizer scoring
are outside these still-appearance checks. No numerical realism score or
human approval is inferred. Keep the maximum-realism goal active while these
visual concerns remain unverified.
