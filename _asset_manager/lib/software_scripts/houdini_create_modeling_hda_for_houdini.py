import sys

main_hda_path = sys.argv[-4]
shading_hda_path = sys.argv[-3]
obj_path = sys.argv[-2].replace("\\", "/")
asset_name = sys.argv[-1]

main_hda = "H:/01-NAD/_pipeline/_utilities/_NEF/main_hda.hdanc"

definition = hou.hda.definitionsInFile(main_hda)
definition[0].copyToHDAFile(main_hda_path, asset_name, asset_name)

hou.hda.installFile(main_hda_path)
asset_node = hou.node("/obj").createNode(asset_name, asset_name)

asset_node.allowEditingOfContents()

# Set parameters
rop_geo_high = hou.node("/obj/" + asset_name + "/layout/save_high_res_geometry")
rop_geo_low = hou.node("/obj/" + asset_name + "/layout/save_low_res_geometry")
rop_geo_high.parm("sopoutput").set(obj_path.replace("lay", "mod"))
rop_geo_low.parm("sopoutput").set(obj_path.replace("_out.obj", "-lowres_out.obj").replace("lay", "mod"))

# Delete nodes
file_highres_node = hou.node("/obj/" + asset_name + "/layout/high-res_obj_from_modeling")
file_lowres_node = hou.node("/obj/" + asset_name + "/layout/low-res_obj_from_modeling")
file_highres_node.destroy()
file_lowres_node.destroy()


# MATERIAL NODE
# Shopnet / Copnet
shopnet_node = hou.node("/obj/" + asset_name).createNode("shopnet")
copnet_node = hou.node("/obj/" + asset_name).createNode("cop2net")
shopnet_node.setName("shopnet")
copnet_node.setName("copnet")

shopnet_node.setColor(hou.Color((0.4, 1, 0.4)))
copnet_node.setColor(hou.Color((0.4, 1, 0.4)))

shopnet_node.moveToGoodPosition()
copnet_node.moveToGoodPosition()

# Create Subnet and HDA for Material Node
material_node = hou.node("/obj/" + asset_name).collapseIntoSubnet([shopnet_node, copnet_node])
material_node = material_node.createDigitalAsset(asset_name + "-shd", shading_hda_path, asset_name + "-shd")
material_node.setName("shader_building")
material_node.moveToGoodPosition()

asset_node.type().definition().updateFromNode(asset_node)



















