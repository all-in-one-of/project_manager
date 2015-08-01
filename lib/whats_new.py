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
        self.blog_gridLayout = QtGui.QGridLayout(self.blogScrollAreaWidgetContents)
        self.newsfeed_gridLayout = QtGui.QGridLayout(self.newsFeedScrollAreaWidgetContents)
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

        # Clear scrollarea
        while self.newsfeed_gridLayout.count():
            item = self.newsfeed_gridLayout.takeAt(0)
            item.widget().deleteLater()

        # Get all log entries based on type
        log_entries_db = self.cursor.execute('''SELECT * FROM log ''').fetchall()

        # List storing log entries objects
        self.log_entries = []

        # Create log entry objects
        for entry in log_entries_db:
            log_id = entry[0]
            log_dependancy = entry[1]
            log_viewed_by = entry[2]
            log_members_concerned = entry[3]
            log_from = entry[4]
            log_to = entry[5]
            log_type = entry[6]
            log_description = entry[7]
            log_time = entry[8]

            log = self.LogEntry(self, log_id, log_dependancy, log_viewed_by, log_members_concerned, log_from, log_to, log_type, log_description, log_time)
            self.log_entries.append(log)

        # Add log entries to GUI
        for log in reversed(self.log_entries):
            self.create_feed_entry(type=log.type, dependancy=log.dependancy, created_by=log.created_by, log_to=log.log_to, description=log.description, log_time=log.time)


    def create_feed_entry(self, type="", dependancy="", created_by="", log_to="", description="", log_time=""):

        # Create Feed Entry
        # Main Frame
        feedEntryFrame = QtGui.QFrame(self.newsFeedScrollArea)
        feedEntryFrame_layout = QtGui.QHBoxLayout(feedEntryFrame)
        feedEntryFrame.setMaximumHeight(120)

        # Picture Frame
        feedPicFrame = QtGui.QFrame(feedEntryFrame)
        feedPicFrame_layout = QtGui.QHBoxLayout(feedPicFrame)


        profilPicFromLbl = QtGui.QLabel(feedEntryFrame)
        profilPicFromLbl.setMinimumSize(80, 80)
        profilPicFromLbl.setMaximumSize(80, 80)
        profilPicFromLbl.setFrameShape(QtGui.QFrame.Box)
        profilPicFromLbl.setFrameShadow(QtGui.QFrame.Sunken)
        profilPicFromLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\members_photos\\" + created_by + ".jpg"))
        feedPicFrame_layout.addWidget(profilPicFromLbl)


        if type == "tasks":
            arrowLbl = QtGui.QLabel("->")
            feedPicFrame_layout.addWidget(arrowLbl)

            profilPibToLbl = QtGui.QLabel(feedEntryFrame)
            profilPibToLbl.setMinimumSize(80, 80)
            profilPibToLbl.setMaximumSize(80, 80)
            profilPibToLbl.setFrameShape(QtGui.QFrame.Box)
            profilPibToLbl.setFrameShadow(QtGui.QFrame.Sunken)
            profilPibToLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\members_photos\\" + log_to + ".jpg"))
            feedPicFrame_layout.addWidget(profilPibToLbl)

        # Text Frame
        feedTextFrame = QtGui.QFrame(feedEntryFrame)
        feedTextFrame_layout = QtGui.QVBoxLayout(feedTextFrame)
        feedTitleFrame = QtGui.QFrame(feedTextFrame)
        feedTitleFrame_layout = QtGui.QHBoxLayout(feedTitleFrame)
        feedIconLbl = QtGui.QLabel()
        feedIconLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\whatsnewicons\\" + type + ".png"))
        if type == "publish":
            feedTitleLbl = QtGui.QLabel("Asset published | " + log_time, feedEntryFrame)
        elif type == "asset":
            feedTitleLbl = QtGui.QLabel("Asset Created | " + log_time, feedEntryFrame)
        elif type == "comment":
            feedTitleLbl = QtGui.QLabel("Comment Added | " + log_time, feedEntryFrame)
        elif type == "task":
            feedTitleLbl = QtGui.QLabel("Task Created | " + log_time, feedEntryFrame)
        elif type == "image":
            feedTitleLbl = QtGui.QLabel("Image Added | " + log_time, feedEntryFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        feedTitleLbl.setFont(font)
        feedTitleFrame_layout.addWidget(feedIconLbl)
        feedTitleFrame_layout.addWidget(feedTitleLbl)

        feedMessageLbl = QtGui.QLabel(description, feedEntryFrame)
        vertical_spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        feedTextFrame_layout.addWidget(feedTitleFrame)
        feedTextFrame_layout.addWidget(feedMessageLbl)
        feedTextFrame_layout.addItem(vertical_spacer)

        # Add Widgets to layout
        feedEntryFrame_layout.addWidget(feedPicFrame)
        feedEntryFrame_layout.addWidget(feedTextFrame)
        horizontal_spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.newsfeed_gridLayout.addWidget(feedEntryFrame)
        feedEntryFrame_layout.addItem(horizontal_spacer)

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