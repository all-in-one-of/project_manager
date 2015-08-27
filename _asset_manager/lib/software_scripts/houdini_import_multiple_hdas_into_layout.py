import sys

hip_file = sys.argv[-2]
hdas_to_import = sys.argv[-1]
hdas_to_import = hdas_to_import.split("|")

hou.hipFile.load(hip_file)
for hda in hdas_to_import:
    hda_name = hda[hda.find("_lay_")+len("_lay_"):hda.rfind("_")]
    hou.hda.installFile(hda)
    hda_node = hou.node("/obj").createNode(hda_name.replace("-", "_"), hda_name.replace("-", "_"))
    hda_node.moveToGoodPosition()
    hda_node.setColor(hou.Color((0, 0.6, 1)))

hou.hipFile.save(hip_file)

