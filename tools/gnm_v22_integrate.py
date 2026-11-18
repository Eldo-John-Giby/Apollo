"""Derive an explicit v22 character timeline with an independent native reference."""
import argparse
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from apollo_core.identity import transport_identity
from gnm_v22_audit import SELECTED, coords, sha
from gnm_surface_attachments import bind
from gnm_template import MODEL_SHA256


def install_keys(obj, poses, sequence, times):
    obj.shape_key_clear()
    obj.data.vertices.foreach_set('co', poses[sequence[0]].ravel())
    obj.shape_key_add(name='Basis')
    for i, pose in enumerate(poses):
        key = obj.shape_key_add(name=f'GNM pose {i:03d}')
        key.data.foreach_set('co', pose.ravel())
        active = sequence == i
        for frame in range(len(sequence)):
            if frame in (0, len(sequence)-1) or active[frame] != active[frame-1]:
                if frame and active[frame] != active[frame-1]:
                    key.value = float(active[frame-1]); key.keyframe_insert('value', frame=float(times[frame-1]))
                key.value = float(active[frame]); key.keyframe_insert('value', frame=float(times[frame]))
    for curve in obj.data.shape_keys.animation_data.action.fcurves:
        for point in curve.keyframe_points:
            point.interpolation = 'LINEAR'


