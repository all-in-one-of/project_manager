import sys
import hou
print("1")

file_path = sys.argv[-3]
export_path = sys.argv[-2]
shot_number = sys.argv[-1]
print(file_path)
print(export_path)
print(shot_number)

cam_hda = "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_NEF/cam_hda.hdanc"
print("3")

definition = hou.hda.definitionsInFile(cam_hda)
definition[0].copyToHDAFile(export_path, "cam_" + shot_number, "cam_" + shot_number)

print("4")

hou.hipFile.load(file_path, suppress_save_prompt=True, ignore_load_warnings=True)
print("5")
hou.hda.installFile(export_path)
print("6")
camera_node = hou.node("/obj").createNode("cam_" + shot_number, "cam_" + shot_number)
print("7")
camera_node.setColor(hou.Color((1, 0, 0)))
print("8")
camera_node.moveToGoodPosition()
print("9")
hou.hipFile.save()
print("10")


