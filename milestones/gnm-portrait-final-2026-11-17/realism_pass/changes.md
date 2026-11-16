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