def main(args):
    source = Path(bpy.data.filepath)
    if sha(source) != SELECTED:
        raise ValueError('Integration requires immutable approved v22')
    if args.out.exists():
        raise FileExistsError(args.out)
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    if head.modifiers:
        raise ValueError('Unexpected modifiers on selected head')
    basis = coords(head.data.shape_keys.reference_key.data)
    evaluated = head.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh(); neutral = coords(mesh.vertices); evaluated.to_mesh_clear()
    with np.load(args.template, allow_pickle=False) as template:
        np.testing.assert_array_equal(basis, template['vertices'].astype(np.float32))
        np.testing.assert_array_equal(np.array([list(f.vertices) for f in head.data.polygons]), template['quads'])
        for name, key in [('GNM UDIM', 'udim'), ('GNM Region', 'legacy')]:
            uv = np.array([tuple(v.uv) for v in head.data.uv_layers[name].data], dtype=np.float32)
            np.testing.assert_array_equal(uv.ravel(), template[key].astype(np.float32).ravel())
        faces = template['quads'].copy()
    eyes = np.array(sorted({i for f in head.data.polygons if f.material_index in (1, 2, 3, 4)
                            for i in f.vertices}), dtype=np.int32)
    delta = neutral-basis
    np.testing.assert_array_equal(delta[eyes], 0)
    with np.load(args.clip, allow_pickle=False) as clip:
        native, sequence, mode = clip['poses'], clip['sequence'], str(clip['mode'])
        sample_frames = clip['sample_frames'] if 'sample_frames' in clip else np.arange(1,193,dtype=float)
        sample_sequence = clip['sample_sequence'] if 'sample_sequence' in clip else sequence
    if native.shape[1:] != basis.shape or sequence.shape != (192,) or mode not in ('left','right','generate-motion'):
        raise ValueError('Invalid native clip dimensions or mode')
    continuity='Not qualified: coarse visual trial'
    if len(sample_frames)>192:
        receipt=json.loads(args.clip.with_suffix('.json').read_text(encoding='utf-8'))
        if receipt['model_sha256']!=MODEL_SHA256 or receipt['clip_sha256']!=sha(args.clip):
            raise ValueError('Unauthenticated dense clip')
        if receipt['midpoint_native_interpolation_error_m']>1e-6:
            raise ValueError('Dense native reference failed its interpolation gate')
        continuity='Direct native samples and midpoint interpolation gate passed'
    skin = np.ones(len(basis), dtype=bool); skin[eyes] = False
    if mode == 'generate-motion' and not np.array_equal(native[sequence[0]], native[sequence[-1]]):
        raise ValueError('Native clip must reset exactly')
    np.testing.assert_array_equal(native[sequence[0]][skin], basis[skin])
    derived = np.stack([transport_identity(basis, pose, delta, faces, eyes) for pose in native])
    np.testing.assert_array_equal(derived[sequence[0]][skin], neutral[skin])
    np.testing.assert_array_equal(derived[:, eyes], native[:, eyes])
    # Remove only objects hidden in the selected render, in this derived file.
    omitted = [o.name for o in scene.objects if o.hide_render and o != head]
    for name in omitted:
        bpy.data.objects.remove(scene.objects[name], do_unlink=True)
    # Freeze the evaluated tear geometry, including its selected corrective keys
    # and bevels, before recording anchors. Original basis coordinates are stale.
    for obj in list(scene.objects):
        if obj.type not in ('MESH','CURVE') or 'tear' not in obj.name.lower() and 'canthus' not in obj.name.lower():
            continue
        depsgraph = bpy.context.evaluated_depsgraph_get()
        mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph),
                                               preserve_all_data_layers=True, depsgraph=depsgraph)
        name, matrix = obj.name, obj.matrix_world.copy()
        bpy.data.objects.remove(obj, do_unlink=True)
        replacement = bpy.data.objects.new(name, mesh)
        scene.collection.objects.link(replacement); replacement.matrix_world = matrix
    attachments = [o for o in scene.objects if o.type == 'CURVES' or
                   (o.type == 'MESH' and ('canthus' in o.name.lower() or 'tear' in o.name.lower()))]
    binding = bind(head, neutral, attachments, mode, sample_frames, derived, sample_sequence)
    reference = head.copy(); reference.data = head.data.copy()
    reference.name = 'Apollo | native motion reference'
    scene.collection.objects.link(reference)
    reference.hide_render = True; reference.hide_set(True)
    reference.data.materials.clear()
    install_keys(reference, native, sample_sequence, sample_frames)
    install_keys(head, derived, sample_sequence, sample_frames)
    scene.frame_start, scene.frame_end, scene.render.fps = 1, 192, 24
    scene['apollo_submission_mode'] = mode
    scene['apollo_gnm_pose_sequence'] = sequence.tolist()
    scene['apollo_identity_source_sha256'] = SELECTED
    scene['apollo_identity_transport'] = 'Native one-ring best-fit rotation; protected native eyes'
    # Use the qualified frontal judging camera; preserve the beauty cameras as
    # separate optional views. Screen-direction thresholds apply to this camera.
    scene.camera = scene.objects['GNM Camera']
    from gnm_portrait_refine import aim
    aim(scene.camera, (0,-.58,.015), (0,0,-.012))
    scene.camera.data.lens = 115
    scene.render.resolution_x = scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.filepath = '//frames/frame_'
    for image in bpy.data.images:
        if image.source not in ('FILE', 'TILED'):
            continue
        if not image.packed_file:
            raise ValueError('Unpacked image '+image.name)
        digest = __import__('hashlib').sha256(bytes(image.packed_file.data)).hexdigest()
        path = f'//packed/{digest}.png'
        image.filepath = path
        for packed in image.packed_files:
            packed.filepath = path
    scene.frame_set(1)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.out.with_suffix('.npz'), poses=derived, native=native,
                        sequence=sequence, eyes=eyes, mode=mode,
                        sample_frames=sample_frames,sample_sequence=sample_sequence)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.out.resolve()), compress=True, relative_remap=False)
    report = dict(source_sha256=SELECTED, clip_sha256=sha(args.clip),
                  template_sha256=sha(args.template), scene_sha256=sha(args.out),
                  geometry_sha256=sha(args.out.with_suffix('.npz')), attachments=binding,
                  omitted_hidden_objects=omitted, mode=mode, frames=192, fps=24,
                  neutral_skin_exact=True,
                  native_continuity=continuity,
                  neutral_native_eye_shift_m=float(np.max(np.linalg.norm(native[sequence[0]][eyes]-basis[eyes], axis=1))),
                  qualification='Experimental integration; reopening, motion and visual gates pending.')
    root=Path(__file__).resolve().parents[1]
    report['recipes']={name:sha(root/name) for name in ('tools/gnm_v22_integrate.py',
                      'tools/gnm_surface_attachments.py','apollo_core/identity.py',
                      'apollo_core/submission_timing.py')}
    if sha(source) != SELECTED:
        raise ValueError('Selected source changed')
    args.out.with_suffix('.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('RESULT '+json.dumps(dict(scene=str(args.out), source_unchanged=True)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('clip', 'template', 'out'):
        parser.add_argument('--'+name, required=True, type=Path)
    main(parser.parse_args(sys.argv[sys.argv.index('--')+1:]))
