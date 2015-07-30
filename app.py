#!/usr/bin/env python
# coding=utf-8
''' 

Author: Thibault Houdon
Email: houdon.thibault@gmail.com


    Files/Folders Structure:

- lib folder contains utilities scripts:
    QtUiConverter to convert .ui file contained in media folder to main_window.py file in ui folder.
    make_exe to create an executable files to launch the application (inside the dist folder).
- media folder which contains all images, the .ui file and the css files.
- ui folder which contains all python scripts which generates GUIs.

The setup.py file is used by py2exe to create the executable file (it is run from the make_exe file which is inside the lib folder).
The _Asset Manager shortcut is pointing toward the app.exe file inside the lib/dist folder
The app.py file is the main python file


    Instructions:
- When working home:
    - uncomment the line with the database on my computer
    - change the self.members list by uncommenting the lines
    - copy the sqlite database to desktop

- Before publishing:
    - Change the database from working database to the official project database



'''

import sys
import os
import subprocess

import sqlite3
import time
import shutil

from datetime import date
from datetime import datetime
from dateutil import relativedelta

import logging
from logging.handlers import RotatingFileHandler

from PyQt4 import QtGui, QtCore

from ui.main_window import Ui_Form
from lib.reference import ReferenceTab
from lib.module import Lib
from lib.module import CheckNews
from lib.task_manager import TaskManager
from lib.my_tasks import MyTasks
from lib.task import Task
from lib.comments import CommentWidget
from lib.whats_new import WhatsNew
from lib.asset import Asset
from lib.asset_loader import AssetLoader
from lib.reference_moodboard import Moodboard_Creator




