#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
from lib.module import Lib
from lib.comments import CommentWidget
import os
import subprocess

class WhatsNew(object):
    def __init__(self):

        self.showOnlyMeWhatsNew.stateChanged.connect(self.load_whats_new)
        self.markAllAsReadBtn.clicked.connect(self.mark_all_as_read)
        self.refreshWhatsNewBtn.clicked.connect(self.load_whats_new)
        self.whatsNewTreeWidget.itemDoubleClicked.connect(self.tree_double_clicked)
        self.load_whats_new()

    def load_whats_new(self):
        self.whatsNewTreeWidget.clear()

        big_font = QtGui.QFont()
        big_font.setPointSize(16)
        small_font = QtGui.QFont()
        small_font.setPointSize(12)

        last_log_id_read = self.cursor.execute('''SELECT last_log_id_read FROM whats_new WHERE member=?''', (self.username,)).fetchone()[0]
        log_entries_length = str(self.cursor.execute('''SELECT max(log_id) FROM log''').fetchone()[0])


        self.log_entries = {}
        log_entries = self.cursor.execute('''SELECT * FROM log WHERE log_id > ? AND log_id <= ?''', (last_log_id_read, log_entries_length)).fetchall()


        if len(log_entries) == 0:
            top_item = QtGui.QTreeWidgetItem(self.whatsNewTreeWidget)
            top_item.setText(0, "There's nothing new :(")
            top_item.setFont(0, big_font)
            self.whatsNewTreeWidget.addTopLevelItem(top_item)
            self.Tabs.setTabText(self.Tabs.count() - 1, "What's New")
            return


        self.Tabs.setTabText(self.Tabs.count() - 1, "What's New (" + str(len(log_entries)) + ")")
        reference_entries = []
        comment_entries = []



        for log_entry in reversed(log_entries):
            log_time = log_entry[1]
            log_text = log_entry[2]
            log_people = log_entry[3]
            if log_people == None: log_people = ""

            if "reference" in log_text:
                if self.showOnlyMeWhatsNew.checkState() == 2:
                    if self.members[self.username] in log_people:
                        reference_entries.append(log_time + " - " + log_text)
                elif self.showOnlyMeWhatsNew.checkState() == 0:
                    reference_entries.append(log_time + " - " + log_text)

            elif "comment" in log_text:
                if self.showOnlyMeWhatsNew.checkState() == 2:
                    if self.members[self.username] in log_people:
                        comment_entries.append(log_time + " - " + log_text)
                elif self.showOnlyMeWhatsNew.checkState() == 0:
                    comment_entries.append(log_time + " - " + log_text)



        self.log_entries["References"] = reference_entries
        self.log_entries["Comments"] = comment_entries

        for top_items, child_items in self.log_entries.items():
            if len(child_items) == 0:
                continue
            top_item = QtGui.QTreeWidgetItem(self.whatsNewTreeWidget)
            top_item.setText(0, top_items + " (" + str(len(child_items)) + ")")
            top_item.setFont(0, big_font)
            self.whatsNewTreeWidget.addTopLevelItem(top_item)
            for child in child_items:
                child_item = QtGui.QTreeWidgetItem(top_item)
                child_item.setText(0, child)
                child_item.setFont(0, small_font)
                top_item.addChild(child_item)

        if self.whatsNewTreeWidget.topLevelItemCount() == 0:
            top_item = QtGui.QTreeWidgetItem(self.whatsNewTreeWidget)
            top_item.setText(0, "There's nothing new :(")
            top_item.setFont(0, big_font)
            self.whatsNewTreeWidget.addTopLevelItem(top_item)

    def mark_all_as_read(self):

        msgbox = QtGui.QMessageBox()
        msgbox.setStandardButtons(QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        msgbox.setDefaultButton(QtGui.QMessageBox.Yes)
        Lib.apply_style(self, msgbox)
        msgbox.setText("Are you sure ?")
        msgbox.setWindowTitle("Mark all as read")
        msgbox.setIcon(QtGui.QMessageBox.Warning)
        button_clicked = msgbox.exec_()
        if button_clicked == 65536:
            return

        log_entries = str(self.cursor.execute('''SELECT max(log_id) FROM log''').fetchone()[0])
        self.cursor.execute('''UPDATE whats_new SET last_log_id_read=? WHERE member=?''', (log_entries, self.username))
        self.db.commit()
        self.load_whats_new()

    def tree_double_clicked(self):

        selected_item = self.whatsNewTreeWidget.selectedItems()[0]
        selected_item_str = str(selected_item.text(0))
        selected_item_time = " - ".join(selected_item_str.split(" - ")[0:2])
        selected_item_description = selected_item_str.split(" - ")[-1]

        clicked_log_entry = self.cursor.execute('''SELECT log_value FROM log WHERE log_time=? AND log_entry=?''', (selected_item_time, selected_item_description,)).fetchone()[0]
        if len(clicked_log_entry) == 0:
            return

        ref_data = clicked_log_entry.split("|")
        try:
            asset_type = ref_data[0]
            asset_name = ref_data[1]
            sequence_name = ref_data[2]
            shot_number = ref_data[3]
            asset_version = ref_data[4]
            asset_path = ref_data[5]
        except:
            return


        if "reference" in selected_item_description:
            if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:
                comment_dialog = CommentWidget(self, 1, asset_type, asset_name, sequence_name, shot_number, asset_version, asset_path)
            else:
                if "video" in selected_item_description:
                    subprocess.Popen(["C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe", asset_path])
                else:
                    if os.path.isfile(self.selected_project_path + asset_path):
                        os.system(self.selected_project_path + asset_path)
                    else:
                        Lib.message_box(self, text="Can't find reference: it must have been deleted.")

        elif "comment" in selected_item_description:
            comment_dialog = CommentWidget(self, 1, asset_type, asset_name, sequence_name, shot_number, asset_version, asset_path)

        return
