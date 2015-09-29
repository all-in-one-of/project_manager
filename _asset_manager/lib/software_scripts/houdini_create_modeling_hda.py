import sys

main_hda_path = sys.argv[-5].replace("\\", "/")
shading_hda_path = sys.argv[-4].replace("\\", "/")
obj_path = sys.argv[-3].replace("\\", "/")
asset_name = sys.argv[-2]
modeling_hda_path = sys.argv[-1].replace("\\", "/")

mod_hda = sys.argv[-6].replace("\\", "/") + "/_NEF/mod_hda.hdanc"
shd_hda = sys.argv[-6].replace("\\", "/") + "/_NEF/shd_hda.hdanc"

# Modeling
definition = hou.hda.definitionsInFile(mod_hda)
definition[0].copyToHDAFile(modeling_hda_path, asset_name.replace("-", "_") + "_mod", asset_name.replace("-", "_") + "_mod")

hou.hda.installFile(modeling_hda_path)
modeling_node = hou.node("/obj").createNode(asset_name.replace("-", "_") + "_mod", "modeling")
modeling_node.moveToGoodPosition()

# Shading
definition = hou.hda.definitionsInFile(shd_hda)
definition[0].copyToHDAFile(shading_hda_path, asset_name.replace("-", "_") + "_shd", asset_name.replace("-", "_") + "_shd")

hou.hda.installFile(shading_hda_path)
shading_node = hou.node("/obj").createNode(asset_name.replace("-", "_") + "_shd", "shading")
shading_node.moveToGoodPosition()

# Subnet
subnet = hou.node("/obj").collapseIntoSubnet([modeling_node, shading_node])
asset_node = subnet.createDigitalAsset(asset_name.replace("-", "_"), main_hda_path, asset_name.replace("-", "_"), ignore_external_references=True)
asset_node.setName(asset_name.replace("-", "_"))

definition = hou.hda.definitionsInFile(main_hda_path)
definition[0].setMaxNumInputs(1)
definition[0].setIcon("Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_asset_manager/media/digital_asset.png")
asset_node.type().definition().updateFromNode(asset_node)



