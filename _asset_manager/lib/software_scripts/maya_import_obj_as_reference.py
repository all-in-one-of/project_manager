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

# Import High Res and Low Res modeling as reference
mc.file(obj_path, r=True, type="OBJ", ignoreVersion=True, gl=True, mergeNamespacesOnClash=False, namespace=namespace_var + "HighRes", options="mo=1;")
mc.setAttr(namespace_var + "HighResRN.proxyTag", "HighRes", type="string")
mc.file(obj_path.replace("_out.obj", "-lowres_out.obj"), r=True, type="OBJ", ignoreVersion=True, gl=True, mergeNamespacesOnClash=False, namespace=namespace_var + "LowRes", options="mo=1;")
mc.setAttr(namespace_var + "LowResRN.proxyTag", "LowRes", type="string")

# Create High resolution display layer
all_objects = mc.ls()
for object in all_objects:
    if "LowRes" in object:
        mc.select(object, add=True)
mc.createDisplayLayer(name="Low Resolution", nr=True)
mc.select(clear=True)

# Create Low resolution display layer
all_objects = mc.ls()
for object in all_objects:
    if "HighRes" in object:
        mc.select(object, add=True)
mc.createDisplayLayer(name="High Resolution", nr=True)
mc.setAttr("Low_Resolution.visibility", False)
mc.setAttr("High_Resolution.visibility", True)

# Save file
mc.file(rename=export_path)
mc.file(save=True, type='mayaAscii', f=True)

