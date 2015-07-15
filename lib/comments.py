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

        self.setWindowTitle("Comments for {0} '{1}'".format(self.asset_type, self.asset_name))
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
        self.commentListWidget.clear()
        if asset_type == "ref":
            asset_comments = self.main.cursor.execute('''SELECT asset_comment FROM assets WHERE asset_name=? AND sequence_name=? AND shot_number=? AND asset_version=? AND asset_path=?''', (self.asset_name, self.sequence_name, self.shot_number, self.asset_version, self.asset_path,)).fetchone()[0]
            asset_comments = asset_comments.split(";")
            asset_comments = filter(None, asset_comments)

            if not asset_comments: return

            comment_authors = []
            cur_alignment = "left"

            for i, each_comment in enumerate(asset_comments):
                comment_text = each_comment.split("(")[0]
                comment_time = each_comment.split("(")[1]
                item = QtGui.QListWidgetItem(comment_text)
                if i == 0:
                    item.setTextAlignment(QtCore.Qt.AlignLeft)
                    cur_alignment = "left"
                    comment_author = comment_text.split(":")[0]
                    comment_authors.append(comment_author)
                else:
                    comment_author = comment_text.split(":")[0]
                    if comment_author == comment_authors[-1]: # Current author is the same as last author
                        if cur_alignment == "left":
                            item.setTextAlignment(QtCore.Qt.AlignLeft)
                        elif cur_alignment == "right":
                            item.setTextAlignment(QtCore.Qt.AlignRight)
                    elif comment_author != comment_authors[-1]: # Current author is different from last author
                        if cur_alignment == "left": # If current alignment is left, align right and change cur_alignment to opposite
                            item.setTextAlignment(QtCore.Qt.AlignRight)
                            cur_alignment = "right"
                        elif cur_alignment == "right": # If current alignment is right, align left and change cur_alignment to opposite
                            item.setTextAlignment(QtCore.Qt.AlignLeft)
                            cur_alignment = "left"
                    comment_authors.append(comment_author)

                item.setToolTip(comment_time.replace(")", ""))
                self.commentListWidget.addItem(item)


        elif asset_type == "task":
            pass


    def add_comment(self):
        comment = unicode(self.commentLineEdit.text())
        comment = Lib.normalize_str(self.main, comment)
        current_time = time.strftime("%d/%m/%Y at %H:%M")
        comment_with_time = "{0}: {1} ({2})".format(Lib.normalize_str(self.main, self.main.members[self.main.username]), comment, current_time)

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


        item = QtGui.QListWidgetItem(Lib.normalize_str(self.main, self.main.members[self.main.username]) + ": " + comment)
        item.setToolTip(current_time)
        self.commentListWidget.addItem(item)
        self.commentLineEdit.clear()

    def delete_comment(self):
        selected_comment = self.commentListWidget.selectedItems()
        try:
            selected_comment_text = str(selected_comment[0].text())
            selected_comment_tooltip = str(selected_comment[0].toolTip())
        except:
            return
        if self.main.members[self.main.username] in selected_comment_text:
            # Remove comment from database and reload comments
            comment_from_db = self.main.cursor.execute('''SELECT asset_comment FROM assets WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_path=? AND asset_version=?''', (self.sequence_name, self.shot_number, self.asset_name, self.asset_path, self.asset_version,)).fetchone()
            try:
                comment_from_db = str(comment_from_db[0])
            except:
                return
            if len(comment_from_db) > 0:
                text_to_remove = selected_comment_text + "(" + selected_comment_tooltip + ")"
                new_comments = comment_from_db.replace(text_to_remove, "")
                self.main.cursor.execute('''UPDATE assets SET asset_comment=? WHERE asset_comment=?''', (new_comments, comment_from_db))
                self.main.db.commit()

            self.load_comments(asset_type="ref")

        else:
            Lib.message_box(self.main, text="You can only delete your own comments")



