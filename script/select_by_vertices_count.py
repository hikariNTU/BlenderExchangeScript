__OP = '''
[python - Select all Objects with "x" amount of Vertices - Blender Stack Exchange](https://blender.stackexchange.com/questions/196713/select-all-objects-with-x-amount-of-vertices/196717#196717)
'''

import bpy

vertCount = 4
context = bpy.context


for obj in context.selected_objects:
    if obj.type != 'MESH':
        obj.select_set(False)  # deselect not mesh type
        continue
    assert obj.type == 'MESH'
    if obj.data and obj.data.vertices and len(obj.data.vertices) == vertCount:
        pass
    else:
        obj.select_set(False)
