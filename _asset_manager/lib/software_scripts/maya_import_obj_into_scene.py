import sys
import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc

file_path = sys.argv[-2]
obj_path = sys.argv[-1]

mc.file(file_path, o=True)
mc.file(obj_path, i=True, type="OBJ", ra=True)
mc.file(save=True, type='mayaAscii', f=True)