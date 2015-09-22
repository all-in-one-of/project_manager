import sys

file_path = sys.argv[-3].replace("\\", "/")
hda_path = sys.argv[-2].replace("\\", "/")
hda_name = sys.argv[-1]

hou.hipFile.load(file_path, suppress_save_prompt=True, ignore_load_warnings=True)

hou.hda.installFile(hda_path)
hda_node = hou.node("/obj").createNode(hda_name, hda_name)
hda_node.setDisplayFlag(False)

out_before_pack_node = hda_node.node("modeling/layout/OUT_BEFORE_PACK")
out_before_pack_node_geo = out_before_pack_node.geometry()
attribs = out_before_pack_node_geo.primAttribs()

attrib_name_list = []
for attrib in attribs:
    attrib_name_list.append(attrib.name())

if "shop_materialpath" in attrib_name_list:
    geo_node = hou.node("/obj/geo")
    object_merge_node = hou.node("/obj/geo/object_merge")
    object_merge_node.parm("objpath1").set("../../" + hda_name + "/modeling/layout/OUT")

    mantra_node = hou.node("/out/out_render")

    key = hou.Keyframe()

    for i in range(24):
        key.setFrame(i+1)
        key.setValue(i*15)
        geo_node.parm("ry").setKeyframe(key)

    mantra_node.render()

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
