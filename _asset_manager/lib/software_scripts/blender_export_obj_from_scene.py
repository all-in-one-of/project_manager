import bpy
import sys

file_path = sys.argv[-2].replace("\\", "/")
export_path = sys.argv[-1]

bpy.ops.wm.open_mainfile(filepath=file_path)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.shade_smooth()
try:
    bpy.ops.object.group_link(group="output")
    bpy.ops.object.select_same_group(group="output")
except:
    bpy.ops.object.select_all(action='SELECT')

bpy.ops.export_scene.obj(filepath=export_path, use_selection=True, use_materials=False, use_mesh_modifiers=True, use_vertex_groups=True, use_blen_objects=False, group_by_object=True)
