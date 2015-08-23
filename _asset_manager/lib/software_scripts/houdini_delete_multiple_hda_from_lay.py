import sys

hip_file = sys.argv[-2]
hdas_to_remove = sys.argv[-1]
hdas_to_remove = hdas_to_remove.split("|")

hou.hipFile.load(hip_file)
for hda in hdas_to_remove:
    hda = hda.replace("\\", "/")
    hda_name = hda[hda.find("_lay_")+len("_lay_"):hda.rfind("_")]
    hda_node = hou.node("/obj/" + hda_name)
    hda_node.destroy()
    hou.hda.uninstallFile(hda)
    hou.hda.uninstallFile("Embedded")


hou.hipFile.save(hip_file)
