"""Refine the packed v2 adult face without rebuilding its calibrated gaze rig."""

import argparse
import hashlib
import heapq
import json
import math
from pathlib import Path
import random
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "milestones/photorealism-v2-candidate/scene.blend"
SOURCE_SHA = "8acd0df98cd2581f54bf83901d56c669795c5eef14e853a378bcb18e6bf71c4d"
sys.path[:0] = [str(ROOT / name) for name in ("build", "tools", "wrapper")]
import eyes
from realism_scene import material, shader, tube
from scene_preflight import run as preflight


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def smoothstep(value):
    t = min(1.0, max(0.0, value))
    return t * t * (3 - 2 * t)


def face_contour(face):
    """Add lower cheek definition and slight corner lift in world meters."""
    transform = face.matrix_world
    inverse = transform.inverted()
    changed = 0
    max_displacement = 0.0
    for vertex in face.data.vertices:
        p = transform @ vertex.co
        x, y, z = p
        lateral = abs(x)
        # Compact lower-face region, separated from the eyelids and ears.
        if not (-0.115 < z < -0.024 and y < 0.055):
            continue
        guard = smoothstep((-0.024 - z) / 0.014) * smoothstep((z + 0.115) / 0.020)
        front = smoothstep((0.055 - y) / 0.060)
        hollow = math.exp(-((lateral - 0.048) / 0.019)**2 - ((z + 0.059) / 0.021)**2)
        taper = math.exp(-((lateral - 0.061) / 0.022)**2 - ((z + 0.077) / 0.025)**2)
        corner = math.exp(-((lateral - 0.023) / 0.010)**2 - ((z + 0.072) / 0.008)**2)
        # Keep a little upper-cheek volume as the area below it recedes.
        cheekbone = math.exp(-((lateral - 0.046) / 0.016)**2 - ((z + 0.037) / 0.010)**2)
        delta = guard * front * Vector((
            -math.copysign(0.0034 * taper * smoothstep(lateral / 0.040), x),
            0.0042 * hollow - 0.0015 * cheekbone,
            (0.00085 + math.copysign(0.00012, x)) * corner,
        ))
        if delta.length > 1e-6:
            vertex.co = inverse @ (p + delta)
            changed += 1
            max_displacement = max(max_displacement, delta.length)
    face.data.update()
    return {"changed_vertices": changed, "maximum_displacement_m": max_displacement}


def lip_blend_attribute(face, lip_slot):
    """Feather tint from the actual material border, including both lip contours."""
    mesh = face.data
    lip_ids = set()
    skin_ids = set()
    for poly in mesh.polygons:
        (lip_ids if poly.material_index == lip_slot else skin_ids).update(poly.vertices)
    border = lip_ids & skin_ids
    if not border:
        raise ValueError("Missing shared lip and skin border")
    width = 0.0033
    coords = {i: face.matrix_world @ mesh.vertices[i].co for i in lip_ids}
    neighbors = {i: [] for i in lip_ids}
    for edge in mesh.edges:
        a, b = edge.vertices
        if a in neighbors and b in neighbors:
            length = (coords[a] - coords[b]).length
            neighbors[a].append((b, length))
            neighbors[b].append((a, length))
    distances = dict.fromkeys(border, 0.0)
    queue = [(0.0, index) for index in border]
    heapq.heapify(queue)
    while queue:
        distance, index = heapq.heappop(queue)
        if distance > distances[index]:
            continue
        for neighbor, length in neighbors[index]:
            candidate = distance + length
            if candidate < min(width, distances.get(neighbor, width)):
                distances[neighbor] = candidate
                heapq.heappush(queue, (candidate, neighbor))
    name = "Apollo lip feather"
    attr = mesh.attributes.new(name, "FLOAT", "POINT")
    values = [0.0] * len(mesh.vertices)
    for i in lip_ids:
        values[i] = smoothstep(distances.get(i, width) / width)
    attr.data.foreach_set("value", values)
    return name


def refine_lips(face):
    slot = next(i for i, mat in enumerate(face.data.materials) if mat.name.endswith(".lips"))
    mat = face.data.materials[slot]
    p = shader(mat)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    base = p.inputs["Base Color"].links[0].from_socket
    feather = nodes.new("ShaderNodeAttribute")
    feather.attribute_name = lip_blend_attribute(face, slot)

    # The existing skin atlas still supplies the underlying UV detail.
    tint = nodes.new("ShaderNodeMixRGB")
    tint.label = "Feathered warm rose lip pigment"
    tint.blend_type = "MULTIPLY"
    tint.inputs[2].default_value = (1.00, 0.73, 0.77, 1.0)
    links.new(feather.outputs["Fac"], tint.inputs[0])
    links.new(base, tint.inputs[1])
    links.new(tint.outputs[0], p.inputs["Base Color"])

    coord = nodes.new("ShaderNodeTexCoord")
    stretch = nodes.new("ShaderNodeVectorMath")
    stretch.operation = "MULTIPLY"
    stretch.inputs[1].default_value = (2400, 520, 370)
    links.new(coord.outputs["Object"], stretch.inputs[0])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.label = "Elongated lip microfolds"
    noise.inputs["Scale"].default_value = 1
    noise.inputs["Detail"].default_value = 2
    links.new(stretch.outputs[0], noise.inputs["Vector"])

    folds = nodes.new("ShaderNodeBump")
    folds.inputs["Distance"].default_value = 0.00007
    links.new(p.inputs["Normal"].links[0].from_socket, folds.inputs["Normal"])
    links.new(feather.outputs["Fac"], folds.inputs["Strength"])
    links.new(noise.outputs["Fac"], folds.inputs["Height"])
    links.new(folds.outputs[0], p.inputs["Normal"])

    rough = nodes.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = 0.30
    rough.inputs["To Max"].default_value = 0.43
    links.new(noise.outputs["Fac"], rough.inputs["Value"])
    links.new(rough.outputs[0], p.inputs["Roughness"])
    # A soft satin highlight follows the vermilion fade.
    coat = nodes.new("ShaderNodeMath")
    coat.operation = "MULTIPLY"
    coat.inputs[1].default_value = 0.22
    links.new(feather.outputs["Fac"], coat.inputs[0])
    links.new(coat.outputs[0], p.inputs["Coat Weight"])
    p.inputs["Coat Roughness"].default_value = 0.31
    links.new(folds.outputs[0], p.inputs["Coat Normal"])


