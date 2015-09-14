import sys

main_hda_path = sys.argv[-5].replace("\\", "/")
shading_hda_path = sys.argv[-4].replace("\\", "/")
obj_path = sys.argv[-3].replace("\\", "/")
asset_name = sys.argv[-2]
modeling_hda_path = sys.argv[-1].replace("\\", "/")

main_hda = sys.argv[-6].replace("\\", "/") + "/_NEF/main_hda.hdanc"

definition = hou.hda.definitionsInFile(main_hda)
definition[0].copyToHDAFile(main_hda_path, asset_name.replace("-", "_"), asset_name.replace("-", "_"))

hou.hda.installFile(main_hda_path)
asset_node = hou.node("/obj").createNode(asset_name.replace("-", "_"), asset_name.replace("-", "_"))

asset_node.allowEditingOfContents()

modeling_node = asset_node.node("modeling")
modeling_node.extractAndDelete()

modeling_subnet = asset_node.collapseIntoSubnet([asset_node.node("layout"), asset_node.node("center")])
modeling_hda_node = modeling_subnet.createDigitalAsset(asset_name.replace("-", "_") + "_mod", modeling_hda_path, asset_name.replace("-", "_") + "_mod")

modeling_hda_node.allowEditingOfContents()

print("1")
# Set parameters
file_highres_node = modeling_hda_node.node("/layout/high-res_obj_from_modeling")
file_lowres_node = modeling_hda_node.node("/layout/low-res_obj_from_modeling")
rop_geo_high = modeling_hda_node.node("/layout/save_low_res_geometry")
rop_geo_low = modeling_hda_node.node("/layout/save_high_res_geometry")
file_highres_node.parm("file").set(obj_path)
file_lowres_node.parm("file").set(obj_path.replace("_out.obj", "-lowres_out.obj"))
rop_geo_high.parm("sopoutput").set(obj_path.replace("mod", "lay"))
rop_geo_low.parm("sopoutput").set(obj_path.replace("_out.obj", "-lowres_out.obj").replace("mod", "lay"))

print("2")

# MATERIAL NODE
# Shopnet / Copnet
shopnet_node = hou.node("/obj").createNode("shopnet")
shopnet_node.setName("shopnet")
shopnet_node.setColor(hou.Color((0.4, 1, 0.4)))
shopnet_node.moveToGoodPosition()
print("3")

# Create Subnet and HDA for Material Node
material_node = hou.node("/obj").collapseIntoSubnet([shopnet_node])
material_node = material_node.createDigitalAsset(asset_name.replace("-", "_") + "-shd", shading_hda_path, asset_name.replace("-", "_") + "-shd")
material_node.setName("shader_building")
material_node.moveToGoodPosition()

print("5")
asset_node.type().definition().updateFromNode(asset_node)
print("End shading")


