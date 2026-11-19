"""Reopen an experimental v22 timeline and measure native and derived motion separately."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from apollo_core.identity import triangle_frames
from apollo_core.submission_timing import expression
from gnm_v22_audit import SELECTED, coords, sha, appearance_signature
from gnm_verify import check_camera
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def surface(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    result = coords(mesh.vertices)
    evaluated.to_mesh_clear()
    return result


def main(args):
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    reference = scene.objects['Apollo | native motion reference']
    if scene['apollo_identity_source_sha256'] != SELECTED or bpy.data.libraries:
        raise ValueError('Unauthenticated identity or external Blender libraries')
    resources = []
    payloads={}
    for image in bpy.data.images:
        if image.source not in ('FILE','TILED'):
            continue
        if not image.packed_file or not image.filepath.startswith('//') or any(
                not p.filepath.startswith('//') for p in image.packed_files):
            raise ValueError('Unpacked image or author path '+image.name)
        resources.append(image.name)
        payloads[image.name]=hashlib.sha256(bytes(image.packed_file.data)).hexdigest()
    texture_identity='not checked against selected source'
    if args.source_audit:
        audit=json.loads(args.source_audit.read_text(encoding='utf-8'))
        if audit['source_sha256']!=SELECTED:
            raise ValueError('Wrong source audit')
        expected={i['name']:i['sha256'] for i in audit['images'] if i['packed']}
        different=(any(payloads.get(name)!=digest for name,digest in expected.items())
                   if args.maps else payloads!=expected)
        if different:
            raise ValueError('Reopened texture payloads differ from selected source')
        if not args.maps and appearance_signature(head)!=audit['appearance_signature']:
            raise ValueError('Full-character shaders differ from selected v22')
        texture_identity='exact selected packed bytes retained with explicit PBR conversion' if args.maps else 'exact selected packed bytes'
    portable_binding=None
    if args.maps:
        from gnm_v22_materials import validate
        portable_binding=validate(head,args.maps,args.layout,full_character=True,require_packed=True)
        if args.source_audit and set(payloads.values())!=set(expected.values())|set(portable_binding['active_maps'].values()):
            raise ValueError('Unexpected packed image payload outside selected source and validated PBR maps')
    if not scene.render.filepath.startswith('//'):
        raise ValueError('Author render path')
    with np.load(args.geometry, allow_pickle=False) as data:
        derived, native, sequence, eyes = [data[n] for n in ('poses','native','sequence','eyes')]
        mode = str(data['mode'])
        sample_frames = data['sample_frames'] if 'sample_frames' in data else np.arange(1,193,dtype=float)
        sample_sequence = data['sample_sequence'] if 'sample_sequence' in data else sequence
    with np.load(args.template, allow_pickle=False) as data:
        template = {k:data[k] for k in data.files}
    np.testing.assert_array_equal(np.array([list(f.vertices) for f in head.data.polygons]), template['quads'])
    for name,key in [('GNM UDIM','udim'),('GNM Region','legacy')]:
        actual = np.array([tuple(p.uv) for p in head.data.uv_layers[name].data], dtype=np.float32)
        np.testing.assert_array_equal(actual.ravel(), template[key].astype(np.float32).ravel())
    frames = [float(f) for f in args.frames.split(',')] if args.frames else (
        list(map(float,range(1,193))) if args.integer_frames else sample_frames[::args.sample_stride].tolist())
    if not frames or any(frame not in sample_frames for frame in frames):
        raise ValueError('Requested frames must be authenticated native sample times')
    lookup = dict(zip(sample_frames,sample_sequence))
    attached = [o for o in scene.objects if o.get('apollo_surface_attached')]
    anchors = {}
    for obj in attached:
        data = obj.data
        count = len(data.points) if obj.type=='CURVES' else len(data.vertices)
        ids = []
        frame_ids=[]
        for i in range(3):
            values = np.empty(count, dtype=np.int32)
            data.attributes[f'apollo_anchor_{i}'].data.foreach_get('value', values)
            ids.append(values)
            if data.attributes.get(f'apollo_frame_{i}'):
                values=np.empty(count,dtype=np.int32)
                data.attributes[f'apollo_frame_{i}'].data.foreach_get('value',values)
                frame_ids.append(values)
        vector = {}
        vector['frame_ids']=np.stack(frame_ids,axis=1) if frame_ids else np.stack(ids,axis=1)
        for role in ('weights','local'):
            values = np.empty(count*3, dtype=np.float32)
            data.attributes['apollo_'+role].data.foreach_get('vector', values)
            vector[role] = values.reshape(-1,3)
        if data.attributes.get('apollo_root_local'):
            values=np.empty(count*3,dtype=np.float32)
            data.attributes['apollo_root_local'].data.foreach_get('vector',values)
            vector['root_local']=values.reshape(-1,3)
            for role in ('right_side','lash_angle'):
                values=np.empty(count,dtype=np.float32)
                data.attributes['apollo_'+role].data.foreach_get('value',values)
                vector[role]=values
        anchors[obj.name] = (np.stack(ids,axis=1), vector)
    report = dict(scene_sha256=sha(bpy.data.filepath), geometry_sha256=sha(args.geometry),
                  template_sha256=sha(args.template), frames=frames, native_max_error_m=0.,
                  derived_max_error_m=0., eye_max_error_m=0., attachments={}, resources=resources,
                  root_offsets_m={}, orientation_step_degrees={},orientation_rate_degrees_per_frame={})
    report['texture_identity']=texture_identity
    if portable_binding:report['portable_binding']=portable_binding
    report['verifier_sha256']=sha(__file__)
    report['status']='running'
    report['frames_checked']=0
    skin_faces = [list(f.vertices) for f in head.data.polygons if f.material_index==0]
    previous_frames = {}
    previous_number = None
    for frame in frames:
        scene.frame_set(int(frame),subframe=frame-int(frame))
        actual = surface(head)
        native_actual = surface(reference)
        expected = derived[lookup[frame]]
        expected_native = native[lookup[frame]]
        for key,a,b in [('native_max_error_m',native_actual,expected_native),
                        ('derived_max_error_m',actual,expected),
                        ('eye_max_error_m',actual[eyes],expected_native[eyes])]:
            error = float(np.max(np.abs(a-b)))
            report[key] = max(report[key],error)
            if error > 1e-6:
                raise ValueError(f'{key} at frame {frame}: {error}')
        tree = BVHTree.FromPolygons(actual.tolist(), skin_faces)
        for obj in attached:
            ids, vector = anchors[obj.name]
            frames_local = triangle_frames(actual, vector['frame_ids'])
            origin = np.einsum('ni,nij->nj',vector['weights'],actual[ids])
            target = origin + np.einsum('nij,nj->ni',frames_local,vector['local'])
            if 'root_local' in vector:
                root_offset=np.einsum('nij,nj->ni',frames_local,vector['root_local'])
                offset=target-origin-root_offset
                left=expression(mode,frame)[2]
                right=expression(mode,max(1,frame-1))[2] if mode=='generate-motion' else left
                angle=(left*(1-vector['right_side'])+right*vector['right_side'])*vector['lash_angle']
                cosine,sine=np.cos(angle),np.sin(angle)
                rotated=offset.copy()
                rotated[:,1]=cosine*offset[:,1]-sine*offset[:,2]
                rotated[:,2]=sine*offset[:,1]+cosine*offset[:,2]
                target=origin+root_offset+rotated
            ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            if obj.type=='CURVES':
                values = np.empty(len(ev.data.points)*3,dtype=np.float32)
                ev.data.attributes['position'].data.foreach_get('vector',values)
                positions = values.reshape(-1,3)
            else:
                positions = surface(obj)
            if positions.shape != target.shape or not np.isfinite(positions).all():
                raise ValueError('Invalid attachment evaluation '+obj.name)
            error = float(np.max(np.abs(positions-target)))
            report['attachments'][obj.name] = max(error,report['attachments'].get(obj.name,0.))
            if error > 2e-6:
                raise ValueError(f'Attachment mismatch {obj.name} frame {frame}: {error}')
            if obj.type == 'CURVES':
                roots = np.array([c.first_point_index for c in obj.data.curves])
                distances = [tree.find_nearest(Vector(p))[3] for p in positions[roots]]
                report['root_offsets_m'][obj.name] = max(max(distances),report['root_offsets_m'].get(obj.name,0.))
                current_frames = frames_local[roots]
                if previous_number is not None and frame-previous_number <= 1 and obj.name in previous_frames:
                    rotation = np.einsum('nji,njk->nik',previous_frames[obj.name],current_frames)
                    angle = float(np.degrees(np.arccos(np.clip((np.trace(rotation,axis1=1,axis2=2)-1)/2,-1,1))).max())
                    report['orientation_step_degrees'][obj.name] = max(angle,report['orientation_step_degrees'].get(obj.name,0.))
                    report['orientation_rate_degrees_per_frame'][obj.name] = max(angle/(frame-previous_number),
                        report['orientation_rate_degrees_per_frame'].get(obj.name,0.))
                previous_frames[obj.name] = current_frames
        previous_number = frame
        report['frames_checked']+=1
        if report['frames_checked']%16==0:
            args.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(f'CHECKED {frame}',flush=True)
    try:
        report['camera_checks'] = check_camera(scene, head, template, derived, sequence, mode)
    except ValueError as error:
        report['camera_error'] = str(error)
        args.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        raise
    report['qualification'] = 'Geometry/resource checks only; image checks, collisions and visual acceptance remain separate.'
    report['limits']=dict(root_distance_m=.00025,orientation_rate_degrees_per_frame=30)
    errors=[]
    for name,distance in report['root_offsets_m'].items():
        if distance>.00025:errors.append(f'{name}: detached root {distance} m')
    for name,rate in report['orientation_rate_degrees_per_frame'].items():
        if rate>30:errors.append(f'{name}: orientation change {rate} degrees/frame')
    report['errors']=errors
    if errors:
        report['status']='failed_attachment_limits'
        args.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        raise ValueError('; '.join(errors))
    report['status']='passed_geometry_and_resources'
    args.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if args.render:
        from gnm_portrait_refine import render
        for frame in [int(f) for f in args.render_frames.split(',')]:
            scene.frame_set(frame)
            render(scene,args.out.parent,f'frame-{frame:03d}',768,24)
    print('RESULT '+json.dumps(dict(report=str(args.out))),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('geometry','template','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--frames')
    parser.add_argument('--integer-frames',action='store_true')
    parser.add_argument('--sample-stride',type=int,choices=(1,2,4,8,16,32),default=1)
    parser.add_argument('--render',action='store_true')
    parser.add_argument('--render-frames',default='1,25,58,106,107,112')
    parser.add_argument('--source-audit',type=Path)
    parser.add_argument('--maps',type=Path,help='Verify a documented packed PBR conversion instead of the original head shader')
    parser.add_argument('--layout',choices=('udim','legacy'),default='udim')
    main(parser.parse_args(sys.argv[sys.argv.index('--')+1:]))
