#!/usr/bin/env python
# coding=utf-8

import sys
import hou

file_path = sys.argv[-3]
export_path = sys.argv[-2]
shot_number = sys.argv[-1]

lgt_hda = "H:/01-NAD/_pipeline/_utilities/_NEF/lgt_hda.hdanc"

definition = hou.hda.definitionsInFile(lgt_hda)
definition[0].copyToHDAFile(export_path, "lgt_" + shot_number, "lgt_" + shot_number)

hou.hipFile.load(file_path)
hou.hda.installFile(export_path)
lighting_node = hou.node("/obj").createNode("lgt_" + shot_number, "lgt_" + shot_number)
lighting_node.setColor(hou.Color((1, 0.8, 0)))
lighting_node.moveToGoodPosition()
hou.hipFile.save()

