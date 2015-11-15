import sys

asset_name = sys.argv[-4]
new_version_number = sys.argv[-3]
old_version = sys.argv[-2].replace("\\", "/")
new_version = sys.argv[-1].replace("\\", "/")

definition = hou.hda.definitionsInFile(asset_path)
definition[0].copyToHDAFile(old_version, asset_name + "_sim_" + new_version_number, asset_name + "_sim_" + new_version_number)
