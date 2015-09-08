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
        self.showImportantMessagesCheckBox.stateChanged.connect(self.filter_feed_entries)
        self.whatsNewFilterByMemberComboBox.currentIndexChanged.connect(self.filter_feed_entries)

        self.showAllNewsCheckBox.stateChanged.connect(self.load_whats_new)

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
        if self.showAllNewsCheckBox.checkState() == 0:
            self.log_entries_db = [entry for entry in self.log_entries_db if self.username in entry[2]]  # Get unread entries

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
        log_day = "0"
        for i, log in enumerate(reversed(self.log_entries)):


            if log_day != str(log.time.split("/")[0]): # If day is different than last log day.
                # Create label
                log_date = log.time.split(" ")[0]  # Ex: 01/01/2015
                log_date = datetime.strptime(log_date, '%d/%m/%Y').strftime('%A %d %B %Y')  # Convert 01/01/2015 to Monday 01 January 2015
                font = QtGui.QFont()
                font.setPointSize(25)
                day_label = QtGui.QLabel("      " + log_date)
                day_label.setFont(font)

                if i != 0:
                    separation_line = QtGui.QFrame()
                    separation_line.setFrameShape(QtGui.QFrame.HLine)
                    separation_line.setFrameShadow(QtGui.QFrame.Sunken)
                    self.newsfeed_gridLayout.addWidget(separation_line)
                self.newsfeed_gridLayout.addWidget(day_label)

            log_day = str(log.time.split("/")[0])

            self.create_feed_entry(type=log.type, members_concerned=log.members_concerned, dependancy=log.dependancy, created_by=log.created_by, log_to=log.log_to, description=log.description, log_time=log.time)



        self.filter_feed_entries()

    def create_feed_entry(self, type="", members_concerned=[], dependancy="", created_by="", log_to="", description="", log_time=""):

        # Create Feed Entry
        # Main Frame
        feedEntryFrame = QtGui.QFrame(self.newsFeedScrollArea)
        feedEntryFrame_layout = QtGui.QHBoxLayout(feedEntryFrame)
        feedEntryFrame.setMaximumHeight(120)
        self.log_widgets.append((feedEntryFrame, type, members_concerned, created_by))

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
        feedIconBtn = QtGui.QPushButton()
        feedIconBtn.setFixedSize(32, 32)

        feedIconBtn.clicked.connect(self.load_log_entry_data)
        feedIconBtn.log_entry_asset_id = dependancy
        feedIconBtn.asset_type = type
        feedIconBtn.setIcon(QtGui.QIcon(self.cur_path + "\\media\\whatsnewicons\\" + type + ".png"))

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
        feedTitleFrame_layout.addWidget(feedIconBtn)
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

        if self.showOnlyMeWhatsNew.checkState() == 2:
            self.whatsNewFilterByMemberComboBox.setEnabled(False)
        else:
            self.whatsNewFilterByMemberComboBox.setEnabled(True)

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
        if self.showImportantMessagesCheckBox.checkState():
            checkbox_states.append("important")
        if self.whatsNewFilterByMemberComboBox.currentText() != "None":
            checkbox_states.append(str(self.whatsNewFilterByMemberComboBox.currentText()))

        for feed_entry, type, members_concerned, created_by in self.log_widgets:
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
                    if self.whatsNewFilterByMemberComboBox.currentText() != "None":
                        if created_by in checkbox_states:
                            feed_entry.show()
                        else:
                            feed_entry.hide()
                    else:
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

    def load_log_entry_data(self):
        asset_id = self.sender().log_entry_asset_id
        asset_type = self.sender().asset_type

        if asset_type in ["publish", "asset"]:

            # Check if asset still exists
            assets_id_list = [asset.id for asset in self.assets.keys()]
            if asset_id not in assets_id_list:
                self.Lib.message_box(self, type="error", text="This asset does not exist. It must have been deleted!")
                return

            for asset, asset_item in self.assets.items():
                asset_item.setHidden(False)
                if asset_id == asset.id:
                    asset_item.setHidden(False)
                else:
                    asset_item.setHidden(True)

            self.Tabs.setCurrentWidget(self.Tabs.widget(0))

        elif asset_type == "task":

            # Check if task still exists
            tasks_id_list = self.cursor.execute('''SELECT task_id FROM tasks WHERE task_confirmation="1"''').fetchall()
            tasks_id_list = [i[0] for i in tasks_id_list]
            if not asset_id in tasks_id_list:
                self.Lib.message_box(self, type="error", text="This task does not exist. It must have been deleted!")
                return

            number_of_rows = self.mtTableWidget.rowCount()
            for row_index in xrange(number_of_rows):
                id_cell = self.mt_widgets[str(row_index) + ":0"]
                task_id = id_cell.text()
                if str(asset_id) == str(task_id):
                    self.mtTableWidget.showRow(row_index)
                else:
                    self.mtTableWidget.hideRow(row_index)

            self.mtTableWidget.resizeColumnsToContents()
            self.mtTableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
            self.Tabs.setCurrentWidget(self.Tabs.widget(self.tabs_list["Tasks"]))

        elif asset_type == "image":

            if len(self.ref_assets_instances) < 1:
                self.Lib.message_box(self, type="error", text="Please load images in Images Manager.")
                return

            # Check if asset still exists
            assets_id_list = [asset[1].id for asset in self.references]
            if asset_id not in assets_id_list:
                self.Lib.message_box(self, type="error", text="This asset does not exist. It must have been deleted!")
                return

            for item in self.references:
                asset_item = item[0]
                asset = item[1]
                if str(asset.id) == str(asset_id):
                    asset_item.setHidden(False)
                else:
                    asset_item.setHidden(True)

            self.Tabs.setCurrentWidget(self.Tabs.widget(self.tabs_list["Images Manager"]))





