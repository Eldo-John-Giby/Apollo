"""Build a packed expression timeline and optionally render its PNG frames."""
import argparse
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'wrapper'))
import eyes
from submission_textures import apply_variant


def smooth(value):
    value = max(0., min(1., value))
    return value * value * (3 - 2 * value)


def track(frame, keys):
    for (start, a), (end, b) in zip(keys, keys[1:]):
        if frame <= end:
            t = smooth((frame - start) / (end - start))
            return tuple(x + (y - x) * t for x, y in zip(a, b))
    return keys[-1][1]


def expression(mode, frame):
    center = (0., 0.)
    if mode in ('left', 'right'):
        side = -0.88 if mode == 'left' else 0.88
        gaze = ((1, center), (21, center), (26, (side, 0.)), (192, (side, 0.)))
    else:
        gaze = ((1, center), (20, center), (25, (-.7, .14)), (53, (-.7, .14)),
                (58, (.65, -.12)), (87, (.65, -.12)), (93, (.23, .72)),
                (124, (.23, .72)), (130, (-.33, -.45)), (159, (-.33, -.45)),
                (164, center), (192, center))
    blink_start = 103 if mode == 'generate-motion' else 99
    blink = ((1, (0.,)), (blink_start, (0.,)), (blink_start + 3, (1.,)),
             (blink_start + 4, (1.,)), (blink_start + 9, (0.,)), (192, (0.,)))
    return (*track(frame, gaze), track(frame, blink)[0])


def closure_key(obj, ipd):
    if obj.data.shape_keys is None:
        obj.shape_key_add(name='Basis')
    basis = obj.data.shape_keys.reference_key
    key = obj.shape_key_add(name='Submission blink', from_mix=False)
    world = obj.matrix_world
    inverse = world.inverted()
    for vertex, destination in zip(basis.data, key.data):
        point = world @ vertex.co
        lateral = abs(abs(point.x) - ipd / 2)
        across = smooth((.014 - lateral) / .006)
        anterior = smooth((.005 - point.y) / .01)
        if point.z >= 0:
            displacement = -.010 * smooth((.017 - point.z) / .009)
        else:
            displacement = .0017 * smooth((point.z + .010) / .007)
        point.z += across * anterior * displacement
        point.y -= .26 * across * anterior * abs(displacement)
        destination.co = inverse @ point
    return key


def build(mode):
    scene = bpy.context.scene
    scene.render.fps = 24
    scene.render.fps_base = 1
    scene.frame_start, scene.frame_end = 1, 192
    scene.cycles.device = 'CPU'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = '//frames/'
    target = scene.objects['FixationTarget']
    arm = scene.objects[scene['apollo_armature']]
    bones = [arm.pose.bones[name] for name in json.loads(scene['apollo_bones']).values()]
    eyes.reset()
    ipd = eyes.calibration()['ipd']
    lids = [closure_key(scene.objects[name], ipd) for name in (
        'Apollo_Face', 'Apollo lid wet margins', 'Apollo tapered eyelashes',
        'Apollo upper lid crease',
    )]
    brows = [(obj, obj.location.z) for obj in scene.objects
             if obj.name.startswith('Apollo sculpted brows')]
    for bone in bones:
        bone.rotation_mode = 'QUATERNION'
    previous = {}
    for frame in range(1, 193):
        scene.frame_set(frame)
        h, v, blink = expression(mode, frame)
        eyes.move(h, v)
        target.keyframe_insert('location', frame=frame)
        for bone in bones:
            rotation = bone.rotation_quaternion.copy()
            if bone.name in previous:
                rotation.make_compatible(previous[bone.name])
            previous[bone.name] = rotation.copy()
            bone.rotation_quaternion = rotation
            bone.keyframe_insert('rotation_quaternion', frame=frame)
        for lid in lids:
            lid.value = blink
            lid.keyframe_insert('value', frame=frame)
        for brow, brow_rest in brows:
            brow.location.z = brow_rest + .00065 * max(0., v) - .0002 * blink
            brow.keyframe_insert('location', index=2, frame=frame)
    scene.frame_set(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True, choices=('left', 'right', 'generate-motion'))
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--variant', type=Path, help='Texture variant manifest')
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--preview-frame', type=int, choices=range(1, 193),
                        metavar='1..192')
    parser.add_argument('--draft', action='store_true',
                        help='Render at 25% resolution and four samples for motion review')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    if args.variant:
        apply_variant(args.variant)
    build(args.mode)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'expression.blend'), compress=True)
    scene = bpy.context.scene
    if args.draft:
        scene.render.resolution_percentage = 25
        scene.cycles.samples = 4
    if args.preview_frame is not None:
        scene.frame_set(args.preview_frame)
        scene.render.filepath = str(out / 'preview.png')
        bpy.ops.render.render(write_still=True)
    if args.render:
        (out / 'frames').mkdir()
        scene.render.filepath = str(out / 'frames' / 'frame_')
        bpy.ops.render.render(animation=True)


if __name__ == '__main__':
    main()
