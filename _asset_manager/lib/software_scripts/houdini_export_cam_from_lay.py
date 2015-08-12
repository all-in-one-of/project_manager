import hou
import sys

export_path = sys.argv[-5]
hda_path = sys.argv[-4]
camera_name = sys.argv[-3].replace("-", "_")
start_frame = sys.argv[-2]
end_frame = sys.argv[-1]

hou.hda.installFile(hda_path)

obj_context = hou.node("/obj")
hda = obj_context.createNode(camera_name, camera_name)
out_context = hou.node("/out")
alembic_rop = out_context.createNode("alembic")
alembic_rop.parm("trange").set(1)
alembic_rop.parm("f1").deleteAllKeyframes()
alembic_rop.parm("f2").deleteAllKeyframes()
alembic_rop.parm("f2").set(start_frame)
alembic_rop.parm("f2").set(end_frame)

alembic_rop.parm("objects").set("/obj/" + camera_name)
alembic_rop.parm("filename").set(export_path)
alembic_rop.render()
