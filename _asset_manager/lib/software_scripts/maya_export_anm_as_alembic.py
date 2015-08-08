import sys
import os
import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc
import maya.mel as mel

file_path = sys.argv[1]
export_path = sys.argv[2]
frame_start = sys.argv[3]
frame_end = sys.argv[4]

asset_name_filename = os.path.split(file_path)[1]
asset_name = asset_name_filename.split("_")[4]

mc.loadPlugin("AbcExport")
mc.file(file_path, o=True)

all_objects = mc.ls(geometry=True)
high_res_object_list = []
for object in all_objects:
    if asset_name in object and "HighRes" in object and "rig" in object:
        high_res_object_list.append(object)

mesh_to_export = mc.listRelatives(high_res_object_list[1], parent=True, fullPath=True)
abc_export_string = '-frameRange ' + str(frame_start) + ' ' + str(frame_end) + ' -noNormals -uvWrite -root ' + mesh_to_export[0] + ' -file ' + export_path
mc.AbcExport(j=abc_export_string)
