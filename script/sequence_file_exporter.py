import bpy
from bpy_extras.io_utils import ExportHelper

class ExportCommon(bpy.types.Operator, ExportHelper):

    bl_idname = "export.common"
    bl_label = "Export common"
    bl_options = {'PRESET'}

    filename_ext = ".fbx"
    filename: bpy.props.StringProperty(
        name="file name",
        default=''
    )
    filepath: bpy.props.StringProperty(
        name="file name",
        default=''
    )
    directory: bpy.props.StringProperty(
        name="file name",
        default=''
    )
    def invoke(self, context, event):       

        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}

    def execute(self, context):

        print(self.filename)
        return {"FINISHED"}

classes = [
    ExportCommon
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()