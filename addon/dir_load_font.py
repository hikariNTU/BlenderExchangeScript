bl_info = {
    "name": "Load Directory fonts",
    "description": "Load all directory fonts at a time.",
    "author": "hikariTW",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "category": "Misc",
}
import bpy
import os


class OpenFontDir(bpy.types.Operator):
    bl_idname = 'data.openfontdir'
    bl_label = "load fontdir"

    directory: bpy.props.StringProperty(
        name="Directory of Font", default="", subtype='DIR_PATH'
    )

    def execute(self, context):
        directory = os.fsencode(self.directory)

        for file in os.listdir(directory):  # list file
            filename = os.fsdecode(file)  # get filename from file
            bpy.ops.font.open(
                filepath=os.path.join(self.directory, filename)
            )  # join the path

        self.report({"INFO"}, "load from: {!r}".format(self.directory))
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class Dirfontpanel(bpy.types.Panel):
    bl_idname = "CATEGORY_PT_Dirfontpanel"
    bl_label = "Dir font panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text="Open directory")
        layout.operator(OpenFontDir.bl_idname)


classes = (Dirfontpanel, OpenFontDir)


def register():
    from bpy.utils import register_class

    for clss in classes:
        register_class(clss)


def unregister():
    from bpy.utils import unregister_class

    for clss in reversed(classes):
        unregister_class(clss)


if __name__ == "__main__":
    register()
