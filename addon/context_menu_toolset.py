# Original Question in BSE
# 
import bpy
from bpy.types import Menu

bl_info = {
    "name": "Toolset in right click context menu",
    "description": "This addon inject the toolset (move, transform, rotate. ..) in to right click menu inside View 3D space.",
    "author": "hikariTW",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "support": "TESTING",
    "category": "Interface",
}

__toolset_list = {
    "builtin.select": {
        'text': "Tweak Select",
        'icon': 'RESTRICT_SELECT_OFF'
    },
    "builtin.select_box": {
        'text': "Select Box",
        'icon': 'STICKY_UVS_LOC'
    },
    "builtin.cursor": {
        'text': "Cursor",
        'icon': 'CURSOR'
    },
    "Separator": None,
    "builtin.move": {
        'text': "Move",
        'icon': 'VIEW_PAN'
    },
    "builtin.rotate": {
        'text': "Rotate",
        'icon': 'ORIENTATION_GIMBAL'
    },
    "builtin.scale": {
        'text': "Scale",
        'icon': 'SNAP_FACE_CENTER'
    },
    "builtin.transform": {
        'text': "Transform",
        'icon': 'PIVOT_CURSOR'
    },
}

__context_menu_list = [
    bpy.types.VIEW3D_MT_edit_mesh_context_menu,
    bpy.types.VIEW3D_MT_object_context_menu,
]


def menu_func(self, context):
    layout = self.layout
    layout.label(text="Set Tool")
    for key, content in __toolset_list.items():
        if content:
            layout.operator(
                "WM_OT_tool_set_by_id",
                **content
            ).name = key
        else:
            layout.separator()
    layout.separator()


def register():
    for menu in __context_menu_list:
        menu.prepend(menu_func)


def unregister():
    for menu in __context_menu_list:
        menu.remove(menu_func)


if __name__ == "__main__":
    register()