class Main(QtGui.QWidget, Ui_Form, ReferenceTab, CommentWidget, Lib, TaskManager, MyTasks, WhatsNew, Asset, Task, AssetLoader, Moodboard_Creator):
    def __init__(self):
        super(Main, self).__init__()

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)

        self.ReferenceTab = ReferenceTab
        self.Lib = Lib
        self.TaskManager = TaskManager
        self.MyTasks = MyTasks
        self.WhatsNew = WhatsNew
        self.CommentWidget = CommentWidget
        self.Task = Task
        self.Asset = Asset
        self.Moodboard_Creator = Moodboard_Creator

        # Database Setup
        #self.db_path = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\db.sqlite"  # Database officielle
        self.db_path = "H:\\01-NAD\\_pipeline\\_utilities\\_database\\db.sqlite" # Copie de travail


        # Backup database
        self.backup_database()

        self.db = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.db.cursor()

        # Initialize the guis
        self.Form = self.setupUi(self)
        self.Form.center_window()

        # Global Variables
        self.i = 0
        self.selected_asset = None
        self.today = time.strftime("%d/%m/%Y", time.gmtime())
        self.cur_path = os.path.dirname(os.path.realpath(__file__))  # H:\01-NAD\_pipeline\_utilities\_asset_manager
        self.cur_path_one_folder_up = self.cur_path.replace("\\_asset_manager", "")  # H:\01-NAD\_pipeline\_utilities
        self.NEF_folder = self.cur_path_one_folder_up + "\\NEF"  # H:\01-NAD\_pipeline\_utilities\NEF
        self.screenshot_dir = self.cur_path_one_folder_up + "\\_database\\screenshots\\"
        self.no_img_found = self.cur_path + "\\media\\no_img_found.png"
        self.username = os.getenv('USERNAME')

        self.members = {"achaput": "Amelie", "costiguy": "Chloe", "cgonnord": "Christopher", "dcayerdesforges": "David",
                        "earismendez": "Edwin", "erodrigue": "Etienne", "jberger": "Jeremy", "lgregoire": "Laurence",
                        "lclavet": "Louis-Philippe", "mchretien": "Marc-Antoine", "mbeaudoin": "Mathieu",
                        "mroz": "Maxime", "obolduc": "Olivier", "slachapelle": "Simon", "thoudon": "Thibault",
                        "vdelbroucq": "Valentin", "yjobin": "Yann", "yshan": "Yi"}
        self.departments_shortname = {"Script": "spt", "Storyboard": "stb", "References": "ref", "Concepts": "cpt",
                                         "Modeling": "mod", "Texturing": "tex", "Rigging": "rig", "Animation": "anm",
                                         "Simulation": "sim", "Shading": "shd", "Layout": "lay", "DMP": "dmp",
                                         "Compositing": "cmp", "Editing": "edt", "RnD": "rnd"}
        refresh_icon = QtGui.QIcon(self.cur_path + "\\media\\refresh.png")
        self.refreshAllBtn.setIcon(refresh_icon)
        self.refreshAllBtn.setIconSize(QtCore.QSize(24, 24))
        self.refreshAllBtn.clicked.connect(self.refresh_all)

        # Setup user session if it is not already setup
        is_setup = self.cursor.execute('''SELECT is_setup FROM preferences WHERE username=?''', (self.username,)).fetchone()[0]
        if is_setup == 0:
            self.Lib.setup_user_session(self)
            self.cursor.execute('''UPDATE preferences SET is_setup=1 WHERE username=?''', (self.username,))
            self.db.commit()

        # Create Favicon
        self.app_icon = QtGui.QIcon()
        self.app_icon.addFile(self.cur_path + "\\media\\favicon_cube.png", QtCore.QSize(64, 64))
        self.Form.setWindowIcon(self.app_icon)

        # Set the StyleSheet
        self.themePrefComboBox.currentIndexChanged.connect(self.change_theme)
        self.theme = self.cursor.execute('''SELECT theme FROM preferences WHERE username=?''', (self.username,)).fetchone()[0]
        self.themePrefComboBox.setCurrentIndex(int(self.theme))
        self.change_theme()

        # Admin Setup
        self.remove_tabs_based_on_members()

        # Get remaining time and set deadline Progress Bar
        day_start = date(2015,6,28)
        day_end = date(2016,5,1)
        day_today = datetime.now()

        day_end_02 = datetime.strptime(str('2016-05-01'), '%Y-%m-%d')
        months_and_days_left = relativedelta.relativedelta(day_end_02, day_today)

        total_days = abs(day_end - day_start).days
        remaining_days = abs(day_end - date.today()).days
        remaining_days_percent = (remaining_days * 100) / total_days # Converts number of remaining day to a percentage

        self.deadlineProgressBar.setFormat("{0} months and {1} days left ({2}%)".format(months_and_days_left.months, months_and_days_left.days, remaining_days_percent))
        self.deadlineProgressBar.setMaximum(total_days)
        self.deadlineProgressBar.setValue(remaining_days)
        hue = self.fit_range(remaining_days, 0, total_days, 0, 76)
        self.deadlineProgressBar.setStyleSheet("QProgressBar::chunk {background-color: hsl(" + str(hue) + ", 255, 205);}")

        # Setup disk usage progress bar
        disk_usage = Lib.get_folder_space(self)
        disk_usage = int(float(disk_usage) * 1000) # Multiply disk usage by 1000. Ex: 1.819 to 1819
        disk_usage = (2000 * int(disk_usage)) / 1862 # 2TO in theory = 1.862GB in reality. Remapping real disk usage to the theoric one
        self.diskUsageProgressBar.setFormat('{0}/2000 GB'.format(str(disk_usage)))
        self.diskUsageProgressBar.setRange(0, 2000)
        self.diskUsageProgressBar.setValue(int(disk_usage))
        hue = self.fit_range(int(disk_usage), 0, 2000, 0, 76)
        self.diskUsageProgressBar.setStyleSheet("QProgressBar::chunk {background-color: hsl(" + str(hue) + ", 255, 205);}")

        # Thumbnail creation progress bar setup
        self.thumbnailProgressBar.setStyleSheet("QProgressBar::chunk {background-color: hsl(0, 100, 175);}")
        self.thumbnailProgressBar.setValue(0)
        self.thumbnailProgressBar.hide()

        # Get software paths from database and put them in preference
        self.photoshop_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Photoshop"''').fetchone()[0])
        self.maya_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Maya"''').fetchone()[0])
        self.maya_batch_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Maya Batch"''').fetchone()[0])
        self.softimage_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Softimage"''').fetchone()[0])
        self.softimage_batch_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Softimage Batch"''').fetchone()[0])
        self.houdini_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Houdini"''').fetchone()[0])
        self.houdini_batch_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Houdini Batch"''').fetchone()[0])
        self.cinema4d_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Cinema 4D"''').fetchone()[0])
        self.nuke_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Nuke"''').fetchone()[0])
        self.zbrush_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="ZBrush"''').fetchone()[0])
        self.mari_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Mari"''').fetchone()[0])
        self.blender_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Blender"''').fetchone()[0])

        self.photoshopPathLineEdit.setText(self.photoshop_path)
        self.mayaPathLineEdit.setText(self.maya_path)
        self.mayaBatchPathLineEdit.setText(self.maya_batch_path)
        self.softimagePathLineEdit.setText(self.softimage_path)
        self.softimageBatchPathLineEdit.setText(self.softimage_batch_path)
        self.houdiniPathLineEdit.setText(self.houdini_path)
        self.houdiniBatchPathLineEdit.setText(self.houdini_batch_path)
        self.cinema4dPathLineEdit.setText(self.cinema4d_path)
        self.nukePathLineEdit.setText(self.nuke_path)
        self.zbrushPathLineEdit.setText(self.zbrush_path)
        self.mariPathLineEdit.setText(self.mari_path)
        self.blenderPathLineEdit.setText(self.blender_path)

        # Preferences setup
        self.prefBckGroundColorSlider.sliderMoved.connect(self.change_pref_background_color_pixmap)
        self.prefBckGroundColorSlider.setStyleSheet("background-color; red;")

        # Systray icon
        self.tray_icon_log_id = ""
        self.tray_icon = QtGui.QSystemTrayIcon(QtGui.QIcon(self.cur_path + "\\media\\favicon_cube.png"), app)
        self.tray_icon.messageClicked.connect(self.tray_icon_message_clicked)
        self.tray_icon.activated.connect(self.tray_icon_clicked)
        self.tray_message = ""

        # Initialize modules and connections
        AssetLoader.__init__(self)
        ReferenceTab.__init__(self)
        TaskManager.__init__(self)
        CommentWidget.__init__(self)
        MyTasks.__init__(self)
        WhatsNew.__init__(self)

        #self.check_news_thread = CheckNews(self)
        #self.check_news_thread.daemon = True
        #self.check_news_thread.start()


    def add_tag_to_tags_manager(self):
        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            Lib.message_box(text="Please select a project first.")
            return

        tag_name = unicode(self.addTagLineEdit.text())
        tag_name = Lib.normalize_str(self, tag_name)

        if len(tag_name) == 0:
            Lib.message_box(text="Please enter a tag name.")
            return

        item = QtGui.QTreeWidgetItem(self.tagsTreeWidget)
        item.setText(0, tag_name)
        self.tagsTreeWidget.addTopLevelItem(item)

        self.addTagLineEdit.setText("")
        self.save_tags_list()

    def remove_selected_tags_from_tags_manager(self):
        root = self.tagsTreeWidget.invisibleRootItem()
        for item in self.tagsTreeWidget.selectedItems():
            (item.parent() or root).removeChild(item)
        self.save_tags_list()

    def save_tags_list(self):
        root = self.tagsTreeWidget.invisibleRootItem() # Fetch the root item
        child_count = root.childCount()
        for item in xrange(child_count):

            # Get the text of the first item in the tree widget
            parent_text = str(root.child(item).text(0))

            # Check if item already exists, if no, add it to the database, if yes, update its name and parent
            already_exist = self.cursor.execute('''SELECT tag_name FROM tags WHERE tag_name=?''', (parent_text,)).fetchone()
            if already_exist == None:
                self.cursor.execute('''INSERT INTO tags(project_name, tag_name, tag_parent) VALUES(?,?,?)''', (self.selected_project_name, parent_text, "",))
            else:
                self.cursor.execute('''UPDATE tags SET tag_name=?, tag_parent=? WHERE tag_name=? AND project_name=?''', (parent_text, "", parent_text, self.selected_project_name,))

            # Get all children of parent item
            nbr_of_children = root.child(item).childCount()
            for i in range(nbr_of_children):
                child_text = str(root.child(item).child(i).text(0))

                # Check if item already exists, if no, add it to the database, if yes, update its name and parent
                already_exist = self.cursor.execute('''SELECT tag_name FROM tags WHERE tag_name=?''', (child_text,)).fetchone()
                if already_exist == None:
                    self.cursor.execute('''INSERT INTO tags(project_name, tag_name, tag_parent) VALUES(?,?,?)''', (self.selected_project_name, child_text, parent_text,))
                else:
                    self.cursor.execute('''UPDATE tags SET tag_name=?, tag_parent=? WHERE tag_name=? AND project_name=?''', (child_text, parent_text, child_text, self.selected_project_name,))

        self.db.commit()

    def add_assets_to_asset_list(self, assets_list):
        """
        Add assets from assets_list to self.assetList

        """

        self.assetList.clear()
        for asset in assets_list:
            self.assetList.addItem(asset[4])

    def clear_filter(self, filter_type):
        """
        Clear the filter edit line
        """
        if filter_type == "seq":
            self.seqFilter.setText("")
        elif filter_type == "asset":
            self.assetFilter.setText("")

    def update_thumb(self):
        """
        Update selected asset thumbnail
        """
        self.Form.showMinimized()

        Lib.take_screenshot(self.screenshot_dir, self.selected_asset_name)

        pixmap = QtGui.QPixmap(self.screenshot_dir + self.selected_asset_name + ".jpg").scaled(1000, 200,
                                                                                               QtCore.Qt.KeepAspectRatio,
                                                                                               QtCore.Qt.SmoothTransformation)
        self.assetImg.setPixmap(pixmap)
        self.Form.showMaximized()
        self.Form.showNormal()

    def filter_assets_for_me(self):

        if not self.meOnlyCheckBox.checkState():
            self.assignedToFilterComboBox.setCurrentIndex(0)
        else:
            if self.username == "achaput":
                self.assignedToFilterComboBox.setCurrentIndex(1)
            elif self.username == "costiguy":
                self.assignedToFilterComboBox.setCurrentIndex(2)
            elif self.username == "cgonnord":
                self.assignedToFilterComboBox.setCurrentIndex(3)
            elif self.username == "dcayerdesforges":
                self.assignedToFilterComboBox.setCurrentIndex(4)
            elif self.username == "earismendez":
                self.assignedToFilterComboBox.setCurrentIndex(5)
            elif self.username == "erodrigue":
                self.assignedToFilterComboBox.setCurrentIndex(6)
            elif self.username == "jberger":
                self.assignedToFilterComboBox.setCurrentIndex(7)
            elif self.username == "lgregoire":
                self.assignedToFilterComboBox.setCurrentIndex(8)
            elif self.username == "lclavet":
                self.assignedToFilterComboBox.setCurrentIndex(9)
            elif self.username == "mchretien":
                self.assignedToFilterComboBox.setCurrentIndex(10)
            elif self.username == "mbeaudoin":
                self.assignedToFilterComboBox.setCurrentIndex(11)
            elif self.username == "mroz":
                self.assignedToFilterComboBox.setCurrentIndex(12)
            elif self.username == "obolduc":
                self.assignedToFilterComboBox.setCurrentIndex(13)
            elif self.username == "slachapelle":
                self.assignedToFilterComboBox.setCurrentIndex(14)
            elif self.username == "thoudon":
                self.assignedToFilterComboBox.setCurrentIndex(15)
            elif self.username == "yjobin":
                self.assignedToFilterComboBox.setCurrentIndex(16)
            elif self.username == "yshan":
                self.assignedToFilterComboBox.setCurrentIndex(17)
            elif self.username == "vdelbroucq":
                self.assignedToFilterComboBox.setCurrentIndex(18)

    def remove_tabs_based_on_members(self):

        if not (self.username == "thoudon" or self.username == "lclavet"):
            self.addProjectFrame.hide()
            self.addSequenceFrame.hide()
            self.addShotFrame.hide()
            self.adminPrefFrame.hide()
            self.createAssetFromScratchBtn.hide()

        self.get_tabs_id_from_name()

        if self.members[self.username] == "Amelie":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Chloe":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Christopher":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "David":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Edwin":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Etienne":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Jeremy":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Laurence":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Louis-Philippe":
            pass

        elif self.members[self.username] == "Marc-Antoine":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Mathieu":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Maxime":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Olivier":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Simon":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Thibault":
            pass

        elif self.members[self.username] == "Yann":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()

        elif self.members[self.username] == "Yi":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

        elif self.members[self.username] == "Valentin":
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])

    def get_tabs_id_from_name(self):
        self.tabs_list = {}
        for i in xrange(self.Tabs.count()):
            self.tabs_list[str(self.Tabs.tabText(i))] = i

    def change_username(self):
        username = str(self.usernameAdminComboBox.currentText())
        self.username = username

    def add_log_entry(self, text, people=[], value=""):

        people = ",".join(people)

        cur_date = time.strftime("%d/%m/%Y")
        cur_time = time.strftime("%H:%M:%S")

        log_time = cur_date + " - " + cur_time

        self.cursor.execute('''INSERT INTO log(log_time, log_entry, log_people, log_value) VALUES (?, ?, ?, ?)''',
                            (log_time, text, people, value))

        self.db.commit()

    def backup_database(self):
        # Get creation_time of last database backup and compare it to current  time
        database_files = Lib.get_files_from_folder(self, path="Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\backup")
        if len(database_files) > 1000:
            Lib.message_box("Trop de backups détectés pour la base de donnée. Veuillez avertir Thibault, merci ;)")

        database_files = sorted(database_files)
        last_database_file = database_files[-1]
        creation_time = time.ctime(os.path.getctime(last_database_file))
        creation_time = time.strptime(creation_time, "%a %b %d %H:%M:%S %Y")
        current_time = str(datetime.now())
        current_time = time.strptime(current_time, "%Y-%m-%d %H:%M:%S.%f")
        time_difference = (time.mktime(current_time) - time.mktime(creation_time)) / 60

        if time_difference > 180: # If last backup is older than 5 hours, do a backup
            fileName, fileExtension = os.path.splitext(last_database_file)
            last_database_file_version = int(fileName.split("_")[-1])
            new_version = str(last_database_file_version + 1).zfill(4)
            backup_database_filename = fileName.replace(str(last_database_file_version).zfill(4), new_version) + ".sqlite"
            shutil.copy("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\db.sqlite", backup_database_filename)

    def refresh_all(self):
        self.load_all_assets_for_first_time()
        self.load_assets_from_selected_seq_shot_dept()
        self.setup_tags()
        self.mt_item_added = True
        MyTasks.mt_add_tasks_from_database(self)
        WhatsNew.load_whats_new(self)
        ReferenceTab.refresh_reference_list(self)

    def change_theme(self):
        if self.themePrefComboBox.currentIndex() == 0:
            self.theme = 0
            self.prefBckGroundColorSlider.setValue(114)
            self.Lib.apply_style(self, self)
            self.cursor.execute('''UPDATE preferences SET theme=? WHERE username=?''', (0, self.username,))
        elif self.themePrefComboBox.currentIndex() == 1:
            self.theme = 1
            self.prefBckGroundColorSlider.setValue(241)
            self.setStyleSheet("")
            app.setStyle(QtGui.QStyleFactory.create("cleanlooks"))
            self.cursor.execute('''UPDATE preferences SET theme=? WHERE username=?''', (1, self.username,))
            css = QtCore.QFile(self.cur_path + "\\media\\cleanlooks.css")
            css.open(QtCore.QIODevice.ReadOnly)
            if css.isOpen():
                self.Form.setStyleSheet(QtCore.QVariant(css.readAll()).toString())
        elif self.themePrefComboBox.currentIndex() == 2:
            self.prefBckGroundColorSlider.setValue(255)
            self.theme = 2
            self.setStyleSheet("")
            app.setStyle(QtGui.QStyleFactory.create("plastique"))
            self.cursor.execute('''UPDATE preferences SET theme=? WHERE username=?''', (2, self.username,))

        self.db.commit()

    def change_pref_background_color_pixmap(self):
        slider_value = self.prefBckGroundColorSlider.value()
        self.referenceThumbListWidget.setStyleSheet("background-color: rgb({0},{0},{0});".format(slider_value))

    def tray_icon_message_clicked(self):

        if self.tray_message == "Manager is in background mode.":
            return

        clicked_log_entry = self.cursor.execute('''SELECT log_value FROM log WHERE log_id=?''', (self.tray_icon_log_id,)).fetchone()[0]
        clicked_log_description = self.cursor.execute('''SELECT log_entry FROM log WHERE log_id=?''', (self.tray_icon_log_id,)).fetchone()[0]

        if len(clicked_log_entry) == 0:
            return

        asset = self.Asset(main=self, id=clicked_log_entry)
        asset.get_infos_from_id()


        if "reference" in clicked_log_description:
            if "video" in clicked_log_description:
                subprocess.Popen(["C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe", asset.dependency])
            else:
                if os.path.isfile(asset.full_path):
                    os.system(asset.full_path)
                else:
                    self.Lib.message_box(self, text="Can't find reference: it must have been deleted.")

        elif "comment" in clicked_log_description:
            self.CommentWidget(main=self, asset=asset)

    def tray_icon_clicked(self, reason):
        if reason == QtGui.QSystemTrayIcon.DoubleClick:
            if self.isHidden():
                self.setWindowFlags(QtCore.Qt.Widget)
                self.show()
                self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                self.tray_icon.hide()
            else:
                self.hide()
                self.tray_icon.show()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        if key == QtCore.Qt.Key_Escape:
            sys.exit()
        if key == QtCore.Qt.Key_Delete:
            ReferenceTab.remove_selected_references(self)
        if key == QtCore.Qt.Key_F2:
            selected_reference = self.referenceThumbListWidget.selectedItems()[0]
            asset = selected_reference.data(QtCore.Qt.UserRole).toPyObject()
            ReferenceTab.rename_reference(self, asset)

    def closeEvent(self, event):
        self.save_tags_list()
        self.Lib.save_prefs
        self.close()
        app.exit()

        # self.quit_msg = "Are you sure you want to exit the program?"
        # reply = QtGui.QMessageBox.question(self, 'Are you leaving :(',
        #                  quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        #
        # if reply == QtGui.QMessageBox.Yes:
        #
        #     event.accept()
        # else:
        #     event.ignore()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                self.setWindowFlags(QtCore.Qt.Tool)
                self.hide()
                self.tray_icon.show()
                self.tray_message = "Manager is in background mode."
                self.tray_icon.showMessage('Still running...', self.tray_message, QtGui.QSystemTrayIcon.Information, 1000)

