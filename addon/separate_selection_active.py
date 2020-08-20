# Original Question in BSE
# [python - code for "separate and select it in object mode" - Blender Stack Exchange]
# (https://blender.stackexchange.com/questions/191394/code-for-separate-and-select-it-in-object-mode/191412#191412)
import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty

bl_info = {
    "name": "Separate Selection Active",
    "description": "Separate the mesh and select them immediately.",
    "author": "hikariTW",
    "version": (0, 4),
    "blender": (2, 80, 0),
    "location": "View3D > Mesh",
    "support": "TESTING",
    "category": "Mesh",
}


class SSAAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    use_invoke: BoolProperty(
        name="Use popup invoke menu",
        description="Show popup when calling operator",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Setting for operator behavior.")
        layout.prop(self, "use_invoke")


_separate_method_enum = bpy.props.EnumProperty(
    items={
        ('SELECTED', 'Selected', "Selected mesh"),
        ('MATERIAL', 'Material', "Based on material"),
        ('LOOSE', 'Loose', "Based on loose part")
    },
    name="Separate Method",
    description="Choose a method to separate mesh",
    default='SELECTED'
)


class SeparateSelectionActive(bpy.types.Operator):
    """Separate object by selection and set it as active object."""
    bl_idname = "mesh.select_separate_active"
    bl_label = "Separate Selection Active"

    # An enum for prompt dialog
    separate_method: _separate_method_enum

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode == 'EDIT_MESH'

    def invoke(self, context, event):
        addon_prefs = context.preferences.addons[__name__].preferences
        # Prompt to ask a method to separate
        if addon_prefs.get('use_invoke', True):
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def execute(self, context):
        org_obj_list = {o.name for o in context.selected_objects}

        # Separate using selected method
        bpy.ops.mesh.separate(type=self.separate_method)
        bpy.ops.object.editmode_toggle()
        for obj in context.selected_objects:
            if obj and obj.name in org_obj_list:
                # Deselect everything selected before
                obj.select_set(False)
            else:
                # Set the new created object to active
                context.view_layer.objects.active = obj
                self.report({'INFO'}, f"Set active object to: {obj.name}")
        return {'FINISHED'}


# A menu inject into View3D > Edit > Mesh tab
def _menu_func(self, context):
    addon_prefs = context.preferences.addons[__name__].preferences
    if addon_prefs.get('use_invoke',True):
        self.layout.operator(SeparateSelectionActive.bl_idname)
    else:
        self.layout.operator_menu_enum(
            SeparateSelectionActive.bl_idname,
            property='separate_method',
            text="Separate, Selection Active"
        )


def register():
    bpy.utils.register_class(SeparateSelectionActive)
    bpy.utils.register_class(SSAAddonPreferences)
    bpy.types.VIEW3D_MT_edit_mesh.append(_menu_func)


def unregister():
    bpy.utils.unregister_class(SSAAddonPreferences)
    bpy.utils.unregister_class(SeparateSelectionActive)
    bpy.types.VIEW3D_MT_edit_mesh.remove(_menu_func)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.mesh.select_separate_active()
