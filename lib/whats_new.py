#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
from lib.module import Lib


class WhatsNew(object):
    def __init__(self):

        self.showOnlyMeWhatsNew.stateChanged.connect(self.load_whats_new)
        self.markAllAsReadBtn.clicked.connect(self.mark_all_as_read)
        self.refreshWhatsNewBtn.clicked.connect(self.load_whats_new)
        self.load_whats_new()

    def load_whats_new(self):
        self.whatsNewTreeWidget.clear()

        big_font = QtGui.QFont()
        big_font.setPointSize(16)
        small_font = QtGui.QFont()
        small_font.setPointSize(12)

        last_log_id_read = self.cursor.execute('''SELECT last_log_id_read FROM whats_new WHERE member=?''', (self.username,)).fetchone()[0]
        log_entries_length = str(len(self.cursor.execute('''SELECT * FROM log''').fetchall()))

        if last_log_id_read == log_entries_length:
            top_item = QtGui.QTreeWidgetItem(self.whatsNewTreeWidget)
            top_item.setText(0, "There's nothing new :(")
            top_item.setFont(0, big_font)
            self.whatsNewTreeWidget.addTopLevelItem(top_item)
            self.Tabs.setTabText(self.Tabs.count() - 1, "What's New")
            return


        self.log_entries = {}
        log_entries = self.cursor.execute('''SELECT * FROM log WHERE log_id >= ? AND log_id < ?''', (last_log_id_read, log_entries_length)).fetchall()


        self.Tabs.setTabText(self.Tabs.count() - 1, "What's New (" + str(len(log_entries)) + ")")
        reference_entries = []
        comment_entries = []



        for log_entry in log_entries:
            log_time = log_entry[1]
            log_text = log_entry[2]
            log_people = log_entry[3]
            if log_people == None: log_people = ""

            if "reference" in log_text:
                if self.showOnlyMeWhatsNew.checkState() == 2:
                    if self.members[self.username] in log_people:
                        reference_entries.append(log_time + "-" + log_text)
                elif self.showOnlyMeWhatsNew.checkState() == 0:
                    reference_entries.append(log_time + "-" + log_text)

            elif "comment" in log_text:
                if self.showOnlyMeWhatsNew.checkState() == 2:
                    if self.members[self.username] in log_people:
                        comment_entries.append(log_time + "-" + log_text)
                elif self.showOnlyMeWhatsNew.checkState() == 0:
                    comment_entries.append(log_time + "-" + log_text)



        self.log_entries["References"] = reference_entries
        self.log_entries["Comments"] = comment_entries

        for top_items, child_items in self.log_entries.items():
            top_item = QtGui.QTreeWidgetItem(self.whatsNewTreeWidget)
            top_item.setText(0, top_items + " (" + str(len(child_items)) + ")")
            top_item.setFont(0, big_font)
            self.whatsNewTreeWidget.addTopLevelItem(top_item)
            for child in child_items:
                child_item = QtGui.QTreeWidgetItem(top_item)
                child_item.setText(0, child)
                child_item.setFont(0, small_font)
                top_item.addChild(child_item)


    def mark_all_as_read(self):
        log_entries = str(len(self.cursor.execute('''SELECT * FROM log''').fetchall()))
        self.cursor.execute('''UPDATE whats_new SET last_log_id_read=? WHERE member=?''', (log_entries, self.username))
        self.db.commit()
        self.load_whats_new()
