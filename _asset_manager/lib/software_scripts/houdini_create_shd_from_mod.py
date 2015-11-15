import sys

main_asset = sys.argv[-3].replace("\\", "/")
shading_scene_path = sys.argv[-2].replace("\\", "/")
asset_name = sys.argv[-1].replace("\\", "/")

print(main_asset)
print(shading_scene_path)
print(asset_name)

light_rig = "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/_prefs/houdini/houdini14.0/otls/MR_lightingRig.hda"

hou.hda.installFile(main_asset)

hou.node("/obj").createNode(asset_name + "_asset", "asset_" + asset_name)
light_rig = hou.node("/obj").createNode("lighting_test_rig")
light_rig.setName("lighting_and_camera_rig")
light_rig.allowEditingOfContents()
render_node = hou.node("/obj/lighting_and_camera_rig/render_settings/pbr")
render_node.parm("vm_picture").set("Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/shd/.thumb/" + asset_name +"_01_full.jpg")

light_rig.moveToGoodPosition()
print("8")

hou.hipFile.save(file_name=shading_scene_path)

print("baa")
