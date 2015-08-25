#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import os
import subprocess
from datetime import datetime
from functools import partial
import sip

class WhatsNew(object):

    def __init__(self):

        if self.username == "thoudon" or self.username == "lclavet":
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

        for i in range(self.newsfeed_gridLayout.count()):
            self.newsfeed_gridLayout.itemAt(i).widget().close()

        # List storing log entries objects
        self.log_entries_db = []
        self.log_entries = []
        self.log_widgets = []

        # Get all log entries based on type
        self.log_entries_db = self.cursor.execute('''SELECT * FROM log ''').fetchall()
        self.log_entries_db = [entry for entry in self.log_entries_db if self.username in entry[2]] # Get unread entries


        if len(self.log_entries_db) == 0:
            self.create_feed_entry(type="nothing", created_by="default", description="Booh :(")
            self.Tabs.setTabText(self.Tabs.count() - 1, "What's New")
            return

        self.Tabs.setTabText(self.Tabs.count() - 1, "What's New (" + str(len(self.log_entries_db)) + ")")

        # Create log entry objects
        for entry in self.log_entries_db:
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
            self.create_feed_entry(type=log.type, members_concerned=log.members_concerned, dependancy=log.dependancy, created_by=log.created_by, log_to=log.log_to, description=log.description, log_time=log.time)

        self.filter_feed_entries()

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

        # If type is important, show warning sign in front of member profile picture
        if type == "important":
            feedEntryFrame.setMaximumHeight(250)
            importantLbl = QtGui.QLabel(feedEntryFrame)
            importantLbl.setMinimumSize(80, 80)
            importantLbl.setMaximumSize(80, 80)
            importantLbl.setLineWidth(0)
            importantLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\warning.png"))
            feedPicFrame_layout.addWidget(importantLbl)

        # Add member profile picture
        profilPicFromLbl = QtGui.QLabel(feedEntryFrame)
        profilPicFromLbl.setMinimumSize(80, 80)
        profilPicFromLbl.setMaximumSize(80, 80)
        profilPicFromLbl.setLineWidth(0)
        profilPicFromLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\members_photos\\" + created_by + ".jpg"))
        feedPicFrame_layout.addWidget(profilPicFromLbl)

        # If type is task, add picture of member to whom the task is assigned
        if type == "task":
            arrowLbl = QtGui.QLabel("->")
            feedPicFrame_layout.addWidget(arrowLbl)

            profilPicToLbl = QtGui.QLabel(feedEntryFrame)
            profilPicToLbl.setMinimumSize(80, 80)
            profilPicToLbl.setMaximumSize(80, 80)
            profilPicToLbl.setLineWidth(0)
            profilPicToLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\members_photos\\" + log_to + ".jpg"))
            feedPicFrame_layout.addWidget(profilPicToLbl)



        # Text Frame
        feedTextFrame = QtGui.QFrame(feedEntryFrame)
        feedTextFrame_layout = QtGui.QVBoxLayout(feedTextFrame)
        feedTitleFrame = QtGui.QFrame(feedTextFrame)
        feedTitleFrame_layout = QtGui.QHBoxLayout(feedTitleFrame)
        feedIconLbl = QtGui.QLabel()
        #if type != "important":
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
        elif type == "important":
            feedTitleLbl = QtGui.QLabel("MESSAGE IMPORTANT | " + log_time, feedEntryFrame)
            feedTitleLbl.setStyleSheet("color: red;")
        elif type == "nothing":
            feedTitleLbl = QtGui.QLabel(" There's nothing new :(", feedEntryFrame)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        feedTitleLbl.setFont(font)
        feedTitleFrame_layout.addWidget(feedIconLbl)
        feedTitleFrame_layout.addWidget(feedTitleLbl)
        feedTitleFrame_layout.addItem(horizontal_spacer)

        feedMessageLbl = QtGui.QLabel(description, feedEntryFrame)
        feedMessageLbl.setWordWrap(True)
        feedTextFrame_layout.addWidget(feedTitleFrame)
        feedTextFrame_layout.addWidget(feedMessageLbl)
        feedTextFrame_layout.addItem(vertical_spacer)

        # Add Widgets to layout
        feedEntryFrame_layout.addWidget(feedPicFrame)
        feedEntryFrame_layout.addWidget(feedTextFrame)
        feedEntryFrame_layout.addItem(horizontal_spacer)

        self.newsfeed_gridLayout.addWidget(feedEntryFrame)


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

        checkbox_states.append("important")

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

        self.db.commit()
        self.load_whats_new()

    def add_post_to_blog(self):

        current_time = datetime.now()
        current_time = current_time.strftime("%d/%m/%Y à %H:%M")
        current_time = unicode(current_time, "utf-8")


        message = self.addNewBlogPostTextEdit.toPlainText()
        message = unicode(self.utf8_codec.fromUnicode(message), 'utf-8')

        log_entry = self.LogEntry(self, 0, "", [], [], self.username, "", "important", message, datetime.now().strftime("%d/%m/%Y at %H:%M"))
        log_entry.add_log_to_database()


