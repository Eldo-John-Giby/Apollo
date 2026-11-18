"""Strict UV-only binding for complete authenticated v22 PBR texture sets."""
from pathlib import Path

import bpy
from gnm_v22_audit import SELECTED
from gnm_pbr_manifest import load_manifest as checked_manifest
import hashlib
import json
import numpy as np

ROLES=('color','roughness','specular','normal')
TILES=(1001,1002,1004)


def cornea_recipes(head):
    result={}
    for slot in (2,4):
        tree=head.data.materials[slot].node_tree
        nodes=list(tree.nodes); entries=[]
        for node in nodes:
            inputs={}
            for i,socket in enumerate(node.inputs):
                if socket.enabled and hasattr(socket,'default_value') and not socket.is_linked:
                    value=socket.default_value
                    inputs[str(i)]=list(value) if hasattr(value,'__iter__') else value
            properties={name:getattr(node,name) for name in ('distribution',) if hasattr(node,name)}
            entries.append(dict(type=node.bl_idname,inputs=inputs,properties=properties))
        links=[(nodes.index(l.from_node),list(l.from_node.outputs).index(l.from_socket),
                nodes.index(l.to_node),list(l.to_node.inputs).index(l.to_socket)) for l in tree.links]
        result[str(slot)]=dict(nodes=entries,links=links)
    return result


def bind_corneas(head,recipes):
    allowed={'ShaderNodeBsdfGlass','ShaderNodeBsdfTransparent','ShaderNodeLightPath',
             'ShaderNodeMixShader','ShaderNodeOutputMaterial','ShaderNodeBsdfRefraction'}
    for slot,recipe in recipes.items():
        mat=bpy.data.materials.new('Apollo v22 | native corneal film '+slot);mat.use_nodes=True
        tree=mat.node_tree;tree.nodes.clear();nodes=[]
        for entry in recipe['nodes']:
            if entry['type'] not in allowed:raise ValueError('Unexpected corneal node type')
            node=tree.nodes.new(entry['type'])
            for name,value in entry['properties'].items():setattr(node,name,value)
            for i,value in entry['inputs'].items():node.inputs[int(i)].default_value=value
            nodes.append(node)
        for a,i,b,j in recipe['links']:tree.links.new(nodes[a].outputs[i],nodes[b].inputs[j])
        head.data.materials[int(slot)]=mat


def load_manifest(maps):
    maps=Path(maps)
    receipt=checked_manifest(maps)
    if receipt['source_sha256']!=SELECTED:
        raise ValueError('Texture set is not derived from the approved v22')
    return receipt


def bind(head,maps,layout='udim',full_character=False):
    if layout not in ('udim','legacy'):
        raise ValueError('Unsupported native UV layout')
    maps=Path(maps); receipt=load_manifest(maps)
    bind_corneas(head,receipt['corneas'])
    uv_name='GNM UDIM' if layout=='udim' else 'GNM Region'
    if uv_name not in head.data.uv_layers:
        raise ValueError('Target has no supported native UV layer '+uv_name)
    for tile in TILES:
        mat=bpy.data.materials.new(f'Apollo v22 | {tile} | {layout}');mat.use_nodes=True
        nodes,links=mat.node_tree.nodes,mat.node_tree.links
        shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        for name,value in receipt['material_settings'][str(tile)].items():
            setattr(shader,name,value)
        for name,value in receipt['material_defaults'][str(tile)].items():
            if name not in shader.inputs:
                raise ValueError('Blender cannot represent selected shader input '+name)
            shader.inputs[name].default_value=value
        uv=nodes.new('ShaderNodeUVMap');uv.uv_map=uv_name
        coordinates=uv.outputs['UV']
        if layout=='udim':
            offset=nodes.new('ShaderNodeVectorMath');offset.operation='SUBTRACT'
            offset.inputs[1].default_value=(tile-1001,0,0)
            links.new(coordinates,offset.inputs[0]);coordinates=offset.outputs['Vector']
        for role in ROLES:
            node=nodes.new('ShaderNodeTexImage');node.name=f'Apollo {role} {tile}'
            filename=f'{role}.{tile}.png'
            if tile==1001 and not full_character and role in receipt.get('texture_only',{}):
                filename=receipt['texture_only'][role]
            node.image=bpy.data.images.load(str((maps/filename).resolve()),check_existing=False)
            node.image.colorspace_settings.name='sRGB' if role=='color' else 'Non-Color'
            links.new(coordinates,node.inputs['Vector'])
            if role=='normal':
                normal=nodes.new('ShaderNodeNormalMap');normal.space='TANGENT';normal.uv_map=uv_name
                links.new(node.outputs['Color'],normal.inputs['Color'])
                links.new(normal.outputs['Normal'],shader.inputs['Normal'])
            else:
                socket={'color':'Base Color','roughness':'Roughness','specular':'Specular IOR Level'}[role]
                links.new(node.outputs['Color'],shader.inputs[socket])
        head.data.materials[tile-1001]=mat
    return receipt


