# Original Question in BSE
# [python - Blender 2.90 : How set an hotkey to run a saved script like ui_menu.py - Blender Stack Exchange]
# (https://blender.stackexchange.com/questions/195050/blender-2-90-how-set-an-hotkey-to-run-a-saved-script-like-ui-menu-py)
__QUESTION = R"""
Following tutorials about how register the hotkey for a script or menu,
i always get an error with "nameofthefile.py" not found
or "error in line x" but i copy/paste the whole script.

So lets say i create a new script, from the template Ui_menu.py
how do i set and register the hotkey to run it while modeling ?

Thanks
"""

bl_info = {
    "name": "Run specified script in all context",
    "description": "Run script in any space with given name of script. This provide the ability to assign a short cut to a script in desired position.",
    "author": "hikariTW",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "TextEditor",
    "support": "TESTING",
    "category": "Interface",
}

import bpy


def create_summary(text: str, length: int = 300) -> str:
    return f"Code Preview:\n\n{text[:length]}"


def list_textname_callback(scene, context):
    return [
        (text.name, text.name, create_summary(text.as_string()))
        for text in bpy.data.texts
    ]


class TEXT_OT_run_specified_script(bpy.types.Operator):
    bl_idname = "text.run_specified_script"
    bl_label = "Run specified text script"
    bl_options = {'REGISTER'}

    # fmt: off
    script_name: bpy.props.EnumProperty(
        name="Run script from:",
        description="Run this specified script.",
        items=list_textname_callback
    )
    # fmt: on

    def invoke(self, context, event):
        # Prompt to ask
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        script = bpy.data.texts.get(self.script_name, None)
        if script != None:
            exec(
                compile(
                    script.as_string(),
                    filename=f"{script.name}",
                    mode='exec',
                ),
            )
        else:
            self.report({'WARNING'}, "No script found.")
        return {'FINISHED'}


def _menu_func(self, context):
    self.layout.operator(
        TEXT_OT_run_specified_script.bl_idname,
        text=TEXT_OT_run_specified_script.bl_label,
    )


# fmt: off
classes = [
    TEXT_OT_run_specified_script,
]
# fmt: on


def register():
    for c in classes:
        bpy.utils.register_class(c)
        bpy.types.TOPBAR_MT_window.append(_menu_func)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        bpy.types.TOPBAR_MT_window.remove(_menu_func)


if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
