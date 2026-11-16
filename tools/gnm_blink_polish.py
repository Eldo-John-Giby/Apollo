"""Build a packed, editable appearance review on the existing blink timeline."""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_portrait_refine import render, smooth
from gnm_timeline_trial import verify_blink


def lash_anchors(head, opened):
    head.data.calc_loop_triangles()
    triangles = np.array([tri.vertices[:] for tri in head.data.loop_triangles
                          if head.data.polygons[tri.polygon_index].material_index == 0])
    tree = BVHTree.FromPolygons(opened.tolist(), triangles.tolist(), all_triangles=True)
    anchors = []
    heights = np.linspace(.298, .314, 160)
    for side in (-1, 1):
        for u in np.linspace(.05, .96, 33):
            x = side*(.020+.023*u)
            hits = [tree.ray_cast(Vector((x, y, .30)), Vector((0, 0, -1))) for y in heights]
            depths = np.array([hit[0].z if hit[0] else .075 for hit in hits])
            index = int(np.argmax(np.diff(depths)))+1
            point, _, face, _ = hits[index]
            if point is None or depths[index]-depths[index-1] < .001:
                continue
            vertices = triangles[face]
            weights = barycentric_transform(point, *(Vector(v) for v in opened[vertices]),
                                            Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
            anchors.append((vertices, tuple(weights), side, u))
    if min(sum(a[2] == side for a in anchors) for side in (-1, 1)) < 24:
        raise ValueError('Insufficient lash anchors on one lid')
    return anchors


def widen(poses, anchors, blink_poses):
    # Gaussian field follows the actual upper rim and fades before the eyebrow.
    for index, pose in enumerate(poses):
        if index in blink_poses:
            continue
        roots = np.array([weights @ pose[vertices] for vertices, weights, _, _ in anchors])
        distance = (pose[:, None, :]-roots[None, :, :])/np.array((.005, .006, .006))
        weight = np.exp(-np.square(distance).sum(2).min(1))
        yield index, weight


def animated_lashes(scene, head, keys, anchors, pose_arrays):
    rng = np.random.default_rng(4141)
    t = np.linspace(0, 1, 7)
    angle = np.arange(4)*np.pi/2
    length_variation = rng.uniform(.87, 1.14, 33)
    faces, offsets = [], []
    for i, (_, _, side, u) in enumerate(anchors):
        length = (.0024+.0022*np.sin(np.pi*u*.83))*length_variation[round((u-.05)/.91*32)]
        path = length*np.column_stack((side*(.73*u-.16)*t, -.37*t+.96*t**2, 1.02*t-.14*t**3))
        radius = .000081*(1-.98*t)**.65
        rings = path[:, None, :]+radius[:, None, None]*np.column_stack(
            (np.cos(angle), np.sin(angle), np.zeros_like(angle)))
        offsets.append(rings)
        base = i*len(t)*4
        faces.extend((base+j*4+k, base+j*4+(k+1)%4, base+(j+1)*4+(k+1)%4,
                      base+(j+1)*4+k) for j in range(len(t)-1) for k in range(4))
    offsets = np.array(offsets)

    def points(pose):
        roots = np.array([weights @ pose[idx] for idx, weights, _, _ in anchors])
        return (offsets+roots[:, None, None, :]).reshape(-1, 3)

    mesh = bpy.data.meshes.new('Blink-follow upper lashes')
    mesh.from_pydata(points(pose_arrays[0]).tolist(), [], faces)
    material = bpy.data.materials.new('Natural dark brown lash fibers')
    material.diffuse_color = (.014, .0065, .0042, 1)
    material.use_nodes = True
    shader = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = material.diffuse_color
    shader.inputs['Roughness'].default_value = .57
    shader.inputs['Specular IOR Level'].default_value = .15
    mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    lashes = bpy.data.objects.new('Blink-follow upper lashes', mesh)
    scene.collection.objects.link(lashes)
    lashes.matrix_world = head.matrix_world.copy()
    for key, pose in zip(keys, pose_arrays):
        added = lashes.shape_key_add(name=key.name)
        added.data.foreach_set('co', points(pose).astype(np.float32).ravel())
    source = head.data.shape_keys.animation_data
    target = lashes.data.shape_keys.animation_data_create()
    target.action = source.action
    target.action_slot = source.action_slot
    return lashes


def matte_regions(head, xyz):
    material = head.data.materials[0]
    tree = material.node_tree
    nodes, links = tree.nodes, tree.links
    shader = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    x, y, z = xyz.T
    ears = smooth((abs(x)-.066)/.012)*smooth((y-.216)/.024)*smooth((.328-y)/.025)
    forehead = smooth((y-.321)/.023)*smooth((z-.083)/.029)
    attribute = head.data.attributes.new('Ear and forehead matte regions', 'FLOAT', 'POINT')
    attribute.data.foreach_set('value', np.maximum(ears, forehead).astype(np.float32))
    mask = nodes.new('ShaderNodeAttribute')
    mask.attribute_name = attribute.name
    for name, value in (('Roughness', .70), ('Specular IOR Level', .20)):
        socket = shader.inputs[name]
        blend = nodes.new('ShaderNodeMix')
        blend.data_type = 'FLOAT'
        links.new(mask.outputs['Fac'], blend.inputs[0])
        if socket.is_linked:
            links.new(socket.links[0].from_socket, blend.inputs[2])
        else:
            blend.inputs[2].default_value = socket.default_value
        blend.inputs[3].default_value = value
        links.new(blend.outputs[0], socket)
    coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 1750
    noise.inputs['Detail'].default_value = 2.2
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = .000052
    links.new(mask.outputs['Fac'], bump.inputs['Strength'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    normal = shader.inputs['Normal']
    if normal.is_linked:
        links.new(normal.links[0].from_socket, bump.inputs['Normal'])
    links.new(bump.outputs['Normal'], normal)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args(sys.argv[sys.argv.index('--')+1:]).out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    path = out/'expression.blend'
    if path.exists():
        raise FileExistsError(path)
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    keys = list(head.data.shape_keys.key_blocks)
    arrays = np.array([[point.co[:] for point in key.data] for key in keys], dtype=np.float32)
    sequence = np.array(scene['apollo_gnm_pose_sequence'])
    anchors = lash_anchors(head, arrays[1+sequence[111]])
    skin = np.array([v.index for v in head.data.vertices
                     if any(head.vertex_groups[g.group].name == 'skin_exterior' for g in v.groups)])
    if not len(skin):
        raise ValueError('Missing skin_exterior group')
    blink_poses = set(1+sequence[102:110])
    for index, weight in widen(arrays, anchors, blink_poses | {0}):
        arrays[index, skin, 1] += .00046*weight[skin]
        keys[index].data.foreach_set('co', arrays[index].ravel())
    verify_blink(head, arrays[1:], sequence)
    animated_lashes(scene, head, keys, anchors, arrays)
    matte_regions(head, arrays[0])
    print('LASH COUNTS', [sum(a[2] == side for a in anchors) for side in (-1, 1)], flush=True)
    scene.frame_set(112)
    scene.render.resolution_percentage = 100
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
    for frame in (105, 106, 112):
        scene.frame_set(frame)
        render(scene, out, f'frame-{frame}', 780, 20)


if __name__ == '__main__':
    main()
