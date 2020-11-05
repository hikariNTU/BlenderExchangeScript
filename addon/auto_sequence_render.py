bl_info = {
    "name": "Auto Renderer",
    "description": "Due to instability of Blender 2.80 beta version, rendering video can be issue-some. In some frame Blender will tend to DROP something in scene. Making it not able to render any animation without fixing those broken frame. This addon use explicit command to render each frame, in this case, most of the frame are good to go.",
    "category": "Misc",
    "version": (0, 0, 1),
    "author": "hikaritw (Taiwan)",
    "blender": (2, 80, 00),
}

import bpy


class AutoRenderer(bpy.types.Operator):
    bl_idname = 'common.auto_renderer'
    bl_label = 'Auto Renderer'
    bl_options = {"REGISTER"}

    start_f: bpy.props.IntProperty(name="Start Frame", default=1)
    end_f: bpy.props.IntProperty(name="End Frame", default=30)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        self.file_path = context.scene.atrender_folder_path
        for i in range(self.start_f, self.end_f + 1):
            bpy.context.scene.frame_set(i)
            bpy.data.scenes['Scene'].render.filepath = self.file_path + str(i)
            bpy.ops.render.render(write_still=True)
        return {'FINISHED'}


class AutoRenderPanel(bpy.types.Panel):
    """AutoRenderPanel"""

    bl_idname = "VIEW3D_PT_autorender"
    bl_label = "Auto Render"
    bl_category = "Render"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        ###### RENDER
        layout.prop(context.scene, "atrender_folder_path")
        layout.operator(AutoRenderer.bl_idname, icon='AUTO', text='Start Render')
        ######


classes = (AutoRenderer, AutoRenderPanel)


def register():
    for klass in classes:
        bpy.utils.register_class(klass)
    bpy.types.Scene.atrender_folder_path = bpy.props.StringProperty(
        name="Directory",
        description="Where to render to",
        default="B:/test/where/",
        subtype='DIR_PATH',
    )


def unregister():
    del bpy.types.Scene.atrender_folder_path
    for klass in classes:
        bpy.utils.unregister_class(klass)


if __name__ == "__main__":
    register()