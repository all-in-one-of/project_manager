#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import subprocess
from functools import partial
import os

class AssetLoader(object):
    def __init__(self):
        # Get projects from database and add them to the projects list
        self.projects = self.cursor.execute('''SELECT project_name FROM projects''').fetchall()
        self.projects = [str(i[0]) for i in self.projects]
        for project in self.projects:
            self.projectList.addItem(project)

        # Select default project
        self.projectList.setCurrentRow(0)
        self.projectList_Clicked()

        self.selected_project_name = str(self.projectList.selectedItems()[0].text())
        self.selected_sequence_name = "xxx"
        self.selected_shot_number = "xxxx"

        # Filtering options
        self.meOnlyCheckBox.stateChanged.connect(self.filter_assets_for_me)

        # Connect the filter textboxes
        self.seqFilter.textChanged.connect(partial(self.filterList_textChanged, "sequence"))
        self.assetFilter.textChanged.connect(partial(self.filterList_textChanged, "asset"))

        # Connect the lists
        self.projectList.itemClicked.connect(self.projectList_Clicked)
        self.projectList.itemDoubleClicked.connect(self.projectList_DoubleClicked)
        self.departmentList.itemClicked.connect(self.load_assets_from_selected_proj_seq_shot_dept)
        self.seqList.itemClicked.connect(self.seqList_Clicked)  # seqList is not calling load_asset_from_selected_proj_seq_shot_dept because it needs to set the shot list
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
        self.openInExplorerBtn.clicked.connect(partial(self.Lib.open_in_explorer, self))
        self.addCommentBtn.clicked.connect(self.add_comment)
        self.updateThumbBtn.clicked.connect(self.update_thumb)

    def add_project(self):
        if not str(self.addProjectLineEdit.text()):
            self.Lib.message_box(text="Please enter a project name")
            return

        project_name = str(self.addProjectLineEdit.text())
        project_shortname = str(self.projectShortnameLineEdit.text())
        selected_folder = str(QtGui.QFileDialog.getExistingDirectory())

        # Prevent two projects from having the same name
        all_projects_name = self.cursor.execute('''SELECT project_name FROM projects''').fetchall()
        all_projects_name = [i[0] for i in all_projects_name]
        if project_name in all_projects_name:
            self.Lib.message_box(text="Project name is already taken.")
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
            self.Lib.message_box(text="Please enter a sequence name")
            return
        elif len(sequence_name) < 3:
            self.Lib.message_box(text="Please enter a 3 letters name")
            return

        # Check if a project is selected
        if not self.projectList.selectedItems():
            self.Lib.message_box(text="Please select a project first")
            return

        # Prevent two sequences from having the same name
        all_sequences_name = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''',
                                                 (self.selected_project_name,)).fetchall()
        all_sequences_name = [i[0] for i in all_sequences_name]
        if sequence_name in all_sequences_name:
            self.Lib.message_box(text="Sequence name is already taken.")
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
            self.Lib.message_box(text="Please select a project and a sequence first.")
            return

        # Prevent two shots from having the same number
        all_shots_number = self.cursor.execute(
            '''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
            (self.selected_project_name, self.selected_sequence_name)).fetchall()
        all_shots_number = [i[0] for i in all_shots_number]
        if shot_number in all_shots_number:
            self.Lib.message_box(text="Shot number already exists.")
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
        self.versions = []
        all_assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''', (self.selected_project_name,)).fetchall()
        for asset in all_assets:
            asset_id = asset[0]
            project_name = asset[1]
            sequence_name = asset[2]
            shot_number = asset[3]
            asset_name = asset[4]
            asset_path = asset[5]
            asset_type = asset[6]
            asset_version = asset[7]
            asset_comment = asset[8]
            asset_tags = asset[9]
            asset_dependency = asset[10]
            last_access = asset[11]
            creator = asset[12]

            asset_item = QtGui.QListWidgetItem(asset_name)
            asset = self.Asset(self, asset_id, project_name, sequence_name, shot_number, asset_name, asset_path, "", asset_type, asset_version, asset_comment, asset_tags, asset_dependency, last_access, creator)
            asset_item.setData(QtCore.Qt.UserRole, asset)
            self.assetList.addItem(asset_item)

            version_item = QtGui.QListWidgetItem(asset_version)
            version_item.setData(QtCore.Qt.UserRole, asset)
            self.versions.append(version_item)
            self.versionList.addItem(version_item)
            version_item.setHidden(True)

    def projectList_Clicked(self):
        # Query the project id based on the name of the selected project
        self.selected_project_name = str(self.projectList.selectedItems()[0].text())
        self.selected_project_path = str(self.cursor.execute('''SELECT project_path FROM projects WHERE project_name=?''', (self.selected_project_name,)).fetchone()[0])
        self.selected_project_shortname = str(self.cursor.execute('''SELECT project_shortname FROM projects WHERE project_name=?''', (self.selected_project_name,)).fetchone()[0])


        # Query the departments associated with the project
        self.departments = (self.cursor.execute('''SELECT DISTINCT asset_type FROM assets WHERE project_name=?''', (self.selected_project_name,))).fetchall()

        # Populate the departments list
        self.departmentList.clear()
        [self.departmentList.addItem(department[0]) for department in self.departments]
        try:
            self.departmentList.setCurrentRow(0)
        except:
            pass


        # Query the sequences associated with the project
        self.sequences = (self.cursor.execute('''SELECT DISTINCT sequence_name FROM sequences WHERE project_name=?''', (self.selected_project_name,))).fetchall()
        self.sequences = sorted(self.sequences)

        # Query the shots associated with each sequence
        self.shots = {}
        for seq in self.sequences:
            shots = (self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''', (self.selected_project_name, seq[0],))).fetchall()
            shots = [str(shot[0]) for shot in shots]
            self.shots[str(seq[0])] = shots

        # Populate the sequences and shots lists
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

        # Select "All" from sequence list and "None" from shot list
        self.seqList.setCurrentRow(0)
        self.shotList.setCurrentRow(0)

        # Load all assets
        self.load_all_assets_for_first_time()

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

    def assetList_Clicked(self):

        selected_asset = self.assetList.selectedItems()[0]
        current_asset = selected_asset.data(QtCore.Qt.UserRole).toPyObject()
        for version in self.versions:
            asset = version.data(QtCore.Qt.UserRole).toPyObject()
            if current_asset.name == asset.name:
                version.setHidden(False)
            else:
                version.setHidden(True)
        return

        all_versions = self.cursor.execute('''SELECT asset_version FROM assets WHERE project_name=? AND asset_name=?''', (self.selected_project_name, self.selected_asset_name,)).fetchall()

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

    def versionList_Clicked(self):
        selected_version = self.versionList.selectedItems()[0]
        asset = selected_version.data(QtCore.Qt.UserRole).toPyObject()
        asset.print_asset()

    def load_assets_from_selected_proj_seq_shot_dept(self):
        return

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

    def projectList_DoubleClicked(self):
        subprocess.Popen(r'explorer /select,' + str(self.selected_project_path))

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
