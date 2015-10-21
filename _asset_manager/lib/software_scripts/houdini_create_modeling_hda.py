import sys

main_hda_path = sys.argv[-4].replace("\\", "/")
obj_path = sys.argv[-3].replace("\\", "/")
low_res_obj_path = obj_path.replace("_out.obj", "-lowres_out.obj")
asset_name = sys.argv[-2]
asset_name = asset_name.replace("-", "_")

main_hda = sys.argv[-5].replace("\\", "/") + "/_NEF/main_asset.hdanc"

definition = hou.hda.definitionsInFile(main_hda)
definition[0].copyToHDAFile(main_hda_path, asset_name + "_asset", asset_name + "_asset")

hou.hda.installFile(main_hda_path)
main_asset_node = hou.node("/obj").createNode(asset_name + "_asset", asset_name + "_asset")
main_asset_node.allowEditingOfContents()
main_asset_node.node("high-res_obj_from_modeling").parm("file").set(obj_path)
main_asset_node.node("low-res_obj_from_modeling").parm("file").set(low_res_obj_path)

definition = hou.hda.definitionsInFile(main_hda_path)
main_asset_node.type().definition().updateFromNode(main_asset_node)
