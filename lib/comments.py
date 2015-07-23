#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import time
from functools import partial

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

        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)

        self.main.Lib.apply_style(self.main, self)

        self.main_layout = QtGui.QVBoxLayout(self)

        self.comment_text_edit_dic = {}

        self.commentLineEdit = QtGui.QLineEdit(self)
        self.commentLineEdit.setPlaceholderText("Enter comment here...")

        self.scrollarea = QtGui.QScrollArea(self)
        self.scrollarea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 380, 280))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.scrollAreaWidgetContents)
        self.gridLayout = QtGui.QGridLayout()
        self.horizontalLayout_2.addLayout(self.gridLayout)
        self.scrollarea.setWidget(self.scrollAreaWidgetContents)

        self.main_layout.addWidget(self.commentLineEdit)
        self.main_layout.addWidget(self.scrollarea)

        self.commentLineEdit.returnPressed.connect(self.add_comment)

        self.commentLineEdit.setFocus()

        self.load_comments()
        self.exec_()

    def load_comments(self):
        self.comment_authors = []
        self.cur_alignment = "left"

        while self.gridLayout.count():
            item = self.gridLayout.takeAt(0)
            item.widget().deleteLater()

        for i, each_comment in enumerate(reversed(self.asset.comments)):
            comment_text_and_author = each_comment.split(":")[0]
            comment_text = each_comment.split("(")[0].split(":")[1]
            comment_text = comment_text.lstrip()
            comment_time = each_comment.split("(")[1]

            if i == 0:  # If first comment, align it to left
                comment_author = comment_text_and_author.split(":")[0]
                self.create_comment_frame(comment_author, comment_text, comment_time)
            else:
                comment_author = comment_text_and_author.split(":")[0]
                if comment_author == self.comment_authors[-1]:  # Current author is the same as last author
                    if self.cur_alignment == "left":
                        self.create_comment_frame(comment_author, comment_text, comment_time)
                    elif self.cur_alignment == "right":
                        self.create_comment_frame(comment_author, comment_text, comment_time)
                elif comment_author != self.comment_authors[-1]:  # Current author is different from last author
                    if self.cur_alignment == "left":  # If current alignment is left, align right and change self.cur_alignment to opposite
                        self.cur_alignment = "right"
                        self.create_comment_frame(comment_author, comment_text, comment_time)
                    elif self.cur_alignment == "right":  # If current alignment is right, align left and change self.cur_alignment to opposite
                        self.cur_alignment = "left"
                        self.create_comment_frame(comment_author, comment_text, comment_time)

            self.comment_authors.append(comment_author)

        try:
            self.scrollarea.setMinimumHeight(self.comment_frame.sizeHint().width())
            self.scrollarea.setMinimumWidth(self.comment_frame.sizeHint().width())
        except:
            self.scrollarea.setMinimumHeight(300)
            self.scrollarea.setMinimumWidth(300)

        # Get all comment authors except me
        self.comment_authors = list(set(self.comment_authors))
        #self.comment_authors = [str(i) for i in self.comment_authors if not self.main.members[self.main.username] in i]

    def create_comment_frame(self, comment_author, comment_text, comment_time):

        comment_author_shortname = [shortname for shortname, longname in self.main.members.items() if comment_author == longname]
        comment_author_shortname = comment_author_shortname[0]

        self.comment_frame = QtGui.QFrame(self.scrollarea)
        self.comment_frame.setMaximumHeight(80)
        comment_frame_layout = QtGui.QHBoxLayout(self.comment_frame)
        comment_frame_layout.setMargin(0)
        comment_frame_layout.setSpacing(1)

        author_picture_lbl = QtGui.QLabel(self.comment_frame)
        author_picture_pixmap = QtGui.QPixmap("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\members_photos\\" + comment_author_shortname + ".jpg")
        author_picture_pixmap = author_picture_pixmap.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        author_picture_lbl.setPixmap(author_picture_pixmap)

        comment_text_edit = QtGui.QTextEdit(self.comment_frame)
        comment_text_edit.setReadOnly(True)
        if comment_author_shortname == self.main.username:
            edit_frame = QtGui.QFrame(self.comment_frame)
            edit_frame_layout = QtGui.QVBoxLayout(edit_frame)
            update_button = QtGui.QPushButton("edit", edit_frame)
            update_button.setMaximumSize(24, 24)
            update_button.clicked.connect(partial(self.edit_comment, comment_text_edit, comment_author, comment_text, comment_time))
            update_button.setAutoDefault(False)
            update_button.setDefault(False)
            update_button.autoDefault()
            delete_button = QtGui.QPushButton("x", edit_frame)
            delete_button.setMaximumSize(24, 24)
            delete_button.clicked.connect(partial(self.delete_comment, comment_author, comment_text, comment_time))
            delete_button.setAutoDefault(False)
            delete_button.setDefault(False)
            edit_frame_layout.addWidget(update_button)
            edit_frame_layout.addWidget(delete_button)


        comment_text_edit.setText(comment_text)
        comment_text_edit.setToolTip(comment_time.replace(")", ""))
        #self.comment_text_edit_dic[comment_text_edit] = comment_author + ": " + comment_text + "(" + comment_time


        if self.cur_alignment == "left":
            comment_frame_layout.addWidget(author_picture_lbl)
            comment_frame_layout.addWidget(comment_text_edit)
            if comment_author_shortname == self.main.username: comment_frame_layout.addWidget(edit_frame)
        elif self.cur_alignment == "right":
            if comment_author_shortname == self.main.username: comment_frame_layout.addWidget(edit_frame)
            comment_frame_layout.addWidget(comment_text_edit)
            comment_frame_layout.addWidget(author_picture_lbl)

        self.gridLayout.addWidget(self.comment_frame)

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

    def delete_comment(self, comment_author, comment_text, comment_time):
        self.asset.remove_comment([comment_author + ": " + comment_text + "(" + comment_time])
        self.load_comments()

    def edit_comment(self, comment_text_edit, comment_author, comment_text, comment_time):
        old_comment = comment_author + ": " + comment_text + "(" + comment_time


        edit_comment_dialog = QtGui.QDialog()
        edit_comment_dialog.setWindowTitle("Edit comment")
        self.main.Lib.apply_style(self.main, edit_comment_dialog)
        edit_comment_layout = QtGui.QVBoxLayout(edit_comment_dialog)
        edit_comment_textbox = QtGui.QTextEdit(comment_text)
        edit_comment_textbox.selectAll()

        edit_comment_acceptBtn = QtGui.QPushButton("Edit")
        edit_comment_acceptBtn.clicked.connect(edit_comment_dialog.accept)

        edit_comment_layout.addWidget(edit_comment_textbox)
        edit_comment_layout.addWidget(edit_comment_acceptBtn)
        edit_comment_dialog.exec_()

        if edit_comment_dialog.result == 0:
            return

        new_comment = comment_author + ": " + edit_comment_textbox.toPlainText() + " (" + comment_time
        self.asset.edit_comment(old_comment, new_comment)
        self.load_comments()
