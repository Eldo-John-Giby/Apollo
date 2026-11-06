"""Read-only character inventory, run in Blender on the supplied asset."""
import argparse
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector


def inspect():
    objects=[]
    for obj in bpy.data.objects:
        item={'name':obj.name,'type':obj.type,'matrix_world':[list(row) for row in obj.matrix_world]}
        if obj.type=='ARMATURE':
            item['bones']=[{'name':b.name,'parent':b.parent.name if b.parent else None,'head_world':list(obj.matrix_world@b.head_local),'tail_world':list(obj.matrix_world@b.tail_local)} for b in obj.data.bones]
        if obj.type=='MESH':
            points=[obj.matrix_world@Vector(p) for p in obj.bound_box]
            item.update(vertices=len(obj.data.vertices),bounds_min=[min(p[i] for p in points) for i in range(3)],bounds_max=[max(p[i] for p in points) for i in range(3)],materials=[s.material.name if s.material else None for s in obj.material_slots],groups=[g.name for g in obj.vertex_groups])
        objects.append(item)
    return {'blender':bpy.app.version_string,'objects':objects,'images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file),'has_data':i.has_data,'path':i.filepath} for i in bpy.data.images]}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(inspect(),indent=2),encoding='utf-8')
