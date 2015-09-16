print("yeah")

import sys

main_hda_path = sys.argv[-5].replace("\\", "/")
shading_hda_path = sys.argv[-4].replace("\\", "/")
obj_path = sys.argv[-3].replace("\\", "/")
asset_name = sys.argv[-2]
modeling_hda_path = sys.argv[-1].replace("\\", "/")

main_hda = sys.argv[-6].replace("\\", "/") + "/_NEF/main_hda.hdanc"

print(main_hda)
print(modeling_hda_path)
print(obj_path)
print(shading_hda_path)
print(main_hda_path)
definition = hou.hda.definitionsInFile(main_hda)
definition[0].copyToHDAFile(main_hda_path, asset_name.replace("-", "_"), asset_name.replace("-", "_"))

hou.hda.installFile(main_hda_path)
asset_node = hou.node("/obj").createNode(asset_name.replace("-", "_"), asset_name.replace("-", "_"))
print("11")

asset_node.allowEditingOfContents()

print("22")
modeling_node = asset_node.node("modeling")
modeling_node.extractAndDelete()

print("33")
modeling_subnet = asset_node.collapseIntoSubnet([asset_node.node("layout"), asset_node.node("center")])
print(modeling_subnet)
print(modeling_hda_path)
modeling_subnet.setName("modeling")
modeling_hda_node = modeling_subnet.createDigitalAsset(asset_name.replace("-", "_") + "_mod", modeling_hda_path, asset_name.replace("-", "_") + "_mod", ignore_external_references=True)
print(modeling_hda_node)
modeling_hda_node.setColor(hou.Color((1, 0.8, 0)))

modeling_hda_node.allowEditingOfContents()
print("44")

# Set parameters
file_highres_node = modeling_hda_node.node("layout/high-res_obj_from_modeling")
file_lowres_node = modeling_hda_node.node("layout/low-res_obj_from_modeling")
print(file_highres_node)
print("66")
file_highres_node.parm("file").set(obj_path)
file_lowres_node.parm("file").set(obj_path.replace("_out.obj", "-lowres_out.obj"))
print("77")
# MATERIAL NODE
# Shopnet / Copnet
shopnet_node = asset_node.createNode("shopnet")
shopnet_node.setName("shopnet")
shopnet_node.moveToGoodPosition()
print("88")

# Create Subnet and HDA for Material Node
material_node = asset_node.collapseIntoSubnet([shopnet_node])
material_node = material_node.createDigitalAsset(asset_name.replace("-", "_") + "_shd", shading_hda_path, asset_name.replace("-", "_") + "_shd", ignore_external_references=True)
material_node.setName("shading")
material_node.setColor(hou.Color((0, 0.4, 1)))
material_node.moveToGoodPosition()

print("99")


# LAYOUT NODE
layout_node = asset_node.createNode("geo")
layout_node.node("file1").destroy()
layout_node.setName("layout")
layout_node.moveToGoodPosition()
print("100")

# Create Subnet and HDA for Layout Node
layout_hda_path = main_hda_path.replace("_lay_" + asset_name + "_out", "_lay_" + asset_name + "-lay_out")
layout_hda_node = asset_node.collapseIntoSubnet([layout_node])
layout_hda_node = layout_hda_node.createDigitalAsset(asset_name.replace("-", "_") + "_lay", layout_hda_path, asset_name.replace("-", "_") + "_lay", ignore_external_references=True)
layout_hda_node.setName("layout")
layout_hda_node.moveToGoodPosition()
layout_hda_node.setColor(hou.Color((0.867, 0, 0)))


asset_node.type().definition().updateFromNode(asset_node)
print("End shading")


