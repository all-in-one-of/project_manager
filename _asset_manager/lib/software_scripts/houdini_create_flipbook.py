import sys
import toolutils
print("1")
scene_path = sys.argv[-4].replace("\\", "/")
print("2")
camera_name = sys.argv[-3].replace("-", "_")
print("3")
start_frame = sys.argv[-2]
print("4")
end_frame = sys.argv[-1]
print("5")


hou.hipFile.load(scene_path)
print("6")

hou.node("/out").createNode("TH_OpenGL", "TH_OpenGL")
print("7")
opengl_node = hou.node("/out/TH_OpenGL/opengl")
print("8")
hou.node("/out/TH_OpenGL").allowEditingOfContents()
print("9")
opengl_node.parm("camera").set("/obj/" + camera_name + "/cam")
print("10")
opengl_node.parm("trange").set(1)
print("11")
opengl_node.parm("f1").set(start_frame)
print("12")
opengl_node.parm("f2").set(end_frame)
print("13")
opengl_node.parm("res1").set("1920")
print("14")
opengl_node.parm("res2").set("1080")
print("15")
opengl_node.parm("aamode").set(4)
print("16")

opengl_node.render()
print("17")
