"""Append four seconds of new gaze beats to a preserved v22 packed timeline.

Run in pinned Blender 4.5.15. Existing poses are a rig pose library: the new
return/refocus and reversed gaze order are keyed into the scene, not video loops.
The original 192 frames remain unchanged. Rendered output is a separate supplement.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

SOURCE_HASHES = {
    'left': 'afb2c2926b891ba18277a4fd52d8d6a93e8600c61c89f6741ac22a34d6f67c9b',
    'right': 'c39c35111f2a80f66746e47c535bc7676e5d96263a6ca0e5b94d301e392ead1c',
    'generate-motion': '1624eb5745558f53117ae644dd4ca0dedb0e0fa96500246e85961dcc1bf70aca',
}
SIDE_BEATS = [(192, 192), (198, 26), (205, 21), (221, 21), (227, 26),
              (241, 99), (244, 102), (245, 103), (250, 108), (288, 192)]
MOTION_BEATS = [(192, 192), (199, 164), (205, 159), (217, 159),
                (223, 130), (230, 124), (231, 103), (234, 106),
                (235, 107), (241, 112), (242, 113), (243, 93), (247, 93), (253, 87),
                (263, 87), (268, 58), (274, 53), (279, 25),
                (284, 20), (288, 20)]


def source_time(mode, frame):
    if mode not in SOURCE_HASHES or not 1 <= frame <= 288:
        raise ValueError('Invalid mode or frame')
    if frame <= 192:
        return float(frame)
    beats = MOTION_BEATS if mode == 'generate-motion' else SIDE_BEATS
    for (a, x), (b, y) in zip(beats, beats[1:]):
        if frame <= b:
            return round((x + (y-x)*(frame-a)/(b-a))*32)/32
    raise AssertionError('Uncovered frame')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    temp.replace(path)


def curves(bpy):
    # The pinned 4.5 scenes use legacy actions; fail rather than omit any action.
    for action in bpy.data.actions:
        if not hasattr(action, 'fcurves'):
            raise RuntimeError('Unsupported action API')
        yield from action.fcurves


def build(args):
    import bpy
    import numpy as np
    scene = bpy.context.scene
    source = Path(bpy.data.filepath)
    mode = scene['apollo_submission_mode']
    assert sha(source) == SOURCE_HASHES[mode], 'Source differs from saved checkpoint'
    assert scene.frame_start == 1 and scene.frame_end == 192
    assert scene.render.fps == 24 and scene.render.fps_base == 1
    assert scene.cycles.samples == 512
    assert scene.render.resolution_x == scene.render.resolution_y == 1024
    assert scene.render.resolution_percentage == 100
    assert not scene.render.use_motion_blur and not scene.cycles.use_animated_seed
    head = scene.objects['GNM Head']
    template_uvs = {u.name: np.array([tuple(x.uv) for x in u.data])
                    for u in head.data.uv_layers}
    mapping = [source_time(mode, f) for f in range(1, 289)]
    original_sequence = list(scene['apollo_gnm_pose_sequence'])
    channels = list(curves(bpy))
    assert channels, 'No animation channels found'
    check_times = [1+i*.5 for i in range(383)]
    before = [[float(c.evaluate(t)) for t in check_times] for c in channels]
    values = [[float(c.evaluate(t)) for t in mapping[192:]] for c in channels]
    # All values are captured before mutation, including the animated lash nodes.
    for channel, tail in zip(channels, values):
        for frame, value in enumerate(tail, 193):
            point = channel.keyframe_points.insert(frame, value, options={'FAST'})
            point.interpolation = 'LINEAR'
        channel.update()
    worst = max(abs(float(c.evaluate(t))-v)
                for c, old in zip(channels, before)
                for t, v in zip(check_times, old))
    assert worst < 1e-7, ('Original animation changed', worst)
    for uv in head.data.uv_layers:
        np.testing.assert_array_equal(template_uvs[uv.name],
                                      np.array([tuple(x.uv) for x in uv.data]))
    # New pose IDs are keyed by the complete animation-channel state. This also
    # includes eyelash closure, rather than assuming matching head geometry suffices.
    lookup = {}
    sequence = []
    for i in range(288):
        if i < 192:
            key = ('original', int(original_sequence[i]))
        else:
            key = tuple(round(tail[i-192], 8) for tail in values)
        if key not in lookup:
            lookup[key] = len(lookup)
        sequence.append(lookup[key])
    scene['apollo_gnm_pose_sequence'] = sequence
    scene['apollo_extension_source_frames'] = mapping
    scene['apollo_extension_original_scene_sha256'] = SOURCE_HASHES[mode]
    scene['apollo_extension_original_frames'] = 192
    scene.frame_end = 288
    scene.frame_set(1)
    assert not bpy.data.libraries
    for image in bpy.data.images:
        if image.source in ('FILE', 'TILED'):
            assert image.packed_file, image.name
    args.out.parent.mkdir(parents=True, exist_ok=True)
    assert not args.out.exists(), 'Refuse to overwrite an existing extended scene'
    bpy.ops.wm.save_as_mainfile(filepath=str(args.out.resolve()), compress=True,
                               relative_remap=False)
    report = dict(mode=mode, frames=288, fps=24, duration_seconds=12,
                  original_scene_sha256=SOURCE_HASHES[mode],
                  scene_sha256=sha(args.out), script_sha256=sha(__file__),
                  source_frames=mapping, new_beats=96,
                  animated_channels=len(channels), original_channel_error=worst,
                  samples=512, resolution=[1024, 1024],
                  pose_ids=sequence, release_ready=False,
                  method='New keyed gaze order and return/refocus using the validated rig pose library; no video looping or slowed playback.')
    write(args.out.with_suffix('.extension.json'), report)
    print('EXTENSION_BUILT '+json.dumps({k: report[k] for k in
          ('mode', 'frames', 'animated_channels', 'original_channel_error')}), flush=True)


def render(args):
    import bpy
    scene = bpy.context.scene
    assert bpy.app.version_string == '4.5.15 LTS'
    assert bpy.app.build_hash.decode() == '5afeabba6097'
    assert scene.frame_end == 288 and scene.cycles.samples == 512
    assert scene.render.resolution_x == scene.render.resolution_y == 1024
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    prefs.refresh_devices()
    devices = [d for d in prefs.devices if d.type == 'CUDA']
    assert devices, 'GPU missing; CPU fallback is forbidden'
    for d in prefs.devices:
        d.use = d == devices[0]
    scene.cycles.device = 'GPU'
    scene.cycles.use_auto_tile = True
    scene.cycles.tile_size = 256
    scene.render.use_persistent_data = True
    scene.render.image_settings.file_format = 'PNG'
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    sys.path.insert(0, str(Path(__file__).resolve().parent/'input'))
    from apollo_core.png import canonicalize
    args.out.mkdir(parents=True, exist_ok=True)
    receipt = args.out/'render-receipt.json'
    identity = dict(scene_sha256=sha(bpy.data.filepath), worker_sha256=sha(__file__),
                    mode=scene['apollo_submission_mode'], range=[193, 288],
                    resolution=[1024, 1024], samples=512, fps=24,
                    device='GPU', backend='CUDA', gpu=devices[0].name,
                    blender=bpy.app.version_string, build=bpy.app.build_hash.decode(),
                    persistent_data=True, tile_size=256)
    state = json.loads(receipt.read_text()) if receipt.exists() else dict(run=identity, frames={})
    assert state['run'] == identity, 'Changed scene/worker settings; use a fresh output'
    holds = {}
    poses = list(scene['apollo_gnm_pose_sequence'])
    import shutil
    import time
    for frame in range(args.first, args.last+1):
        name = f'frame_{frame:04d}.png'
        target = args.out/name
        if name in state['frames'] and target.exists() and sha(target) == state['frames'][name]['sha256']:
            holds.setdefault(poses[frame-1], frame)
            continue
        start = time.monotonic()
        reused = holds.get(poses[frame-1])
        temp = args.out/'.rendering.png'
        if reused is None:
            scene.frame_set(frame)
            scene.render.filepath = str(temp.resolve())
            assert bpy.ops.render.render(write_still=True) == {'FINISHED'}
            canonicalize(temp)
        else:
            shutil.copyfile(args.out/f'frame_{reused:04d}.png', temp)
        # Decode and validate actual dimensions using Blender's own image loader.
        image = bpy.data.images.load(str(temp.resolve()), check_existing=False)
        assert tuple(image.size) == (1024, 1024)
        bpy.data.images.remove(image)
        temp.replace(target)
        state['frames'][name] = dict(sha256=sha(target), reused_frame=reused,
                                     seconds=time.monotonic()-start)
        write(receipt, state)
        holds.setdefault(poses[frame-1], frame)
        print('EXTENDED_FRAME '+json.dumps(dict(mode=identity['mode'], frame=frame,
              reused_frame=reused, seconds=state['frames'][name]['seconds'])), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('build', 'render'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--first', type=int, default=193)
    parser.add_argument('--last', type=int, default=288)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    assert 193 <= args.first <= args.last <= 288
    (build if args.phase == 'build' else render)(args)


if __name__ == '__main__':
    main()
