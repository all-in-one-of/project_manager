#!/usr/bin/env python
# coding=utf-8

import sys
import hou

file_path = sys.argv[-3]
export_path = sys.argv[-2]
shot_number = sys.argv[-1]

lighting_subnet = hou.node("/obj").createNode("subnet")
lighting_subnet.setName("lgt-" + shot_number)
lighting_hda = lighting_subnet.createDigitalAsset("lgt-" + shot_number, export_path, "lgt-" + shot_number)

hou.hipFile.load(file_path)
hou.hda.installFile(export_path)
lighting_node = hou.node("/obj").createNode("lgt-" + shot_number, "lgt-" + shot_number)
lighting_node.setColor(hou.Color((1, 0.8, 0)))
lighting_node.moveToGoodPosition()
hou.hipFile.save()

