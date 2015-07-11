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
import urllib
import shutil

from PIL import Image
from datetime import date
from datetime import datetime
from collections import Counter
from random import randint

from PyQt4 import QtGui, QtCore, Qt

from ui.main_window import Ui_Form
from lib.reference import ReferenceTab
from lib.module import Lib
from lib.task_manager import TaskManager
from lib.my_tasks import MyTasks

class Main(QtGui.QWidget, Ui_Form, ReferenceTab, Lib, TaskManager, MyTasks):
    def __init__(self):
        super(Main, self).__init__()
        #QtGui.QMainWindow.__init__(self)
        #Ui_Form.__init__(self)

        # Database Setup
        #self.db_path = "H:\\01-NAD\\_pipeline\\_utilities\\_database\\db.sqlite" # Copie de travail
        self.db_path = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\db.sqlite" # Database officielle
        #self.db_path = "C:\\Users\\Thibault\\Desktop\\db.sqlite" # Database maison

        # Backup database
        self.backup_database()

        self.db = sqlite3.connect(self.db_path)
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
        #self.members = {"achaput": "Amelie", "costiguy": "Chloe", "cgonnord": "Christopher", "dcayerdesforges": "David",
        #         "earismendez": "Edwin", "erodrigue": "Etienne", "jberger": "Jeremy", "lgregoire": "Laurence",
        #         "lclavet": "Louis-Philippe", "mchretien": "Marc-Antoine", "mbeaudoin": "Mathieu",
        #         "mroz": "Maxime", "obolduc": "Olivier", "slachapelle": "Simon", "thoudon": "Thibault",
        #         "vdelbroucq": "Valentin", "yjobin": "Yann", "yshan": "Yi", "Thibault":"Thibault"}


        # Initialize modules and connections
        ReferenceTab.__init__(self)


        # Select default project
        self.projectList.setCurrentRow(0)
        self.projectList_Clicked()

        self.selected_project_name = str(self.projectList.selectedItems()[0].text())
        self.selected_sequence_name = "xxx"
        self.selected_shot_number = "xxxx"
        self.today = time.strftime("%d/%m/%Y", time.gmtime())

        TaskManager.__init__(self)
        MyTasks.__init__(self)

        # Create Favicon
        self.app_icon = QtGui.QIcon()
        self.app_icon.addFile(self.cur_path + "\\media\\favicon.png", QtCore.QSize(16, 16))
        self.Form.setWindowIcon(self.app_icon)

        # Set the StyleSheet
        css = QtCore.QFile(self.cur_path + "\\media\\style.css")
        css.open(QtCore.QIODevice.ReadOnly)
        if css.isOpen():
            self.Form.setStyleSheet(QtCore.QVariant(css.readAll()).toString())

        # Overrides
        self.publishBtn.setStyleSheet("background-color: #77D482;")
        self.loadBtn.setStyleSheet(
            "QPushButton {background-color: #77B0D4;} QPushButton:hover {background-color: #1BCAA7;}")
        self.assetDependencyList.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.logTextEdit.setFont(font)

        eye_icon = QtGui.QPixmap("H:\\01-NAD\\_pipeline\\_utilities\\_asset_manager\\media\\eye_icon.png")
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
        self.diskUsageProgressBar.setFormat('{0}/2.0 Tera'.format(disk_usage))
        disk_usage = disk_usage.replace(".", "")
        self.diskUsageProgressBar.setRange(0, 20)
        self.diskUsageProgressBar.setValue(int(disk_usage))
        if disk_usage >= 15:
            self.diskUsageProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #98cd00;} QProgressBar {color: #323232;}")
        elif disk_usage >= 10:
            self.diskUsageProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #d7b600;} QProgressBar {color: #323232;}")
        elif disk_usage >= 5:
            self.diskUsageProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #f35905;} QProgressBar {color: #323232;}")
        elif disk_usage >= 0:
            self.diskUsageProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #fe2200;} QProgressBar {color: #323232;}")



        # Get software paths from database and put them in preference
        self.photoshop_path = str(self.cursor.execute(
            '''SELECT software_path FROM software_paths WHERE software_name="Photoshop"''').fetchone()[0])
        self.maya_path = str(
            self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Maya"''').fetchone()[
                0])
        self.softimage_path = str(self.cursor.execute(
            '''SELECT software_path FROM software_paths WHERE software_name="Softimage"''').fetchone()[0])
        self.houdini_path = str(self.cursor.execute(
            '''SELECT software_path FROM software_paths WHERE software_name="Houdini"''').fetchone()[0])
        self.cinema4d_path = str(self.cursor.execute(
            '''SELECT software_path FROM software_paths WHERE software_name="Cinema 4D"''').fetchone()[0])
        self.nuke_path = str(
            self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Nuke"''').fetchone()[
                0])
        self.zbrush_path = str(
            self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="ZBrush"''').fetchone()[
                0])
        self.mari_path = str(
            self.cursor.execute('''SELECT software_path FROM software_paths WHERE software_name="Mari"''').fetchone()[
                0])
        self.blender_path = str(self.cursor.execute(
            '''SELECT software_path FROM software_paths WHERE software_name="Blender"''').fetchone()[0])

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
        self.departmentList.itemClicked.connect(self.departmentList_Clicked)
        self.seqList.itemClicked.connect(self.seqList_Clicked)
        self.seqCreationList.itemClicked.connect(self.seqCreationList_Clicked)
        self.seqReferenceList.itemClicked.connect(self.seqReferenceList_Clicked)
        self.shotList.itemClicked.connect(self.shotList_Clicked)
        self.shotReferenceList.itemClicked.connect(self.shotReferenceList_Clicked)
        self.assetList.itemClicked.connect(self.assetList_Clicked)
        self.departmentCreationList.itemClicked.connect(self.departmentCreationList_Clicked)

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

        self.savePrefBtn.clicked.connect(partial(Lib.save_prefs, self))
        self.createAssetBtn.clicked.connect(self.create_asset)



        self.updateLogBtn.clicked.connect(self.update_log)

        # Tags Manager Buttons
        self.addTagBtn.clicked.connect(self.add_tag_to_tags_manager)
        self.addTagLineEdit.returnPressed.connect(self.add_tag_to_tags_manager)
        self.removeSelectedTagsBtn.clicked.connect(self.remove_selected_tags_from_tags_manager)

        # Other connects
        self.update_log()



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
        self.departmentList.addItem("All")
        [self.departmentList.addItem(department[0]) for department in self.departments]

        # Query the sequences associated with the project
        self.sequences = (self.cursor.execute('''SELECT DISTINCT sequence_name FROM sequences WHERE project_name=?''',
                                              (self.selected_project_name,))).fetchall()
        self.sequences = sorted(self.sequences)

        # Populate the sequences lists
        self.seqList.clear()
        self.seqList.addItem("All")
        self.seqCreationList.clear()
        self.seqCreationList.addItem("All")
        self.seqReferenceList.clear()
        self.seqReferenceList.addItem("All")
        self.seqReferenceList.addItem("None")
        self.shotList.clear()
        self.shotList.addItem("None")
        self.shotCreationList.clear()
        self.shotCreationList.addItem("None")
        self.shotReferenceList.clear()
        self.shotReferenceList.addItem("None")
        [(self.seqList.addItem(sequence[0]), self.seqCreationList.addItem(sequence[0]),
          self.seqReferenceList.addItem(sequence[0])) for sequence in self.sequences]


        # Populate the assets list
        self.all_assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''',
                                              (self.selected_project_name,)).fetchall()
        self.add_assets_to_asset_list(self.all_assets)

        # Populate the asset dependency list
        self.assetDependencyList.clear()
        for asset in self.all_assets:
            self.assetDependencyList.addItem(asset[4])

    def projectList_DoubleClicked(self):
        subprocess.Popen(r'explorer /select,' + str(self.selected_project_path))

    def departmentList_Clicked(self):
        self.selected_department = str(self.departmentList.selectedItems()[0].text())

        if len(self.seqList.selectedItems()) == 0:
            if self.selected_department == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''',
                                             (self.selected_project_name,))
            else:
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND asset_type=?''',
                                             (self.selected_project_name, self.selected_department,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)

        else:

            if self.selected_department == "All" and self.selected_sequence_name == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''',
                                             (self.selected_project_name,))
            elif self.selected_department == "All" and self.selected_sequence_name != "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND sequence_id=?''',
                                             (self.selected_project_name, self.selected_sequence_id))
            elif self.selected_department != "All" and self.selected_sequence_name == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND asset_type=?''',
                                             (self.selected_project_name, self.selected_department))
            else:
                self.selected_sequence_id = str(
                    self.cursor.execute('''SELECT sequence_id FROM sequences WHERE sequence_name=?''',
                                        (self.selected_sequence_name,)).fetchone()[0])
                assets = self.cursor.execute(
                    '''SELECT * FROM assets WHERE project_name=? AND sequence_id=? AND asset_type=?''',
                    (self.selected_project_name, self.selected_sequence_id, self.selected_department,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)

    def seqList_Clicked(self):
        self.selected_sequence_name = str(self.seqList.selectedItems()[0].text())

        # Add shots to shot list, shot creation list and reference tool shot list
        if self.selected_sequence_name == "All":
            self.selected_sequence_name = "xxx"
            self.shotList.clear()
            self.shotList.addItem("None")
            self.shotCreationList.clear()
            self.shotCreationList.addItem("None")
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")
        else:
            shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
                                        (self.selected_project_name, self.selected_sequence_name,)).fetchall()
            self.shotList.clear()
            self.shotList.addItem("None")
            self.shotCreationList.clear()
            self.shotCreationList.addItem("None")
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")
            shots = [i[0] for i in shots]
            shots = sorted(shots)
            [(self.shotList.addItem(shot), self.shotCreationList.addItem(shot), self.shotReferenceList.addItem(shot))
             for shot in shots]

        if len(self.departmentList.selectedItems()) == 0:
            if self.selected_sequence_name == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''',
                                             (self.selected_project_name,))
            else:
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND sequence_name=?''',
                                             (self.selected_project_name, self.selected_sequence_name,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)

        else:
            if self.selected_department == "All" and self.selected_sequence_name == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''',
                                             (self.selected_project_name,))
            elif self.selected_department == "All" and self.selected_sequence_name != "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND sequence_name=?''',
                                             (self.selected_project_name, self.selected_sequence_name))
            elif self.selected_department != "All" and self.selected_sequence_name == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND asset_type=?''',
                                             (self.selected_project_name, self.selected_department))
            else:
                assets = self.cursor.execute(
                    '''SELECT * FROM assets WHERE project_name=? AND sequence_name=? AND asset_type=?''',
                    (self.selected_project_name, self.selected_sequence_name, self.selected_department,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)



        # Mirror selection to Asset Creation tab
        seq_list_selected_index = self.seqList.selectedIndexes()[0].row()
        self.seqCreationList.setCurrentRow(seq_list_selected_index)

        # Mirror selection to Reference Tool tab
        seq_list_selected_index = self.seqList.selectedIndexes()[0].row()
        self.seqReferenceList.setCurrentRow(seq_list_selected_index)

        # Load thumbnails on Reference Tool tab
        ReferenceTab.load_reference_thumbnails(self)

    def seqCreationList_Clicked(self):
        self.selected_sequence_name = str(self.seqCreationList.selectedItems()[0].text())

        # Add shots to shot list and shot creation list
        if self.selected_sequence_name == "All":
            self.selected_sequence_name = "xxx"
            self.shotCreationList.clear()
            self.shotCreationList.addItem("None")

        else:
            shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
                                        (self.selected_project_name, self.selected_sequence_name,)).fetchall()
            self.shotCreationList.clear()
            self.shotCreationList.addItem("None")
            shots = [i[0] for i in shots]
            shots = sorted(shots)
            [self.shotCreationList.addItem(shot) for shot in shots]

    def seqReferenceList_Clicked(self):
        self.selected_sequence_name = str(self.seqReferenceList.selectedItems()[0].text())

        # Add shots to shot list and shot creation list
        if self.selected_sequence_name == "All":
            self.selected_sequence_name = "xxx"
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")

        else:
            shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
                                        (self.selected_project_name, self.selected_sequence_name,)).fetchall()
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")
            shots = [i[0] for i in shots]
            shots = sorted(shots)
            [self.shotReferenceList.addItem(shot) for shot in shots]

        # Load thumbnails
        ReferenceTab.load_reference_thumbnails(self)

    def shotReferenceList_Clicked(self):

        if str(self.shotReferenceList.selectedItems()[0].text()) == "None":
            self.selected_shot_number = "xxxx"

        # Load thumbnails
        ReferenceTab.load_reference_thumbnails(self)

    def shotList_Clicked(self):

        if str(self.shotList.selectedItems()[0].text()) == "None":
            self.selected_shot_number = "xxxx"

        # Mirror selection to Asset Creation tab
        shot_list_selected_index = self.shotList.selectedIndexes()[0].row()
        self.shotCreationList.setCurrentRow(shot_list_selected_index)
        self.shotReferenceList.setCurrentRow(shot_list_selected_index)

    def assetList_Clicked(self):

        self.selected_asset_type = str(self.assetList.selectedItems()[0].text()).split("_")[0]
        self.selected_asset_name = str(self.assetList.selectedItems()[0].text()).split("_")[1]
        self.selected_asset_version = str(self.assetList.selectedItems()[0].text()).split("_")[2]
        self.selected_asset_path = self.cursor.execute(
            '''SELECT asset_path FROM assets WHERE project_name=? AND asset_type=? AND asset_name=? AND asset_version=?''',
            (self.selected_project_name, self.selected_asset_type, self.selected_asset_name,
             self.selected_asset_version)).fetchone()[0]

        cur_asset = Asset(self.selected_asset_name, self.selected_asset_path)
        print(cur_asset.name)
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

    def departmentCreationList_Clicked(self):
        '''Filter the softwareCreationList based on the type of department selected.
        ex. if "Concept" is selected, only show Photoshop.
        '''

        # Global overrides
        selected_department = str(self.departmentCreationList.selectedItems()[0].text())
        self.webGroupBox.setEnabled(False)

        if selected_department == "Concept":
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(0), True)  # Blender
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(1), True)  # Cinema 4D
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(2), True)  # Houdini
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(3), True)  # Maya
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(4), False)  # Photoshop
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(5), True)  # Softimage
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(6), True)  # ZBrush

            self.assetDependencyList.setEnabled(False)
            self.webGroupBox.setEnabled(True)
            self.referenceWebLineEdit.setEnabled(True)
            try:
                self.softwareCreationList.setItemSelected(
                    self.softwareCreationList.setItemSelected(self.softwareCreationList.item(4), True))
            except:
                pass

        elif selected_department == "Modeling":
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(1), False)  # Cinema 4D
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(0), False)  # Blender
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(2), False)  # Houdini
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(3), False)  # Maya
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(4), True)  # Photoshop
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(5), False)  # Softimage
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(6), False)  # ZBrush
            self.assetDependencyList.setEnabled(False)

        elif selected_department == "Layout":
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(1), True)  # Cinema 4D
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(0), False)  # Blender
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(2), True)  # Houdini
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(3), False)  # Maya
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(4), True)  # Photoshop
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(5), False)  # Softimage
            self.softwareCreationList.setItemHidden(self.softwareCreationList.item(6), False)  # ZBrush
            self.assetDependencyList.setEnabled(True)

        elif selected_department == "References":
            self.softwareCreationList.setEnabled(False)
            self.webGroupBox.setEnabled(True)
            self.referenceWebLineEdit.setEnabled(True)

    def create_asset(self):
        '''Create asset
        '''

        asset_name = unicode(self.assetNameCreationLineEdit.text())
        asset_name = Lib.normalize_str(asset_name)

        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            Lib.message_box(text="Please select a project first")
            return

        asset_filename = "\\assets\\" + self.selected_project_shortname + "_"

        # Check if a department is selected
        try:
            selected_department = str(self.departmentCreationList.selectedItems()[0].text())
        except:
            Lib.message_box(text="You must first select a project and department")
            return

        # Check if a name is defined for the asset
        if len(asset_name) == 0:
            Lib.message_box(text="Please enter a name for the asset")
            return

        # Check if a sequence is selected
        try:
            selected_sequence = str(self.seqCreationList.selectedItems()[0].text())
            asset_filename += selected_sequence + "_"
        except:
            selected_sequence = "xxx"
            asset_filename += "xxx_"

        # Check if a shot is selected
        try:
            selected_shot = str(self.shotCreationList.selectedItems()[0].text())
            asset_filename += selected_shot + "_"
        except:
            selected_shot = "xxxx"
            asset_filename += "xxxx_"


        # Create asset depending on selected department
        if selected_department == "References":

            last_version = ReferenceTab.check_if_ref_already_exists(asset_name, selected_sequence, selected_shot)
            if last_version:
                last_version = str(int(last_version) + 1).zfill(2)
                asset_filename += "ref_" + asset_name + "_" + last_version
            else:
                asset_filename += "ref_" + asset_name + "_01"

            print(asset_filename)



        elif selected_department == "Concept":

            oUrl = str(self.referenceWebLineEdit.text())
            if not len(oUrl) == 0:
                asset_path += "\\concepts\\concept_{0}_01.jpg".format(asset_name)
                asset_path, asset_name = self.check_if_asset_already_exists(asset_path, asset_name, "jpg")
                urllib.urlretrieve(oUrl, asset_path)
            else:
                asset_path += "\\concepts\\concept_{0}_01.psd".format(asset_name)
                asset_path, asset_name = self.check_if_asset_already_exists(asset_path, asset_name, "psd")
                shutil.copyfile("H:\\01-NAD\\_pipeline\\_utilities\\default_scenes\\photoshop.psd",
                                asset_path)

            self.cursor.execute(
                '''INSERT INTO assets(project_id, sequence_id, asset_name, asset_path, asset_type, asset_version, creator) VALUES(?,?,?,?,?,?,?)''',
                (
                    self.selected_project_name, selected_sequence_id, asset_name, asset_path, "concept", "01",
                    self.username))

            self.db.commit()

        elif selected_department == "Modeling":
            pass

        elif selected_department == "Layout":
            pass

        #        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
        #            subprocess.Popen([self.photoshop_path, asset_path])

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

        tabs_list = {"Asset Loader":0, "Task Manager":1, "My Tasks":2, "Asset Creator":3, "References Tool":4,
                     "Tags Manager":5, "Log":6, "Preferences":7}

        if self.members[self.username] == "Amelie":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Chloe":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Christopher":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "David":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Edwin":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Etienne":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Jeremy":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Laurence":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Louis-Philippe":
            pass

        elif self.members[self.username] == "Marc-Antoine":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Mathieu":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Maxime":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Olivier":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Simon":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Thibault":
            pass

        elif self.members[self.username] == "Yann":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(5)

        elif self.members[self.username] == "Yi":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

        elif self.members[self.username] == "Valentin":
            self.Tabs.removeTab(1)
            self.Tabs.removeTab(2)
            self.Tabs.removeTab(3)
            self.Tabs.removeTab(4)

    def add_log_entry(self, text):
        cur_date = time.strftime("%d/%m/%Y")
        cur_time = time.strftime("%H:%M:%S")

        log_time = cur_date + " - " + cur_time

        self.cursor.execute('''INSERT INTO log(log_time, log_entry) VALUES (?, ?)''',
                            (log_time, text))

        self.db.commit()

        self.update_log()

    def update_log(self):
        # Select all log entries from database
        log_db_entries = self.cursor.execute('''SELECT * FROM log''').fetchall()

        self.logTextEdit.clear()

        # Formatting the entries
        log_entries = ""
        for entry in reversed(log_db_entries):
            log_entries += str(entry[1] + ": " + entry[2] + "<br>")

        # Add log entries to GUI
        self.logTextEdit.setText(log_entries)
        self.logLbl.setText("Total log entries: " + str(len(log_db_entries)))

    def setup_tags(self):

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

        self.maximum_tag_occurence = max(self.tags_frequency.values())

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

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        if key == QtCore.Qt.Key_Escape:
            sys.exit()


    def closeEvent(self, event):
        self.save_tags_list()
        # quit_msg = "Are you sure you want to exit the program?"
        # reply = QtGui.QMessageBox.question(self, 'Are you leaving :(',
        #                  quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        #
        # if reply == QtGui.QMessageBox.Yes:
        #
        #     event.accept()
        # else:
        #     event.ignore()



class SoftwareDialog(QtGui.QDialog):
    def __init__(self, asset, parent=None):
        super(SoftwareDialog, self).__init__(parent)

        self.asset = asset

        self.setWindowTitle("Choose a software")
        self.horizontalLayout = QtGui.QHBoxLayout(self)

        if self.asset.endswith(".jpg"):
            self.photoshopBtn = QtGui.QPushButton("Photoshop")
            self.pictureviewerBtn = QtGui.QPushButton("Picture Viewer")

            self.photoshopBtn.clicked.connect(partial(self.btn_clicked, "photoshop"))
            self.pictureviewerBtn.clicked.connect(partial(self.btn_clicked, "pictureviewer"))

            self.horizontalLayout.addWidget(self.photoshopBtn)
            self.horizontalLayout.addWidget(self.pictureviewerBtn)

        elif self.asset.endswith(".obj"):
            self.mayaBtn = QtGui.QPushButton("Maya")
            self.softimageBtn = QtGui.QPushButton("Softimage")
            self.blenderBtn = QtGui.QPushButton("Blender")
            self.c4dBtn = QtGui.QPushButton("Cinema 4D")

            self.mayaBtn.clicked.connect(partial(self.btn_clicked, "maya"))
            self.softimageBtn.clicked.connect(partial(self.btn_clicked, "softimage"))
            self.blenderBtn.clicked.connect(partial(self.btn_clicked, "blender"))
            self.c4dBtn.clicked.connect(partial(self.btn_clicked, "c4d"))

            self.horizontalLayout.addWidget(self.mayaBtn)
            self.horizontalLayout.addWidget(self.softimageBtn)
            self.horizontalLayout.addWidget(self.blenderBtn)
            self.horizontalLayout.addWidget(self.c4dBtn)

    def btn_clicked(self, software):
        self.close()
        if software == "photoshop":
            subprocess.Popen(["C:\\Program Files\\Adobe\\Adobe Photoshop CS6 (64 Bit)\\Photoshop.exe", self.asset])
        elif software == "pictureviewer":
            os.system(self.asset)
        elif software == "maya":
            subprocess.Popen(["C:\\Program Files\\Autodesk\\Maya2015\\bin\\maya.exe", self.asset])
        elif software == "softimage":
            subprocess.Popen(["", self.asset])
        elif software == "blender":
            subprocess.Popen(["H:\\Dossiers Importants\\Google Drive\\Blender\\2.74\\blender.exe", "--python",
                              "H:\\01-NAD\\_pipeline\\_utilities\\software_scripts\\blender\\blender_obj_load.py",
                              self.asset])
        elif software == "c4d":
            subprocess.Popen(["H:\\Programmes\\Cinema 4D R16\\CINEMA 4D.exe", self.asset])



























            # Main Loop



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    # Show Splashscreen
    splash_pix = QtGui.QPixmap("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\splashscreen.jpg")
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()

    time.sleep(0.1)

    splash.setPixmap(QtGui.QPixmap("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\splashscreen-02.jpg"))
    splash.repaint()

    time.sleep(0.2)

    splash.setPixmap(QtGui.QPixmap("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\splashscreen-03.jpg"))
    splash.repaint()

    time.sleep(0.1)

    splash.setPixmap(QtGui.QPixmap("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\splashscreen-04.jpg"))
    splash.repaint()

    time.sleep(0.05)

    splash.setPixmap(QtGui.QPixmap("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\splashscreen-05.jpg"))
    splash.repaint()


    window = Main()
    window.show()

    splash.finish(window)
    sys.exit(app.exec_())
