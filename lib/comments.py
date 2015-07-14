#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
from lib.module import Lib
import time

class CommentWidget(QtGui.QDialog):

    def __init__(self, main, task_id=1, asset_type="ref", asset_name="", sequence_name="", shot_number="", asset_version="", asset_path=""):
        super(CommentWidget, self).__init__()

        self.main = main

        self.asset_id = task_id
        self.asset_type = asset_type
        self.asset_name = asset_name
        self.sequence_name = sequence_name
        self.shot_number = shot_number
        self.asset_version = asset_version
        self.asset_path = asset_path

        self.setWindowTitle("Comments for {0} {1}".format(self.asset_type, self.asset_name))
        Lib.apply_style(self.main, self)

        self.main_layout = QtGui.QVBoxLayout(self)

        self.commentListWidget = QtGui.QListWidget(self)


        self.commentLineEdit = QtGui.QLineEdit(self)
        self.commentLineEdit.setPlaceholderText("Enter comment here...")

        self.deleteCommentBtn = QtGui.QPushButton("Delete comment", self)

        self.main_layout.addWidget(self.commentListWidget)
        self.main_layout.addWidget(self.commentLineEdit)
        self.main_layout.addWidget(self.deleteCommentBtn)

        self.commentLineEdit.returnPressed.connect(self.add_comment)
        self.deleteCommentBtn.clicked.connect(self.delete_comment)

        self.commentLineEdit.setFocus()


        self.load_comments(self.asset_type)
        self.exec_()

    def load_comments(self, asset_type):
        if asset_type == "ref":
            asset_comments = self.main.cursor.execute('''SELECT asset_comment FROM assets WHERE asset_name=? AND sequence_name=? AND shot_number=? AND asset_version=? AND asset_path=?''', (self.asset_name, self.sequence_name, self.shot_number, self.asset_version, self.asset_path,)).fetchone()[0]
            asset_comments = asset_comments.split(";")

            if len(asset_comments[0]) == 0:
                return

            for each_comment in asset_comments:
                comment_text = each_comment.split("(")[0]
                comment_time = each_comment.split("(")[1]
                item = QtGui.QListWidgetItem(comment_text)
                item.setToolTip(comment_time)
                self.commentListWidget.addItem(item)


        elif asset_type == "task":
            pass


    def add_comment(self):
        comment = str(self.commentLineEdit.text())
        current_time = time.strftime("%d/%m/%Y at %H:%M")
        comment_with_time = "{0}: {1} ({2})".format(self.main.members[self.main.username], comment, current_time)

        if self.asset_type == "ref":
            asset_comment = self.main.cursor.execute('''SELECT asset_comment FROM assets WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_path=? AND asset_version=?''', (self.sequence_name, self.shot_number, self.asset_name, self.asset_path, self.asset_version,)).fetchone()

            if asset_comment[0] == None or asset_comment[0] == "":
                asset_comment = comment_with_time
            else:
                asset_comment = asset_comment[0]
                asset_comment += ";" + comment_with_time
            self.main.cursor.execute('''UPDATE assets SET asset_comment=? WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_path=? AND asset_version=?''', (asset_comment, self.sequence_name, self.shot_number, self.asset_name, self.asset_path, self.asset_version,))
            self.main.db.commit()
        elif self.asset_type == "task":
            pass


        item = QtGui.QListWidgetItem(self.main.members[self.main.username] + ": " + comment)
        item.setToolTip(current_time)
        self.commentListWidget.addItem(item)

    def delete_comment(self):
        selected_comment = self.commentListWidget.selectedItems()

        try:
            selected_comment_text = str(selected_comment[0].text())
        except:
            return

        if self.main.members[self.main.username] in selected_comment_text:
            pass
            # Remove comment from database and reload comments
            #self.commentListWidget.removeItemWidget(selected_comment[0])


