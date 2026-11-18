# Realism pass, Sections 1 and 2

## Base mesh verdict: KEEP

- Blender 4.5.15 LTS. The head has 17,821 vertices and 17,662 quads with enough density for local lid and lip refinement. Within 6 mm of the sampled corners, each inner eye has four valence-5-or-higher poles, each outer eye has one, and the mouth corners have none. Keep the inner-corner edits small.
- Both skin UV layouts showed zero overlaps at 768 × 768 sampling. Density varies by about 1.6× from the 10th to the 90th percentile. There are 142 split skin edges per layout, including 63 in the frontal measurement box. Seams are not confined to the back and hairline. Eyelids and lips use the same skin material. Island-level seam placement around their margins remains unverified.
- Pupil spacing is 61.8 mm. Each eye group spans 29.2 mm. Front-image landmarks projected onto the mesh estimate a 36.7 mm inner-corner gap, 25–26 mm visible eye widths, a 28.2 mm nose width and a 49.2 mm mouth width.
- Estimated facial thirds are 56, 61 and 69 mm. The lower third is longest. Head width at eye level is about 154 mm, or six visible eye widths. On the sampled side, the ear top sits about 19 mm below the brow and the lobe about 15 mm below the nose base. These measurements use manually selected image landmarks.
- This saved portrait has six shape keys, including Basis, but no armature, head modifiers or shape-key drivers. The eyes are integrated mesh regions. The requested controlled gaze test remains pending on a rigged version of this same portrait.

## Setup changes

- Saved the byte-for-byte source backup as `portrait_BACKUP_pre_realism.blend` and the evaluation setup as `portrait_v01.blend`.
- Added three evaluation cameras, all at 85 mm and 36 mm sensor width, aimed at (0, 0, -0.025) m. Front position (0, -0.82, 0.03) m. Side positions (±0.40, -0.72, 0.03) m. The existing cameras and Key, Fill and Rim lights are unedited.
- AgX, Medium High Contrast, exposure 0, gamma 1. Cycles total/diffuse/glossy/transmission/volume bounces 12/4/4/8/0. Reflective and refractive caustics off. Indirect clamp 10. 64 samples, adaptive threshold 0.05, OpenImageDenoise. Portraits at 700 × 700 and crops at the native 1400-pixel frame scale. Cycles did not report a CUDA or OptiX device, so these previews used CPU.
- Embedded `realism_helpers.py` as a Blender text block. No geometry or material changes were made in this phase.
- Baseline reviewed in front, both three-quarter views, and the eye, mouth and hairline crops. Baseline scores in checklist order: 3, 2, 3, 3, 3, 2, 3, 2, 3, 2. Dense scalp coverage and a bright reflection create a pronounced light-dark split. Upper lashes are hard to see, cheek color reads blotchy, and ear and forehead surfaces read too smooth.

## Geometry, version 02

Eleven separate 0 to 1 shape keys are active at 1. The sculpt fields apply to skin vertices only. Existing keys are kept. The direction and position values below are in the mesh's local coordinates.

| Shape key | Edit at value 1 |
| --- | --- |
| `face_width` | Up to 7.5% jaw narrowing and 2.6% cheek narrowing, spatially blended |
| `forehead_height` | Up to 4.5 mm downward with 1.4 mm frontal-bone and 1 mm flattening fields |
| `jaw_chin` | 1.2 mm jaw-angle field and up to 1.5 mm chin projection |
| `cheekbones` | Up to 1.2 mm lift, 2.5 mm projection and 1.6 mm hollow |
| `nose` | Up to 0.8 mm alar widening per side, 0.42 mm lift and 1.1 mm dorsum offset |
| `lips` | 0.7 mm corner lift and up to 1.4 mm lower-vermilion projection |
| `eyelids` | Up to 0.58 mm upper-lid lift, 0.32 mm upper margin and 0.53 mm lower fullness |
| `ears` | Up to 1.1 mm rim width, 1.15 mm fold field and 1.2 mm lobe projection |
| `neck` | Up to 1.3 mm lateral muscle projection and 1.25 mm throat projection |
| `asymmetry` | Up to 0.6 mm signed shifts on orbital, ear, lip, nose and cheek fields |
| `resting_expression` | 0.28 mm upper and 0.45 mm lower lip separation fields with a 0.48 mm corner lift |

