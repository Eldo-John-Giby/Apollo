"""Bake selected v22 shader channels to native region UVs, without lighting."""
import argparse
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gnm_v22_audit import SELECTED, sha
from gnm_v22_materials import cornea_recipes

ROOT=Path(__file__).resolve().parents[1]
RECIPE_FILES=('tools/gnm_v22_bake.py','tools/gnm_v22_materials.py',
              'tools/gnm_v22_audit.py','tools/gnm_pbr_manifest.py')
RECIPE_HASHES={name:sha(ROOT/name) for name in RECIPE_FILES}


def main(args):
    source = Path(bpy.data.filepath)
    if sha(source) != SELECTED:
        raise ValueError('Expected immutable selected v22')
    if args.out.exists():
        raise FileExistsError(args.out)
    args.out.mkdir(parents=True)
    scene = bpy.context.scene
    head = scene.objects['GNM Head']
    originals = list(head.data.materials)
    regions=np.empty(len(head.data.polygons),dtype=np.int32)
    head.data.polygons.foreach_get('material_index',regions)
    source_uv=next(layer.name for layer in head.data.uv_layers if layer.active_render)
    # Native region UVs overlap between materials; each material gets its own
    # target image, so no other region can overwrite the skin or either eye.
    head.data.uv_layers.active = head.data.uv_layers['GNM Region']
    head.data.uv_layers['GNM Region'].active_render = True
    for obj in scene.objects:
        obj.select_set(False)
    head.hide_set(False); head.select_set(True)
    bpy.context.view_layer.objects.active = head
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = args.samples
    scene.render.bake.use_selected_to_active = False
    scene.render.bake.margin = args.size//128
    scene.render.bake.use_clear = True
    export = bpy.data.scenes.new('Apollo | map serialization')
    export.render.image_settings.file_format = 'PNG'
    export.render.image_settings.color_mode = 'RGB'
    export.render.image_settings.color_depth = '16'
    export.view_settings.look = 'None'
    export.view_settings.exposure = 0
    export.view_settings.gamma = 1
    manifest = dict(source_sha256=SELECTED, blender=bpy.app.version_string,
                    recipe_sha256=sha(__file__), samples=args.samples,
                    recipes=RECIPE_HASHES,complete=False,
                    uv_layout='GNM Region (equivalent UDIM offsets retained in target)',
                    margin_px=args.size//128, maps={}, material_defaults={},material_settings={},
                    corneas=cornea_recipes(head),
                    detail='Tangent-space OpenGL normal includes the complete selected bump stack; do not layer its source height again.',
                    qualification='Bake prototype; fresh target wrapping and visual comparisons pending.')
    for role in args.roles.split(','):
        if role not in ('color','roughness','normal','specular'):
            raise ValueError('Unknown map role '+role)
        images = {}
        for index, original in enumerate(originals):
            mat = original.copy()
            mat.use_nodes = True
            # Replacing slots preserves polygon region indices. Clearing all
            # slots first would silently remap every eye/interior face to skin.
            head.data.materials[index]=mat
            nodes, links = mat.node_tree.nodes, mat.node_tree.links
            # Baking changes the active render UV. Freeze implicit source UV
            # reads first, otherwise UDIM eye offsets sample outside their maps.
            explicit=nodes.new('ShaderNodeUVMap'); explicit.uv_map=source_uv
            for n in list(nodes):
                if n.type=='TEX_COORD':
                    for link in list(n.outputs['UV'].links):
                        links.new(explicit.outputs['UV'],link.to_socket)
                elif n.type=='TEX_IMAGE' and not n.inputs['Vector'].is_linked:
                    links.new(explicit.outputs['UV'],n.inputs['Vector'])
                elif n.type in ('NORMAL_MAP','TANGENT') and hasattr(n,'uv_map') and not n.uv_map:
                    n.uv_map=source_uv
            size = args.size if index==0 else args.eye_size if index in (1,3) else 64
            image = bpy.data.images.new(f'Apollo bake {role} {index}',size,size,alpha=False,float_buffer=True)
            image.colorspace_settings.name = 'sRGB' if role=='color' else 'Non-Color'
            target = nodes.new('ShaderNodeTexImage'); target.image = image
            for node in nodes:
                node.select = node==target
            nodes.active = target
            shader = next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
            if index in (0,1,3):
                if shader is None:
                    raise ValueError('Missing pigment shader '+mat.name)
                values = {}
                for socket in shader.inputs:
                    if not socket.enabled or not hasattr(socket,'default_value') or socket.is_linked:
                        continue
                    value = socket.default_value
                    values[socket.name] = list(value) if hasattr(value,'__iter__') else value
                manifest['material_defaults'][str(index+1001)] = values
                manifest['material_settings'][str(index+1001)] = dict(subsurface_method=shader.subsurface_method,
                                                                    distribution=shader.distribution)
            if role != 'normal':
                emission = nodes.new('ShaderNodeEmission')
                if shader is None:
                    # Discarded corneal/interior targets still need a valid
                    # active bake image, but no pigment map is delivered for them.
                    emission.inputs['Color'].default_value=(0,0,0,1)
                else:
                    socket = shader.inputs[{'color':'Base Color','roughness':'Roughness',
                                            'specular':'Specular IOR Level'}[role]]
                    if socket.is_linked:
                        links.new(socket.links[0].from_socket,emission.inputs['Color'])
                    else:
                        value = socket.default_value
                        emission.inputs['Color'].default_value = tuple(value) if role=='color' else (value,value,value,1)
                output = next(n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
                links.new(emission.outputs[0],output.inputs['Surface'])
            images[index] = image
        current=np.empty_like(regions)
        head.data.polygons.foreach_get('material_index',current)
        np.testing.assert_array_equal(current,regions)
        result = bpy.ops.object.bake(type='NORMAL' if role=='normal' else 'EMIT',
                                      normal_space='TANGENT', uv_layer='GNM Region')
        if result != {'FINISHED'}:
            raise RuntimeError('Bake failed '+role)
        for index,tile in [(0,1001),(1,1002),(3,1004)]:
            image = images[index]
            output = args.out/f'{role}.{tile}.png'
            export.view_settings.view_transform = 'Standard' if role=='color' else 'Raw'
            image.save_render(str(output.resolve()),scene=export)
            if output.read_bytes()[24] != 16:
                raise ValueError('Bake lost 16-bit precision')
            values = np.empty(len(image.pixels),dtype=np.float32)
            image.pixels.foreach_get(values)
            pixels = values.reshape(-1,4)[:,:3]
            if not np.isfinite(pixels).all() or pixels.std()<1e-5:
                raise ValueError('Invalid or empty bake '+str(output))
            manifest['maps'][output.name] = dict(sha256=sha(output),size=list(image.size),
                    colorspace=image.colorspace_settings.name,min=float(pixels.min()),max=float(pixels.max()))
            print('BAKED '+str(output),flush=True)
        for image in images.values():
            bpy.data.images.remove(image,do_unlink=True)
        (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    if sha(source) != SELECTED:
        raise ValueError('Selected source changed')
    if any(sha(ROOT/name)!=digest for name,digest in RECIPE_HASHES.items()):
        raise ValueError('Bake recipes changed during execution')
    manifest['complete']=all(f'{role}.{tile}.png' in manifest['maps']
                             for role in ('color','roughness','specular','normal')
                             for tile in (1001,1002,1004))
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('RESULT '+json.dumps(dict(manifest=str(args.out/'manifest.json'),source_unchanged=True)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--size',type=int,default=4096)
    parser.add_argument('--eye-size',type=int,default=2048)
    parser.add_argument('--samples',type=int,default=32)
    parser.add_argument('--roles',default='color,roughness,specular,normal')
    main(parser.parse_args(sys.argv[sys.argv.index('--')+1:]))
