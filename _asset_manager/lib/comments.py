#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import time
from functools import partial
from datetime import datetime
import os
import shutil
import webbrowser
import subprocess

class CommentWidget(object):

    def __init__(self):
        self.comment_text_edit_dic = {}
        self.comments_gridLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.commentLineEdit.returnPressed.connect(self.add_comment)

    def load_comments(self):
        current_tab_text = self.Tabs.tabText(self.Tabs.currentIndex())

        if current_tab_text == "Images Manager":
            comments = self.cursor.execute('''SELECT * FROM comments WHERE asset_id=? AND comment_type="ref"''', (self.selected_asset.id,)).fetchall()
        elif current_tab_text in ["Task Manager", "Tasks"]:
            comments = self.cursor.execute('''SELECT * FROM comments WHERE asset_id=? AND comment_type="task"''', (self.selected_asset.id,)).fetchall()
            self.commentsForAssetLbl.setText("Comments for task #{0}".format(self.selected_asset.id, ))
        elif current_tab_text == "Asset Loader":
            comments = self.cursor.execute('''SELECT * FROM comments WHERE asset_id=? AND comment_type="asset"''', (self.selected_asset.id,)).fetchall()
            self.commentsForAssetLbl.setText("Comments for asset: {0} ({1})".format(self.selected_asset.name, self.selected_asset.type))
        elif "What's New" in current_tab_text:
            comments = self.cursor.execute('''SELECT * FROM comments WHERE asset_id=?''', (self.selected_asset.id,)).fetchall()

        self.comment_authors = []
        self.cur_alignment = "left"

        while self.comments_gridLayout.count():
            item = self.comments_gridLayout.takeAt(0)
            item.widget().deleteLater()

        if len(comments) == 0:
            self.create_comment_frame("default", "There's no comments", "", "", "")

        for i, comment in enumerate(reversed(comments)):
            comment_id = comment[0]
            asset_id = comment[1]
            comment_author = comment[2]
            comment_text = comment[3]
            comment_time = comment[4]

            if i == 0:  # If first comment, align it to left
                self.create_comment_frame(comment_author, comment_text, comment_time, asset_id, comment_id)
            else:
                if comment_author == self.comment_authors[-1]:  # Current author is the same as last author
                    if self.cur_alignment == "left":
                        self.create_comment_frame(comment_author, comment_text, comment_time, asset_id, comment_id)
                    elif self.cur_alignment == "right":
                        self.create_comment_frame(comment_author, comment_text, comment_time, asset_id, comment_id)
                elif comment_author != self.comment_authors[-1]:  # Current author is different from last author
                    if self.cur_alignment == "left":  # If current alignment is left, align right and change self.cur_alignment to opposite
                        self.cur_alignment = "right"
                        self.create_comment_frame(comment_author, comment_text, comment_time, asset_id, comment_id)
                    elif self.cur_alignment == "right":  # If current alignment is right, align left and change self.cur_alignment to opposite
                        self.cur_alignment = "left"
                        self.create_comment_frame(comment_author, comment_text, comment_time, asset_id, comment_id)

            self.comment_authors.append(comment_author)

        try:
            self.commentsScrollArea.setMinimumHeight(self.comment_frame.sizeHint().width())
            self.commentsScrollArea.setMinimumWidth(self.comment_frame.sizeHint().width())
        except:
            self.commentsScrollArea.setMinimumHeight(300)
            self.commentsScrollArea.setMinimumWidth(300)

        # Get all comment authors except me
        self.comment_authors = list(set(self.comment_authors))

    def create_comment_frame(self, comment_author, comment_text, comment_time, asset_id, comment_id):

        self.comment_frame = QtGui.QFrame(self.commentsScrollArea)
        self.comment_frame.setMaximumHeight(80)
        comment_frame_layout = QtGui.QHBoxLayout(self.comment_frame)
        comment_frame_layout.setContentsMargins(0, 0, 0, 0)
        comment_frame_layout.setSpacing(0)

        author_picture_lbl = QtGui.QLabel(self.comment_frame)
        author_picture_pixmap = QtGui.QPixmap(self.cur_path + "\\media\\members_photos\\" + comment_author + ".jpg")
        author_picture_pixmap = author_picture_pixmap.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        author_picture_lbl.setPixmap(author_picture_pixmap)
        if comment_author != "default":
            author_picture_lbl.setToolTip(self.members[comment_author])

        comment_text_edit = QtGui.QTextEdit(self.comment_frame)
        comment_text_edit.setReadOnly(True)
        if comment_author == self.username:
            edit_frame = QtGui.QFrame(self.comment_frame)
            edit_frame_layout = QtGui.QVBoxLayout(edit_frame)
            edit_frame_layout.setContentsMargins(2, 0, 0, 0)
            edit_frame_layout.setSpacing(0)
            add_img_button = QtGui.QPushButton(edit_frame)
            comment_image = self.cursor.execute('''SELECT comment_image FROM comments WHERE comment_id=?''', (comment_id,)).fetchone()[0]
            if len(comment_image) < 1:
                add_img_button.setIcon(QtGui.QIcon(self.cur_path + "\\media\\custom_media_icon_disabled.png"))
                add_img_button.clicked.connect(partial(self.add_img_to_comment, comment_id))
            else:
                add_img_button.setIcon(QtGui.QIcon(self.cur_path + "\\media\\custom_media_icon.png"))
                add_img_button.clicked.connect(partial(self.show_comment_img, comment_id))
            add_img_button.setIconSize(QtCore.QSize(24, 24))
            add_img_button.setMaximumSize(24, 24)
            add_img_button.setToolTip("Use Ctrl to delete or Alt to replace image. Use shift to open image in Windows Explorer")
            update_button = QtGui.QPushButton(edit_frame)
            update_button.setIcon(QtGui.QIcon(self.cur_path + "\\media\\add_task_to_asset.png"))
            update_button.setIconSize(QtCore.QSize(24, 24))
            update_button.setMaximumSize(24, 24)
            update_button.clicked.connect(partial(self.edit_comment, comment_text_edit, comment_author, comment_text, comment_time))
            update_button.setAutoDefault(False)
            update_button.setDefault(False)
            update_button.autoDefault()
            delete_button = QtGui.QPushButton(edit_frame)
            delete_button.setIcon(QtGui.QIcon(self.cur_path + "\\media\\delete_asset.png"))
            delete_button.setIconSize(QtCore.QSize(18, 18))
            delete_button.setMaximumSize(24, 24)
            delete_button.clicked.connect(partial(self.delete_comment, comment_author, comment_text, comment_time))
            delete_button.setAutoDefault(False)
            delete_button.setDefault(False)
            edit_frame_layout.addWidget(add_img_button)
            edit_frame_layout.addWidget(update_button)
            edit_frame_layout.addWidget(delete_button)


        comment_text_edit.setText(comment_text)
        comment_text_edit.setToolTip(comment_time.replace(")", ""))
        #self.comment_text_edit_dic[comment_text_edit] = comment_author + ": " + comment_text + "(" + comment_time

        if self.cur_alignment == "left":
            comment_frame_layout.addWidget(author_picture_lbl)
            comment_frame_layout.addWidget(comment_text_edit)
            if comment_author == self.username: comment_frame_layout.addWidget(edit_frame)
        elif self.cur_alignment == "right":
            if comment_author == self.username: comment_frame_layout.addWidget(edit_frame)
            comment_frame_layout.addWidget(comment_text_edit)
            comment_frame_layout.addWidget(author_picture_lbl)

        self.comments_gridLayout.addWidget(self.comment_frame)

    def add_comment(self):
        current_tab_text = self.Tabs.tabText(self.Tabs.currentIndex())

        comment = self.commentLineEdit.text()
        comment = unicode(self.utf8_codec.fromUnicode(comment), 'utf-8')
        current_time = time.strftime("%d/%m/%Y at %H:%M")

        if current_tab_text == "Images Manager":
            self.selected_asset.add_comment(self.username, comment, current_time, "ref")
            self.add_comment_log_entry(self.selected_asset, "image")

        elif current_tab_text == "Task Manager" or current_tab_text == "Tasks":
            self.selected_asset.add_comment(self.username, comment, current_time, "task")
            self.add_comment_log_entry(self.selected_asset, "task")

        elif current_tab_text == "Asset Loader":
            self.selected_asset.add_comment(self.username, comment, current_time, "asset")
            self.add_comment_log_entry(self.selected_asset, "asset")

        elif "What's New" in current_tab_text:
            if self.selected_asset.type == "ref":
                self.selected_asset.add_comment(self.username, comment, current_time, "ref")
                self.add_comment_log_entry(self.selected_asset, "image")

            else:
                self.selected_asset.add_comment(self.username, comment, current_time, "asset")
                self.add_comment_log_entry(self.selected_asset, "asset")

        self.load_comments()
        self.commentLineEdit.clear()

    def add_comment_log_entry(self, asset, type):
        # Add Log Entry
        log_entry = self.LogEntry(self, 0, asset.id, [], [], self.username, "", "comment", "{0} added a new comment on {1} {2}.".format(self.members[self.username], type, asset.id), datetime.now().strftime("%d/%m/%Y at %H:%M"))
        log_entry.add_log_to_database()

    def delete_comment(self, comment_author, comment_text, comment_time):
        self.selected_asset.remove_comment(comment_author, comment_text, comment_time)
        self.Lib.remove_log_entry_from_asset_id(self, self.selected_asset.id, "comment")
        self.load_comments()

    def edit_comment(self, comment_text_edit, comment_author, comment_text, comment_time):
        edit_comment_dialog = QtGui.QDialog()
        edit_comment_dialog.setWindowTitle("Edit comment")
        self.Lib.apply_style(self, edit_comment_dialog)
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

        new_comment = str(edit_comment_textbox.toPlainText())
        self.selected_asset.edit_comment(new_comment, comment_author, comment_text, comment_time)
        self.load_comments()

    def add_img_to_comment(self, comment_id):
        # Ask for user to select files
        selected_image_path = QtGui.QFileDialog.getOpenFileName(self, 'Select Files', 'H:/', "Images Files (*.jpg *.png)")

        if len(selected_image_path) < 1:
            return

        comment_img_path = self.selected_asset.comment_filename + "_" + str(comment_id) + ".jpg"
        shutil.copy(selected_image_path, comment_img_path)
        self.Lib.compress_image(self, os.path.abspath(comment_img_path), 1920, 75)

        self.cursor.execute('''UPDATE comments SET comment_image=? WHERE comment_id=?''', (comment_img_path, comment_id,))
        self.db.commit()

        self.load_comments()

    def show_comment_img(self, comment_id):
        comment_img_path = self.cursor.execute('''SELECT comment_image FROM comments WHERE comment_id=?''', (comment_id,)).fetchone()

        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:
            self.add_img_to_comment(comment_id)
            return
        elif QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            self.cursor.execute('''UPDATE comments SET comment_image="" WHERE comment_id=?''', (comment_id,))
            self.load_comments()
            return
        elif QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            subprocess.Popen(r'explorer /select,' + str(comment_img_path[0]))
            return

        subprocess.Popen([self.cur_path_one_folder_up + "\\_soft\\ImageGlass\\ImageGlass.exe", comment_img_path[0]])
