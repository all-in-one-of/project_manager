import sys
import hou

hda_path = sys.argv[-1].replace("\\", "/")

hou.hda.installFile(hda_path)
hda_name = hda_path[hda_path.find("_mod_")+len("_mod_"):hda_path.rfind("_")]
hou.node("/obj").createNode(hda_name + "_mod", hda_name + "_mod")
hou.node("/obj/" + hda_name + "_mod").allowEditingOfContents()
rop_high_geo = hou.node("/obj/{0}/Modeling/EXPORT_HIGH_RES".format(hda_name + "_mod"))
rop_low_geo = hou.node("/obj/{0}/Modeling/EXPORT_LOW_RES".format(hda_name + "_mod"))
rop_high_geo.render()
rop_low_geo.render()
