# https://blender.stackexchange.com/a/212521/73532
# [python - Finding the 8 outer corner vertices of an object - Blender Stack Exchange](https://blender.stackexchange.com/questions/212513/finding-the-8-outer-corner-vertices-of-an-object/212521#212521)

from bmesh import from_edit_mesh
import bpy


def select4vertTop(k: int = 8) -> None:
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = from_edit_mesh(bpy.context.object.data)
    # Define a helper function that we calculate distance, using Euclidean distance.
    get_distance = lambda v: v.co.x ** 2 + v.co.y ** 2 + v.co.z ** 2
    # We sorted our verts using the helper, reverse flag is set to true.
    verts = sorted(mesh.verts, reverse=True, key=get_distance)
    bpy.ops.mesh.select_all(action='DESELECT')
    # From the first k vertex, set select to True.
    for v in verts[:k]:
        v.select_set(True)


if __name__ == '__main__':
    select4vertTop()
