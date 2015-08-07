import bpy
import sys

file_path = sys.argv[-2]
export_path = sys.argv[-1]

bpy.ops.wm.open_mainfile(filepath=file_path)






