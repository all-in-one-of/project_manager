#!/usr/bin/env python
# coding=utf-8
import sys


hip_file = sys.argv[-2]
hdas_to_import = sys.argv[-1]
hdas_to_import = hdas_to_import.split("|")

hou.hipFile.load(hip_file)
for hda in hdas_to_import:
    hou.hda.installFile(hda)
hou.hipFile.save(hip_file)

