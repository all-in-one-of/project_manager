import sys

file_path = sys.argv[-1].replace("\\", "/")

hou.hipFile.load(file_path, suppress_save_prompt=True, ignore_load_warnings=True)

render_node = hou.node("/obj/lighting_and_camera_rig/render_settings/pbr")
render_node.render()
