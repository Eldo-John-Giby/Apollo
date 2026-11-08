"""Optional Blender sidebar; no handlers, constraints, or independent gaze math."""
from pathlib import Path
import sys
import bpy
from bpy.props import FloatProperty,StringProperty,PointerProperty
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'wrapper'))
import eyes


def update(self,context):
    if 'apollo_calibration' in context.scene:eyes.move(self.h,self.v)


class ApolloSettings(bpy.types.PropertyGroup):
    h:FloatProperty(name='Horizontal',min=-1,max=1,default=0,update=update)
    v:FloatProperty(name='Vertical',min=-1,max=1,default=0,update=update)
    output:StringProperty(name='Render file',default='//apollo-preview.png',subtype='FILE_PATH')
    sweep_folder:StringProperty(name='Sweep folder',default='//apollo-demo-sweep',subtype='DIR_PATH')


class ApolloPose(bpy.types.Operator):
    bl_idname='apollo.pose';bl_label='Set gaze'
    h:FloatProperty();v:FloatProperty()
    def execute(self,context):
        settings=context.scene.apollo_controls;settings.h=self.h;settings.v=self.v
        eyes.move(self.h,self.v);return {'FINISHED'}


class ApolloRender(bpy.types.Operator):
    bl_idname='apollo.render_pose';bl_label='Render current pose'
    def execute(self,context):
        eyes.render(bpy.path.abspath(context.scene.apollo_controls.output));return {'FINISHED'}


class ApolloPanel(bpy.types.Panel):
    bl_label='Apollo gaze';bl_idname='APOLLO_PT_gaze';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Apollo'
    def draw(self,context):
        layout=self.layout
        if 'apollo_calibration' not in context.scene:
            layout.label(text='Open a calibrated Apollo scene');return
        settings=context.scene.apollo_controls
        layout.prop(settings,'h',slider=True);layout.prop(settings,'v',slider=True)
        for name,h,v in [('Left',-1,0),('Right',1,0),('Up',0,1),('Down',0,-1),('Reset',0,0)]:
            button=layout.operator('apollo.pose',text=name);button.h=h;button.v=v
        cfg=eyes.calibration();layout.label(text=f"Camera: {cfg['cam_dist']*100:.0f} cm; target: {cfg['target_dist']*100:.0f} cm")
        layout.prop(settings,'output');layout.operator('apollo.render_pose')
        layout.prop(settings,'sweep_folder');layout.operator('apollo.sweep')


class ApolloSweep(bpy.types.Operator):
    bl_idname='apollo.sweep';bl_label='Run official sweep'
    def execute(self,context):
        destination=Path(bpy.path.abspath(context.scene.apollo_controls.sweep_folder)).resolve()
        if destination==Path(bpy.data.filepath).resolve().parent:
            self.report({'ERROR'},'Use a separate demo output folder');return {'CANCELLED'}
        eyes.sweep(out_dir=destination);return {'FINISHED'}


CLASSES=[ApolloSettings,ApolloPose,ApolloRender,ApolloSweep,ApolloPanel]
def register():
    for cls in CLASSES:bpy.utils.register_class(cls)
    bpy.types.Scene.apollo_controls=PointerProperty(type=ApolloSettings)
def unregister():
    del bpy.types.Scene.apollo_controls
    for cls in reversed(CLASSES):bpy.utils.unregister_class(cls)
if __name__=='__main__':register()
