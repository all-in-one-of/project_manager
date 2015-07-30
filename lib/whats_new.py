#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import os
import subprocess



class WhatsNew(object):
    def __init__(self):

        self.log_entries = {}
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

        # Get all log entries based on type
        publishes_log_entries = self.cursor.execute('''SELECT * FROM log WHERE log_type="publish"''').fetchall()
        assets_log_entries = self.cursor.execute('''SELECT * FROM log WHERE log_type="asset"''').fetchall()
        comments_log_entries = self.cursor.execute('''SELECT * FROM log WHERE log_type="comment"''').fetchall()
        tasks_log_entries = self.cursor.execute('''SELECT * FROM log WHERE log_type="task"''').fetchall()
        images_log_entries = self.cursor.execute('''SELECT * FROM log WHERE log_type="image"''').fetchall()

        # Get entries that user did not read
        publishes_log_entries = [entry for entry in publishes_log_entries if self.username in entry[2]]
        assets_log_entries = [entry for entry in assets_log_entries if self.username in entry[2]]
        # If show only news concerning me checkbox is checked, only get comments where I am included
        if self.showOnlyMeWhatsNew.checkState() == 2:
            comments_log_entries = [entry for entry in comments_log_entries if self.username in entry[2]]
        tasks_log_entries = [entry for entry in tasks_log_entries if self.username in entry[2]]
        images_log_entries = [entry for entry in images_log_entries if self.username in entry[2]]

        # Set number of new log entries
        number_of_log_entries = len(publishes_log_entries) + len(assets_log_entries) + len(comments_log_entries) + len(tasks_log_entries) + len(images_log_entries)

        # Set tab text
        self.Tabs.setTabText(self.Tabs.count() - 1, "What's New (" + str(number_of_log_entries) + ")")

        # Create empty lists to store log informations
        publishes_entries = []
        assets_entries = []
        comments_entries = []
        tasks_entries = []
        images_entries = []


        for entry in reversed(publishes_log_entries):
            asset_id = entry[1]
            log_description = entry[4]
            asset = self.Asset(self, asset_id)
            asset.get_infos_from_id()
            publishes_entries.append((log_description, asset))

        for entry in reversed(images_log_entries):
            asset_id = entry[1]
            log_description = entry[4]
            asset = self.Asset(self, asset_id)
            asset.get_infos_from_id()
            images_entries.append((log_description, asset))

        for entry in reversed(comments_log_entries):
            asset_id = entry[1]
            log_description = entry[4]
            asset = self.Asset(self, asset_id)
            asset.get_infos_from_id()
            comments_entries.append((log_description, asset))



        self.log_entries["Publishes"] = publishes_entries
        self.log_entries["Assets"] = assets_entries
        self.log_entries["Comments"] = comments_entries
        self.log_entries["Tasks"] = tasks_entries
        self.log_entries["Images"] = images_entries

        for top_items, child_items in self.log_entries.items():
            if len(child_items) == 0: # There's nothing new in current category
                continue
            top_item = QtGui.QTreeWidgetItem(self.whatsNewTreeWidget)
            top_item.setText(0, top_items + " (" + str(len(child_items)) + ")")
            top_item.setFont(0, big_font)
            self.whatsNewTreeWidget.addTopLevelItem(top_item)
            for child in child_items:
                child_item = QtGui.QTreeWidgetItem(top_item)
                child_item.setText(0, child[0])
                child_item.setFont(0, small_font)
                child_item.setData(0, QtCore.Qt.UserRole, child)
                top_item.addChild(child_item)

        if self.whatsNewTreeWidget.topLevelItemCount() == 0:
            top_item = QtGui.QTreeWidgetItem(self.whatsNewTreeWidget)
            top_item.setText(0, "There's nothing new :(")
            top_item.setFont(0, big_font)
            self.whatsNewTreeWidget.addTopLevelItem(top_item)

    def mark_all_as_read(self):

        confirm_dialog = QtGui.QMessageBox()
        reply = confirm_dialog.question(self, 'Mark all as read', "Are you sure ?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        self.Lib.apply_style(self, confirm_dialog)
        if reply == QtGui.QMessageBox.No:
            return

        log_entries = self.cursor.execute('''SELECT * FROM log''').fetchall()
        for entry in log_entries:
            log_id = entry[0]
            viewed_by = entry[2]
            viewed_by = viewed_by.replace("|{0}|".format(self.username), "")
            self.cursor.execute('''UPDATE log SET viewed_by=? WHERE log_id=?''', (viewed_by, log_id,))

        self.db.commit()
        self.load_whats_new()

    def tree_double_clicked(self):

        selected_item = self.whatsNewTreeWidget.selectedItems()[0]
        selected_item_str = str(selected_item.text(0)).split(" ")[0]
        # Top level object clicked

        if selected_item_str in ("Publishes", "Assets", "Comments", "Tasks", "Images"):
            return

        data = selected_item.data(0, QtCore.Qt.UserRole).toPyObject()
        log_description = data[0]
        self.selected_asset = data[1]

        if "new image" in log_description:
            if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:
                self.CommentsFrame.show()
                self.commentLineEdit.setFocus()
                self.CommentWidget.load_comments(self)
            else:
                if "_VIDEO" in self.selected_asset.tags:
                    subprocess.Popen(["C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe", self.selected_asset.dependency])
                else:
                    if os.path.isfile(self.selected_asset.full_path):
                        os.system(self.selected_asset.full_path)


        elif "new comment" in log_description:
            self.CommentsFrame.show()
            self.commentLineEdit.setFocus()
            self.CommentWidget.load_comments(self)




        return
