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
from functools import partial
import sqlite3
import time
import shutil

from datetime import date
from datetime import datetime
from collections import Counter

from PyQt4 import QtGui, QtCore, Qt

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

import logging
from logging.handlers import RotatingFileHandler


class Main(QtGui.QWidget, Ui_Form, ReferenceTab, Lib, TaskManager, MyTasks, WhatsNew, Asset, Task):
    def __init__(self):
        super(Main, self).__init__()
        #QtGui.QMainWindow.__init__(self)
        #Ui_Form.__init__(self)

        self.ReferenceTab = ReferenceTab
        self.Lib = Lib
        self.TaskManager = TaskManager
        self.MyTasks = MyTasks
        self.WhatsNew = WhatsNew
        self.CommentWidget = CommentWidget
        self.Task = Task
        self.Asset = Asset

        # Database Setup
        self.db_path = "H:\\01-NAD\\_pipeline\\_utilities\\_database\\db.sqlite" # Copie de travail
        #self.db_path = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\db.sqlite" # Database officielle
        #self.db_path = "C:\\Users\\Thibault\\Desktop\\db.sqlite" # Database maison

        # Backup database
        self.backup_database()

        self.db = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.db.cursor()

        # Initialize the guis
        self.Form = self.setupUi(self)
        self.Form.center_window()

        # Get projects from database and add them to the projects list
        self.projects = self.cursor.execute('''SELECT project_name FROM projects''').fetchall()
        self.projects = [str(i[0]) for i in self.projects]
        for project in self.projects:
            self.projectList.addItem(project)

        # Global Variables
        self.cur_path = os.path.dirname(os.path.realpath(__file__))  # H:\01-NAD\_pipeline\_utilities\_asset_manager
        self.cur_path_one_folder_up = self.cur_path.replace("\\_asset_manager", "")  # H:\01-NAD\_pipeline\_utilities
        self.screenshot_dir = self.cur_path_one_folder_up + "\\_database\\screenshots\\"
        self.username = os.getenv('USERNAME')
        self.members = {"achaput": "Amelie", "costiguy": "Chloe", "cgonnord": "Christopher", "dcayerdesforges": "David",
                        "earismendez": "Edwin", "erodrigue": "Etienne", "jberger": "Jeremy", "lgregoire": "Laurence",
                        "lclavet": "Louis-Philippe", "mchretien": "Marc-Antoine", "mbeaudoin": "Mathieu",
                        "mroz": "Maxime", "obolduc": "Olivier", "slachapelle": "Simon", "thoudon": "Thibault",
                        "vdelbroucq": "Valentin", "yjobin": "Yann", "yshan": "Yi"}
        refresh_icon = QtGui.QIcon(self.cur_path + "\\media\\refresh.png")
        self.refreshAllBtn.setIcon(refresh_icon)
        self.refreshAllBtn.setIconSize(QtCore.QSize(24, 24))
        self.refreshAllBtn.clicked.connect(self.refresh_all)

        # Setup logging error
        self.Lib.log_error_setup(self)

        # Select default project
        self.projectList.setCurrentRow(0)
        self.projectList_Clicked()

        self.selected_project_name = str(self.projectList.selectedItems()[0].text())
        self.selected_sequence_name = "xxx"
        self.selected_shot_number = "xxxx"
        #self.selected_department_name = str(self.departmentList.item(0).text())
        self.today = time.strftime("%d/%m/%Y", time.gmtime())


        # Create Favicon
        self.app_icon = QtGui.QIcon()
        self.app_icon.addFile(self.cur_path + "\\media\\favicon.png", QtCore.QSize(16, 16))
        self.Form.setWindowIcon(self.app_icon)

        # Set the StyleSheet
        self.themePrefComboBox.currentIndexChanged.connect(self.change_theme)
        theme = self.cursor.execute('''SELECT theme FROM preferences WHERE username=?''', (self.username,)).fetchone()[0]
        self.themePrefComboBox.setCurrentIndex(int(theme))
        self.change_theme()


        # Overrides
        self.publishBtn.setStyleSheet("background-color: #77D482;")
        self.loadBtn.setStyleSheet(
            "QPushButton {background-color: #77B0D4;} QPushButton:hover {background-color: #1BCAA7;}")
        font = QtGui.QFont()
        font.setPointSize(12)

        eye_icon = QtGui.QPixmap(self.cur_path + "\\media\\eye_icon.png")
        eye_icon = QtGui.QIcon(eye_icon)
        self.showUrlImageBtn.setIcon(eye_icon)

        # Admin Setup
        self.remove_tabs_based_on_members()

        # Tags setup
        self.setup_tags()

        # Get remaining time and set deadline Progress Bar
        day_start = date(2015,6,28)
        day_end = date(2016,5,1)
        day_today = date.today()

        total_days = abs(day_end - day_start).days
        remaining_days = abs(day_end - day_today).days
        remaining_days_percent = (remaining_days * 100) / total_days # Converts number of remaining day to a percentage

        self.deadlineProgressBar.setFormat("{0} days left ({1}%)".format(remaining_days, remaining_days_percent))
        self.deadlineProgressBar.setMaximum(total_days)
        self.deadlineProgressBar.setValue(remaining_days)
        self.deadlineProgressBar.setStyleSheet("")
        if remaining_days >= 231:
            self.deadlineProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #98cd00;} QProgressBar {color: #323232;}")
        elif remaining_days >= 154:
            self.deadlineProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #d7b600;} QProgressBar {color: #fff;}")
        elif remaining_days >= 77:
            self.deadlineProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #f35905;} QProgressBar {color: #fff;}")
        elif remaining_days >= 0:
            self.deadlineProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #fe2200;} QProgressBar {color: #fff;}")

        # Setup disk usage progress bar
        disk_usage = Lib.get_folder_space(self)
        disk_usage = int(float(disk_usage) * 1000) # Multiply disk usage by 1000. Ex: 1.819 to 1819
        disk_usage = (2000 * int(disk_usage)) / 1862 # 2TO in theory = 1.862GB in reality. Remapping real disk usage to the theoric one
        self.diskUsageProgressBar.setFormat('{0}/2000 GB'.format(str(disk_usage)))
        self.diskUsageProgressBar.setRange(0, 2000)
        self.diskUsageProgressBar.setValue(int(disk_usage))
        if disk_usage >= 1500:
            self.diskUsageProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #98cd00;} QProgressBar {color: #323232;}")
        elif disk_usage >= 1000:
            self.diskUsageProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #d7b600;} QProgressBar {color: #323232;}")
        elif disk_usage >= 500:
            self.diskUsageProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #f35905;} QProgressBar {color: #323232;}")
        elif disk_usage >= 0:
            self.diskUsageProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #fe2200;} QProgressBar {color: #323232;}")


        # Get software paths from database and put them in preference
        self.photoshop_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Photoshop"''').fetchone()[0])
        self.maya_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Maya"''').fetchone()[0])
        self.softimage_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Softimage"''').fetchone()[0])
        self.houdini_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Houdini"''').fetchone()[0])
        self.cinema4d_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Cinema 4D"''').fetchone()[0])
        self.nuke_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Nuke"''').fetchone()[0])
        self.zbrush_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="ZBrush"''').fetchone()[0])
        self.mari_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Mari"''').fetchone()[0])
        self.blender_path = str(self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Blender"''').fetchone()[0])

        self.photoshopPathLineEdit.setText(self.photoshop_path)
        self.mayaPathLineEdit.setText(self.maya_path)
        self.softimagePathLineEdit.setText(self.softimage_path)
        self.houdiniPathLineEdit.setText(self.houdini_path)
        self.cinema4dPathLineEdit.setText(self.cinema4d_path)
        self.nukePathLineEdit.setText(self.nuke_path)
        self.zbrushPathLineEdit.setText(self.zbrush_path)
        self.mariPathLineEdit.setText(self.mari_path)
        self.blenderPathLineEdit.setText(self.blender_path)

        # Filtering options
        self.meOnlyCheckBox.stateChanged.connect(self.filter_assets_for_me)

        # Connect the filter textboxes
        self.seqFilter.textChanged.connect(partial(self.filterList_textChanged, "sequence"))
        self.assetFilter.textChanged.connect(partial(self.filterList_textChanged, "asset"))

        # Connect the lists
        self.projectList.itemClicked.connect(self.projectList_Clicked)
        self.projectList.itemDoubleClicked.connect(self.projectList_DoubleClicked)
        self.departmentList.itemClicked.connect(self.load_assets_from_selected_proj_seq_shot_dept)
        self.seqList.itemClicked.connect(self.seqList_Clicked) # seqList is not calling load_asset_from_selected_proj_seq_shot_dept because it needs to set the shot list
        self.shotList.itemClicked.connect(self.load_assets_from_selected_proj_seq_shot_dept)
        self.assetList.itemClicked.connect(self.assetList_Clicked)
        self.versionList.itemClicked.connect(self.versionList_Clicked)

        self.usernameAdminComboBox.currentIndexChanged.connect(self.change_username)

        # Connect the buttons
        self.addProjectBtn.clicked.connect(self.add_project)
        self.addSequenceBtn.clicked.connect(self.add_sequence)
        self.addShotBtn.clicked.connect(self.add_shot)

        self.seqFilterClearBtn.clicked.connect(partial(self.clear_filter, "seq"))
        self.assetFilterClearBtn.clicked.connect(partial(self.clear_filter, "asset"))
        self.loadBtn.clicked.connect(self.load_asset)
        self.openInExplorerBtn.clicked.connect(partial(Lib.open_in_explorer, self))
        self.addCommentBtn.clicked.connect(self.add_comment)
        self.updateThumbBtn.clicked.connect(self.update_thumb)

        # Tags Manager Buttons
        self.addTagBtn.clicked.connect(self.add_tag_to_tags_manager)
        self.addTagLineEdit.returnPressed.connect(self.add_tag_to_tags_manager)
        self.removeSelectedTagsBtn.clicked.connect(self.remove_selected_tags_from_tags_manager)

        # Systray icon
        self.tray_icon_log_id = ""
        self.tray_icon = QtGui.QSystemTrayIcon(QtGui.QIcon(self.cur_path + "\\media\\favicon.png"), app)
        self.tray_icon.messageClicked.connect(self.tray_icon_message_clicked)
        self.tray_icon.activated.connect(self.tray_icon_clicked)
        self.tray_message = ""

        # Initialize modules and connections
        ReferenceTab.__init__(self)
        TaskManager.__init__(self)
        MyTasks.__init__(self)
        WhatsNew.__init__(self)

        self.check_news_thread = CheckNews(self)
        self.check_news_thread.daemon = True
        self.check_news_thread.start()

    def add_project(self):
        if not str(self.addProjectLineEdit.text()):
            Lib.message_box(text="Please enter a project name")
            return

        project_name = str(self.addProjectLineEdit.text())
        project_shortname = str(self.projectShortnameLineEdit.text())
        selected_folder = str(QtGui.QFileDialog.getExistingDirectory())

        # Prevent two projects from having the same name
        all_projects_name = self.cursor.execute('''SELECT project_name FROM projects''').fetchall()
        all_projects_name = [i[0] for i in all_projects_name]
        if project_name in all_projects_name:
            Lib.message_box(text="Project name is already taken.")
            return

        # Create project's folder
        project_path = selected_folder + "\\" + project_name
        os.makedirs(project_path + "\\assets")
        os.makedirs(project_path + "\\assets\\spt")
        os.makedirs(project_path + "\\assets\\stb")
        os.makedirs(project_path + "\\assets\\ref")
        os.makedirs(project_path + "\\assets\\cpt")
        os.makedirs(project_path + "\\assets\\mod")
        os.makedirs(project_path + "\\assets\\tex")
        os.makedirs(project_path + "\\assets\\rig")
        os.makedirs(project_path + "\\assets\\anm")
        os.makedirs(project_path + "\\assets\\sim")
        os.makedirs(project_path + "\\assets\\shd")
        os.makedirs(project_path + "\\assets\\lay")
        os.makedirs(project_path + "\\assets\\dmp")
        os.makedirs(project_path + "\\assets\\cmp")
        os.makedirs(project_path + "\\assets\\edt")
        os.makedirs(project_path + "\\assets\\rnd")

        # Add project to database
        self.cursor.execute('''INSERT INTO projects(project_name, project_shortname, project_path) VALUES (?, ?, ?)''',
                            (project_name, project_shortname, project_path))
        self.db.commit()

        # Get projects from database and add them to the projects list
        self.projectList.clear()
        projects = self.cursor.execute('''SELECT * FROM projects''')
        for project in projects:
            self.projectList.addItem(project[1])

    def add_sequence(self):

        """Add specified sequence to the selected project
        """

        sequence_name = str(self.addSequenceLineEdit.text())

        # Check if user entered a 3 letter sequence name
        if len(sequence_name) == 0:
            Lib.message_box(text="Please enter a sequence name")
            return
        elif len(sequence_name) < 3:
            Lib.message_box(text="Please enter a 3 letters name")
            return

        # Check if a project is selected
        if not self.projectList.selectedItems():
            Lib.message_box(text="Please select a project first")
            return

        # Prevent two sequences from having the same name
        all_sequences_name = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''',
                                                 (self.selected_project_name,)).fetchall()
        all_sequences_name = [i[0] for i in all_sequences_name]
        if sequence_name in all_sequences_name:
            Lib.message_box(text="Sequence name is already taken.")
            return

        # Add sequence to database
        self.cursor.execute('''INSERT INTO sequences(project_name, sequence_name) VALUES (?, ?)''',
                            (self.selected_project_name, sequence_name))

        self.db.commit()

        # Add sequence to GUI
        self.seqList.addItem(sequence_name)
        self.seqList_Clicked()

    def add_shot(self):

        shot_number = str(self.shotSpinBox.text()).zfill(4)

        # Check if a project and a sequence are selected
        if not (self.projectList.selectedItems() and self.seqList.selectedItems()):
            Lib.message_box(text="Please select a project and a sequence first.")
            return

        # Prevent two shots from having the same number
        all_shots_number = self.cursor.execute(
            '''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
            (self.selected_project_name, self.selected_sequence_name)).fetchall()
        all_shots_number = [i[0] for i in all_shots_number]
        if shot_number in all_shots_number:
            Lib.message_box(text="Shot number already exists.")
            return

        # Add shot to database
        self.cursor.execute('''INSERT INTO shots(project_name, sequence_name, shot_number) VALUES (?, ?, ?)''',
                            (self.selected_project_name, self.selected_sequence_name, shot_number))

        self.db.commit()

        # Add shot to GUI
        self.shotList.addItem(shot_number)
        self.seqList_Clicked()

    def load_all_assets_for_first_time(self):
        '''
        Add all assets from selected project. Only run once to rebuild assets objects from Asset class.
        '''

        all_assets = self.cursor.execute('''SELECT DISTINCT asset_name FROM assets WHERE project_name=?''', (self.selected_project_name,)).fetchall()
        for asset in all_assets:
            asset_name = asset[0]
            # sequence_name = asset[2]
            # shot_number = asset[3]
            # asset_name = asset[4]
            # asset_path = asset[5]
            # asset_type = asset[6]
            # asset_version = asset[7]
            # asset_comment = asset[8]
            # asset_tags = asset[9]
            # asset_dependency = asset[11]
            # last_access = asset[12]
            # creator = asset[13]
            #
            # asset_item = QtGui.QListWidgetItem(asset_name)
            # asset = Asset(sequence_name, shot_number, asset_name, asset_path, asset_type, asset_version,
            #               asset_comment, asset_tags, asset_dependency, last_access, creator)
            # asset_item.setData(QtCore.Qt.UserRole, asset)
            self.assetList.addItem(asset_name)

    def filterList_textChanged(self, list_type):

        if list_type == "sequence":
            seq_filter_str = str(self.seqFilter.text())
            if seq_filter_str > 0:
                for i in xrange(0, self.seqList.count()):
                    if seq_filter_str.lower() in self.seqList.item(i).text():
                        self.seqList.setItemHidden(self.seqList.item(i), False)
                    else:
                        self.seqList.setItemHidden(self.seqList.item(i), True)


        elif list_type == "asset":
            asset_filter_str = str(self.assetFilter.text())
            if asset_filter_str > 0:
                for i in xrange(0, self.assetList.count()):
                    if asset_filter_str.lower() in self.assetList.item(i).text():
                        self.assetList.setItemHidden(self.assetList.item(i), False)
                    else:
                        self.assetList.setItemHidden(self.assetList.item(i), True)

    def projectList_Clicked(self):

        # Query the project id based on the name of the selected project
        self.selected_project_name = str(self.projectList.selectedItems()[0].text())
        self.selected_project_path = str(
            self.cursor.execute('''SELECT project_path FROM projects WHERE project_name=?''',
                                (self.selected_project_name,)).fetchone()[0])

        self.selected_project_shortname = str(
            self.cursor.execute('''SELECT project_shortname FROM projects WHERE project_name=?''',
                                (self.selected_project_name,)).fetchone()[0])


        # Query the departments associated with the project
        self.departments = (self.cursor.execute('''SELECT DISTINCT asset_type FROM assets WHERE project_name=?''',
                                                (self.selected_project_name,))).fetchall()

        # Populate the departments list
        self.departmentList.clear()
        [self.departmentList.addItem(department[0]) for department in self.departments]
        try:
            self.departmentList.setCurrentRow(0)
        except:
            pass


        # Query the sequences associated with the project
        self.sequences = (self.cursor.execute('''SELECT DISTINCT sequence_name FROM sequences WHERE project_name=?''',
                                              (self.selected_project_name,))).fetchall()
        self.sequences = sorted(self.sequences)

        # Query the shots associated with each sequence
        self.shots = {}
        for seq in self.sequences:
            shots = (self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''', (self.selected_project_name, seq[0],))).fetchall()
            shots = [str(shot[0]) for shot in shots]
            self.shots[str(seq[0])] = shots

        # Populate the sequences lists
        self.seqList.clear()
        self.seqList.addItem("None")
        self.seqReferenceList.clear()
        self.seqReferenceList.addItem("All")
        self.seqReferenceList.addItem("None")
        self.shotList.clear()
        self.shotList.addItem("None")
        self.shotReferenceList.clear()
        self.shotReferenceList.addItem("None")
        [(self.seqList.addItem(sequence[0]), self.seqReferenceList.addItem(sequence[0])) for sequence in self.sequences]

        self.load_all_assets_for_first_time()

        # Select "All" from sequence list and "None" from shot list
        self.seqList.setCurrentRow(0)
        self.shotList.setCurrentRow(0)

    def seqList_Clicked(self):
        self.selected_sequence_name = str(self.seqList.selectedItems()[0].text())

        # Add shots to shot list and reference tool shot list
        if self.selected_sequence_name == "None":
            self.selected_sequence_name = "xxx"
            self.shotList.clear()
            self.shotList.addItem("None")
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")
        else:
            shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
                                        (self.selected_project_name, self.selected_sequence_name,)).fetchall()
            self.shotList.clear()
            self.shotList.addItem("None")
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")
            shots = [i[0] for i in shots]
            shots = sorted(shots)
            [(self.shotList.addItem(shot), self.shotReferenceList.addItem(shot)) for shot in shots]

        self.shotList.setCurrentRow(0)
        self.load_assets_from_selected_proj_seq_shot_dept()

    def assetList_Clicked(self, item_clicked=None):
        self.selected_asset_name = str(item_clicked.text())
        all_versions = self.cursor.execute('''SELECT asset_version FROM assets WHERE project_name=? AND asset_name=?''',
                                           (self.selected_project_name, self.selected_asset_name,)).fetchall()

        all_versions = [str(i[0]) for i in all_versions]

        self.versionList.clear()
        for version in all_versions:
            asset = self.cursor.execute(
                '''SELECT * FROM assets WHERE project_name=? AND asset_name=? AND asset_version=? AND asset_type=?''',
                (self.selected_project_name, self.selected_asset_name, version, self.selected_department_name)).fetchone()
            self.versionList.addItem(asset[7])

        return

        self.versionList.addItems()
        # print(selected_asset.data(QtCore.Qt.UserRole).toPyObject())
        return

        self.selected_asset_type = str(self.assetList.selectedItems()[0].text()).split("_")[0]
        self.selected_asset_name = str(self.assetList.selectedItems()[0].text()).split("_")[1]
        self.selected_asset_version = str(self.assetList.selectedItems()[0].text()).split("_")[2]
        self.selected_asset_path = self.cursor.execute(
            '''SELECT asset_path FROM assets WHERE project_name=? AND asset_type=? AND asset_name=? AND asset_version=?''',
            (self.selected_project_name, self.selected_asset_type, self.selected_asset_name,
             self.selected_asset_version)).fetchone()[0]

        cur_asset = Asset(self.selected_asset_name, self.selected_asset_path)
        cur_asset.create_version(self.selected_project_name)

        asset_extension = os.path.splitext(self.selected_asset_path)[-1]
        if self.selected_asset_path.endswith(".jpg") or self.selected_asset_path.endswith(".png"):

            self.fileTypeLbl.setText("Image (" + asset_extension + ")")

            for i in reversed(range(self.actionFrameLayout.count())):  # Delete all items from layout
                self.actionFrameLayout.itemAt(i).widget().close()

            # Create action interface
            self.loadInKuadroBtn = QtGui.QPushButton(self.actionFrame)
            self.actionFrameLayout.addWidget(self.loadInKuadroBtn)
            self.loadInKuadroBtn.setText("Load in Kuadro")
            self.loadInKuadroBtn.clicked.connect(partial(self.load_asset, "Kuadro"))

        elif self.selected_asset_path.endswith(".mb") or self.selected_asset_path.endswith(".ma"):
            self.fileTypeLbl.setText("Maya (" + asset_extension + ")")

        elif self.selected_asset_path.endswith(".obj"):
            self.fileTypeLbl.setText("Geometry (" + asset_extension + ")")


        # Load thumbnail image
        if self.selected_asset_path.endswith(".jpg") or self.selected_asset_path.endswith(".png"):
            pixmap = QtGui.QPixmap(self.selected_asset_path).scaled(1000, 200, QtCore.Qt.KeepAspectRatio,
                                                                    QtCore.Qt.SmoothTransformation)
            self.assetImg.setPixmap(pixmap)
        else:
            asset_name = "_".join([self.selected_asset_type, self.selected_asset_name, self.selected_asset_version])
            thumb_path = self.screenshot_dir + asset_name + ".jpg"
            if os.path.isfile(thumb_path):
                pixmap = QtGui.QPixmap(thumb_path).scaled(1000, 200, QtCore.Qt.KeepAspectRatio,
                                                          QtCore.Qt.SmoothTransformation)
                self.assetImg.setPixmap(pixmap)
            else:
                pixmap = QtGui.QPixmap(self.screenshot_dir + "default\\no_img_found.png").scaled(1000, 200,
                                                                                                 QtCore.Qt.KeepAspectRatio,
                                                                                                 QtCore.Qt.SmoothTransformation)
                self.assetImg.setPixmap(pixmap)

        # Change path label
        self.assetPathLbl.setText(self.selected_asset_path)

        # Load comments
        self.commentTxt.setText("")  # Clear comment section
        asset_comment = self.cursor.execute(
            '''SELECT asset_comment FROM assets WHERE project_name=? AND asset_type=? AND asset_name=? AND asset_version=?''',
            (self.selected_project_name, self.selected_asset_type, self.selected_asset_name,
             self.selected_asset_version)).fetchone()[0]
        if asset_comment:
            self.commentTxt.setText(asset_comment)

    def versionList_Clicked(self, item_clicked=None):
        selected_version = item_clicked

    def projectList_DoubleClicked(self):
        subprocess.Popen(r'explorer /select,' + str(self.selected_project_path))

    def load_assets_from_selected_proj_seq_shot_dept(self):
        return
        # Get selected sequence name
        try:
            self.selected_sequence_name = str(self.seqList.selectedItems()[0].text())
            if self.selected_sequence_name == "None": self.selected_sequence_name = "xxx"
        except:
            self.selected_sequence_name = "xxx"


        # Get selected shot number
        try:
            self.selected_shot_number = str(self.shotList.selectedItems()[0].text())
            if self.selected_shot_number == "None": self.selected_shot_number = "xxxx"
        except:
            self.selected_shot_number = "xxxx"

        # Get selected department name
        try:
            self.selected_department_name = str(self.departmentList.selectedItems()[0].text())
        except:
            self.selected_department_name = "xxx"

        query_str = "SELECT * FROM assets"
        where_statment = []
        if self.selected_sequence_name != "xxx":
            where_statment.append("sequence_name='" + self.selected_sequence_name + "'")

        if self.selected_shot_number != "xxxx":
            where_statment.append("shot_number='" + self.selected_shot_number + "'")

        if self.selected_department_name != "xxx":
            where_statment.append("asset_type='" + self.selected_department_name + "'")

        where_statment = " AND ".join(where_statment)
        if len(where_statment) > 0:
            query_str += " WHERE " + where_statment

        assets = self.cursor.execute(query_str).fetchall()


        for asset in assets:
            sequence_name = asset[2]
            shot_number = asset[3]
            asset_name = asset[4]
            asset_path = asset[5]
            asset_type = asset[6]
            asset_version = asset[7]
            asset_comment = asset[8]
            asset_tags = asset[9]
            asset_dependency = asset[11]
            last_access = asset[12]
            creator = asset[13]

            asset_item = QtGui.QListWidgetItem(asset_name)
            asset = Asset(sequence_name, shot_number, asset_name, asset_path, asset_type, asset_version,
                           asset_comment, asset_tags, asset_dependency, last_access, creator)

            #self.assetList.addItem(asset_name)

    def check_if_asset_already_exists(self, asset_path, asset_name, asset_type):
        if os.path.isfile(asset_path):
            asset_tmp = asset_name
            folder_path = "\\".join(asset_path.split("\\")[0:-1])
            assets_name_list = []

            new_asset_name = asset_name

            for cur_file in next(os.walk(folder_path))[2]:
                if asset_tmp in cur_file and asset_type in cur_file:
                    assets_name_list.append(cur_file.split("_")[1])

            assets_name_list = sorted(assets_name_list)
            try:
                asset_nbr = int(assets_name_list[-1].split("-")[-1])
                asset_nbr += 1
                new_asset_name += "-" + str(asset_nbr).zfill(3)
            except:
                new_asset_name += "-001"

            asset_path = asset_path.replace(asset_name, new_asset_name)

            return (asset_path, new_asset_name)
        else:
            return (asset_path, asset_name)

    def load_asset(self, action):
        if action == "Kuadro":

            if not QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
                os.system("taskkill /im kuadro.exe /f")
            subprocess.Popen(
                ["H:\\01-NAD\\_pipeline\\_utilities\\_soft\\kuadro.exe", self.selected_asset_path])
            return




        # Add last_access entry to database
        last_access = time.strftime("%B %d %Y at %H:%M:%S") + " by " + self.username
        self.cursor.execute('''UPDATE assets SET last_access = ? WHERE asset_path = ?''',
                            (last_access, self.selected_asset_path))

        self.db.commit()

        if self.selected_asset_path.endswith(".jpg") or self.selected_asset_path.endswith(
                ".png") or self.selected_asset_path.endswith(".obj"):
            SoftwareDialog(self.selected_asset_path, self).exec_()
        elif self.selected_asset_path.endswith(".ma") or self.selected_asset_path.endswith(".mb"):
            subprocess.Popen(["C:\\Program Files\\Autodesk\\Maya2015\\bin\\maya.exe", self.selected_asset_path])

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

    def add_comment(self):
        if self.username == "Thibault":
            username = "<font color=red>Thibault</font>"

        # Check if there is already a comment or not to avoid empty first line due to HTML
        if self.commentTxt.toPlainText():
            comments = str(self.commentTxt.toHtml())
        else:
            comments = str(self.commentTxt.toPlainText())

        new_comment = "<b>{1}</b>: {0} ({2})\n".format(str(self.commentTxtLine.text()), username,
                                                       time.strftime("%d/%m/%Y"))
        new_comment = comments + new_comment
        self.cursor.execute('''UPDATE assets SET asset_comment = ? WHERE asset_path = ?''',
                            (new_comment, self.selected_asset_path,))
        self.db.commit()

        # Update comment field
        asset_comment = self.cursor.execute('''SELECT asset_comment FROM assets WHERE asset_path=?''',
                                            (self.selected_asset_path,)).fetchone()[0]
        self.commentTxt.setText(asset_comment)

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

        tabs_list = {}

        for i in xrange(self.Tabs.count()):
            tabs_list[str(self.Tabs.tabText(i))] = i

        if self.members[self.username] == "Amelie":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Chloe":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Christopher":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "David":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Edwin":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Etienne":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Jeremy":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Laurence":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Louis-Philippe":
            pass

        elif self.members[self.username] == "Marc-Antoine":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Mathieu":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Maxime":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Olivier":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Simon":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Thibault":
            pass

        elif self.members[self.username] == "Yann":
            self.Tabs.removeTab(tabs_list["Task Manager"])

        elif self.members[self.username] == "Yi":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

        elif self.members[self.username] == "Valentin":
            self.Tabs.removeTab(tabs_list["Task Manager"])
            self.Tabs.removeTab(tabs_list["Tags Manager"])

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

    def setup_tags(self):

        self.allTagsTreeWidget.clear()
        self.tagsTreeWidget.clear()

        self.tagsTreeWidget.itemSelectionChanged.connect(self.save_tags_list)

        # Select all tags
        tags = self.cursor.execute('''SELECT * FROM tags WHERE project_name=?''', (self.selected_project_name,)).fetchall()

        # Select all tags associated to assets
        tags_frequency = self.cursor.execute('''SELECT asset_tags FROM assets''').fetchall()
        tags_frequency_tmp = []

        # Create a list with all asset tags (ex: ["feu", "lighting", "feu", "feu", "lighting", "architecture"])
        for tag in tags_frequency:
            tag = list(tag)[0]
            try:
                tag = tag.split(",")
                tags_frequency_tmp.append(tag)
            except:
                tags_frequency_tmp.append(tag)

        tags_frequency_tmp = filter(None, tags_frequency_tmp)
        tags_frequency_tmp = sum(tags_frequency_tmp, []) # Join all lists into one list
        tags_frequency_tmp = [str(i) for i in tags_frequency_tmp] # Convert all items from unicode to string
        self.tags_frequency = Counter(tags_frequency_tmp) # Create a dictionary from list with number of occurences

        if len(self.tags_frequency.values()) > 0:
            self.maximum_tag_occurence = max(self.tags_frequency.values())
        else:
            self.maximum_tag_occurence = 1

        parent_tags = []
        child_tags = []

        # Separate parent tags to children tags
        for tag in tags:
            tag_name = tag[2]
            tag_parent = tag[3]
            if tag_parent:
                child_tags.append(tag)
            else:
                parent_tags.append(tag)

        # Add all parents tags to the tags manager list
        for tag in parent_tags:
            tag_name = tag[2]
            tag_frequency = self.tags_frequency[tag_name] # Get the frequency of current tag (ex: 1, 5, 15)
            tag_frequency = Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 10, 30) # Fit frequency in the 10-30 range
            font = QtGui.QFont()
            font.setPointSize(tag_frequency)
            top_item = QtGui.QTreeWidgetItem(self.tagsTreeWidget)
            top_item.setText(0, tag_name)
            top_item.setFont(0, font)
            top_item.setExpanded(True)
            self.tagsTreeWidget.addTopLevelItem(top_item)

        # Add all children to parents (tags manager list)
        root = self.tagsTreeWidget.invisibleRootItem()
        child_count = root.childCount()
        for item in xrange(child_count):
            top_item = root.child(item)
            top_item_name = str(root.child(item).text(0))
            for tag in child_tags:
                tag_name = tag[2]
                tag_parent = tag[3]
                if tag_parent == top_item_name: # Check if the tag_parent of current child is equal to the current top item
                    tag_frequency = self.tags_frequency[tag_name] # Get the frequency of current tag (ex: 1, 5, 15)
                    tag_frequency = Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 10, 30) # Fit frequency in the 10-30 range
                    font = QtGui.QFont()
                    font.setPointSize(tag_frequency)
                    child_item = QtGui.QTreeWidgetItem(top_item)
                    child_item.setText(0, tag_name)
                    child_item.setFont(0, font)
                    top_item.addChild(child_item)

        # Add all parents tags to the add tags list
        for tag in parent_tags:
            tag_name = tag[2]
            tag_frequency = self.tags_frequency[tag_name] # Get the frequency of current tag (ex: 1, 5, 15)
            tag_frequency = Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 9, 20) # Fit frequency in the 9-20 range
            font = QtGui.QFont()
            font.setPointSize(tag_frequency)
            top_item = QtGui.QTreeWidgetItem(self.allTagsTreeWidget)
            top_item.setText(0, tag_name)
            top_item.setFont(0, font)
            top_item.setExpanded(True)
            self.allTagsTreeWidget.addTopLevelItem(top_item)

        # Add all children to parents (add tags list)
        root = self.allTagsTreeWidget.invisibleRootItem()
        child_count = root.childCount()
        for item in xrange(child_count):
            top_item = root.child(item)
            top_item_name = str(root.child(item).text(0))
            for tag in child_tags:
                tag_name = tag[2]
                tag_parent = tag[3]
                if tag_parent == top_item_name: # Check if the tag_parent of current child is equal to the current top item
                    tag_frequency = self.tags_frequency[tag_name] # Get the frequency of current tag (ex: 1, 5, 15)
                    tag_frequency = Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 9, 20) # Fit frequency in the 9-20 range
                    font = QtGui.QFont()
                    font.setPointSize(tag_frequency)
                    child_item = QtGui.QTreeWidgetItem(top_item)
                    child_item.setText(0, tag_name)
                    child_item.setFont(0, font)
                    top_item.addChild(child_item)

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
        self.setup_tags()
        self.mt_item_added = True
        MyTasks.mt_add_tasks_from_database(self)
        WhatsNew.load_whats_new(self)
        ReferenceTab.refresh_reference_list(self)

    def change_theme(self):
        if self.themePrefComboBox.currentIndex() == 0:
            self.Lib.apply_style(self, self)
            self.cursor.execute('''UPDATE preferences SET theme=? WHERE username=?''', (0, self.username,))

        elif self.themePrefComboBox.currentIndex() == 1:
            self.setStyleSheet("")
            app.setStyle(QtGui.QStyleFactory.create("cleanlooks"))
            self.cursor.execute('''UPDATE preferences SET theme=? WHERE username=?''', (1, self.username,))
            css = QtCore.QFile(self.cur_path + "\\media\\cleanlooks.css")
            css.open(QtCore.QIODevice.ReadOnly)
            if css.isOpen():
                self.Form.setStyleSheet(QtCore.QVariant(css.readAll()).toString())
        elif self.themePrefComboBox.currentIndex() == 2:
            self.setStyleSheet("")
            app.setStyle(QtGui.QStyleFactory.create("plastique"))
            self.cursor.execute('''UPDATE preferences SET theme=? WHERE username=?''', (2, self.username,))

        self.db.commit()

    def tray_icon_message_clicked(self):

        if self.tray_message == "Manager is in background mode.": return

        clicked_log_entry = self.cursor.execute('''SELECT log_value FROM log WHERE log_id=?''', (self.tray_icon_log_id,)).fetchone()[0]
        clicked_log_description = self.cursor.execute('''SELECT log_entry FROM log WHERE log_id=?''', (self.tray_icon_log_id,)).fetchone()[0]

        if len(clicked_log_entry) == 0: return

        asset = Asset(self, id=clicked_log_entry)
        asset.get_infos_from_id()

        if "reference" in clicked_log_description:
            if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:
                comment_dialog = CommentWidget(self, asset)
            else:
                if "video" in clicked_log_description:
                    subprocess.Popen(["C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe", asset.dependency])
                else:
                    if os.path.isfile(asset.full_path):
                        os.system(asset.full_path)
                    else:
                        Lib.message_box(self, text="Can't find reference: it must have been deleted.")

        #elif "comment" in clicked_log_description:
            #self.setWindowFlags(QtCore.Qt.Widget)
            #self.show()
            #self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            #self.tray_icon.hide()
            #comment_dialog = CommentWidget(self, asset)

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
    app = QtGui.QApplication(sys.argv)


    cur_path = os.path.dirname(os.path.realpath(__file__))

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
