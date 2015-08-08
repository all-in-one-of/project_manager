import sys
import hou

file_path = sys.argv[-3]
export_path = sys.argv[-2]
shot_number = sys.argv[-1]

camera_node = hou.node("/obj").createNode("cam")
camera_node.setName("cam-" + shot_number)
camera_subnet = hou.node("/obj").collapseIntoSubnet([camera_node])
camera_subnet.setName("cam-" + shot_number)
camera_hda = camera_subnet.createDigitalAsset("cam-" + shot_number, export_path, "cam-" + shot_number)


hou.hipFile.load(file_path)
hou.hda.installFile(export_path)
camera_node = hou.node("/obj").createNode("cam-" + shot_number, "cam-" + shot_number)
camera_node.setColor(hou.Color((0.7, 0.7, 0.7)))
camera_node.moveToGoodPosition()
hou.hipFile.save()


