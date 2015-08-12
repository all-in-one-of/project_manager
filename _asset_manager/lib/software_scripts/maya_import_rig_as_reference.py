import sys
import os

import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc

rig_path = sys.argv[-2]
export_path = sys.argv[-1]
namespace_var = os.path.split(rig_path)[1]
namespace_var = os.path.splitext(namespace_var)[0]

mc.file(rig_path, r=True, type="mayaAscii", ignoreVersion=True, gl=True, mergeNamespacesOnClash=False, namespace=namespace_var, options="mo=1;")

mc.workspace("C:/Temp", o=True)
mc.setAttr('defaultRenderGlobals.currentRenderer', 'mayaHardware2', type='string')
mc.setAttr("defaultRenderGlobals.imageFormat", 8)
mc.setAttr("defaultRenderGlobals.outFormatControl", 0)
mc.setAttr("defaultRenderGlobals.animation", 1)
mc.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
mc.setAttr("defaultRenderGlobals.animationRange", 0)
mc.setAttr("defaultRenderGlobals.startFrame", 1)
mc.setAttr("defaultRenderGlobals.endFrame", 50)

mc.setAttr("defaultResolution.width", 1920)
mc.setAttr("defaultResolution.height", 1080)

mc.setAttr("hardwareRenderingGlobals.vertexAnimationCache", 2)
mc.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)
mc.setAttr("hardwareRenderingGlobals.ssaoSamples", 16)
mc.setAttr("hardwareRenderingGlobals.lineAAEnable", 1)

mc.setAttr("frontShape.renderable", 0)
mc.setAttr("perspShape.renderable", 0)
mc.setAttr("sideShape.renderable", 0)
mc.setAttr("topShape.renderable", 0)

mc.file(rename=export_path)
mc.file(save=True, type='mayaAscii', f=True)
