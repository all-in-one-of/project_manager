
import sys
import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc
import maya.mel as mel

file_path = sys.argv[1]
export_path = sys.argv[2]
frame_start = sys.argv[3]
frame_end = sys.argv[4]

mc.loadPlugin("AbcExport")
mc.file(file_path, o=True)

all_objects = mc.ls()
high_res_object_list = []
for object in all_objects:
    if "HighRes" in object:
        high_res_object_list.append(object)

abc_export_string = '-frameRange ' + str(frame_start) + ' ' + str(frame_end) + ' -uvWrite -root |' + high_res_object_list[1] + ' -file ' + export_path
mc.AbcExport(j=abc_export_string)
