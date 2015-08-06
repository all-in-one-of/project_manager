#!/usr/bin/env python
# coding=utf-8
import sys
import hou

hda_file = sys.argv[-1]
hda_name = sys.argv[-2]
abc_path = sys.argv[-3]

hou.hda.installFile(hda_file)
digital_asset_node = hou.node("/obj").createNode(hda_name)
digital_asset_node.allowEditingOfContents()
alembic_node_path = "/obj/{0}/layout/alembic_from_animation".format(digital_asset_node.name())
alembic_node = hou.node(alembic_node_path)
alembic_node.parm("fileName").set(abc_path)
digital_asset_node.type().definition().updateFromNode(digital_asset_node)