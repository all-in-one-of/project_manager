import sys
import os

import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc
import maya.mel as mel

obj_path = sys.argv[-2]
export_path = sys.argv[-1]
namespace_var = os.path.split(obj_path)[1]
namespace_var = os.path.splitext(namespace_var)[0]

mc.file(obj_path, r=True, type="OBJ", ignoreVersion=True, gl=True, mergeNamespacesOnClash=False, namespace=namespace_var, options="mo=1;")
selected_obj = mc.ls(references=True)
mel.eval('proxyAdd "' + selected_obj[0] + '" "' + obj_path.replace("_out.obj", "-lowres_out.obj") + '" "";')
mc.file(rename=export_path)
mc.file(save=True, type='mayaAscii', f=True)

