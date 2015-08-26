import bpy
import sys

file_path = sys.argv[-2]
obj_filepath = sys.argv[-1]

bpy.ops.wm.open_mainfile(filepath=file_path)
bpy.ops.import_scene.obj(filepath=obj_filepath, use_split_objects=True, use_split_groups=True)
bpy.ops.wm.save_mainfile()




