# Original Question in BSE
# [Could you run some parts in the script of blender?]
# (https://blender.stackexchange.com/questions/192882/could-you-run-some-parts-in-the-script-of-blender)
__QUESTION = """
In MATLAB you could sometimes break the code into cells and run them individually, this usually saves a lot of time. So i was curious if you could do the same in blenders script.
"""

_TEST_EDITOR_TEXT = R"""
# region Hello
a = "Hello world"
# endregion

# region print
print(a)
# endregion

# region import BPY
import bpy
# endregion

# region move obj
bpy.context.object.location.x += 0.1
# endregion
"""

import bpy
import json

bl_info = {
    "name": "Run cell script in python",
    "description": "Provide the ability to use VS-like region and endregion tag for cell execute script in Blender text editor.",
    "author": "hikariTW",
    "version": (0, 3),
    "blender": (2, 80, 0),
    "location": "TextEditor",
    "support": "TESTING",
    "category": "Interface",
}

# Specified tag.
_START_TAG = '# region'
_END_TAG = '# endregion'

# link between each cell call
_CELL_EXEC_LOCAL = {}


class TEXT_OT_check_cell(bpy.types.Operator):
    bl_idname = "text.check_cell"
    bl_description = "Check cell in active text block"
    bl_label = "Check script cell"
    bl_options = {'REGISTER'}

    @staticmethod
    def get_codecells_mapping(c_lines: list) -> dict:
        """
        Using stack to find matching region. Will deal with broken region.

        Args:
            c_lines (list): A separated codes string list, will be join with '\\n'

        Returns:
            dict: A dictionary mapping key[start: int]: (name, start, end)
        """
        stack = []
        cells = {}
        for idx, line in enumerate(c_lines):
            if line.startswith(_START_TAG):
                stack.append((line[len(_START_TAG) :], idx))
            elif line.startswith(_END_TAG):
                if len(stack) == 0:
                    continue  # skip for unexpected end region
                cell_name, idx_start = stack.pop()
                cells[idx_start] = (
                    cell_name.strip() if cell_name.strip() else 'no name',
                    idx_start,
                    idx,
                )
        for cell_name, idx_start in stack:
            # Fill unmatched block
            cells[idx_start] = (
                cell_name.strip() if cell_name.strip() else 'no name',
                idx_start,
                len(c_lines) - 1,
            )
        return cells

    def execute(self, context):
        area = next(area for area in context.screen.areas if area.type == 'TEXT_EDITOR')
        text_obj = area.spaces.active.text
        codes = text_obj.as_string()
        c_lines = codes.split('\n')
        cells = self.get_codecells_mapping(c_lines)
        context.scene.cells_json = json.dumps(cells)
        return {'FINISHED'}


class TEXT_OT_run_cell_script(bpy.types.Operator):
    """Run closest current cell script in text editor."""

    bl_idname = "text.run_cell_script"
    bl_label = "Run current cell"
    bl_options = {'REGISTER'}
    # fmt: off
    force_index: bpy.props.IntProperty(
        name="Use this line index",
        description="Use this line index instead of closest cell.",
        default= -1,
        options={'SKIP_SAVE'}
    )
    # fmt: on
    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    @staticmethod
    def get_closest_idx(c_lines, current_idx):
        for i in range(current_idx, -1, -1):
            if c_lines[i].startswith(_START_TAG):
                return i
        return -1

    def execute(self, context):
        text_obj = context.area.spaces.active.text
        c_lines = text_obj.as_string().split('\n')
        bpy.ops.text.check_cell()
        cells = json.loads(context.scene.cells_json)

        if cells:
            cell_idx = self.force_index
            if cell_idx == -1:
                cell_idx = self.get_closest_idx(c_lines, text_obj.current_line_index)
            name, start, end = cells.get(
                str(cell_idx),  # JSON doesn't support int as key?
                (text_obj.name, 0, len(c_lines) - 1),
            )

            self.report({'INFO'}, f"Execute cell: ({start+1}:{end+1}) {name}")
            cell_code_str = '\n'.join(c_lines[start:end])
            global _CELL_EXEC_LOCAL
            exec(
                compile(
                    cell_code_str,
                    filename=f"Cell-{name}",
                    mode='exec',
                ),
                {},  # ignore global
                _CELL_EXEC_LOCAL,  # reuse local
            )
        else:
            self.report({'WARNING'}, "No cell found.")
        return {'FINISHED'}


class TEXT_PT_cells(bpy.types.Panel):
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Text"
    bl_label = "Cells Script"

    def check_cell(self, context):
        """Simple check mapping to avoid operator."""
        text_obj = context.area.spaces.active.text
        codes = text_obj.as_string()
        c_lines = codes.split('\n')
        return TEXT_OT_check_cell.get_codecells_mapping(c_lines)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, 'cell_live_check', text="Live Check")
        live_check = context.scene.cell_live_check
        if live_check:
            cells = self.check_cell(context)
        else:
            row.operator(TEXT_OT_check_cell.bl_idname, text='Check Cell')
            cells = json.loads(context.scene.cells_json)
        layout.separator()

        if not cells:
            row = layout.row()
            row.label(text="No cell found in text editor.")
        else:
            text_obj = context.area.spaces.active.text
            c_lines = text_obj.as_string().split('\n')
            cell_idx = TEXT_OT_run_cell_script.get_closest_idx(
                c_lines, text_obj.current_line_index
            )

            for name, start, end in sorted(cells.values(), key=lambda x: x[1]):
                row = layout.row()
                row.label(
                    text=f"[{start+1}:{end+1}) {name}",
                    icon="LINENUMBERS_OFF" if start != cell_idx else "LINENUMBERS_ON",
                    #  Show ON in closest cell block.
                )
                row.operator(
                    TEXT_OT_run_cell_script.bl_idname, text="Execute cell", icon='PLAY'
                ).force_index = start


# fmt: off
classes = [
    TEXT_OT_check_cell,
    TEXT_OT_run_cell_script,
    TEXT_PT_cells
]
# fmt: on


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.cell_live_check = bpy.props.BoolProperty(
        name="Live check text editor cell",
        description="Live check text editor cell",
        default=True,
        options={'SKIP_SAVE'},
    )
    bpy.types.Scene.cells_json = bpy.props.StringProperty(
        name="Script cell stored in json",
        description="Script cell stored in json",
        default='',
        options={'SKIP_SAVE'},
    )


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.cells_json
    del bpy.types.Scene.cell_live_check


if __name__ == "__main__":
    try:
        unregister()
    except:
        del bpy.types.Scene.cells_json
        del bpy.types.Scene.cell_live_check
        pass
    register()
