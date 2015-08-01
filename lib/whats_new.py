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

        print(assets_log_entries)

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
            log_from = entry[4]
            log_to = entry[5]
            log_description = entry[7]
            log_time = entry[8]
            asset = self.Asset(self, asset_id)
            asset.get_infos_from_id()
            publishes_entries.append((log_description, log_from, log_to, log_time, asset))

        for entry in reversed(assets_log_entries):
            asset_id = entry[1]
            log_from = entry[4]
            log_description = entry[7]
            asset = self.Asset(self, asset_id)
            asset.get_infos_from_id()
            images_entries.append((log_description, log_from, asset))

        for entry in reversed(images_log_entries):
            asset_id = entry[1]
            log_from = entry[4]
            log_description = entry[7]
            asset = self.Asset(self, asset_id)
            asset.get_infos_from_id()
            images_entries.append((log_description, log_from, asset))

        for entry in reversed(comments_log_entries):
            asset_id = entry[1]
            log_from = entry[4]
            log_description = entry[7]
            asset = self.Asset(self, asset_id)
            asset.get_infos_from_id()
            comments_entries.append((log_description, log_from, asset))



        self.log_entries["publishes"] = publishes_entries
        self.log_entries["assets"] = assets_entries
        self.log_entries["comments"] = comments_entries
        self.log_entries["tasks"] = tasks_entries
        self.log_entries["images"] = images_entries

        for key, values in self.log_entries.items():
            if key == "publishes":
                for each_entry in values:
                    log_description = each_entry[0]
                    log_from = each_entry[1]
                    log_to = each_entry[2]
                    log_time = each_entry[3]
                    self.create_feed_entry(feed_type="publishes", log_from=log_from, log_to=log_to, log_description=log_description, log_time=log_time)


    def create_feed_entry(self, feed_type="", dependancy="", log_from="", log_to="", log_description="", log_time=""):

        # Create Feed Entry
        # Main Frame
        feedEntryFrame = QtGui.QFrame(self.newsFeedScrollArea)
        feedEntryFrame_layout = QtGui.QHBoxLayout(feedEntryFrame)
        feedEntryFrame.setMaximumHeight(120)

        # Profile Picture Frame
        feedPicFrame = QtGui.QFrame(feedEntryFrame)
        feedPicFrame_layout = QtGui.QHBoxLayout(feedPicFrame)


        profilPicFromLbl = QtGui.QLabel(feedEntryFrame)
        profilPicFromLbl.setMinimumSize(80, 80)
        profilPicFromLbl.setMaximumSize(80, 80)
        profilPicFromLbl.setFrameShape(QtGui.QFrame.Box)
        profilPicFromLbl.setFrameShadow(QtGui.QFrame.Sunken)
        profilPicFromLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\members_photos\\" + log_from + ".jpg"))
        feedPicFrame_layout.addWidget(profilPicFromLbl)




        if feed_type == "tasks":
            arrowLbl = QtGui.QLabel("->")
            feedPicFrame_layout.addWidget(arrowLbl)

            profilPibToLbl = QtGui.QLabel(feedEntryFrame)
            profilPibToLbl.setMinimumSize(80, 80)
            profilPibToLbl.setMaximumSize(80, 80)
            profilPibToLbl.setFrameShape(QtGui.QFrame.Box)
            profilPibToLbl.setFrameShadow(QtGui.QFrame.Sunken)
            profilPibToLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\members_photos\\" + log_to + ".jpg"))
            feedPicFrame_layout.addWidget(profilPibToLbl)

        # Profile Text Frame
        feedTextFrame = QtGui.QFrame(feedEntryFrame)
        feedTextFrame_layout = QtGui.QVBoxLayout(feedTextFrame)
        if feed_type == "publishes":
            feedTitleLbl = QtGui.QLabel("Asset published | " + log_time, feedEntryFrame)
        elif feed_type == "assets":
            feedTitleLbl = QtGui.QLabel("Asset Created | " + log_time, feedEntryFrame)
        elif feed_type == "comments":
            feedTitleLbl = QtGui.QLabel("Comment Added | " + log_time, feedEntryFrame)
        elif feed_type == "tasks":
            feedTitleLbl = QtGui.QLabel("Task Created | " + log_time, feedEntryFrame)
        elif feed_type == "images":
            feedTitleLbl = QtGui.QLabel("Image Added | " + log_time, feedEntryFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        feedTitleLbl.setFont(font)

        feedMessageLbl = QtGui.QLabel(log_description, feedEntryFrame)
        vertical_spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        feedTextFrame_layout.addWidget(feedTitleLbl)
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