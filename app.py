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


'''

import sys
import os
import subprocess
from functools import partial
import sqlite3
import time
from thibh import modules
import urllib
import shutil
from PIL import Image

from PyQt4 import QtGui, QtCore, Qt
from ui.main_window import Ui_Form


class Main(QtGui.QWidget, Ui_Form):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_Form.__init__(self)

        self.Form = self.setupUi(self)
        self.Form.center_window()

        # Global Variables
        self.cur_path = os.path.dirname(os.path.realpath(__file__))  # H:\01-NAD\_pipeline\_utilities\_asset_manager
        self.cur_path_one_folder_up = self.cur_path.replace("\\_asset_manager", "")  # H:\01-NAD\_pipeline\_utilities
        self.screenshot_dir = self.cur_path_one_folder_up + "\\_database\\screenshots\\"
        self.username = os.getenv('USERNAME')
        self.members = {"achaput": "Amélie", "costiguy": "Chloé", "cgonnord": "Christopher", "dcayerdesforges": "David",
                        "earismendez": "Edwin", "erodrigue": "Étienne", "jberger": "Jérémy", "lgregoire": "Laurence",
                        "lclavet": "Louis-Philippe", "mchretien": "Marc-Antoine", "mbeaudoin": "Mathieu",
                        "mroz": "Maxime", "obolduc": "Olivier", "slachapelle": "Simon", "thoudon": "Thibault",
                        "yjobin": "Yann", "yshan": "Yi", "vdelbroucq": "Valentin"}

        self.selected_project_name = ""
        self.selected_sequence_name = "xxx"
        self.selected_shot_number= "xxxx"

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

        # Admin Setup
        if not (self.username == "thoudon" or self.username == "lclavet"):
            self.addProjectFrame.hide()
            self.addSequenceFrame.hide()
            self.addShotFrame.hide()

        if not (self.username == "yjobin" or self.username == "thoudon" or self.username == "lclavet"):
            self.Tabs.removeTab(3)

        # Database Setup
        self.db_path = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\db.sqlite"
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()

        # Get tags from database and add them to the tags manager list and to the allTagsListWidget
        all_tags = self.cursor.execute('''SELECT tag_name FROM tags''').fetchall()
        all_tags = [str(i[0]) for i in all_tags]
        self.tagsListWidget.clear()
        for tag in all_tags:
            self.tagsListWidget.addItem(tag)
            self.allTagsListWidget.addItem(tag)

        # Get projects from database and add them to the projects list
        projects = self.cursor.execute('''SELECT * FROM projects''')
        for project in projects:
            self.projectList.addItem(project[1])

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
        self.filterByNameLineEdit.textChanged.connect(self.filter_reference_thumb)

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
        self.referenceThumbListWidget.itemSelectionChanged.connect(self.referenceThumbListWidget_itemSelectionChanged)


        # Connect the buttons
        self.addProjectBtn.clicked.connect(self.add_project)
        self.addSequenceBtn.clicked.connect(self.add_sequence)
        self.addShotBtn.clicked.connect(self.add_shot)

        self.seqFilterClearBtn.clicked.connect(partial(self.clear_filter, "seq"))
        self.assetFilterClearBtn.clicked.connect(partial(self.clear_filter, "asset"))
        self.loadBtn.clicked.connect(self.load_asset)
        self.openInExplorerBtn.clicked.connect(self.open_in_explorer)
        self.addCommentBtn.clicked.connect(self.add_comment)
        self.updateThumbBtn.clicked.connect(self.update_thumb)

        self.savePrefBtn.clicked.connect(self.save_prefs)
        self.createAssetBtn.clicked.connect(self.create_asset)
        self.createReferenceFromWebBtn.clicked.connect(self.create_reference_from_web)
        self.createReferencesFromFilesBtn.clicked.connect(self.create_reference_from_files)
        self.removeRefsBtn.clicked.connect(self.remove_selected_references)

        self.openRefInKuadroBtn.clicked.connect(self.load_ref_in_kuadro)
        self.openRefInPhotoshopBtn.clicked.connect(self.load_ref_in_photoshop)

        self.updateLogBtn.clicked.connect(self.update_log)

        # Tags Manager Buttons
        self.addTagBtn.clicked.connect(self.add_tag)
        self.addTagLineEdit.returnPressed.connect(self.add_tag)
        self.removeSelectedTagsBtn.clicked.connect(self.remove_selected_tags)

        self.addTagsBtn.clicked.connect(self.add_tags_to_selected_references)
        self.removeTagsBtn.clicked.connect(self.remove_tags_from_selected_references)

        # Other connects
        self.referenceThumbSizeSlider.sliderMoved.connect(self.change_reference_thumb_size)

        self.update_log()

    def add_project(self):
        if not str(self.addProjectLineEdit.text()):
            self.message_box(text="Please enter a project name")
            return

        project_name = str(self.addProjectLineEdit.text())
        project_shortname = str(self.projectShortnameLineEdit.text())
        selected_folder = str(QtGui.QFileDialog.getExistingDirectory())

        # Prevent two projects from having the same name
        all_projects_name = self.cursor.execute('''SELECT project_name FROM projects''').fetchall()
        all_projects_name = [i[0] for i in all_projects_name]
        if project_name in all_projects_name:
            self.message_box(text="Project name is already taken.")
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
            self.message_box(text="Please enter a sequence name")
            return
        elif len(sequence_name) < 3:
            self.message_box(text="Please enter a 3 letters name")
            return

        # Check if a project is selected
        if not self.projectList.selectedItems():
            self.message_box(text="Please select a project first")
            return

        # Prevent two sequences from having the same name
        all_sequences_name = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''',
                                                 (self.selected_project_name,)).fetchall()
        all_sequences_name = [i[0] for i in all_sequences_name]
        if sequence_name in all_sequences_name:
            self.message_box(text="Sequence name is already taken.")
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
            self.message_box(text="Please select a project and a sequence first.")
            return

        # Prevent two shots from having the same number
        all_shots_number = self.cursor.execute(
            '''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
            (self.selected_project_name, self.selected_sequence_name)).fetchall()
        all_shots_number = [i[0] for i in all_shots_number]
        if shot_number in all_shots_number:
            self.message_box(text="Shot number already exists.")
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
        self.load_reference_thumbnails()

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
        self.load_reference_thumbnails()

    def shotReferenceList_Clicked(self):

        if str(self.shotReferenceList.selectedItems()[0].text()) == "None":
            self.selected_shot_number = "xxxx"

        # Load thumbnails
        self.load_reference_thumbnails()

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
        asset_name = modules.normalize_str(asset_name)

        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            self.message_box(text="Please select a project first")
            return

        asset_filename = "\\assets\\" + self.selected_project_shortname + "_"

        # Check if a department is selected
        try:
            selected_department = str(self.departmentCreationList.selectedItems()[0].text())
        except:
            self.message_box(text="You must first select a project and department")
            return

        # Check if a name is defined for the asset
        if len(asset_name) == 0:
            self.message_box(text="Please enter a name for the asset")
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

            last_version = self.check_if_ref_already_exists(asset_name, selected_sequence, selected_shot)
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

    def create_reference_from_web(self):

        self.referenceProgressBar.setValue(0)
        self.referenceProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #f04545;}")

        asset_name = unicode(self.referenceNameLineEdit.text())
        asset_name = modules.normalize_str(asset_name)
        asset_name = modules.convert_to_camel_case(asset_name)


        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            self.message_box(text="Please select a project first")
            return

        asset_filename = "\\assets\\ref\\" + self.selected_project_shortname + "_"

        # Check if a name is defined for the asset
        if len(asset_name) == 0:
            self.message_box(text="Please enter a name for the asset")
            return

        # Check if a sequence is selected
        try:
            selected_sequence = str(self.seqReferenceList.selectedItems()[0].text())
        except:
            self.message_box(text="Please enter a name for the asset")
            return

        if selected_sequence == "All":
            selected_sequence = "xxx"
            asset_filename += "xxx_"

        # Check if a shot is selected
        try:
            selected_shot = str(self.shotReferenceList.selectedItems()[0].text())
            asset_filename += selected_shot + "_"
        except:
            selected_shot = "xxxx"
            asset_filename += "xxxx_"


        # Check if a version already exists
        last_version = self.check_if_ref_already_exists(asset_name, selected_sequence, selected_shot)
        if last_version:
            last_version = str(int(last_version) + 1).zfill(2)
            asset_filename += "ref_" + asset_name + "_" + last_version
        else:
            last_version = "01"
            asset_filename += "ref_" + asset_name + "_" + last_version

        asset_filename += ".jpg"

        self.referenceProgressBar.setValue(25)

        # Fetch image from web and compress it
        URL = str(self.referenceWebLineEdit.text())
        if len(URL) > 0:
            urllib.urlretrieve(URL, self.selected_project_path + asset_filename)
            downloaded_img = Image.open(self.selected_project_path + asset_filename)
            image_width = downloaded_img.size[0]
            if image_width > 1920: image_width = 1920
            modules.compress_image(self.selected_project_path + asset_filename, image_width, 60)

            self.referenceProgressBar.setValue(50)

        # Add reference to database
        self.cursor.execute(
            '''INSERT INTO assets(project_name, sequence_name, shot_number, asset_name, asset_path, asset_type, asset_version, creator) VALUES(?,?,?,?,?,?,?,?)''',
            (self.selected_project_name, selected_sequence, selected_shot, asset_name, asset_filename, "ref",
             last_version,
             self.username))

        self.db.commit()

        self.add_log_entry("{0} added a reference from web".format(self.members[self.username]))

        self.referenceProgressBar.setValue(100)
        self.referenceProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #56bb4e;}")

        self.load_reference_thumbnails()

    def create_reference_from_files(self):

        self.referenceProgressBar.setValue(0)
        self.referenceProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #f04545;}")

        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            self.message_box(text="Please select a project first")
            return

        asset_filename = "\\assets\\ref\\" + self.selected_project_shortname + "_"

        # Check if a sequence is selected
        try:
            selected_sequence = str(self.seqReferenceList.selectedItems()[0].text())
            asset_filename += selected_sequence + "_"
        except:
            selected_sequence = "xxx"
            asset_filename += "xxx_"

        # Check if a shot is selected
        try:
            selected_shot = str(self.shotReferenceList.selectedItems()[0].text())
            asset_filename += selected_shot + "_"
        except:
            selected_shot = "xxxx"
            asset_filename += "xxxx_"


        # Ask for user to select files
        selected_files_path = QtGui.QFileDialog.getOpenFileNames(self, 'Select Files',
                                                                 'Z:\\Groupes-cours\\NAND999-A15-N01\\Nature',
                                                                 "Images Files (*.jpg *.png *bmp)")

        self.referenceProgressBar.setValue(25)

        # Get file name
        selected_files_name = []
        files_name = []
        for path in selected_files_path:
            file_name = unicode(path.split("\\")[-1].split(".")[0])
            file_name = modules.normalize_str(file_name)
            file_name = modules.convert_to_camel_case(file_name)
            last_version = self.check_if_ref_already_exists(file_name, selected_sequence, selected_shot)
            if last_version:
                last_version = str(int(last_version) + 1).zfill(2)
            else:
                last_version = "01"
            files_name.append(file_name)
            file_path = asset_filename + file_name + "_" + last_version + ".jpg"
            selected_files_name.append(file_path)

        # Convert file paths to ascii
        selected_files_path = [str(i.toAscii()) for i in selected_files_path]

        self.referenceProgressBar.setValue(50)

        # Rename images
        for i, path in enumerate(selected_files_path):
            if not os.path.isfile(self.selected_project_path + selected_files_name[i]):
                # Backup file
                fileName, fileExtension = os.path.splitext(path)
                backup_path = path.replace(fileExtension, "") + "_backup" + ".jpg"
                shutil.copy(path, backup_path)

                # Rename file and place it in correct folder
                os.rename(path, self.selected_project_path + selected_files_name[i])

                # Update progress bar
                progressbar_value = self.referenceProgressBar.value()
                self.referenceProgressBar.setValue(progressbar_value + 1)

        # Compress images
        for path in selected_files_name:
            img = Image.open(self.selected_project_path + path)
            image_width = img.size[0]
            modules.compress_image(self.selected_project_path + path, image_width, 50)

        self.referenceProgressBar.setValue(75)

        # Add reference to database
        number_of_refs_added = 0
        for i, path in enumerate(selected_files_name):
            number_of_refs_added += 1
            last_version = path.split("\\")[-1].split(".")[0].split("_")[-1]

            self.cursor.execute(
                '''INSERT INTO assets(project_name, sequence_name, shot_number, asset_name, asset_path, asset_type, asset_version, creator) VALUES(?,?,?,?,?,?,?,?)''',
                (self.selected_project_name, selected_sequence, selected_shot, files_name[i], path, "ref", last_version,
                 self.username))

        self.add_log_entry(
            "{0} added {1} references from files".format(self.members[self.username], number_of_refs_added))

        self.db.commit()

        self.referenceProgressBar.setValue(100)
        self.referenceProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #56bb4e;}")

        self.load_reference_thumbnails()

    def remove_selected_references(self):

        # Retrieve selected references
        selected_references = self.referenceThumbListWidget.selectedItems()
        selected_references = [str(i.text()) for i in selected_references]

        # Delete references on database and on disk
        number_of_refs_removed = 0
        for ref in selected_references:
            number_of_refs_removed += 1
            ref_name = ref.split("_")[0]
            ref_version = ref.split("_")[1]
            ref_path = self.cursor.execute(
                '''SELECT asset_path FROM assets WHERE asset_name=? AND asset_version=? AND asset_type="ref" AND sequence_name=? AND shot_number=?''',
                (ref_name, ref_version, self.selected_sequence_name,self.selected_shot_number,)).fetchone()[0]
            os.remove(self.selected_project_path + str(ref_path))
            self.cursor.execute('''DELETE FROM assets WHERE asset_name=? AND asset_version=? AND asset_type="ref" AND sequence_name=? AND shot_number=?''',
                                (ref_name, ref_version, self.selected_sequence_name, self.selected_shot_number,))

        if number_of_refs_removed > 1:
            self.add_log_entry(
                "{0} deleted {1} reference(s)".format(self.members[self.username], number_of_refs_removed))
        else:
            self.add_log_entry("{0} deleted {1} reference".format(self.members[self.username], number_of_refs_removed))

        self.db.commit()
        self.load_reference_thumbnails()

    def check_if_ref_already_exists(self, ref_name, sequence_name, shot_number):
        all_versions = self.cursor.execute(
            '''SELECT asset_version FROM assets WHERE asset_name=? AND asset_type="ref" AND sequence_name=? AND shot_number=?''',
            (ref_name, sequence_name, shot_number)).fetchall()
        if len(all_versions) == 0:
            return
        else:
            all_versions = [str(i[0]) for i in all_versions]
            all_versions = sorted(all_versions)
            last_version = all_versions[-1]
            return last_version

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

    def load_reference_thumbnails(self):

        self.referenceProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #f04545;}")
        self.referenceThumbListWidget.clear()

        # Retrieve selected sequence and shot
        try:
            selected_sequence = str(self.seqReferenceList.selectedItems()[0].text())
        except:
            selected_sequence = "xxx"
        try:
            selected_shot = str(self.shotReferenceList.selectedItems()[0].text())
        except:
            selected_shot = "xxxx"

        # Get reference paths from database based on selected sequence and shot
        if selected_sequence == "All" and selected_shot == "None":
            references_list = self.cursor.execute(
                '''SELECT asset_name, asset_path, asset_version FROM assets''').fetchall()
        elif selected_sequence == "All" and selected_shot != "None":
            references_list = self.cursor.execute(
                '''SELECT asset_name, asset_path, asset_version FROM assets WHERE shot_number=?''',
                (selected_shot,)).fetchall()
        elif selected_sequence != "All" and selected_shot == "None":
            references_list = self.cursor.execute(
                '''SELECT asset_name, asset_path, asset_version FROM assets WHERE sequence_name=?''',
                (selected_sequence,)).fetchall()
        else:
            references_list = self.cursor.execute(
                '''SELECT asset_name, asset_path, asset_version FROM assets WHERE sequence_name=? AND shot_number=?''',
                (selected_sequence, selected_shot,)).fetchall()


        # Load thumbnails
        if len(references_list) > 0:

            self.referenceProgressBar.setMaximum(len(references_list))

            # Create a dictionary with reference_name = reference_path (ex: {musee:C:\musee.jpg})
            self.references = {}
            for reference in references_list:
                reference_path = str(reference[1])
                reference_version = str(reference[2])
                reference_name = str(reference[0]) + "_" + reference_version
                self.references[reference_path] = reference_name

            thumbnails_widgets = {}

            for i, reference in enumerate(self.references.items()):
                reference_path = self.selected_project_path + reference[0]
                reference_name = reference[1]

                thumbnails_widgets[i] = QtGui.QListWidgetItem(reference_name)
                thumbnails_widgets[i].setIcon(QtGui.QIcon(reference_path))
                data = (i)
                thumbnails_widgets[i].setData(QtCore.Qt.UserRole, data)

                self.referenceThumbListWidget.addItem(thumbnails_widgets[i])
                self.referenceThumbListWidget.repaint()

                # Add 1 to progress bar
                self.referenceProgressBar.setValue(i + 1)

        # Change progress bar color to green
        self.referenceProgressBar.setStyleSheet("QProgressBar::chunk {background-color: #56bb4e;}")

    def change_reference_thumb_size(self):
        slider_size = self.referenceThumbSizeSlider.value()
        icon_size = QtCore.QSize(slider_size, slider_size)
        self.referenceThumbListWidget.setIconSize(icon_size)

    def filter_reference_thumb(self):

        filter_str = str(self.filterByNameLineEdit.text()).lower()
        if filter_str > 0:
            for i in xrange(0, self.referenceThumbListWidget.count()):
                item_text = str(self.referenceThumbListWidget.item(i).text()).lower()
                if filter_str in item_text:
                    self.referenceThumbListWidget.setItemHidden(self.referenceThumbListWidget.item(i), False)
                else:
                    self.referenceThumbListWidget.setItemHidden(self.referenceThumbListWidget.item(i), True)

    def referenceThumbListWidget_itemSelectionChanged(self):
        self.selected_references = self.referenceThumbListWidget.selectedItems()
        self.selected_references = [str(i.text()) for i in self.selected_references]

    def load_ref_in_kuadro(self):

        os.system("taskkill /im kuadro.exe /f")

        selected_thumbs_name = [str(i.text()) for i in self.referenceThumbListWidget.selectedItems()]

        references_to_load = []
        for value, key in self.references.items():
            if key in selected_thumbs_name:
                references_to_load.append(self.selected_project_path + value)

        for reference_path in references_to_load:
            subprocess.Popen(["H:\\01-NAD\\_pipeline\\_utilities\\_soft\\kuadro.exe", reference_path])

    def load_ref_in_photoshop(self):

        selected_thumbs_name = [str(i.text()) for i in self.referenceThumbListWidget.selectedItems()]

        references_to_load = []
        for value, key in self.references.items():
            if key in selected_thumbs_name:
                references_to_load.append(self.selected_project_path + value)

        for reference_path in references_to_load:
            subprocess.Popen([self.photoshop_path, reference_path])

    def add_tag(self):

        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            self.message_box(text="Please select a project first.")
            return

        tag_name = unicode(self.addTagLineEdit.text())
        tag_name = modules.normalize_str(tag_name)

        if len(tag_name) == 0:
            self.message_box(text="Please enter a tag name.")
            return

        self.tagsListWidget.addItem(tag_name)
        self.cursor.execute('''INSERT INTO tags(project_name, tag_name) VALUES (?, ?)''',
                            (self.selected_project_name, tag_name))

        self.db.commit()

        self.addTagLineEdit.setText("")

    def remove_selected_tags(self):
        selected_tags = self.tagsListWidget.selectedItems()
        selected_tags = [str(i.text()) for i in selected_tags]

        for tag in selected_tags:
            self.cursor.execute('''DELETE FROM tags WHERE tag_name = ? ''', (tag,))

        self.db.commit()

        all_tags = self.cursor.execute('''SELECT tag_name FROM tags''').fetchall()
        all_tags = [str(i[0]) for i in all_tags]
        self.tagsListWidget.clear()
        for tag in all_tags:
            self.tagsListWidget.addItem(tag)

    def add_tags_to_selected_references(self):

        # Retrieve selected references thumbnails names
        selected_references = self.referenceThumbListWidget.selectedItems()
        for i in selected_references:
            test = i.data(QtCore.Qt.UserRole).toPyObject()
            print(test)

        return

        selected_references = [str(i.text()) for i in selected_references]



        # Retrieve selected tags and join them with a comma (ex: character,lighting,architecture)
        selected_tags = self.allTagsListWidget.selectedItems()
        selected_tags = [str(i.text()) for i in selected_tags]

        for ref_path in self.references.keys():
            ref_nomenclature = ref_path.split("\\")[-1].split(".")[0]
            ref_project_name = self.selected_project_name
            ref_sequence_name = ref_nomenclature.split("_")[1]
            ref_shot_number = ref_nomenclature.split("_")[2]
            ref_name = ref_nomenclature.split("_")[4]
            ref_version = ref_nomenclature.split("_")[5]
            tags = self.cursor.execute(
                '''SELECT asset_tags FROM assets WHERE project_name=? AND sequence_name=? AND shot_number=? AND asset_name=? AND asset_version=?''',
                (ref_project_name, ref_sequence_name, ref_shot_number, ref_name, ref_version,)).fetchone()[0]

            if not tags:
                tags = ""
            tags_list = tags.split(",")
            tags_list_without_dups = list(set(tags_list + selected_tags))
            tags_list_without_dups = [i for i in tags_list_without_dups if i] # Remove empty strings from list
            tags_to_add = ",".join(tags_list_without_dups)

            self.cursor.execute(
                '''UPDATE assets SET asset_tags=? WHERE project_name=? AND sequence_name=? AND shot_number=? AND asset_name=? AND asset_version=?''',
                (tags_to_add, ref_project_name, ref_sequence_name, ref_shot_number, ref_name, ref_version,))

        self.db.commit()


    def remove_tags_from_selected_references(self):
        pass


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

    def save_prefs(self):
        """
        Save preferences

        """
        photoshop_path = str(self.photoshopPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Photoshop"''',
                            (photoshop_path,))

        maya_path = str(self.mayaPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Maya"''', (maya_path,))

        softimage_path = str(self.softimagePathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Softimage"''',
                            (softimage_path,))

        houdini_path = str(self.houdiniPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Houdini"''',
                            (houdini_path,))

        cinema4d_path = str(self.cinema4dPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Cinema 4D"''',
                            (cinema4d_path,))

        nuke_path = str(self.nukePathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Nuke"''', (nuke_path,))

        zbrush_path = str(self.zbrushPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="ZBrush"''',
                            (zbrush_path,))

        mari_path = str(self.mariPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Mari"''', (mari_path,))

        blender_path = str(self.blenderPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Blender"''',
                            (blender_path,))

        self.db.commit()

    def message_box(self, type="Warning", text="Warning"):
        self.msgBox = QtGui.QMessageBox()
        self.msgBox.setWindowIcon(self.app_icon)

        # Apply custom CSS to msgBox
        css = QtCore.QFile(self.cur_path + "\\media\\style.css")
        css.open(QtCore.QIODevice.ReadOnly)
        if css.isOpen():
            self.msgBox.setStyleSheet(QtCore.QVariant(css.readAll()).toString())
        css.close()

        self.msgBox.setWindowTitle("Warning!")
        self.msgBox.setText(text)

        self.msgBox_okBtn = self.msgBox.addButton(QtGui.QMessageBox.Ok)
        self.msgBox_okBtn.setStyleSheet("width: 64px;")
        self.msgBox.setDefaultButton(self.msgBox_okBtn)

        if type == "Warning":
            self.msgBox.setIcon(QtGui.QMessageBox.Warning)
        elif type == "Error":
            self.msgBox.setIcon(QtGui.QMessageBox.Critical)

        return self.msgBox.exec_()

    def center_window(self):
        """
        Move the window to the center of the screen

        """
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def open_in_explorer(self):
        """
        Open selected assets in explorer
        """
        subprocess.Popen(r'explorer /select,' + str(self.assetPathLbl.text()))

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

        modules.take_screenshot(self.screenshot_dir, self.selected_asset_name)

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
    window = Main()
    window.show()
    sys.exit(app.exec_())
