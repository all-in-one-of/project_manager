#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
from lib.module import Lib


class WhatsNew(object):
    def __init__(self):

        big_font = QtGui.QFont()
        big_font.setPointSize(16)

        small_font = QtGui.QFont()
        small_font.setPointSize(12)

        reference_top_item = QtGui.QTreeWidgetItem(self.whatsNewTreeWidget)
        reference_top_item.setText(0, "References")
        reference_top_item.setFont(0, big_font)
        self.whatsNewTreeWidget.addTopLevelItem(reference_top_item)

        log_entries = self.cursor.execute('''SELECT * FROM log''').fetchall()

        for log_entry in log_entries:
            if "reference" in log_entry[2]:
                reference_item = QtGui.QTreeWidgetItem(self.whatsNewTreeWidget)
                reference_item.setText(0, log_entry[2])
                reference_item.setFont(0, small_font)
                reference_top_item.addChild(reference_item)




    def mark_all_as_read(self):
        pass
