#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import os
import subprocess
from datetime import datetime
from functools import partial

class WhatsNew(object):


    def __init__(self):

        if self.username == "yjobin" or self.username == "lclavet":
            self.addBlogPostFrame.show()
        else:
            self.addBlogPostFrame.hide()

        self.log_entries = {}

        self.addNewBlogPostTextEdit.setStyleSheet("background-color: #f1f1f1;")

        self.addNewBlogPostBtn.clicked.connect(self.add_post_to_blog)
        self.showOnlyMeWhatsNew.stateChanged.connect(self.load_whats_new)
        self.markAllNewsAsReadBtn.clicked.connect(self.mark_all_as_read)
        self.whatsNewTreeWidget.itemDoubleClicked.connect(self.tree_double_clicked)
        self.blog_gridLayout = QtGui.QGridLayout(self.blogScrollAreaWidgetContents)
        self.load_blog_posts()
        self.load_whats_new()

    def load_blog_posts(self):

        while self.blog_gridLayout.count():
            item = self.blog_gridLayout.takeAt(0)
            item.widget().deleteLater()

        blog_posts = self.cursor.execute('''SELECT * FROM blog''').fetchall()
        for post in reversed(blog_posts):
            post_id = post[0]
            post_datetime = post[1]
            post_title = post[2]
            post_message = post[3]
            post_author = post[4]

            title = u"{0} | par {1} | le {2}".format(post_title, self.members[post_author], post_datetime)

            # Frames creation
            entry_frame = QtGui.QFrame(self.whatsNewMessagesScrollArea)
            entry_frame_layout = QtGui.QHBoxLayout(entry_frame)
            entry_frame.setMaximumHeight(150)

            blog_frame = QtGui.QFrame(entry_frame)
            blog_frame_layout = QtGui.QVBoxLayout(blog_frame)

            buttons_frame = QtGui.QFrame(entry_frame)
            buttons_frame.setMaximumWidth(60)
            buttons_frame_layout = QtGui.QVBoxLayout(buttons_frame)

            entry_frame_layout.addWidget(blog_frame)
            entry_frame_layout.addWidget(buttons_frame)



            # Blog frame widgets
            title_lbl = QtGui.QLabel(blog_frame)
            title_lbl.setText(title)

            message_lbl = QtGui.QLabel(blog_frame)
            message_lbl.setTextFormat(QtCore.Qt.RichText)
            message_lbl.setWordWrap(True)
            message_lbl.setText(post_message + "<br>")

            blog_frame_layout.addWidget(title_lbl)
            blog_frame_layout.addWidget(message_lbl)

            if self.username == "thoudon" or self.username == "lclavet":
                # Buttons frame widgets
                edit_post_button = QtGui.QPushButton("Edit", buttons_frame)
                delete_post_button = QtGui.QPushButton("Delete", buttons_frame)
                edit_post_button.clicked.connect(partial(self.edit_blog_post, post_id, post_message))
                delete_post_button.clicked.connect(partial(self.delete_blog_post, post_id))
                edit_post_button.setMaximumWidth(64)
                delete_post_button.setMaximumWidth(64)

                buttons_frame_layout.addWidget(edit_post_button)
                buttons_frame_layout.addWidget(delete_post_button)

            line_01 = QtGui.QFrame()
            line_01.setFrameShape(QtGui.QFrame.HLine)
            line_01.setLineWidth(1)
            line_01.setFrameShadow(QtGui.QFrame.Sunken)


            self.blog_gridLayout.addWidget(entry_frame)
            self.blog_gridLayout.addWidget(line_01)

    def edit_blog_post(self, post_id, post_message):
        edit_blog_post_dialog = QtGui.QDialog()
        edit_blog_post_dialog.setWindowTitle("Edit blog post")
        self.Lib.apply_style(self, edit_blog_post_dialog)
        edit_blog_layout = QtGui.QVBoxLayout(edit_blog_post_dialog)
        edit_post_textEdit = QtGui.QTextEdit(post_message)
        edit_post_textEdit.selectAll()

        edit_post_acceptBtn = QtGui.QPushButton("Edit")
        edit_post_acceptBtn.clicked.connect(edit_blog_post_dialog.accept)

        edit_blog_layout.addWidget(edit_post_textEdit)
        edit_blog_layout.addWidget(edit_post_acceptBtn)
        edit_blog_post_dialog.exec_()

        if edit_blog_post_dialog.result == 0:
            return

        edited_blog_post = edit_post_textEdit.toPlainText()
        edited_blog_post = unicode(self.utf8_codec.fromUnicode(edited_blog_post), 'utf-8')
        self.cursor.execute('''UPDATE blog SET message=? WHERE blog_id=?''', (edited_blog_post, post_id,))
        self.db.commit()
        self.load_blog_posts()

    def delete_blog_post(self, post_id):
        self.cursor.execute('''DELETE FROM blog WHERE blog_id=?''', (post_id,))
        self.db.commit()
        self.load_blog_posts()

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
        comments_log_entries = [entry for entry in comments_log_entries if self.username in entry[2]]
        tasks_log_entries = [entry for entry in tasks_log_entries if self.username in entry[2]]
        images_log_entries = [entry for entry in images_log_entries if self.username in entry[2]]

        # If show only news concerning me checkbox is checked, only get comments where I am included
        if self.showOnlyMeWhatsNew.checkState() == 2:
            publishes_log_entries = [entry for entry in publishes_log_entries if self.username in entry[3]]
            assets_log_entries = [entry for entry in assets_log_entries if self.username in entry[3]]
            comments_log_entries = [entry for entry in comments_log_entries if self.username in entry[3]]
            tasks_log_entries = [entry for entry in tasks_log_entries if self.username in entry[3]]
            images_log_entries = [entry for entry in images_log_entries if self.username in entry[3]]

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
            log_description = entry[5]
            asset = self.Asset(self, asset_id)
            asset.get_infos_from_id()
            publishes_entries.append((log_description, asset))

        for entry in reversed(images_log_entries):
            asset_id = entry[1]
            log_description = entry[5]
            asset = self.Asset(self, asset_id)
            asset.get_infos_from_id()
            images_entries.append((log_description, asset))

        for entry in reversed(comments_log_entries):
            asset_id = entry[1]
            log_description = entry[5]
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

    def add_post_to_blog(self):

        current_time = datetime.now()
        current_time = current_time.strftime("%d/%m/%Y à %H:%M")
        current_time = unicode(current_time, "utf-8")

        title = self.blogPostTitleComboBox.currentText()
        title = unicode(self.utf8_codec.fromUnicode(title), 'utf-8')

        message = self.addNewBlogPostTextEdit.toPlainText()
        message = unicode(self.utf8_codec.fromUnicode(message), 'utf-8')

        self.cursor.execute('''INSERT INTO blog(blog_datetime, title, message, author, read_by) VALUES(?,?,?,?,?)''', (current_time, title, message, self.username, "",))
        self.db.commit()

        self.load_blog_posts()