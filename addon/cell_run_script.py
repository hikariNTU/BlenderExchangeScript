# Original Question in BSE
# [Could you run some parts in the script of blender?]
# (https://blender.stackexchange.com/questions/192882/could-you-run-some-parts-in-the-script-of-blender)
__QUESTION = """
In MATLAB you could sometimes break the code into cells and run them individually, this usually saves a lot of time. So i was curious if you could do the same in blenders script.
"""

testcode = """
filename = R"E:\BSE\addon\cell_run_script.py"
exec(compile(open(filename).read(), filename, 'exec'))
# region Hello
# endregion

# region print
print("hello world")
# endregion
"""

import bpy
import json

bl_info = {
    "name": "Run cell script in python",
    "description": "Provide the ability to use VS-like region and endregion tag for cell execute script in Blender text editor.",
    "author": "hikariTW",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "TextEditor",
    "support": "TESTING",
    "category": "Interface",
}

# Specified tag.
_START_TAG = '# region'
_END_TAG = '# endregion'


class TEXT_OT_check_cell(bpy.types.Operator):
    bl_idname = "text.check_cell"
    bl_description = "Check cell in active text block"
    bl_label = "Check script cell"
    bl_options = {'REGISTER'}

    @staticmethod
    def get_codecells_mapping(c_lines: list) -> dict:
        stack = []
        cells = {}
        for idx, line in enumerate(c_lines):
            if line.startswith(_START_TAG):
                stack.append((line[len(_START_TAG) :], idx))
            elif line.startswith(_END_TAG):
                if len(stack) == 0:
                    continue
                cell_name, idx_start = stack.pop()
                cells[idx_start] = (cell_name, idx_start, idx)
        for cell_name, idx_start in stack:
            # Fill unmatched block
            cells[idx_start] = (cell_name, idx_start, len(c_lines) - 1)
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
    """Run current selected cell script in python."""

    bl_idname = "text.run_cell_script"
    bl_label = "Run current cell"
    bl_options = {'REGISTER'}
    # fmt: off
    force_index: bpy.props.IntProperty(
        name="Use this line index",
        description="Use this line index.",
        default= -1,
        options={'SKIP_SAVE'}
    )
    # fmt: on
    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    @staticmethod
    def get_codecells_mapping(c_lines: list) -> dict:
        stack = []
        cells = {}
        for idx, line in enumerate(c_lines):
            if line.startswith(_START_TAG):
                stack.append((line[len(_START_TAG) :], idx))
            elif line.startswith(_END_TAG):
                if len(stack) == 0:
                    continue
                cell_name, idx_start = stack.pop()
                cells[idx_start] = (cell_name, idx_start, idx)
        for cell_name, idx_start in stack:
            # Fill unmatched block
            cells[idx_start] = (cell_name, idx_start, len(c_lines) - 1)
        return cells

    def execute(self, context):
        text_obj = context.area.spaces.active.text
        codes = text_obj.as_string()
        c_lines = codes.split('\n')
        bpy.ops.text.check_cell()
        cells = json.loads(context.scene.cells_json)
        if cells:
            cell_idx = self.force_index
            if cell_idx == -1:
                idx = text_obj.current_line_index
                for i in range(idx, -1, -1):
                    if c_lines[i].startswith(_START_TAG):
                        cell_idx = i
                        break
            name, start, end = cells.get(cell_idx, (text_obj.name, 0, len(c_lines) - 1))
            # print((name, start, end))
            self.report({'INFO'}, f"Execute cell: {name.strip()}({start+1}:{end+1})")
            exec(
                compile(
                    '\n'.join(c_lines[start:end]),
                    filename=f"S-Cell-{name}",
                    mode='exec',
                )
            )
        return {'FINISHED'}


class TEXT_PT_cells(bpy.types.Panel):
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Text"
    bl_label = "Cells Script"

    def check_cell(self, context):
        text_obj = context.area.spaces.active.text
        codes = text_obj.as_string()
        c_lines = codes.split('\n')
        return TEXT_OT_check_cell.get_codecells_mapping(c_lines)

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        live_check = context.scene.cell_live_check
        if live_check:
            cells = self.check_cell(context)
        else:
            row.operator(TEXT_OT_check_cell.bl_idname, text='Check Cell')
            cells = json.loads(context.scene.cells_json)
        row.prop(context.scene, 'cell_live_check')

        if not cells:
            row = layout.row()
            row.label(text="No cell found in text editor.")
        for name, start, end in cells.values():
            row = layout.row()
            row.label(text=f"{name.strip()} [{start+1}:{end+1})")
            row.operator(
                TEXT_OT_run_cell_script.bl_idname, text="Run this cell", icon='PLAY'
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
    )
    bpy.types.Scene.cells_json = bpy.props.StringProperty(
        name="Script cell stored in json",
        description="Script cell stored in json",
        default='',
    )


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    from bpy.utils import register_class

    for c in classes:
        register_class(c)

    bpy.types.Scene.cell_live_check = bpy.props.BoolProperty(
        name="Live check text editor cell",
        description="Live check text editor cell",
        default=True,
    )
    bpy.types.Scene.cells_json = bpy.props.StringProperty(
        name="Script cell stored in json",
        description="Script cell stored in json",
        default='',
    )
