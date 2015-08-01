import sys


main_hda_path = sys.argv[-4]
shading_hda_path = sys.argv[-3]
obj_path = sys.argv[-2]
asset_name = sys.argv[-1]

# SOURCE NODE
source_node = hou.node("/obj").createNode("geo")
source_node.setName("layout")
source_node.node("file1").destroy()

# Create inside nodes
file_node = source_node.createNode("file")
material_node = source_node.createNode("material")
transform_node = source_node.createNode("xform")
out_layout_node = source_node.createNode("null")
switch_node = source_node.createNode("switch")
out_node = source_node.createNode("null")

alembic_node = source_node.createNode("alembic")
attribCopy_node = source_node.createNode("attribcopy")

# Rename inside nodes
file_node.setName("obj_from_modeling")
material_node.setName("shader")
transform_node.setName("layout_transform")
out_layout_node.setName("OUT_LAYOUT")
switch_node.setName("switch_between_static_and_anim")
out_node.setName("OUT_ASSET")

alembic_node.setName("alembic_from_animation")
attribCopy_node.setName("copy_shader_to_animation")

# Make connections
material_node.setInput(0, file_node)
transform_node.setInput(0, material_node)
out_layout_node.setInput(0, transform_node)
out_node.setInput(0, switch_node)

attribCopy_node.setInput(0, alembic_node)
attribCopy_node.setInput(1, out_layout_node)

switch_node.setInput(0, attribCopy_node)
switch_node.setInput(1, out_layout_node)

# Set parameters
file_node.parm("file").set(obj_path)
switch_node.parm("input").set(1)

file_node.setColor(hou.Color((1, 1, 0.4)))
alembic_node.setColor(hou.Color((1, 1, 0.4)))
transform_node.setColor(hou.Color((0.4, 1, 0.4)))
switch_node.setColor(hou.Color((0.4, 1, 0.4)))
material_node.setColor(hou.Color((0.4, 1, 0.4)))
attribCopy_node.setColor(hou.Color((0.867, 0, 0)))
out_node.setColor(hou.Color((0, 0, 0)))
out_layout_node.setColor(hou.Color((0, 0, 0)))

out_node.setDisplayFlag(True)
out_node.setRenderFlag(True)

# Layout nodes
source_node.layoutChildren()

# CENTER OF THE WORLD NODE
center_node = hou.node("/obj").createNode("geo")
center_node.setName("center")
center_node.node("file1").destroy()
center_node.moveToGoodPosition()
objectMerge_node = center_node.createNode("object_merge")
objectMerge_node.setName("object_merge")
objectMerge_node.setColor(hou.Color((0.867, 0, 0)))
objectMerge_node.parm("objpath1").set("../../layout/shader")

center_node.setDisplayFlag(False)
center_node.layoutChildren()

# MATERIAL NODE
# Shopnet / Copnet
shopnet_node = hou.node("/obj").createNode("shopnet")
copnet_node = hou.node("/obj").createNode("cop2net")
shopnet_node.setName("shopnet")
copnet_node.setName("copnet")

shopnet_node.setColor(hou.Color((0.4, 1, 0.4)))
copnet_node.setColor(hou.Color((0.4, 1, 0.4)))

shopnet_node.moveToGoodPosition()
copnet_node.moveToGoodPosition()


# Create Subnet and HDA for Material Node
material_node = hou.node("/obj").collapseIntoSubnet([shopnet_node, copnet_node])
material_node = material_node.createDigitalAsset(asset_name + "-shd", shading_hda_path, asset_name + "-shd")
material_node.setName("shader_building")
material_node.moveToGoodPosition()

# Create Subnet and HDA for main node
main_digital_asset = hou.node("/obj").collapseIntoSubnet([source_node, center_node, material_node])
main_digital_asset.setName(asset_name)
main_digital_asset.createDigitalAsset(asset_name, main_hda_path, asset_name)

