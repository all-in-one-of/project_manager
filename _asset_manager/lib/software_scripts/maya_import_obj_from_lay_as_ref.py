print("bssdcsdcsdc")
import sys
import os

import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc
import maya.mel as mel

file_path = sys.argv[-3].replace("\\", "/")
assets_to_remove = sys.argv[-2]
assets_to_add = sys.argv[-1]

assets_to_add = assets_to_add.split("|")
assets_to_remove = assets_to_remove.split("|")
mc.file(file_path, o=True)
if len(assets_to_add[0]) > 0:
    for asset_to_add in assets_to_add:
        asset_to_add = asset_to_add.replace(".hda", ".obj").replace("\\", "/")
        namespace_var = os.path.split(asset_to_add)[1]
        namespace_var = os.path.splitext(namespace_var)[0]
        all_objects = mc.ls(references=True)
        print(namespace_var)
        if any(namespace_var in s for s in all_objects):
            continue

        mc.file(asset_to_add, r=True, type="OBJ", ignoreVersion=True, gl=True, mergeNamespacesOnClash=False, namespace=namespace_var + "HighRes", options="mo=1;")
        proxy_add_string = 'proxyAdd "' + namespace_var + 'HighResRN" "' + asset_to_add.replace("_out.obj", "-lowres_out.obj") + '" "LowRes";'
        mel.eval(proxy_add_string)
if len(assets_to_remove[0]) > 0:
    for asset_to_remove in assets_to_remove:
        try:
            asset_to_remove = asset_to_remove.replace(".hda", ".obj")
            asset_name = asset_to_remove[asset_to_remove.find("_lay_") + len("_lay_"):asset_to_remove.rfind("_out.")]
            mc.file(asset_to_remove, removeReference=True)
            mc.file(asset_to_remove.replace("_out.obj", "-lowres_out.obj"), removeReference=True)
            all_objects = mc.ls()
            for object in all_objects:
                if asset_name in object:
                    mc.delete(object)

        except:
            pass


mc.file(save=True, type='mayaAscii', f=True)
print("success")





