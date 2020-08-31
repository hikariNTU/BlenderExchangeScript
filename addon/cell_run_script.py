# Original Question in BSE
# [Could you run some parts in the script of blender?]
# (https://blender.stackexchange.com/questions/192882/could-you-run-some-parts-in-the-script-of-blender)
__QUESTION = """
In MATLAB you could sometimes break the code into cells and run them individually, this usually saves a lot of time. So i was curious if you could do the same in blenders script.
"""
import bpy

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

_START_TAG = '# region'
_END_TAG = '# endregion'


class TEXT_OT_run_cell_script(bpy.types.Operator):
    """Run current selected cell script in python."""
    bl_idname = "text.runcell"
    bl_label = "Run current cell"

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
        # print('EXECUTE addon')
        text_obj = context.area.spaces.active.text
        codes = text_obj.as_string()
        # print(codes)
        c_lines = codes.split('\n')
        cells = self.get_codecells_mapping(c_lines)
        # print(cells)
        if cells:
            cell_idx = -1
            idx = text_obj.current_line_index
            for i in range(idx, -1, -1):
                if c_lines[i].startswith(_START_TAG):
                    cell_idx = i
                    break
            name, start, end = cells.get(
                cell_idx,
                (text_obj.name, 0, len(c_lines) - 1)
            )
            # print((name, start, end))
            self.report({'INFO'}, f"Execute cell: [{name}]({start}:{end})")
            exec(
                compile(
                    '\n'.join(c_lines[start:end]),
                    filename=f"S-Cell-{name}",
                    mode='exec',
                )
            )
        return {'FINISHED'}


def register():
    bpy.utils.register_class(TEXT_OT_run_cell_script)


def unregister():
    bpy.utils.unregister_class(TEXT_OT_run_cell_script)
