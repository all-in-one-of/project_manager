import sys
import os

import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc

file_path = sys.argv[-3]
rigs_to_add = sys.argv[-2]
rigs_to_remove = sys.argv[-1]

rigs_to_add = rigs_to_add.split("|")
rigs_to_remove = rigs_to_remove.split("|")

mc.file(file_path, o=True)

for rig_path in rigs_to_add:
    try:
        mc.file(rig_path, r=True, type="mayaAscii", ignoreVersion=True, gl=True, mergeNamespacesOnClash=False, namespace="", options="mo=1;")
    except:
        pass

for rig_path in rigs_to_remove:
    try:
        mc.file(rig_path, removeReference=True)
    except:
        pass

mc.file(save=True, type='mayaAscii', f=True)
