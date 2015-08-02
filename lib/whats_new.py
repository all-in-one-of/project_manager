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

        self.first_load = True

        self.log_entries = []
        self.log_entries_db = []
        self.new_entries = []

        self.addNewBlogPostTextEdit.setStyleSheet("background-color: #f1f1f1;")

        self.addNewBlogPostBtn.clicked.connect(self.add_post_to_blog)
        self.markAllNewsAsReadBtn.clicked.connect(self.mark_all_log_as_read)

        self.showOnlyMeWhatsNew.stateChanged.connect(self.filter_feed_entries)
        self.showNewPublishesCheckBox.stateChanged.connect(self.filter_feed_entries)
        self.showNewAssetsCheckBox.stateChanged.connect(self.filter_feed_entries)
        self.showNewTasksCheckBox.stateChanged.connect(self.filter_feed_entries)
        self.showNewImagesCheckBox.stateChanged.connect(self.filter_feed_entries)
        self.showNewCommentsCheckBox.stateChanged.connect(self.filter_feed_entries)

        self.newsfeed_gridLayout = QtGui.QVBoxLayout(self.newsFeedScrollAreaWidgetContents)
        self.newsfeed_gridLayout.setMargin(0)
        self.newsfeed_gridLayout.setSpacing(3)


    def load_whats_new(self):

        self.log_entries_db_new = []

        # Get all log entries based on type
        self.log_entries_db_new = self.cursor.execute('''SELECT * FROM log ''').fetchall()
        self.log_entries_db_new = [entry for entry in self.log_entries_db_new if self.username in entry[2]] # Get unread entries

        if self.log_entries_db_new > self.log_entries_db:
            seen = set(self.log_entries_db)
            seen_add = seen.add
            self.new_entries = [x for x in self.log_entries_db_new if not (x in seen or seen_add(x))]
            self.log_entries_db = self.log_entries_db_new
        else:
            self.new_entries = []

        self.Tabs.setTabText(self.Tabs.count() - 1, "What's New (" + str(len(self.log_entries_db)) + ")")

        # List storing log entries objects
        self.log_entries = []
        self.log_widgets = []

        # Create log entry objects
        for entry in self.new_entries:
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
        for log in self.log_entries[::-1]:
            self.create_feed_entry(type=log.type, members_concerned=log.members_concerned, dependancy=log.dependancy, created_by=log.created_by, log_to=log.log_to, description=log.description, log_time=log.time)

        self.filter_feed_entries()
        self.first_load = False

    def create_feed_entry(self, type="", members_concerned=[], dependancy="", created_by="", log_to="", description="", log_time=""):

        # Create Feed Entry
        # Main Frame
        feedEntryFrame = QtGui.QFrame(self.newsFeedScrollArea)
        feedEntryFrame_layout = QtGui.QHBoxLayout(feedEntryFrame)
        feedEntryFrame.setMaximumHeight(120)
        self.log_widgets.append((feedEntryFrame, type, members_concerned))

        vertical_spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        horizontal_spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        # Picture Frame
        feedPicFrame = QtGui.QFrame(feedEntryFrame)
        feedPicFrame_layout = QtGui.QHBoxLayout(feedPicFrame)


        profilPicFromLbl = QtGui.QLabel(feedEntryFrame)
        profilPicFromLbl.setMinimumSize(80, 80)
        profilPicFromLbl.setMaximumSize(80, 80)
        profilPicFromLbl.setFrameShape(QtGui.QFrame.Box)
        profilPicFromLbl.setFrameShadow(QtGui.QFrame.Plain)
        profilPicFromLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\members_photos\\" + created_by + ".jpg"))
        feedPicFrame_layout.addWidget(profilPicFromLbl)


        if type == "task":
            arrowLbl = QtGui.QLabel("->")
            feedPicFrame_layout.addWidget(arrowLbl)

            profilPicToLbl = QtGui.QLabel(feedEntryFrame)
            profilPicToLbl.setMinimumSize(80, 80)
            profilPicToLbl.setMaximumSize(80, 80)
            profilPicToLbl.setFrameShape(QtGui.QFrame.Box)
            profilPicToLbl.setFrameShadow(QtGui.QFrame.Plain)
            profilPicToLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\members_photos\\" + log_to + ".jpg"))
            feedPicFrame_layout.addWidget(profilPicToLbl)

        # Text Frame
        feedTextFrame = QtGui.QFrame(feedEntryFrame)
        feedTextFrame_layout = QtGui.QVBoxLayout(feedTextFrame)
        feedTitleFrame = QtGui.QFrame(feedTextFrame)
        feedTitleFrame_layout = QtGui.QHBoxLayout(feedTitleFrame)
        feedIconLbl = QtGui.QLabel()
        feedIconLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\whatsnewicons\\" + type + ".png"))
        if type == "publish":
            feedTitleLbl = QtGui.QLabel(" Asset published | " + log_time, feedEntryFrame)
        elif type == "asset":
            feedTitleLbl = QtGui.QLabel(" Asset Created | " + log_time, feedEntryFrame)
        elif type == "comment":
            feedTitleLbl = QtGui.QLabel(" Comment Added | " + log_time, feedEntryFrame)
        elif type == "task":
            feedTitleLbl = QtGui.QLabel(" Task Created | " + log_time, feedEntryFrame)
        elif type == "image":
            feedTitleLbl = QtGui.QLabel(" Image Added | " + log_time, feedEntryFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        feedTitleLbl.setFont(font)
        feedTitleFrame_layout.addWidget(feedIconLbl)
        feedTitleFrame_layout.addWidget(feedTitleLbl)
        feedTitleFrame_layout.addItem(horizontal_spacer)

        feedMessageLbl = QtGui.QLabel(description, feedEntryFrame)
        feedTextFrame_layout.addWidget(feedTitleFrame)
        feedTextFrame_layout.addWidget(feedMessageLbl)
        feedTextFrame_layout.addItem(vertical_spacer)

        # Add Widgets to layout
        feedEntryFrame_layout.addWidget(feedPicFrame)
        feedEntryFrame_layout.addWidget(feedTextFrame)
        feedEntryFrame_layout.addItem(horizontal_spacer)
        if self.first_load:
            self.newsfeed_gridLayout.addWidget(feedEntryFrame)
        else:
            self.newsfeed_gridLayout.insertWidget(0, feedEntryFrame)

    def filter_feed_entries(self):

        # Create a list which store which checkbox is checked (ex: ["publish", "asset"])
        checkbox_states = []

        if self.showNewPublishesCheckBox.checkState():
            checkbox_states.append("publish")
        if self.showNewAssetsCheckBox.checkState():
            checkbox_states.append("asset")
        if self.showNewTasksCheckBox.checkState():
            checkbox_states.append("task")
        if self.showNewImagesCheckBox.checkState():
            checkbox_states.append("image")
        if self.showNewCommentsCheckBox.checkState():
            checkbox_states.append("comment")

        for feed_entry, type, members_concerned in self.log_widgets:
            # Current feed entry type is checked
            if type in checkbox_states:
                # Show only concerning me is checked
                if self.showOnlyMeWhatsNew.checkState() == 2:
                    # If current feed entry is concerning current user, show it, otherwise, hide it.
                    if self.username in members_concerned:
                        feed_entry.show()
                    else:
                        feed_entry.hide()
                elif self.showOnlyMeWhatsNew.checkState() == 0:
                    feed_entry.show()
            # Current feed entry type is unchecked, hide entry even if user is concerned.
            else:
                feed_entry.hide()

    def mark_all_log_as_read(self):

        confirm_dialog = QtGui.QMessageBox()
        reply = confirm_dialog.question(self, 'Mark all as read', "Are you sure ?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        self.Lib.apply_style(self, confirm_dialog)
        if reply == QtGui.QMessageBox.No:
            return

        for log_entry in self.log_entries:
            log_entry.update_viewed_by()

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
