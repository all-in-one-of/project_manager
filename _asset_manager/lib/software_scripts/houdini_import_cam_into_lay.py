import sys
import hou

file_path = sys.argv[-3]
export_path = sys.argv[-2]
shot_number = sys.argv[-1]

lgt_hda = "H:/01-NAD/_pipeline/_utilities/_NEF/cam_hda.hdanc"

definition = hou.hda.definitionsInFile(lgt_hda)
definition[0].copyToHDAFile(export_path, "cam_" + shot_number, "cam_" + shot_number)


hou.hipFile.load(file_path)
hou.hda.installFile(export_path)
camera_node = hou.node("/obj").createNode("cam_" + shot_number, "cam_" + shot_number)
camera_node.setColor(hou.Color((1, 0, 0)))
camera_node.moveToGoodPosition()
hou.hipFile.save()


