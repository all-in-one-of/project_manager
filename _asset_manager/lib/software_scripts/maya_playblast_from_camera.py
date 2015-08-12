import sys

import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc

file_path = sys.argv[-1]
mc.loadPlugin("AbcImport")

camera_animation = mc.listCameras()[0]

mc.file(file_path, o=True)

mc.workspace("C:/Temp", o=True)
mc.setAttr('defaultRenderGlobals.currentRenderer', 'mayaHardware2', type='string')

mc.setAttr("defaultResolution.width", 1920)
mc.setAttr("defaultResolution.height", 1080)

mc.setAttr("hardwareRenderingGlobals.vertexAnimationCache", 2)
mc.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)
mc.setAttr("hardwareRenderingGlobals.ssaoSamples", 16)
mc.setAttr("hardwareRenderingGlobals.lineAAEnable", 1)
mc.setAttr("hardwareRenderingGlobals.imageFormat", 8)
mc.setAttr("hardwareRenderingGlobals.animation", 1)
mc.setAttr("hardwareRenderingGlobals.animationRange", 0)
mc.setAttr("hardwareRenderingGlobals.startFrame", 1)
mc.setAttr("hardwareRenderingGlobals.endFrame", 50)
mc.setAttr(camera_animation + ":cameraProperties.renderable", 1)
mc.setAttr("frontShape.renderable", 0)
mc.setAttr("perspShape.renderable", 0)
mc.setAttr("sideShape.renderable", 0)
mc.setAttr("topShape.renderable", 0)

mc.batchRender()







