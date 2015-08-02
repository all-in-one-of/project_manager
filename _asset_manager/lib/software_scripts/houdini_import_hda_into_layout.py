#!/usr/bin/env python
# coding=utf-8
import sys

hip_file = sys.argv[-2]
hda_to_import = sys.argv[-1]

hou.hipFile.load(hip_file)
hou.hda.installFile(hda_to_import)
hou.hipFile.save(hip_file)

