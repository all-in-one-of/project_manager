import sys
import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc

file_path = sys.argv[-2]
export_path = sys.argv[-1]

mc.loadPlugin("objExport")

mc.file(file_path, o=True)

try:
    objects_to_select = mc.editDisplayLayerMembers("output", query=True)
    mc.select(objects_to_select)
except:
    mc.select(all=True)
mc.delete(constructionHistory=True)

mc.file(export_path, force=True, options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1", typ="OBJexport", es=True)

