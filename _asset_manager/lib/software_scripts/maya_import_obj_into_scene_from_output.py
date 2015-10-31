import sys
import os
import maya.standalone
maya.standalone.initialize( name='python')
import maya.cmds as mc
import maya.mel as mel

file_path = sys.argv[-2]
obj_path = sys.argv[-1]
obj_name = os.path.split(obj_path)[-1]
obj_name = obj_name.replace('.obj', '')

mc.file(file_path, o=True)
mc.file(obj_path, i=True, type="OBJ", ra=True)
mel.eval('searchReplaceNames "' + obj_name + '_" " " "all";')
mc.file(save=True, type='mayaAscii', f=True)