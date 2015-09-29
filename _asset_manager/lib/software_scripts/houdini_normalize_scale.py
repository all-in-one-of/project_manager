print("1")
import sys
print("2")

obj_path = sys.argv[-1].replace("\\", "/")
print("3")

geo_node = hou.node("/obj").createNode("geo")
print("4")
geo_node.node("file1").destroy()
print("5")

hou.hda.installFile("Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/_prefs/houdini/houdini14.0/otls/normalize_scale_hda.hdanc")
print("6")

hda = geo_node.createNode("normalize_scale", "normalize_scale")
print("7")
hda.allowEditingOfContents()
print("8")
hda.node("file").parm("file").set(obj_path)
print("9")
hda.node("output").render()
print("10")
