import sys

obj_path = sys.argv[-1].replace("\\", "/")

geo_node = hou.node("/obj").createNode("geo")
geo_node.node("file1").destroy()

hou.hda.installFile("Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/_prefs/houdini/houdini14.0/otls/normalize_scale_hda.hdanc")

hda = geo_node.createNode("normalize_scale", "normalize_scale")
hda.allowEditingOfContents()
hda.node("file").parm("file").set(obj_path)
hda.node("output").render()
print("yeah")