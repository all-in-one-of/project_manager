import hou
import sys

export_path = sys.argv[-5]
layout_path = sys.argv[-4].replace("\\", "/")
camera_name = sys.argv[-3].replace("-", "_")
start_frame = sys.argv[-2]
end_frame = sys.argv[-1]

hou.hipFile.load(layout_path)


obj_context = hou.node("/obj")


out_context = hou.node("/out")

alembic_rop = out_context.createNode("alembic")

alembic_rop.parm("trange").set(1)
alembic_rop.parm("f1").deleteAllKeyframes()
alembic_rop.parm("f2").deleteAllKeyframes()
alembic_rop.parm("f1").set(start_frame)
alembic_rop.parm("f2").set(end_frame)
alembic_rop.parm("format").set(2)


export_cam_node = hou.node("obj/" + camera_name)
export_cam_node.allowEditingOfContents()
export_cam_node.setDisplayFlag(True)

alembic_rop.parm("objects").set(camera_name + "/exportCam")
alembic_rop.parm("filename").set(export_path)

alembic_rop.render()

