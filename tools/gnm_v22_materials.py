"""Strict UV-only binding for complete authenticated v22 PBR texture sets."""
import hashlib
import json
from pathlib import Path

import bpy
from gnm_v22_audit import SELECTED

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
    receipt=json.loads((maps/'manifest.json').read_text(encoding='utf-8'))
    if receipt['source_sha256']!=SELECTED:
        raise ValueError('Texture set is not derived from the approved v22')
    required={f'{role}.{tile}.png' for tile in TILES for role in ROLES}
    if not required.issubset(receipt['maps']):raise ValueError('Incomplete PBR manifest')
    for name,entry in receipt['maps'].items():
        if Path(name).name!=name:raise ValueError('Invalid map filename')
        digest=hashlib.sha256((maps/name).read_bytes()).hexdigest()
        if entry['sha256']!=digest:raise ValueError('Texture checksum mismatch '+name)
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
