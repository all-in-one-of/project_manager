import sys

obj_path = sys.argv[-1].replace("\\", "/")
print(obj_path)
geo_node = hou.node("/obj").createNode("geo")
geo_node.node("file1").destroy()

hda = geo_node.createNode("normalize_scale", "normalize_scale")
hda.allowEditingOfContents()
hda.node("file").parm("file").set(obj_path)
hda.node("output").render()
print("yeah")