import sys
import hou

scene_path = sys.argv[-2].replace("\\", "/")
hda_paths = sys.argv[-1]
hda_paths = hda_paths.split("|")
hou.hipFile.load(scene_path, suppress_save_prompt=True, ignore_load_warnings=True)
for hda_path in hda_paths:
    hda_name = hda_path.replace("\\", "/").split("/")[-1].split("_")[0]
    hou.node("/obj/" + hda_name).allowEditingOfContents()
    switch_node = hou.node("/obj/{0}/layout/switch_between_high-res_and_low-res".format(hda_name))
    rop_high_geo = hou.node("/obj/{0}/layout/save_high_res_geometry".format(hda_name))
    rop_low_geo = hou.node("/obj/{0}/layout/save_low_res_geometry".format(hda_name))
    switch_node.parm("input").set(0)
    rop_high_geo.render()
    switch_node.parm("input").set(1)
    rop_low_geo.render()
