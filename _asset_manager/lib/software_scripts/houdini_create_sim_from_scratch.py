#!/usr/bin/env python
# coding=utf-8

import sys

export_path = sys.argv[-1].replace("\\", "/")

sim_hda = "H:/01-NAD/_pipeline/_utilities/_NEF/sim_hda.hdanc"
definition = hou.hda.definitionsInFile(sim_hda)
definition[0].copyToHDAFile(export_path, "sim", "sim")