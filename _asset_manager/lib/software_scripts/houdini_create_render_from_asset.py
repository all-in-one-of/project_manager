import sys

file_path = sys.argv[-3].replace("\\", "/")
hda_path = sys.argv[-2].replace("\\", "/")
hda_name = sys.argv[-1]
print(file_path)
print(hda_path)
print(hda_name)

hou.hipFile.load(file_path, suppress_save_prompt=True, ignore_load_warnings=True)
print("1")

hou.hda.installFile(hda_path)
print("2")
hda_node = hou.node("/obj").createNode(hda_name, hda_name)
print("3")
hda_node.setDisplayFlag(False)
print("4")


geo_node = hou.node("/obj/geo")
print("5")
object_merge_node = hou.node("/obj/geo/object_merge")
print("6")
object_merge_node.parm("objpath1").set("../../" + hda_name + "/modeling/layout/OUT")
print("7")

mantra_node = hou.node("/out/out_render")

print("8")
key = hou.Keyframe()

for i in range(24):
    key.setFrame(i+1)
    key.setValue(i*15)
    geo_node.parm("ry").setKeyframe(key)


mantra_node.render()
print("3")

mantra_node.parm("vm_picture").set("H:/tmp/turn_hdr.$F4.jpg")
geo_node.parm("ry").deleteAllKeyframes()
geo_node.parm("ry").set(30)

hdr_node = hou.node("/obj/TH_HDR")
key = hou.Keyframe()

for i in range(24):
    key.setFrame(i+1)
    key.setValue(i*15)
    hdr_node.parm("r2y").setKeyframe(key)

mantra_node.render()
