"""Pack surface-triangle anchors and local strand frames into Geometry Nodes."""
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

from apollo_core.identity import barycentric, triangle_frames
from apollo_core.submission_timing import expression


def attachment_group(head, mode, times):
    group = bpy.data.node_groups.new('Apollo | surface-local attachments', 'GeometryNodeTree')
    group.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes, links = group.nodes, group.links
    def node(kind):
        return nodes.new(kind)
    def vector(operation, a, b=None, scale=None):
        n = node('ShaderNodeVectorMath'); n.operation = operation
        links.new(a, n.inputs[0])
        if b is not None:
            links.new(b, n.inputs[1])
        if scale is not None:
            links.new(scale, n.inputs[3])
        return n.outputs['Vector']
    def attr(name, dtype):
        n = node('GeometryNodeInputNamedAttribute'); n.data_type = dtype
        n.inputs['Name'].default_value = name
        return n.outputs['Attribute']
    def split(value):
        n = node('ShaderNodeSeparateXYZ'); links.new(value, n.inputs[0])
        return list(n.outputs)
    source = node('GeometryNodeObjectInfo'); source.transform_space = 'RELATIVE'
    source.inputs['Object'].default_value = head
    position = node('GeometryNodeInputPosition')
    def sample_attribute(name):
        sample = node('GeometryNodeSampleIndex'); sample.data_type = 'FLOAT_VECTOR'; sample.domain = 'POINT'
        links.new(source.outputs['Geometry'], sample.inputs['Geometry'])
        links.new(position.outputs[0], sample.inputs['Value'])
        links.new(attr(name, 'INT'), sample.inputs['Index'])
        return sample.outputs['Value']
    vertices = [sample_attribute(f'apollo_anchor_{i}') for i in range(3)]
    orientation = [sample_attribute(f'apollo_frame_{i}') for i in range(3)]
    weights = split(attr('apollo_weights', 'FLOAT_VECTOR'))
    local = split(attr('apollo_local', 'FLOAT_VECTOR'))
    root = vector('ADD', vector('SCALE', vertices[0], scale=weights[0]),
                  vector('SCALE', vertices[1], scale=weights[1]))
    root = vector('ADD', root, vector('SCALE', vertices[2], scale=weights[2]))
    tangent = vector('NORMALIZE', vector('SUBTRACT', orientation[1], orientation[0]))
    normal = vector('NORMALIZE', vector('CROSS_PRODUCT', tangent,
                     vector('SUBTRACT', orientation[2], orientation[0])))
    bitangent = vector('CROSS_PRODUCT', normal, tangent)
    offset = vector('ADD', vector('SCALE',tangent,scale=local[0]),
                    vector('SCALE',bitangent,scale=local[1]))
    offset = vector('ADD',offset,vector('SCALE',normal,scale=local[2]))
    root_local = split(attr('apollo_root_local','FLOAT_VECTOR'))
    root_offset = vector('ADD',vector('SCALE',tangent,scale=root_local[0]),
                         vector('SCALE',bitangent,scale=root_local[1]))
    root_offset = vector('ADD',root_offset,vector('SCALE',normal,scale=root_local[2]))
    def math(operation,a,b=None,value=None):
        n=node('ShaderNodeMath'); n.operation=operation
        if a is not None: links.new(a,n.inputs[0])
        if b is not None: links.new(b,n.inputs[1])
        if value is not None: n.inputs[0].default_value=value
        return n.outputs[0]
    blink=[]
    for delay in (0,1):
        value=node('ShaderNodeValue')
        for time in times:
            value.outputs[0].default_value=expression(mode,max(1,time-delay if mode=='generate-motion' else time))[2]
            value.outputs[0].keyframe_insert('default_value',frame=float(time))
        blink.append(value.outputs[0])
    side=attr('apollo_right_side','FLOAT')
    amount=math('ADD',math('MULTIPLY',blink[0],math('SUBTRACT',None,side,value=1)),
                math('MULTIPLY',blink[1],side))
    angle=math('MULTIPLY',amount,attr('apollo_lash_angle','FLOAT'))
    rotate=node('ShaderNodeVectorRotate'); rotate.rotation_type='AXIS_ANGLE'
    rotate.inputs['Axis'].default_value=(1,0,0)
    links.new(vector('SUBTRACT',offset,root_offset),rotate.inputs['Vector'])
    links.new(angle,rotate.inputs['Angle'])
    root=vector('ADD',root,vector('ADD',root_offset,rotate.outputs['Vector']))
    incoming, outgoing = node('NodeGroupInput'), node('NodeGroupOutput')
    setter = node('GeometryNodeSetPosition')
    links.new(incoming.outputs['Geometry'], setter.inputs['Geometry'])
    links.new(root, setter.inputs['Position'])
    links.new(setter.outputs['Geometry'], outgoing.inputs['Geometry'])
    if not all(link.is_valid for link in links):
        raise ValueError('Invalid attachment node link')
    for curve in group.animation_data.action.fcurves:
        for point in curve.keyframe_points:
            point.interpolation='LINEAR'
    return group


