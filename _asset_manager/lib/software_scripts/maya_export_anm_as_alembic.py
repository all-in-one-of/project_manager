import sys
import os
import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc
import maya.mel as mel

file_path = sys.argv[1]
export_path = sys.argv[2]
frame_start = int(sys.argv[3])
frame_end = int(sys.argv[4])

mc.loadPlugin("AbcExport")
mc.file(file_path, o=True)

all_objects = mc.ls(transforms=True)
objects_to_export = []
for object in all_objects:
    if "_out:rig" in object:
        if mc.listRelatives(object, parent=True) == None:
            objects_to_export.append(object)

objects_to_export = ["-root " + i for i in objects_to_export]
objects_to_export = " ".join(objects_to_export)

abc_export_string = '-frameRange 1001 1010 -noNormals -uvWrite ' + objects_to_export + ' -file C:/temp/test.abc'
mc.AbcExport(j=abc_export_string)
