import hou
import sys

hip_file = sys.argv[-2]
hdas_to_import = sys.argv[-1]
hdas_to_import = hdas_to_import.split("|")


hou.hipFile.load(hip_file, suppress_save_prompt=True, ignore_load_warnings=True)
for hda in hdas_to_import:
    print(hda)
    hda_name = hda.replace("\\", "/").split("/")[-1].split("_")[0]
    print("6")
    hou.hda.installFile(hda)
    print("7")
    hda_node = hou.node("/obj").createNode(hda_name.replace("-", "_"), hda_name.replace("-", "_"))
    print("8")
    hda_node.moveToGoodPosition()
    print("9")
    hda_node.setColor(hou.Color((0, 0.6, 1)))
    print("10")

hou.hipFile.save(hip_file)
print("11")

