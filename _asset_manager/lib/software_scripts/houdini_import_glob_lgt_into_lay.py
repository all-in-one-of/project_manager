import hou
import sys

hda_export_path = sys.argv[-2].replace("\\", "/")
file_path = sys.argv[-1].replace("\\", "/")

lgt_hda = "H:/01-NAD/_pipeline/_utilities/_NEF/lgt_glob_hda.hdanc"

definition = hou.hda.definitionsInFile(lgt_hda)
definition[0].copyToHDAFile(hda_export_path, "global_lgt", "global_lgt")

hou.hipFile.load(file_path)
hou.hda.installFile(hda_export_path)
lighting_node = hou.node("/obj").createNode("global_lgt", "global_lgt")
lighting_node.setColor(hou.Color((1, 0.8, 0)))
lighting_node.moveToGoodPosition()
hou.hipFile.save()
