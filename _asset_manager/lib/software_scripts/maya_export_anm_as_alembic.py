
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
abc_export_string = '-frameRange ' + str(frame_start) + ' ' + str(frame_end) + ' -uvWrite -file ' + export_path
mc.AbcExport(j=abc_export_string)
