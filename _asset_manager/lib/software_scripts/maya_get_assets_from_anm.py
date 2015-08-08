import sys
import os

import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc
import maya.mel as mel

file_path = sys.argv[-1].replace("\\", "/")
mc.file(file_path, o=True)

objects = mc.ls(geometry=True)

for obj in objects:
    if not "_rig_" in obj:
        print(obj.split(":")[0])