Added a charcoal neckline over the bust. Cloth roughness 0.79, sheen 0.18, bump 0.00012 m with noise scale 195, detail 2 and strength 0.2. Final color (0.013, 0.017, 0.023), specular 0.22. Welded the collar after the geometry review showed faceting. Curve roots follow the deformed skin at checkpoint values.

## Skin, version 03

Edited a duplicate skin material named `skin_v2`. Retained the packed registered relief and lip microstructure. The existing registered scan relief entered upstream through `tools/gnm_peak_maps.py` and remains in the active packed `height.1001.png` lineage. The complexion masks in this phase are procedural. Random Walk Skin uses weight 0.24, scale 0.0022 m, radius (1, 0.25, 0.10), IOR 1.4, sheen weight 0.08 and sheen roughness 0.51. The forehead and ears blend toward roughness 0.70 and specular 0.20, with 0.000052 m bump. The forehead crease field uses 0.000049 m bump. Cheek, temple and beard masks multiply the underlying color toward (0.85, 1.01, 1.03), (1.01, 0.99, 0.94) and (0.84, 0.91, 1.0). The original cheek mark remains visible.

## Eyes, version 04

Duplicated four existing materials as `eye_v2_1` through `eye_v2_4`. Retained the photographic iris texture, existing warm inner corners and tear geometry. Cornea IOR 1.376, roughness 0.024. Eye substrate specular 0.045. Kept all native eye vertices exact. The new matched grooms use 118 upper and 46 lower hairs per eye. Root radii vary by strand and taper to the tips. The final pass increased upper radius 17%. Dark brown lash shader color (0.027, 0.013, 0.008), roughness 0.58, specular 0.14. Original lash objects are preserved and hidden.

## Hair, version 05

Copied the existing scalp material to `Scalp_v2 brunette`. Huang Principled Hair with seeded strand variation, melanin 0.64 to 0.82, redness 0.33, roughness 0.42, radial roughness 0.41, IOR 1.55, coat 0.03 where exposed. The hairline keeps its prior feathered strands and fitted nape. The neutral-light image still shows a bright strip where the key catches the sweep.

## Lighting and final, versions 06 and 07

Organized original lights under `LIGHTS_EVAL`. Separate `LIGHTS_BEAUTY` uses three area lights, all aimed at (0, 0, -0.02) m.

| Light | Position, m | Size, m | Final watts | RGB |
| --- | --- | --- | --- | --- |
| Key | (-0.62, -0.63, 0.48) | 0.67 by 0.58 | 43 | (1, 0.94, 0.87) |
| Fill | (0.60, -0.36, 0.08) | 0.78 by 0.67 | 9 | (0.87, 0.93, 1) |
| Rim | (0.28, 0.43, 0.42) | 0.68 disk | 9 | (0.86, 0.93, 1) |

Beauty camera at (0.108, -0.78, 0.015) m aims at (0, 0, -0.036) m, at 85 mm, f/5.6 and 0.78 m focus distance, with 2 degrees of roll. The final camera-ray background interpolates (0.034, 0.042, 0.054) to (0.10, 0.109, 0.121), using world-direction Z from -0.19 to 0.21. The existing ambient world remains active on non-camera rays. The final denoiser uses RGB, albedo and normal. The final CPU run has a 1024-sample ceiling and a 540-second sampling cap. Final bounces are 10 total, 3 diffuse, 3 glossy, 8 transmission and 0 volume.

## Pending rig gate

The supplied version has no rotatable eye rig. Native eye geometry, vertices and UVs passed the reopened checks. The ±30° horizontal and ±20° vertical gaze tests require the user's rigged file. No pivots, bones, constraints or drivers were created or edited.

## Compositor and review, version 08

The editable compositor uses Fog Glow threshold 1.6, smoothness 0.25, strength 0.06 and size 0.22, lens dispersion 0.002, a blurred elliptical vignette at 0.07 and fine noise mixed at 0.02. The published composite uses the rendered PNG as its input. The saved scene uses Render Layers. Localized sharpening and an HDRI were omitted. The rectangular key and existing ambient world provide the reflections.

The 1400 × 1400 beauty render took 558 seconds including saving, then Blender took about 20 seconds to make the display composite. Cycles reached 125 samples before the time cap. The 1024 value is the ceiling. The backup and original remain byte-identical. The final scene passed the reopened checks for native topology, Basis, UVs, native eye vertices, packed relief and root attachment.

Scores are visual assessments in the brief's checklist order.

