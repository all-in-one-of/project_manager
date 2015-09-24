print("Yeah")

import sys
import os

max_frame = sys.argv[-3]
file = sys.argv[-2]
shot = sys.argv[-1]


print(max_frame)
print(file)
print(shot)


hou.hipFile.load(file, ignore_load_warnings=True)

out_node = hou.node("out/out_" + shot)
out_node.parm("trange").set("off")

print(out_ifd_node)
print(out_node)

cur_file = out_node.parm("vm_picture").eval()

while os.path.isfile(cur_file):
    hou.setFrame(int(hou.frame()) + 1)
    cur_file = out_node.parm("vm_picture").eval()
    print(cur_file)

print("Rendering file " + str(int(hou.frame())))
hou.setFrame(hou.frame())
if int(hou.frame()) < max_frame:
    print(hou.frame())
    out_node.render()
else:
    print("No more frames to render")

