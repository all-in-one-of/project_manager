import sys
import hou

scene_path = sys.argv[-2].replace("\\", "/")
hda_paths = sys.argv[-1]
hda_paths = hda_paths.split("|")
print(hda_paths)
hou.hipFile.load(scene_path)
for hda_path in hda_paths:
    hda_name = hda_path[hda_path.find("_lay_")+len("_lay_"):hda_path.rfind("_out.")]
    print(hda_name)
    hou.node("/obj/" + hda_name).allowEditingOfContents()
    switch_node = hou.node("/obj/{0}/layout/switch_between_high-res_and_low-res".format(hda_name))
    rop_high_geo = hou.node("/obj/{0}/layout/save_high_res_geometry".format(hda_name))
    rop_low_geo = hou.node("/obj/{0}/layout/save_low_res_geometry".format(hda_name))
    switch_node.parm("input").set(0)
    rop_high_geo.render()
    switch_node.parm("input").set(1)
    rop_low_geo.render()
