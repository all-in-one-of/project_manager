import sys

import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc
import maya.mel as mel



def __init__(self):
    self.get_camera()
    self.default_render_format()
    self.playblast()

def get_camera(self):
    camera_animation = mc.listCameras()[0]
    mc.lookThru(camera_animation)

def playblast(self):
    path = "H:\\Image Test\\"
    output_name = "shit"
    mc.playblast(filename= path + output_name, format="image", viewer=False, showOrnaments=False, framePadding=4, )

def default_render_format(self):
    mel.eval("setAttr defaultRenderGlobals.imageFormat 8;")