def refine_brows(face):
    original = bpy.data.objects["Apollo v2 individual brows"]
    target = original.users_collection[0]
    bpy.context.view_layer.update()
    tree = BVHTree.FromObject(face, bpy.context.evaluated_depsgraph_get())
    transform = face.matrix_world
    inverse = transform.inverted()
    direction = (inverse.to_3x3() @ Vector((0, 1, 0))).normalized()
    rng = random.Random(20261111)
    shades = [(0.027, 0.014, 0.009), (0.042, 0.023, 0.014), (0.060, 0.034, 0.021)]
    groups = [[] for _ in shades]
    for side in (-1, 1):
        for _ in range(1050):
            t = rng.betavariate(1.55, 1.48)
            x = 0.013 + 0.045 * t + rng.uniform(-0.0013, 0.0013) * (1 - t)**4
            center = 0.0116 + 0.0051 * math.sin(math.pi * t) - 0.0021 * t**3
            width = 0.00265 * (1 - 0.86 * t**2) * smoothstep(t / 0.14 + 0.55)
            z = center + width * rng.uniform(-1, 1) + side * 0.00025 * math.sin(math.pi * t)
            length = rng.uniform(0.0017, 0.0035) * (1 - 0.35 * t)
            slope = 1.35 * math.exp(-6 * t) - 0.53 * t + rng.uniform(-0.25, 0.25)
            path = []
            for step in range(4):
                u = step / 3
                sx = side * (x + length * u)
                sz = z + length * (slope * u - 0.14 * u**2)
                point, _, _, _ = tree.ray_cast(inverse @ Vector((sx, -0.25, sz)), direction)
                if point is None:
                    raise ValueError("Brow fiber missed the face")
                point = transform @ point
                point.y -= 0.00007 + 0.00023 * math.sin(math.pi * u)
                path.append(point)
            group = rng.choices(range(len(shades)), weights=(55, 34, 11))[0]
            groups[group].append((path, False))

    bpy.data.objects.remove(original, do_unlink=True)
    for index, (paths, color) in enumerate(zip(groups, shades)):
        name = f"Apollo sculpted brows {index + 1}"
        fibers = tube(name, paths, (0.000039, 0.000035, 0.000029)[index],
                      material(name, (*color, 1.0), 0.52))
        if fibers.name not in target.objects:
            target.objects.link(fibers)
        for collection in list(fibers.users_collection):
            if collection != target:
                collection.objects.unlink(fibers)
        for poly in fibers.data.polygons:
            poly.use_smooth = True
    return sum(map(len, groups))


def eye_meshes():
    result = {}
    for side in "LR":
        for part in ("Pupil", "Iris", "Sclera"):
            obj = bpy.data.objects[f"{part}.{side}"]
            payload = [[list(v.co) for v in obj.data.vertices],
                       [list(p.vertices) for p in obj.data.polygons]]
            result[obj.name] = hashlib.sha256(json.dumps(payload).encode()).hexdigest()
    return result


def build(folder):
    source = Path(bpy.data.filepath).resolve()
    if digest(source) != SOURCE_SHA:
        raise ValueError(f"Expected the original packed v2 scene at {SOURCE}")
    folder = folder.resolve()
    if folder.exists():
        raise ValueError("Use a new output directory")

    eyes.reset()
    calibration = eyes.calibration()
    protected = eye_meshes()
    face = bpy.data.objects["Apollo_Face"]
    contour = face_contour(face)
    refine_lips(face)
    strand_count = refine_brows(face)
    eyes.reset()
    if eyes.calibration() != calibration or eye_meshes() != protected:
        raise RuntimeError("Protected eye geometry or calibration changed")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    polygons = sum(len(obj.evaluated_get(depsgraph).data.polygons)
                   for obj in bpy.context.scene.objects if obj.type == "MESH" and not obj.hide_render)
    if polygons >= 500_000:
        raise RuntimeError("Appearance geometry exceeds the v2 polygon budget")

    folder.mkdir(parents=True)
    bpy.ops.file.pack_all()
    scene = folder / "scene.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(scene), compress=True)
    preflight(folder / "scene-preflight.json")
    receipt = {
        "source_sha256": digest(source),
        "scene_sha256": digest(scene),
        "recipe_sha256": digest(__file__),
        "brow_helper_sha256": digest(ROOT / "build/realism_scene.py"),
        "protected_eye_meshes": protected,
        "visible_evaluated_polygons": polygons,
        "brow_strands": strand_count,
        "face_contour": contour,
        "qualified": False,
    }
    (folder / "build.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    build(args.folder)
