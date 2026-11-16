"""Helpers embedded in the versioned Blender scene."""
from pathlib import Path

import bpy


def quick_render(scene, path):
    scene.render.filepath = str(Path(path).resolve())
    bpy.ops.render.render(write_still=True)


def crop_render(scene, path, bounds, percentage=100):
    render = scene.render
    old = render.use_border, render.use_crop_to_border, render.resolution_percentage
    render.border_min_x, render.border_max_x, render.border_min_y, render.border_max_y = bounds
    render.use_border = render.use_crop_to_border = True
    render.resolution_percentage = percentage
    try:
        quick_render(scene, path)
    finally:
        render.use_border, render.use_crop_to_border, render.resolution_percentage = old


def add_shape_key(object, name, value=0):
    key = object.shape_key_add(name=name, from_mix=False)
    key.value = value
    return key


def set_node_input(node, name, value):
    node.inputs[name].default_value = value


def save_version(path):
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(path).resolve()), compress=True, copy=True)