| Checkpoint | Pores | Redness | Lighting | Eyes | Lips | Hairline | Asymmetry | Ear, nose, neck | Proportions | Overall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Geometry | 3 | 2 | 3 | 3 | 4 | 2 | 3 | 2 | 4 | 2 |
| Skin | 3 | 3 | 3 | 3 | 4 | 2 | 3 | 3 | 4 | 3 |
| Eyes | 3 | 3 | 3 | 4 | 4 | 2 | 4 | 3 | 4 | 3 |
| Hair | 3 | 3 | 3 | 4 | 4 | 3 | 4 | 3 | 4 | 3 |
| Beauty and composite | 4 | 3 | 4 | 4 | 4 | 3 | 4 | 3 | 4 | 3 |

### Highest-value follow-up

1. Get a rigged copy of this same haired portrait, or authorize a separate rig build so the gaze and eyelid-follow checks can run on this model.
2. Break up the continuous frontal sweep with a sparser, more irregular first row of scalp fibers and blend the residual key highlight.
3. Use registered skin scans with more variation at the forehead and ears, and retouch the cheek mark and redness on the atlas. The current mesh can support those improvements.

## Temple, lid and material review, version 12

The update starts from v08. Changed the front-to-side junction at both temples by moving nearby root and tip positions along the scalp, tapering the dense row and adding finer transition strands. The temple band uses a local lateral center of 53 mm and a width of 16 mm, with up to 7.2 mm of vertical root shift before weighting. Core hair and temple tufts remain editable curves.

Added `Aperture balance | image right` with up to 0.43 mm upper lift and 0.15 mm lower drop in the unweighted field. Seven head-on ray samples near the center of each opening measured approximately 8.53 versus 8.01 mm before and 8.53 versus 8.54 mm after, in image-left to image-right order. The tear meniscus has a separate 0.10 mm lid-follow key. Native eye geometry remains exact.

Copied the cornea materials and reduced the glass contribution by mixing in 39% refraction at the same IOR. Glass roughness 0.036, refraction roughness 0.026. Added ear cartilage color and relief on a copied skin material. Local ear roughness blends toward 0.81 and specular toward 0.12. The ear bump distance is 0.000082 m. The renders are 850-pixel review stills under the existing lights.

## Forehead and inner-eye review, version 13

Added a forehead mask that fades through the brow and temples. It layers broad complexion variation, fine pore pigment and local bump on a duplicate skin shader. The new pore spacing uses scale 1780 and a bump distance of 0.000090 m at up to 0.58 strength.

Added a packed rose capillary mask projected across both eyes. The native radial UV gate excludes the iris and limbus. Raised the refraction blend to 65% and the glass roughness to 0.042. In the matched crop the large rectangular reflections are weaker. Fine vessels remain subtle at portrait scale.

The existing inner-corner tissue has a reversible `Fitted tear corner fold` shape key and an updated warm, low-gloss surface. The lower tear meniscus and native eye geometry remain in place. Reopening confirmed that the new mask is packed and the native eyes and UV layouts remain exact.

## Scleral vessel visibility, version 14

Kept the v13 eye geometry, tear corners and lighting. The packed vessel mask now widens selected primary branches from 3 to 6 texture pixels and increases their opacity by 72%. Fine branches remain narrower. The matched crop shows more distinct pink branching near the corners, especially on the whites toward the outside of the eyes.

## Natural vessel refinement, version 16

Continued from v15 on the same haired portrait. The strongest scleral paths now use curved interpolation with local variation, progressively thinner tips, uneven pigment density and a warmer rose color. The visibility mask remains packed. Only copied eye materials change in this pass.

The saved scene reopened without new render gate errors. Native eye geometry and UV layouts remain preserved. This is a still portrait check and does not validate gaze animation.

## Softer jaw, lashes and anatomical depth, versions 17 and 18

Version 17 reduces the existing jaw definition key to 0.30 and jaw/chin key to 0.35. It refits the facial fibers, replaces the visible groom with 170 upper and 82 lower tapered lashes per eye, and enlarges the existing tear-corner tissue slightly on a new reversible key. Existing groom objects remain hidden and preserved.

Version 18 adds four independent skin-only depth keys for the orbital crease, cheek transition, nose/cheek groove and philtrum/lip relief. Maximum unmasked field magnitudes range from approximately 0.4 to 0.9 mm. Native eye vertices are excluded. Jaw softening and the v17 lashes remain in place. Review images include matched front and eye crops plus a three-quarter angle.
