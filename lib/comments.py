#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import time

class CommentWidget(QtGui.QDialog):

    def __init__(self, main, asset):
        super(CommentWidget, self).__init__()

        self.main = main
        self.asset = asset
        self.type = self.asset.__class__.__name__

        if self.type == "Asset":
            self.setWindowTitle("Comments for {0} '{1}'".format(self.type, self.asset.name))
        elif self.type == "Task":
            self.setWindowTitle("Comments for {0} #{1}".format(self.type, self.asset.id))

        self.main.Lib.apply_style(self.main, self)

        self.main_layout = QtGui.QVBoxLayout(self)

        self.commentListWidget = QtGui.QListWidget(self)

        self.commentLineEdit = QtGui.QLineEdit(self)
        self.commentLineEdit.setPlaceholderText("Enter comment here...")

        self.main_layout.addWidget(self.commentListWidget)
        self.main_layout.addWidget(self.commentLineEdit)

        self.commentLineEdit.returnPressed.connect(self.add_comment)

        self.commentLineEdit.setFocus()

        self.load_comments()
        self.exec_()

    def load_comments(self):
        self.comment_authors = []
        self.commentListWidget.clear()
        cur_alignment = "left"

        for i, each_comment in enumerate(self.asset.comments):
            comment_text = each_comment.split("(")[0]
            comment_time = each_comment.split("(")[1]
            item = QtGui.QListWidgetItem(comment_text)
            if i == 0: # If first comment, align it to left
                item.setTextAlignment(QtCore.Qt.AlignLeft)
                comment_author = comment_text.split(":")[0]
                self.comment_authors.append(comment_author)
            else:
                comment_author = comment_text.split(":")[0]
                if comment_author == self.comment_authors[-1]: # Current author is the same as last author
                    if cur_alignment == "left":
                        item.setTextAlignment(QtCore.Qt.AlignLeft)
                    elif cur_alignment == "right":
                        item.setTextAlignment(QtCore.Qt.AlignRight)
                elif comment_author != self.comment_authors[-1]: # Current author is different from last author
                    if cur_alignment == "left": # If current alignment is left, align right and change cur_alignment to opposite
                        item.setTextAlignment(QtCore.Qt.AlignRight)
                        cur_alignment = "right"
                    elif cur_alignment == "right": # If current alignment is right, align left and change cur_alignment to opposite
                        item.setTextAlignment(QtCore.Qt.AlignLeft)
                        cur_alignment = "left"
                self.comment_authors.append(comment_author)

            item.setToolTip(comment_time.replace(")", ""))
            self.commentListWidget.addItem(item)



        # Get all comment authors except me
        self.comment_authors = list(set(self.comment_authors))
        #self.comment_authors = [str(i) for i in self.comment_authors if not self.main.members[self.main.username] in i]

    def add_comment(self):
        comment = unicode(self.commentLineEdit.text())
        comment = self.main.Lib.normalize_str(self.main, comment)
        comment = comment.replace(":", "")
        current_time = time.strftime("%d/%m/%Y at %H:%M")
        comment_with_time = "{0}: {1} ({2})".format(self.main.Lib.normalize_str(self.main, self.main.members[self.main.username]), comment, current_time)
        comment_with_time.replace(";", "")

        if self.type == "Asset":
            self.asset.add_comment([comment_with_time])
            self.main.add_log_entry(text="{0} added a comment on image {1} (seq: {2})".format(self.main.members[self.main.username], self.asset.name, self.asset.sequence), people=self.comment_authors, value=self.asset.id)


        elif self.type == "Task":
            self.asset.add_comment([comment_with_time])
            self.main.add_log_entry(text="{0} added a comment on task #{1}".format(self.main.members[self.main.username], self.asset.id), people=self.comment_authors, value=self.asset.id)

        self.load_comments()
        self.commentLineEdit.clear()

    def delete_comment(self):
        selected_comment = self.commentListWidget.selectedItems()
        try:
            selected_comment_text = str(selected_comment[0].text())
            selected_comment_tooltip = str(selected_comment[0].toolTip())
        except:
            return

        if self.main.members[self.main.username] in selected_comment_text or self.main.username == "thoudon":
            self.asset.remove_comment([selected_comment_text + "(" + selected_comment_tooltip + ")"])
            self.load_comments()

        else:
            self.main.Lib.message_box(self.main, text="You can only delete your own comments")

    def keyPressEvent(self, event):
       key = event.key()
       if key == QtCore.Qt.Key_Delete:
           self.delete_comment()

