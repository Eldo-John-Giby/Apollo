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

V5 passed the reopened geometry, packed texture and attachment checks. The
bound 16-bit height map had a normalized standard deviation of 0.0202 and
the projected vellus roots were within 0.009 mm of the evaluated surface.
The macro render shows fine relief on the nose and vertical lip striations.

The next groom trial restored native ear colour from the uncapped complexion
atlas and faded the original scalp density into short posterior strands. A
hard change in strand direction remained visible near the temple. The groom
recipe now blends the original lifted strand shape continuously into the
shorter, flatter strands. Review this change in profile and three-quarter
views before choosing it.

The eye trial uses the grey-blue photographic iris source documented in
`assets/gnm-eye-photo/ATTRIBUTION.md`. The transfer reconstructs occluded
sectors from unobstructed parts of the source and uses additional fitted
lashes and lower-lid pigment. Compare the close-up with the prior procedural
iris and check for angular smearing, a hard iris border and conspicuous lash
clumps.

The first photographic close-up showed a concentric band. The revised atlas
combines photographic variation with the earlier radial structure and
preserves the earlier pupil radius. An iris-only update reuses the existing
framing details for a direct comparison. The revised temple taper softens
the horizontal band in the three-quarter view.

The reviewed combined portrait is saved in
`milestones/gnm-portrait-realism-2026-11-16`. Its front and eye crop
come from the same packed scene. A subsequent lighting and skin study used
a 190 mm disk key with less specular contribution from the fill. Under that
same lighting, reducing skin subsurface weight from 0.65 to 0.46 and raising
the roughness range reduced broad glare on the nose and cheeks. The study
renders and scene are under `out/peak-skin-balance`. The remaining cues are
the uniform forehead and the rigid neutral expression. A first-impression
human review of the combined portrait has been requested.

The relaxed asymmetric mouth and cheek pose is saved under
`out/peak-expression`. Its three-quarter renders use the same geometry
under neutral and directional light. The reopened checks passed. Two
localized forehead studies changed pigment and roughness under matched
front lighting. The low-strength study barely changed visible pixels,
while the stronger study produced a blotchy patch near the temple.
Neither forehead study was added to the reviewed portrait.

The subsequent groom trial feathers the frontal scalp pigment and fits
short fibers to the front edge. The crown uses unequal clump heights and
spacing, followed by a sparse layer of tapered flyaways rooted in the
existing groom. The matched front render shows small silhouette changes
while the mid and lower face pixels match the previous render. The current
trial is saved under `out/peak-flyaways`.

The groom is static. Motion deformation, engine export and organizer scoring
are outside these still-appearance checks. No numerical realism score or
human approval is inferred. Keep the maximum-realism goal active while these
visual concerns remain unverified.