if __name__ == "__main__":

    log_to_file = False

    cur_path = os.path.dirname(os.path.realpath(__file__))

    # création de l'objet logger qui va nous servir à écrire dans les logs
    logger = logging.getLogger()
    # on met le niveau du logger à DEBUG, comme ça il écrit tout
    logger.setLevel(logging.DEBUG)
    # création d'un formateur qui va ajouter le temps, le niveau
    # de chaque message quand on écrira un message dans le log
    formatter = logging.Formatter('%(asctime)s ::: %(filename)s ::: ''%(funcName)s() ::: line ''%(lineno)d ::: ''%(message)s')
    # création d'un handler qui va rediriger une écriture du log vers
    # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo

    file_handler = RotatingFileHandler(cur_path + '\\bin\\activity.log', 'a', 1000000, 1)
    # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
    # créé précédement et on ajoute ce handler au logger
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # création d'un second handler qui va rediriger chaque écriture de log
    # sur la console
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.DEBUG)
    logger.addHandler(steam_handler)



    if log_to_file == False:
        app = QtGui.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        # Show Splashscreen
        splash_pix = QtGui.QPixmap(cur_path + "\\media\\splashscreen.jpg")
        splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())

        splash.show()

        splash.setPixmap(QtGui.QPixmap(cur_path + "\\media\\splashscreen-02.jpg"))
        splash.repaint()

        splash.setPixmap(QtGui.QPixmap(cur_path + "\\media\\splashscreen-03.jpg"))
        splash.repaint()

        splash.setPixmap(QtGui.QPixmap(cur_path + "\\media\\splashscreen-04.jpg"))
        splash.repaint()

        splash.setPixmap(QtGui.QPixmap(cur_path + "\\media\\splashscreen-05.jpg"))
        splash.repaint()

        window = Main()
        window.show()

        splash.finish(window)

        sys.exit(app.exec_())
    else:
        try:
            app = QtGui.QApplication(sys.argv)
            app.setQuitOnLastWindowClosed(False)

            # Show Splashscreen
            splash_pix = QtGui.QPixmap(cur_path + "\\media\\splashscreen.jpg")
            splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
            splash.setMask(splash_pix.mask())

            splash.show()

            splash.setPixmap(QtGui.QPixmap(cur_path + "\\media\\splashscreen-02.jpg"))
            splash.repaint()

            splash.setPixmap(QtGui.QPixmap(cur_path + "\\media\\splashscreen-03.jpg"))
            splash.repaint()

            splash.setPixmap(QtGui.QPixmap(cur_path + "\\media\\splashscreen-04.jpg"))
            splash.repaint()

            splash.setPixmap(QtGui.QPixmap(cur_path + "\\media\\splashscreen-05.jpg"))
            splash.repaint()

            window = Main()
            window.show()

            splash.finish(window)
            sys.exit(app.exec_())

        except Exception as e:
            logger.debug(e)


