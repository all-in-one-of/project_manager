import sys
import hou

hda_path = sys.argv[-1]
hda_path = hda_path.split("|")

for hda in hda_path:
    hda_name = hda[hda.find("_lay_") + len("_lay_"):hda.rfind("_out.")]
    hou.hda.installFile(hda, hda_name)
    hou.node("/obj").createNode(hda_name, hda_name)
    hou.node("/obj/" + hda_name).allowEditingOfContents()
    switch_node = hou.node("/obj/{0}/layout/switch_between_high-res_and_low-res".format(hda_name))
    switch_node_out = hou.node("/obj/{0}/layout/switch_between_static_and_anim".format(hda_name))
    switch_node.parm("input").set(0)
    switch_node_out.geometry().saveToFile(hda.replace(".hda", ".obj"))
    switch_node.parm("input").set(1)
    switch_node_out.geometry().saveToFile(hda.replace("_out.hda", "-lowres_out.obj"))
