print("Yeah")

import sys
import os

file = sys.argv[-2]
frame = sys.argv[-1]

print(file)
print(frame)

hou.hipFile.load(file)

out_node = hou.node("out/out")
out_node.parm("trange").set("off")

cur_file = out_node.parm("vm_picture").eval()
print(cur_file)

while os.path.isfile(cur_file):
    hou.setFrame(int(hou.frame()) + 1)
    cur_file = out_node.parm("vm_picture").eval()
    print(cur_file)

print("Rendering file " + str(int(hou.frame())))
hou.setFrame(hou.frame())
print(hou.frame())
out_node.render()

