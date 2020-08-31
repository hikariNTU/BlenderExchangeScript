# Causing crash.
import bpy
from bpy.app.handlers import persistent
import os

dealing_files = iter([
    R'D:\\hello\a.blend',
    R'D:\\hello\b.blend',
    R'D:\\hello\c.blend',
])
# Or
dir_path = R'T:\\blend_test\\'
dealing_files = iter(map(lambda x: os.path.join(dir_path,x), os.listdir(dir_path)))

def load_next():
    nextfile = next(dealing_files, None)
    if nextfile is not None:
        # r = input(nextfile)
        bpy.ops.wm.open_mainfile(filepath=nextfile)
    else:
        raise StopIteration
        # bpy.app.handlers.load_post.remove(load_handler)
        # print("done")
__IDX = 0
# This handler will excute after loading a new blend file.
@persistent
def load_handler(dummy):
    global __IDX
    __IDX += 1
    print("Current Files:", bpy.data.filepath)
    ...
    # Do Your Stuff here:
    bpy.ops.wm.save_as_mainfile(filepath=f"T://blend_save/{__IDX}.blend")
    ...
    # This will load next files
    load_next()


bpy.app.handlers.load_post.append(load_handler)

# Start loading the file
load_next()