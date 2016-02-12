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

import socket

import sqlite3
import time
import shutil

from datetime import date
from datetime import datetime
from dateutil import relativedelta
from functools import partial

import logging
from logging.handlers import RotatingFileHandler

from PyQt4 import QtGui, QtCore

from ui.main_window import Ui_Form
from lib.reference import ReferenceTab
from lib.module import Lib
from lib.task_manager import TaskManager
from lib.render_tab import RenderTab
from lib.my_tasks import MyTasks
from lib.task import Task
from lib.comments import CommentWidget
from lib.whats_new import WhatsNew
from lib.asset import Asset
from lib.asset_loader import AssetLoader
from lib.reference_moodboard import Moodboard_Creator
from lib.log import LogEntry
from lib.people import PeopleTab
from lib.batch_monitoring import Monitoring

from shotgun_api3 import Shotgun

class Main(QtGui.QWidget, Ui_Form, ReferenceTab, CommentWidget, Lib, TaskManager, MyTasks, WhatsNew, Asset, LogEntry, Task, AssetLoader, Moodboard_Creator, PeopleTab, RenderTab):
    def __init__(self):
        super(Main, self).__init__()

        self.username = os.getenv('USERNAME')

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)

        self.ReferenceTab = ReferenceTab
        self.Lib = Lib
        self.TaskManager = TaskManager
        self.RenderTab = RenderTab
        self.MyTasks = MyTasks
        self.WhatsNew = WhatsNew
        self.CommentWidget = CommentWidget
        self.Task = Task
        self.Asset = Asset
        self.AssetLoader = AssetLoader
        self.LogEntry = LogEntry
        self.Moodboard_Creator = Moodboard_Creator
        self.PeopleTab = PeopleTab

        sg_url = "http://nad.shotgunstudio.com"
        sg_script_name = "ThibaultGenericScript"
        sg_key = "e014f12acda4074561022f165e8cd1913af2ba4903324a72edbb21430abbb2dc"
        self.sg_project_id = 146

        self.sg = Shotgun(sg_url, sg_script_name, sg_key)

        # Initialize the guis
        self.Form = self.setupUi(self)
        self.Form.center_window()

        self.setMinimumSize(1453, 923)
        self.setMaximumSize(1453, 923)

        self.db_to_load = ""
        self.db_path = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\nature.sqlite"  # Database nature


        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            # Database Setup
            self.db_path = "H:\\01-NAD\\_pipeline\\_utilities\\_database\\db.sqlite"  # Copie de travail

        # Backup database
        if self.db_path not in ["H:\\01-NAD\\_pipeline\\_utilities\\_database\\db.sqlite", "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering.sqlite"]:
            self.backup_database()

        self.db = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        self.cursor = self.db.cursor()

        # Global Variables
        self.projectList.hide()
        self.i = 0
        self.computer_id = socket.gethostname()
        self.ref_assets_instances = []
        self.selected_asset = None
        self.utf8_codec = QtCore.QTextCodec.codecForName("utf-8")
        self.today = time.strftime("%d/%m/%Y", time.gmtime())
        self.cur_path = os.path.dirname(os.path.realpath(__file__))  # H:\01-NAD\_pipeline\_utilities\_asset_manager
        self.cur_path_one_folder_up = self.cur_path.replace("\\_asset_manager", "")  # H:\01-NAD\_pipeline\_utilities
        self.NEF_folder = self.cur_path_one_folder_up + "\\_NEF"  # H:\01-NAD\_pipeline\_utilities\NEF
        self.screenshot_dir = self.cur_path_one_folder_up + "\\_database\\screenshots\\"
        self.no_img_found = self.cur_path + "\\media\\no_img_found.png"
        self.number_of_refreshes = 0
        self.members = {"acorbin":"Alexandre", "fpasquarelli":"Francis", "costiguy": "Chloe", "cgonnord": "Christopher",
                        "erodrigue": "Etienne", "jberger": "Jeremy", "lgregoire": "Laurence",
                        "lclavet": "Louis-Philippe", "mbeaudoin": "Mathieu",
                        "mroz": "Maxime", "obolduc": "Olivier", "slachapelle": "Simon", "thoudon": "Thibault",
                        "vdelbroucq": "Valentin", "yjobin": "Yann", "yshan": "Yi"}
        self.sg_members = {"acorbin": "3dalcor", "fpasquarelli": "francis.pasquarelli", "costiguy": "ostiguy.chloe", "cgonnord": "christopher.gonnord",
                           "erodrigue": "etienne.rodrigue89", "jberger": "jeremy.berger3d", "lgregoire": "lau-gregoire",
                           "lclavet": "clavet.lp", "mbeaudoin": "beaudoinmathieu",
                           "mroz": "maximeroz", "obolduc": "ol.bolduc", "slachapelle": "simonlachapelle", "thoudon": "houdon.thibault",
                           "vdelbroucq": "valentin.delbroucq", "yjobin": "yannjobinphoto", "yshan": "yishan3d"}
        self.departments_shortname = {"Script": "spt", "Storyboard": "stb", "References": "ref", "Concepts": "cpt",
                                      "Modeling": "mod", "Texturing": "tex", "Rigging": "rig", "Animation": "anm",
                                      "Simulation": "sim", "Shading": "shd", "Camera": "cam", "Lighting": "lgt", "Layout": "lay", "DMP": "dmp", "Rendering":"rdr",
                                      "Compositing": "cmp", "Editing": "edt", "RnD": "rnd"}
        self.departments_longname = {"spt": "Script", "stb": "Storyboard", "ref": "References", "cam": "Camera", "cpt": "Concepts", "lgt": "Lighting",
                                     "mod": "Modeling", "tex": "Texturing", "rig": "Rigging", "anm": "Animation",
                                     "sim": "Simulation", "shd": "Shading", "lay": "Layout", "dmp": "DMP", "rdr":"Rendering",
                                     "cmp": "Compositing", "edt": "Editing", "rnd": "RnD"}

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

        # Clear temp folder
        if os.path.isdir("H:/tmp"):
            try:
                shutil.rmtree("H:/tmp")
            except:
                pass

        try:
            os.makedirs("H:/tmp")
        except:
            pass

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
        day_end = date(2016,4,25)
        day_today = datetime.now().date()

        months_and_days_left = relativedelta.relativedelta(day_end, day_today)

        total_days = abs(day_end - day_start).days
        remaining_days = abs(day_end - date.today()).days
        remaining_days_percent = (remaining_days * 100) / total_days # Converts number of remaining day to a percentage

        self.deadlineProgressBar.setFormat("{0} months and {1} days left ({2}%)".format(months_and_days_left.months, months_and_days_left.days, remaining_days_percent))
        self.deadlineProgressBar.setMaximum(total_days)
        self.deadlineProgressBar.setValue(remaining_days)
        hue = self.fit_range(remaining_days, 0, total_days, 0, 76)
        self.deadlineProgressBar.setStyleSheet("QProgressBar::chunk {background-color: hsl(" + str(hue) + ", 255, 205);}")

        if self.username not in ["thoudon", "lclavet", "costiguy"]:
            self.deadlineFrame.hide()

        # Setup disk usage progress bar
        disk_usage = self.Lib.get_folder_space(self)
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
        if os.path.exists("C:/Program Files/Mari2.6v2/Bundle/bin/Mari2.6v2.exe"):
            self.mari_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Mari"''').fetchone()[0])
        else:
            self.mari_path = "C:/Program Files/Mari2.6v5/Bundle/bin/Mari2.6v5.exe"
        self.blender_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Blender"''').fetchone()[0])

        self.cursor.execute('''UPDATE preferences SET is_online=1 WHERE username=?''', (self.username,))
        self.db.commit()

        # Preferences setup
        self.prefBckGroundColorSlider.sliderMoved.connect(self.change_pref_background_color_pixmap)
        self.prefBckGroundColorSlider.setStyleSheet("background-color; red;")

        # Set systray actions
        self.quitAction = QtGui.QAction("Quit", self, triggered=self.terminate_program)
        self.quitAction.setIcon(QtGui.QIcon(self.cur_path + "/media/turn_off.png"))

        # Systray icon
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.quitAction)

        self.tray_icon = QtGui.QIcon(self.cur_path + "\\media\\favicon_cube.png")
        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(self.tray_icon)

        self.tray_icon_log_id = ""
        self.tray_message = ""

        self.trayIcon.hide()

        #self.tray_icon.messageClicked.connect(self.tray_icon_message_clicked)
        self.trayIcon.activated.connect(self.tray_icon_clicked)

        # Initialize modules and connections
        AssetLoader.__init__(self)
        self.ReferenceTab.__init__(self)
        self.RenderTab.__init__(self)
        self.CommentWidget.__init__(self)
        self.WhatsNew.__init__(self)
        self.PeopleTab.__init__(self)
        self.WhatsNew.load_whats_new(self)
        self.check_last_active()

        #self.check_news_thread = CheckNews(self)
        #self.connect(self.check_news_thread, QtCore.SIGNAL("check_last_active"), self.check_last_active)
        #self.check_news_thread.daemon = True
        #self.check_news_thread.start()

        self.show()

        #self.check_shotgun_time_log()

    def check_shotgun_time_log(self):
        self.username = "mbeaudoin"
        peoples = {"acorbin":"Alexandre Corbin", "costiguy":"Chloé Ostiguy", "cgonnord":"Christopher Gonnord", "erodrigue":"Etienne Rodrigue", "fpasquarelli":"Francis Pasquarelli", "jberger":"Jérémy Berger", "lgregoire":"Laurence Grégoire", "lclavet":"Louis-Philippe Clavet", "mbeaudoin":"Mathieu Beaudoin", "mroz":"Maxime Roz", "thoudon":"Thibault Houdon", "vdelbroucq":"Valentin Delbroucq", "yjobin":"Yann Jobin", "yshan":"Yi Shan"}
        user = peoples[self.username]

        project = self.sg.find_one("Project", [["id", "is", self.sg_project_id]])
        time_log = self.sg.find("TimeLog", [["date", "in_calendar_day", -1], ["project", "is", project]], ["user"])
        people_logged = [log["user"]["name"] for log in time_log]
        people_logged = list(set(people_logged))

        if user not in people_logged:
            time_log_window = QtGui.QDialog(self)
            time_log_window.setWindowTitle("Add your time log entry")
            layout = QtGui.QVBoxLayout(time_log_window)
            descriptionLabel = QtGui.QLabel(time_log_window)
            durationLabel = QtGui.QLabel(time_log_window)
            descriptionLabel.setText("Description")
            durationLabel.setText("Duration")
            self.description = QtGui.QLineEdit(time_log_window)
            self.duration = QtGui.QLineEdit(time_log_window)

            addLogEntryBtn = QtGui.QPushButton(time_log_window)
            addLogEntryBtn.setText("Add Time Log Entry")
            addLogEntryBtn.clicked.connect(self.shotgun_add_time_log)

            didntWorkBtn = QtGui.QPushButton(time_log_window)
            didntWorkBtn.setText("I didn't work on this project yesterday.")

            layout.addWidget(durationLabel)
            layout.addWidget(self.duration)
            layout.addWidget(descriptionLabel)
            layout.addWidget(self.description)
            layout.addWidget(addLogEntryBtn)
            layout.addWidget(didntWorkBtn)

            time_log_window.exec_()

    def shotgun_add_empty_time_log(self):
        pass

    def shotgun_add_time_log(self):

        print(self.description.text())
        print(self.duration.text())

    def add_tag_to_tags_manager(self):
        # Check if a project is selected
        if len(self.projectList.currentText()) == 0:
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

    def remove_tabs_based_on_members(self):

        if not (self.username == "thoudon" or self.username == "lclavet"):
            self.adminPrefFrame.hide()
            self.createAssetFromScratchBtn.hide()

        self.get_tabs_id_from_name()


        if self.members[self.username] == "Chloe":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])

        elif self.members[self.username] == "Francis":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Render"])


        elif self.members[self.username] == "Alexandre":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Render"])


        elif self.members[self.username] == "Christopher":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])


        elif self.members[self.username] == "Etienne":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Render"])


        elif self.members[self.username] == "Jeremy":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Render"])


        elif self.members[self.username] == "Laurence":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Render"])

        elif self.members[self.username] == "Louis-Philippe":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])

        elif self.members[self.username] == "Mathieu":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Render"])


        elif self.members[self.username] == "Maxime":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])



        elif self.members[self.username] == "Olivier":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Render"])


        elif self.members[self.username] == "Simon":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Render"])


        elif self.members[self.username] == "Thibault":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()

        elif self.members[self.username] == "Yann":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Render"])

        elif self.members[self.username] == "Yi":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Render"])


        elif self.members[self.username] == "Valentin":
            self.Tabs.removeTab(self.tabs_list["Tasks"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Task Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Tags Manager"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Misc"])
            self.get_tabs_id_from_name()
            self.Tabs.removeTab(self.tabs_list["Render"])

    def get_tabs_id_from_name(self):
        self.tabs_list = {}
        for i in xrange(self.Tabs.count()):
            self.tabs_list[str(self.Tabs.tabText(i))] = i

    def change_username(self):
        username = str(self.usernameAdminComboBox.currentText())
        self.username = username

    def backup_database(self):
        # Get creation_time of last database backup and compare it to current  time
        database_files = Lib.get_files_from_folder(self, path="Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\_backup")
        if len(database_files) > 1000:
            self.Lib.message_box(self, type="error", text=u"Trop de backups détectés pour la base de donnée. Veuillez avertir Thibault, merci ;)")

        cur_db_name = os.path.split(self.db_path)[-1].replace(".sqlite", "")
        database_files = [i for i in database_files if cur_db_name in os.path.split(i)[-1]]
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
            shutil.copy(self.db_path, backup_database_filename)

    def refresh_all(self):
        self.blockSignals(True)

        #Default refreshes
        self.mt_item_added = True
        self.item_added = True
        self.setup_tags()

        #Get current tab text
        current_tab_text = self.Tabs.tabText(self.Tabs.currentIndex())

        if current_tab_text == "Asset Loader":
            self.statusLbl.setText("Status: Refreshing Asset Loader tab...")
            self.repaint()
            self.AssetLoader.load_all_assets_for_first_time(self)
            self.AssetLoader.load_assets_from_selected_seq_shot_dept(self)

        elif current_tab_text == "Task Manager":
            self.statusLbl.setText("Status: Refreshing Task Manager tab...")
            self.repaint()
            TaskManager.add_tasks_from_database(self)

        elif current_tab_text == "Tasks":
            self.statusLbl.setText("Status: Refreshing Tasks tab...")
            self.repaint()
            MyTasks.mt_add_tasks_from_database(self)

        elif current_tab_text == "Render":
            self.statusLbl.setText("Status: Refreshing Render tab...")
            self.repaint()
            RenderTab.add_computers_from_database(self)
            RenderTab.add_jobs_from_database(self)
            RenderTab.add_frames_from_database(self)

        elif current_tab_text == "People":
            self.statusLbl.setText("Status: Refreshing People tab...")
            self.repaint()
            self.PeopleTab.get_online_status(self)
            self.cursor.execute('''UPDATE preferences SET last_active=? WHERE username=?''', (datetime.now().strftime("%d/%m/%Y at %H:%M"), self.username,))
            self.db.commit()

        elif current_tab_text == "Images Manager":
            self.statusLbl.setText("Status: Refreshing Images Manager tab...")
            self.repaint()
            if len(self.ref_assets_instances) > 1:
                self.ReferenceTab.refresh_reference_list(self)

        elif "What's New" in current_tab_text:
            self.statusLbl.setText("Status: Refreshing What's New tab...")
            self.repaint()
            self.WhatsNew.load_whats_new(self)

        self.statusLbl.setText("Status: Idle...")
        self.blockSignals(False)

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
                self.Form.setStyleSheet(QtCore.QVariant(css.readAll()).toString().replace("checkbox|placeholder", self.cur_path.replace("\\", "/") + "/media/checkbox.png"))
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

        asset = self.Asset(main=self, id=clicked_log_entry, get_infos_from_id=True)

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
                self.trayIcon.hide()
            else:
                self.hide()
                self.trayIcon.show()

    def keyPressEvent(self, event):

        global_pos = self.mapFromGlobal(QtGui.QCursor.pos())
        widget_under_mouse = self.childAt(global_pos)

        key = event.key()
        if key == QtCore.Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif key == QtCore.Qt.Key_Delete:
            current_tab_text = self.Tabs.tabText(self.Tabs.currentIndex())
            if current_tab_text == "Images Manager":
                ReferenceTab.remove_selected_references(self)
        elif key == QtCore.Qt.Key_F2:
            selected_reference = self.referenceThumbListWidget.selectedItems()[0]
            asset = selected_reference.data(QtCore.Qt.UserRole).toPyObject()
            ReferenceTab.rename_reference(self, asset)

        elif key == QtCore.Qt.Key_F1:
            self.show_wiki_help(widget_under_mouse)

        elif key == QtCore.Qt.Key_F5:
            self.refresh_all()

    def show_wiki_help(self, widget):
        if widget.objectName() == "publishBtn":
            subprocess.Popen(["C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe", "file:///Z:/Groupes-cours/NAND999-A15-N01/Nature/_info/wiki/wiki.html#Modeling"])

    def closeEvent(self, event):
        if not self.trayIcon.isVisible():
            self.setWindowFlags(QtCore.Qt.Tool)
            self.hide()
            self.trayIcon.show()
            self.tray_message = "Manager is in background mode."
            self.trayIcon.showMessage('Still running...', self.tray_message, QtGui.QSystemTrayIcon.Information, 1000)
            self.hide()
            event.ignore()
            self.trayIcon.show()

    def terminate_program(self):
        # tasks = subprocess.check_output(['tasklist'])
        # if "houdin" in tasks.lower():
        #     self.Lib.message_box(self, type="error", text="Please close Houdini layout scenes before closing the Manager!")
        #     return


        self.cursor.execute('''UPDATE preferences SET is_online=0 WHERE username=?''', (self.username,))
        self.db.commit()
        self.Lib.switch_mari_cache(self, "perso")
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
                self.trayIcon.show()
                self.tray_message = "Manager is in background mode."
                self.trayIcon.showMessage('Still running...', self.tray_message, QtGui.QSystemTrayIcon.Information, 1000)

    def check_last_active(self):
        for user in self.members.keys():
            last_active = datetime.now().strftime("%d/%m/%Y at %H:%M")
            last_active_datetime = datetime.strptime(last_active, '%d/%m/%Y at %H:%M')

            last_active_db = self.cursor.execute('''SELECT last_active FROM preferences WHERE username=?''', (user, )).fetchone()[0]
            last_active_db_datetime = datetime.strptime(last_active_db, '%d/%m/%Y at %H:%M')

            time_difference = last_active_datetime - last_active_db_datetime
            if time_difference.seconds > 600:
                self.cursor.execute('''UPDATE preferences SET is_online=0 WHERE username=?''', (user,))
            else:
                self.cursor.execute('''UPDATE preferences SET is_online=1 WHERE username=?''', (user,))

        last_active = datetime.now().strftime("%d/%m/%Y at %H:%M")
        self.cursor.execute('''UPDATE preferences SET last_active=? WHERE username=?''', (last_active, self.username,))
        self.db.commit()


class CheckNews(QtCore.QThread):
    def __init__(self, main):
        QtCore.QThread.__init__(self)
        self.main = main

    def run(self):
        while True:
            self.emit(QtCore.SIGNAL("check_last_active"))
            time.sleep(300)


if __name__ == "__main__":

    log_to_file = False
    cur_path = os.path.dirname(os.path.realpath(__file__))
    cur_path_one_folder_up = cur_path.replace("\\_asset_manager", "")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s ::: %(filename)s ::: ''%(funcName)s() ::: line ''%(lineno)d ::: ''%(message)s')
    file_handler = RotatingFileHandler(cur_path_one_folder_up + '\\_database\\activity.log', 'a', 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.DEBUG)
    logger.addHandler(steam_handler)

    if log_to_file == False:
        app = QtGui.QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        window = Main()

        sys.exit(app.exec_())
    else:
        try:
            app = QtGui.QApplication(sys.argv)
            app.setQuitOnLastWindowClosed(False)

            window = Main()

            sys.exit(app.exec_())
        except Exception as e:
            logger.debug(e)


