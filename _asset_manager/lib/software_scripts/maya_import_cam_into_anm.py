import sys
import os

import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc
import maya.mel as mel

file_path = sys.argv[-2].replace("\\", "/")
cam_path = sys.argv[-1].replace("\\", "/")



mc.file(file_path, o=True)
mc.loadPlugin("AbcImport")

namespace = cam_path[cam_path.find("_cam_")+len("_cam_"):cam_path.rfind("_out.abc")]
namespace = namespace.replace("-", "_")

all_references = mc.ls(references=True)
for ref in all_references:
    if "cam" in ref:
        ref_path = mc.referenceQuery(ref, filename=True)
        mc.file(ref_path, removeReference=True)



mc.file(cam_path, r=True, type="Alembic", ignoreVersion=True, gl=True, namespace=namespace, mergeNamespacesOnClash=False, options="mo=1;")
mc.file(save=True, type='mayaAscii', f=True)
print("yeah")