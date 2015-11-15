import sys

export_path = sys.argv[-2].replace("\\", "/")
asset_name = sys.argv[-1].replace("\\", "/")
sim_scene_path = export_path.replace("_01.hda", "_out.hipnc")

light_rig = "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/_prefs/houdini/houdini14.0/otls/MR_lightingRig.hda"
sim_hda = "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_NEF/sim_hda.hdanc"

definition = hou.hda.definitionsInFile(sim_hda)
definition[0].copyToHDAFile(export_path, asset_name + "_sim", asset_name + "_sim")

hou.hda.installFile(export_path)
hou.node("/obj").createNode(asset_name + "_sim", "sim_" + asset_name)
hou.hipFile.save(file_name=sim_scene_path)