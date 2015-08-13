import sys
import toolutils

scene_path = sys.argv[-2]
camera_name = sys.argv[-1]

hou.ui.paneTabOfType(hou.paneTabType.SceneViewer).curViewport().setCamera(hou.node("/obj/" + camera_name + "/cam"))

desktop = hou.ui.curDesktop()
scene_view = toolutils.sceneViewer()
viewport = scene_view.curViewport()
view = desktop.name() + '.' + scene_view.name() + '.world.' + viewport.name()

hou.hscript('viewwrite -f 1 4 ' + view + ' C:/temp/test.$F4.jpg')



scene_path = "H:/01-NAD/_pipeline/test_project_files/assets/lay/nat_mus_xxxx_lay_musee_01.hipnc"
camera_name = "cam_0010"

hou.hipFile.load(scene_path)

opengl_node = hou.node("/out").createNode("opengl")
opengl_node.parm("camera").set("/obj/" + camera_name + "/cam")
opengl_node.parm("trange").set(1)
opengl_node.parm("f1").set("1")
opengl_node.parm("f2").set("24")
opengl_node.parm("res1").set("1920")
opengl_node.parm("res2").set("1080")
opengl_node.parm("aamode").set(4)
#opengl_node.setExpressionLanguage(hou.exprLanguage.Python)
#setKey = hou.StringKeyframe()
#setKey.setFrame(0)

#opengl_node.parm("picture").setKeyframe(setKey)
#opengl_node.parm("picture").deleteAllKeyframes()
opengl_node.parm("picture").set('C:/Temp/test.$F.jpg')

opengl_node.render()

# Z:\RFRENC~1\Outils\SPCIFI~1\Houdini\HOUDIN~1.13\bin\hython.exe "\\rd-srvhd2\Enseignement\Utilisateurs\thoudon\Home\Desktop\testhoudinihda.py"