def validate(head,maps,layout='udim',full_character=False,require_packed=True):
    """Verify active PBR dataflow and payloads independently of stored node names."""
    maps=Path(maps);receipt=load_manifest(maps)
    if layout not in ('udim','legacy'):raise ValueError('Unsupported native UV layout')
    uv_name='GNM UDIM' if layout=='udim' else 'GNM Region'
    checked={}
    def linked(socket):
        if len(socket.links)!=1:raise ValueError('Expected one portable material link: '+socket.name)
        return socket.links[0].from_node
    for tile in TILES:
        material=head.data.materials[tile-1001]
        shader=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        for name,value in receipt['material_settings'][str(tile)].items():
            if getattr(shader,name)!=value:raise ValueError('PBR shader mode changed: '+name)
        for name,value in receipt['material_defaults'][str(tile)].items():
            if name in ('Base Color','Roughness','Specular IOR Level','Normal'):
                continue  # These selected channels are intentionally map-bound.
            socket=shader.inputs[name]
            if socket.is_linked:raise ValueError('Unexpected link on constant material input '+name)
            np.testing.assert_allclose(socket.default_value,value,atol=1e-7,rtol=0)
        for role in ROLES:
            socket=shader.inputs[{'color':'Base Color','roughness':'Roughness',
                                  'specular':'Specular IOR Level','normal':'Normal'}[role]]
            texture=linked(socket)
            if role=='normal':
                if texture.type!='NORMAL_MAP' or texture.space!='TANGENT' or texture.uv_map!=uv_name:
                    raise ValueError('Incorrect tangent normal binding')
                if texture.inputs['Strength'].is_linked or texture.inputs['Strength'].default_value!=1:
                    raise ValueError('Normal map strength changed')
                texture=linked(texture.inputs['Color'])
            if texture.type!='TEX_IMAGE' or not texture.image:raise ValueError('Expected portable texture '+role)
            filename=f'{role}.{tile}.png'
            if tile==1001 and not full_character and role in receipt.get('texture_only',{}):
                filename=receipt['texture_only'][role]
            image=texture.image
            if image.colorspace_settings.name!=('sRGB' if role=='color' else 'Non-Color'):
                raise ValueError('Incorrect map color space '+filename)
            if image.packed_file:
                digest=hashlib.sha256(bytes(image.packed_file.data)).hexdigest()
            elif require_packed:
                raise ValueError('Unpacked portable map '+filename)
            else:
                digest=hashlib.sha256(Path(bpy.path.abspath(image.filepath)).read_bytes()).hexdigest()
            if digest!=receipt['maps'][filename]['sha256']:raise ValueError('Active map payload differs '+filename)
            uv=linked(texture.inputs['Vector'])
            if layout=='udim':
                if uv.type!='VECT_MATH' or uv.operation!='SUBTRACT':raise ValueError('Missing UDIM offset')
                np.testing.assert_array_equal(uv.inputs[1].default_value,(tile-1001,0,0))
                uv=linked(uv.inputs[0])
            if uv.type!='UVMAP' or uv.uv_map!=uv_name:raise ValueError('Incorrect portable UV binding')
            checked[filename]=digest
        output=next(n for n in material.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
        if linked(output.inputs['Surface'])!=shader:raise ValueError('Unexpected final material shader')
    if json.dumps(cornea_recipes(head),sort_keys=True)!=json.dumps(receipt['corneas'],sort_keys=True):
        raise ValueError('Native corneal recipe changed')
    return dict(manifest_sha256=hashlib.sha256((maps/'manifest.json').read_bytes()).hexdigest(),
                active_maps=checked,layout=layout,full_character=full_character,packed_required=require_packed)
