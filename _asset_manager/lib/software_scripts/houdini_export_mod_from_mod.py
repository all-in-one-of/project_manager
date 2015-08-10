import sys
import hou

hda_path = sys.argv[-1].replace("\\", "/")

hou.hda.installFile(hda_path)
hda_name = hda_path[hda_path.find("_mod_")+len("_mod_"):hda_path.rfind("_")]
hou.node("/obj").createNode(hda_name, hda_name)
hou.node("/obj/" + hda_name).allowEditingOfContents()
switch_node = hou.node("/obj/{0}/layout/switch_between_high-res_and_low-res".format(hda_name))
rop_high_geo = hou.node("/obj/{0}/layout/save_high_res_geometry".format(hda_name))
rop_low_geo = hou.node("/obj/{0}/layout/save_low_res_geometry".format(hda_name))
switch_node.parm("input").set(0)
rop_high_geo.render()
switch_node.parm("input").set(1)
rop_low_geo.render()