def bind(head, neutral, objects, mode, times, poses, sequence):
    triangles = []
    for face in head.data.polygons:
        if face.material_index != 0:
            continue
        ids = list(face.vertices)
        triangles.extend((ids[0], ids[i], ids[i+1]) for i in range(1, len(ids)-1))
    triangles = np.asarray(triangles, dtype=np.int32)
    tree = BVHTree.FromPolygons(neutral.tolist(), triangles.tolist(), all_triangles=True)
    group = attachment_group(head, mode, times)
    report = {}
    for obj in objects:
        if not np.allclose(np.array(obj.matrix_world), np.array(head.matrix_world), atol=1e-7, rtol=0):
            raise ValueError(f'Attachment must use head local coordinates: {obj.name}')
        data = obj.data
        if obj.type == 'CURVES':
            flat = np.empty(len(data.points)*3, dtype=np.float32)
            data.attributes['position'].data.foreach_get('vector', flat)
            points = flat.reshape(-1, 3)
            roots = np.asarray([c.first_point_index for c in data.curves])
            lengths = np.asarray([c.points_length for c in data.curves])
        else:
            flat = np.empty(len(data.vertices)*3, dtype=np.float32)
            data.vertices.foreach_get('co', flat); points = flat.reshape(-1, 3)
            roots = np.arange(len(points)); lengths = np.ones(len(points), dtype=int)
        hits = [tree.find_nearest(Vector(p)) for p in points[roots]]
        if any(h[0] is None for h in hits):
            raise ValueError(f'Unbound attachment: {obj.name}')
        ids = triangles[[h[2] for h in hits]]
        positions = np.asarray([tuple(h[0]) for h in hits])
        weights = barycentric(positions, neutral[ids])
        orientation_ids=ids.copy()
        orientation_report={}
        if 'upper lashes' in obj.name:
            # Contact triangles at a folding eyelid rim can turn inside out.
            # Choose the nearest proximal lid patch whose frame remains stable.
            chosen=np.zeros(len(roots),dtype=bool)
            best=np.full(len(roots),np.inf)
            selected_distance=np.zeros(len(roots))
            for distance in (0,.001,.002,.003,.004,.006):
                probes=points[roots]+np.array((0,distance,0))
                candidate=triangles[[tree.find_nearest(Vector(p))[2] for p in probes]]
                previous=None; previous_index=None; worst=np.zeros(len(roots))
                for index in sequence:
                    if index==previous_index:
                        continue
                    current=triangle_frames(poses[index],candidate)
                    if previous is not None:
                        relative=np.einsum('nji,njk->nik',previous,current)
                        angle=np.degrees(np.arccos(np.clip((np.trace(relative,axis1=1,axis2=2)-1)/2,-1,1)))
                        worst=np.maximum(worst,angle)
                    previous=current
                    previous_index=index
                improve=(~chosen)&(worst<best)
                orientation_ids[improve]=candidate[improve]
                selected_distance[improve]=distance
                best[improve]=worst[improve]
                chosen|=worst<30
            if not chosen.all():
                raise ValueError('No stable proximal orientation patch for every upper lash')
            orientation_report=dict(max_step_degrees=float(best.max()),
                                    max_patch_search_offset_m=float(selected_distance.max()))
        frames = triangle_frames(neutral, orientation_ids)
        ids = np.repeat(ids, lengths, axis=0)
        orientation_ids=np.repeat(orientation_ids,lengths,axis=0)
        weights = np.repeat(weights, lengths, axis=0)
        frames = np.repeat(frames, lengths, axis=0)
        origin = np.einsum('ni,nij->nj', weights, neutral[ids])
        local = np.einsum('nji,nj->ni', frames, points-origin)
        root_local = np.repeat(local[roots],lengths,axis=0)
        reconstructed = origin + np.einsum('nij,nj->ni', frames, local)
        error = float(np.max(np.abs(reconstructed-points)))
        if error > 1e-7:
            raise ValueError(f'Neutral attachment reconstruction failed: {obj.name}')
        for i in range(3):
            a = data.attributes.new(f'apollo_anchor_{i}', 'INT', 'POINT')
            a.data.foreach_set('value', ids[:, i].astype(np.int32))
            a = data.attributes.new(f'apollo_frame_{i}', 'INT', 'POINT')
            a.data.foreach_set('value',orientation_ids[:,i].astype(np.int32))
        for name, values in [('apollo_weights', weights), ('apollo_local', local),
                             ('apollo_root_local',root_local)]:
            a = data.attributes.new(name, 'FLOAT_VECTOR', 'POINT')
            a.data.foreach_set('vector', values.astype(np.float32).ravel())
        for name,values in [('apollo_right_side',np.repeat(points[roots,0]<0,lengths).astype(np.float32)),
                            ('apollo_lash_angle',np.full(len(points),np.radians(70) if 'upper lashes' in obj.name else 0,dtype=np.float32))]:
            a=data.attributes.new(name,'FLOAT','POINT'); a.data.foreach_set('value',values)
        modifier = obj.modifiers.new('Apollo | surface-local attachment', 'NODES')
        modifier.node_group = group
        obj['apollo_surface_attached'] = True
        obj['portrait_static_groom'] = False
        report[obj.name] = dict(points=len(points), anchors=len(roots),
                               orientation=orientation_report,
                               neutral_reconstruction_error_m=error,
                               max_root_offset_m=max(h[3] for h in hits))
        print('BOUND '+obj.name, flush=True)
    return report
