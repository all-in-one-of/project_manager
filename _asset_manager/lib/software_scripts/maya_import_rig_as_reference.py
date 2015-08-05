#!/usr/bin/env python
# coding=utf-8

import sys
import os

import maya.standalone
maya.standalone.initialize( name='python' )
import maya.cmds as mc


rig_path = sys.argv[-2]
export_path = sys.argv[-1]
namespace_var = os.path.split(rig_path)[1]
namespace_var = os.path.splitext(namespace_var)[0]

mc.file(rig_path, r=True, type="mayaAscii", ignoreVersion=True, gl=True, mergeNamespacesOnClash=False, namespace=namespace_var, options="mo=1;")
mc.file(rename=export_path)
mc.file(save=True, type='mayaAscii', f=True)
