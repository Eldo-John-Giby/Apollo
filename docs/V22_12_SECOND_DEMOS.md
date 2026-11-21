# Twelve-second v22 demonstrations

These demonstrations were explicitly requested on 22 November 2026. They extend
the preserved eight-second checkpoint `a2c02d8`; they do not replace or rewrite
the original technical archive and its 192-frame reproduction contract.

Each mode runs for 288 frames at 24 fps: 12 seconds, below the organizer's
15-second cap. The approved character, textures, camera, lighting, 1024×1024
resolution, and 512 Cycles samples remain unchanged.

Left and Right add a return to center, a second look toward the requested side,
and another blink. Generate Motion adds a different order of gaze shifts across
both axes, a blink, and a return to neutral. These are new timeline keys using
the validated rig pose library. The clips are not slowed down or made by looping
the original video. Exact held poses can reuse authenticated PNG bytes.

## Files

- `videos/left.mp4`, `videos/right.mp4`, `videos/generate_motion.mp4`: H.264
  demonstrations, encoded at CRF 15 and decoded to check all 288 frame timestamps.
- `timelines/<mode>/expression.blend`: packed 288-frame timelines, playable offline.
- `timelines/<mode>/expression.extension.json`: source scene hashes and timing maps.
- `frames/<mode>/frame_0193.png` through `frame_0288.png`: GPU-rendered extension
  frames, with full render receipts. The first 192 frames remain in the preserved
  base archive; they are reused byte-for-byte in the new videos.
- `checks/`: fresh-process scene comparison and image-only direction/blink results.
- `delivery.json`: complete 864-frame combined inventory and video checksums.
- `manifest.json`: supplement payload hashes and the required base archive hash.

The supplement includes the original asset licenses. It does not include cloud
credentials, SSH keys, personal endpoint responses, or private assessor answers.

## Reproduce

Extract the preserved base archive and the supplement into separate directories.
Open an extended `.blend`, select its camera, and play frames 1–288 at 24 fps.
All textures and groom data are packed into the scene.

To build an extended scene from an untouched base timeline with pinned Blender
4.5.15 LTS (build `5afeabba6097`):

```powershell
blender --offline-mode -b --factory-startup base/timelines/left/expression.blend --python-exit-code 1 -P tools/gnm_v22_extend.py -- --phase build --out extended/timelines/left/expression.blend
```

To render its added frames on an NVIDIA CUDA GPU:

```powershell
blender --offline-mode -b --factory-startup extended/timelines/left/expression.blend --python-exit-code 1 -P tools/gnm_v22_extend.py -- --phase render --out extended/frames/left
```

Repeat with `right` and `generate-motion`. The worker requires CUDA and refuses
CPU fallback. It records the actual device, build, scene hash, settings, and
every completed image hash. Matching receipts allow interruption/resume.

The independently reopened scenes are compared against their original animation
channels and unchanged geometry, UVs, packed textures, and material nodes.
The Left build used the preserved `provenance/worker-v1.py` snapshot; later builds
use the final worker. The difference adjusts only Generate Motion's added blink
timing. Each scene/report remains bound to its actual worker hash.

To verify and encode, install Pillow and provide an FFmpeg binary with libx264:

```powershell
python tools/gnm_v22_extended_delivery.py --base base --supplement extended --ffmpeg ffmpeg
```

Encoding requires the preserved base PNGs and authenticated extension PNGs. A
combined image directory uses local hard links to avoid duplicating all images.

## Acceptance boundary

These are demonstration and technical verification outputs. They do not establish
independent human acceptance, an organizer score, or final qualification of the
original archive on both Windows and Linux. Those gates remain separate, and
`release_ready` remains false. The original eight-second checkpoint is retained
as a fallback.
