"""Create an isolated procedural-iris look candidate from a calibrated scene.

Run in a disposable Blender process; never overwrites the input scene.
"""
import argparse
import json
from pathlib import Path
import sys
import bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wrapper'))
import eyes


def iris_material():
    material=bpy.data.materials.new('Apollo radial hazel iris')
    material.use_nodes=True
    nodes=material.node_tree.nodes; nodes.clear(); links=material.node_tree.links
    def node(kind): return nodes.new(kind)
    def calc(operation,a,b=0.):
        n=node('ShaderNodeMath'); n.operation=operation
        for socket,value in zip(n.inputs,[a,b]):
            if isinstance(value,(float,int)): socket.default_value=value
            else: links.new(value,socket)
        return n.outputs[0]
    uv=node('ShaderNodeTexCoord'); separate=node('ShaderNodeSeparateXYZ')
    links.new(uv.outputs['UV'],separate.inputs[0])
    x=calc('ADD',separate.outputs['X'],-.5)
    y=calc('ADD',separate.outputs['Y'],-.5)
    radius=calc('MULTIPLY',calc('SQRT',calc('ADD',calc('MULTIPLY',x,x),calc('MULTIPLY',y,y))),2.)
    angle=calc('ARCTAN2',y,x)
    warp=calc('SINE',calc('ADD',calc('MULTIPLY',angle,13.),calc('MULTIPLY',radius,32.)))
    fine=calc('SINE',calc('ADD',calc('MULTIPLY',angle,173.),calc('MULTIPLY',warp,1.8)))
    coarse=calc('SINE',calc('ADD',calc('MULTIPLY',angle,61.),calc('MULTIPLY',radius,14.)))
    fibers=calc('ADD',calc('MULTIPLY',fine,.22),calc('ADD',calc('MULTIPLY',coarse,.18),.5))
    ramp=node('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(.12,.26,.14,1)
    ramp.color_ramp.elements[1].color=(.30,.48,.22,1)
    links.new(fibers,ramp.inputs[0])
    rings=node('ShaderNodeValToRGB')
    stops=[(0.,(.80,.85,.60,1)),(.32,(.80,.85,.60,1)),(.43,(1,1,1,1)),(.89,(1,1,1,1)),(1.,(.42,.50,.38,1))]
    rings.color_ramp.elements.remove(rings.color_ramp.elements[1])
    for i,(position,color) in enumerate(stops):
        element=rings.color_ramp.elements[0] if i==0 else rings.color_ramp.elements.new(position)
        element.position=position; element.color=color
    links.new(radius,rings.inputs[0])
    mix=node('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=1
    links.new(ramp.outputs[0],mix.inputs[1]); links.new(rings.outputs[0],mix.inputs[2])
    shader=node('ShaderNodeBsdfPrincipled')
    links.new(mix.outputs[0],shader.inputs['Base Color'])
    shader.inputs['Roughness'].default_value=.6
    shader.inputs['Specular IOR Level'].default_value=0
    output=node('ShaderNodeOutputMaterial'); links.new(shader.outputs[0],output.inputs['Surface'])
    return material


def apply_iris():
    """Apply the tested material and UVs without changing calibrated geometry."""
    rig=eyes._rig(); eyes.reset(); material=iris_material()
    for side in 'LR':
        obj=bpy.data.objects['Iris.'+side]; mesh=obj.data
        uv=mesh.uv_layers.get('Iris polar coordinates') or mesh.uv_layers.new(name='Iris polar coordinates')
        center=rig.rest[side][0].translation
        for loop in mesh.loops:
            point=obj.matrix_world@mesh.vertices[loop.vertex_index].co
            uv.data[loop.index].uv=((point.x-center.x)/.013+.5,(point.z-center.z)/.013+.5)
        mesh.materials.clear(); mesh.materials.append(material)
    eyes.reset()


def run(folder):
    folder=Path(folder).resolve()
    source=Path(bpy.data.filepath).resolve()
    if source==folder/'scene.blend': raise ValueError('Use a separate candidate folder')
    folder.mkdir(parents=True,exist_ok=True)
    apply_iris()
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),compress=True)
    ev=folder/'verification'; ev.mkdir(exist_ok=True)
    eyes.render(ev/'baseline.png')
    report={'config':eyes.calibration(),'directions':{},'source':str(source),'stage':'directions_complete'}
    for name,h,v in [('left',-1,0),('right',1,0),('up',0,1),('down',0,-1),('reset',0,0)]:
        eyes.move(h,v); report['directions'][name]=eyes.render(ev/(name+'.png'))['record']
        print('Polish render:',name,flush=True)
    report['reset_identical']=(ev/'baseline.png').read_bytes()==(ev/'reset.png').read_bytes()
    (ev/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
    eyes.reset()


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--folder',type=Path,required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]); run(args.folder)
