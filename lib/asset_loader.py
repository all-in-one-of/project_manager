#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import subprocess
from functools import partial
import os
import shutil
from threading import Thread


class AssetLoader(object):
    def __init__(self):

        self.assets = {}
        self.selected_asset = None

        # Get projects from database and add them to the projects list
        self.projects = self.cursor.execute('''SELECT project_name FROM projects''').fetchall()
        self.projects = [str(i[0]) for i in self.projects]
        for project in self.projects:
            self.projectList.addItem(project)

        # Select default project
        self.projectList.setCurrentRow(0)
        self.departmentList.setCurrentRow(0)
        self.projectList_Clicked()

        self.selected_project_name = str(self.projectList.selectedItems()[0].text())
        self.selected_department_name = "All"
        self.selected_sequence_name = "xxx"
        self.selected_shot_number = "xxxx"

        qpixmap = QtGui.QPixmap(self.no_img_found)
        qpixmap = qpixmap.scaledToWidth(300, QtCore.Qt.SmoothTransformation)
        self.assetImg.setPixmap(qpixmap)

        # Filtering options
        self.meOnlyCheckBox.stateChanged.connect(self.filter_assets_for_me)

        # Connect the filter textboxes
        self.seqFilter.textChanged.connect(partial(self.filterList_textChanged, "sequence"))
        self.assetFilter.textChanged.connect(partial(self.filterList_textChanged, "asset"))

        # Connect the lists
        self.projectList.itemClicked.connect(self.projectList_Clicked)
        self.projectList.itemDoubleClicked.connect(self.projectList_DoubleClicked)
        self.departmentList.itemClicked.connect(self.departmentList_Clicked)
        self.seqList.itemClicked.connect(self.seqList_Clicked)  # seqList is not calling load_asset_from_selected_proj_seq_shot_dept because it needs to set the shot list
        self.shotList.itemClicked.connect(self.shotList_Clicked)
        self.assetList.itemSelectionChanged.connect(self.assetList_Clicked)
        self.versionList.itemDoubleClicked.connect(self.versionList_DoubleClicked)
        self.versionList.itemClicked.connect(self.versionList_Clicked)

        self.usernameAdminComboBox.currentIndexChanged.connect(self.change_username)

        # Connect the buttons
        self.addProjectBtn.clicked.connect(self.add_project)
        self.addSequenceBtn.clicked.connect(self.add_sequence)
        self.addShotBtn.clicked.connect(self.add_shot)

        self.thumbFullBtn.clicked.connect(partial(self.switch_thumbnail_display, "full"))
        self.thumbQuadBtn.clicked.connect(partial(self.switch_thumbnail_display, "quad"))
        self.thumbTurnBtn.clicked.connect(partial(self.switch_thumbnail_display, "turn"))

        self.seqFilterClearBtn.clicked.connect(partial(self.clear_filter, "seq"))
        self.assetFilterClearBtn.clicked.connect(partial(self.clear_filter, "asset"))
        self.addCommentBtn.clicked.connect(self.add_comment)
        self.updateThumbBtn.clicked.connect(self.update_thumbnail)
        self.loadAssetBtn.clicked.connect(self.load_asset)
        self.createAssetFromScratchBtn.clicked.connect(self.create_asset_from_scratch)

        self.createVersionBtn.clicked.connect(self.create_new_version)
        self.publishBtn.clicked.connect(self.publish_asset)

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
        self.assets = {}
        self.versions = []
        assets_list = []
        self.assetList.clear()
        self.versionList.clear()

        all_assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=?''', (self.selected_project_name,)).fetchall()
        for asset in all_assets:
            asset_id = asset[0]
            project_name = asset[1]
            sequence_name = asset[2]
            shot_number = asset[3]
            asset_name = asset[4]
            asset_path = asset[5]
            asset_extension = asset[6]
            asset_type = asset[7]
            asset_version = asset[8]
            asset_comment = asset[9]
            asset_tags = asset[10]
            asset_dependency = asset[11]
            last_access = asset[12]
            creator = asset[13]

            asset_item = QtGui.QListWidgetItem(asset_name)
            asset = self.Asset(self, asset_id, project_name, sequence_name, shot_number, asset_name, asset_path, asset_extension, asset_type, asset_version, asset_tags, asset_dependency, last_access, creator)
            asset_item.setData(QtCore.Qt.UserRole, asset)
            assets_list.append((asset.sequence, asset.shot, asset.name, asset.type))
            self.assets[asset] = asset_item
            if assets_list.count((asset.sequence, asset.shot, asset.name, asset.type)) < 2:
                self.assetList.addItem(asset_item)

            if asset.extension == "obj" or asset.extension == "hda":
                version_item = QtGui.QListWidgetItem(asset.version + "-" + asset.extension)
            else:
                version_item = QtGui.QListWidgetItem(asset.version)
            version_item.setData(QtCore.Qt.UserRole, asset)
            self.versions.append(version_item)
            self.versionList.addItem(version_item)
            version_item.setHidden(True)

    def projectList_Clicked(self):
        # Query the project id based on the name of the selected project
        self.selected_project_name = str(self.projectList.selectedItems()[0].text())
        self.selected_project_path = str(self.cursor.execute('''SELECT project_path FROM projects WHERE project_name=?''', (self.selected_project_name,)).fetchone()[0])
        self.selected_project_shortname = str(self.cursor.execute('''SELECT project_shortname FROM projects WHERE project_name=?''', (self.selected_project_name,)).fetchone()[0])

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
        self.seqList.addItem("All")
        self.seqList.addItem("None")
        self.seqReferenceList.clear()
        self.seqReferenceList.addItem("All")
        self.seqReferenceList.addItem("None")
        self.shotList.clear()
        self.shotReferenceList.clear()
        self.shotReferenceList.addItem("None")
        [(self.seqList.addItem(sequence[0]), self.seqReferenceList.addItem(sequence[0])) for sequence in self.sequences]

        # Select "All" from sequence list and "None" from shot list
        self.seqList.setCurrentRow(0)
        self.shotList.setCurrentRow(0)


        # Load all assets
        if self.assetList.count() == 0:
            self.load_all_assets_for_first_time()

    def projectList_DoubleClicked(self):
        subprocess.Popen(r'explorer /select,' + str(self.selected_project_path))

    def seqList_Clicked(self):
        self.selected_sequence_name = str(self.seqList.selectedItems()[0].text())
        if self.selected_sequence_name == "None" or self.selected_sequence_name == "All":
            self.selected_sequence_name = "xxx"


        # Add shots to shot list and reference tool shot list
        if self.selected_sequence_name == "xxx":
            self.shotList.clear()
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")
        else:
            shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''', (self.selected_project_name, self.selected_sequence_name,)).fetchall()
            self.shotList.clear()
            self.shotList.addItem("All")
            self.shotList.addItem("None")
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")
            shots = [i[0] for i in shots]
            shots = sorted(shots)
            [(self.shotList.addItem(shot), self.shotReferenceList.addItem(shot)) for shot in shots]

        self.shotList.setCurrentRow(0)
        self.load_assets_from_selected_seq_shot_dept()

    def shotList_Clicked(self):
        self.selected_shot_number = str(self.shotList.selectedItems()[0].text())
        if self.selected_shot_number == "None" or self.selected_shot_number == "All":
            self.selected_shot_number = "xxxx"
        self.load_assets_from_selected_seq_shot_dept()

    def departmentList_Clicked(self):
        self.selected_department_name = str(self.departmentList.selectedItems()[0].text())
        if self.selected_department_name != "All":
            self.selected_department_name = self.departments_shortname[self.selected_department_name]
        self.load_assets_from_selected_seq_shot_dept()

    def assetList_Clicked(self):
        selected_asset = self.assetList.selectedItems()[0]
        current_asset = selected_asset.data(QtCore.Qt.UserRole).toPyObject()
        for version in self.versions:
            asset = version.data(QtCore.Qt.UserRole).toPyObject()
            if current_asset.name == asset.name:
                version.setHidden(False)
                version.setSelected(True)
            else:
                version.setHidden(True)

        self.versionList_Clicked()

    def versionList_Clicked(self):
        selected_version = self.versionList.selectedItems()[0]
        self.selected_asset = selected_version.data(QtCore.Qt.UserRole).toPyObject()

        if self.selected_asset.type == "ref":
            qpixmap = QtGui.QPixmap(self.selected_asset.full_path)
            qpixmap = qpixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
            self.assetImg.setData(self.selected_asset)
            self.assetImg.setPixmap(qpixmap)
            self.updateThumbBtn.setVisible(False)
            self.createVersionBtn.setVisible(False)
            self.publishBtn.setVisible(False)

        elif self.selected_asset.type == "mod":
            if self.selected_asset.extension == "obj":
                qpixmap = QtGui.QPixmap(self.selected_asset.full_path.replace(".obj", "_full.jpg"))
                qpixmap = qpixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
                self.assetImg.setData(self.selected_asset)
                self.assetImg.setPixmap(qpixmap)

            else:
                qpixmap = QtGui.QPixmap(self.no_img_found)
                qpixmap = qpixmap.scaledToWidth(300, QtCore.Qt.SmoothTransformation)
                self.assetImg.setData(self.selected_asset)
                self.assetImg.setPixmap(qpixmap)




        self.createdByValueLbl.setText(self.members[self.selected_asset.creator])

    def versionList_DoubleClicked(self):
        selected_version = self.versionList.selectedItems()[0]
        self.selected_asset = selected_version.data(QtCore.Qt.UserRole).toPyObject()
        subprocess.Popen(r'explorer /select,' + str(self.selected_asset.full_path))

    def load_assets_from_selected_seq_shot_dept(self):
        # Unhide all assets
        [asset.setHidden(False) for asset in self.assets.values()]

        for asset, asset_item in self.assets.items():
            if asset.sequence != self.selected_sequence_name and str(self.seqList.selectedItems()[0].text()) != "All":
                asset_item.setHidden(True)

            try: # If this block succeed, it means that item selected on sequence list is something else than "All" or "None".
                if asset.shot != self.selected_shot_number and str(self.shotList.selectedItems()[0].text()) != "All":
                    asset_item.setHidden(True)
            except:
                if asset.shot != self.selected_shot_number and self.selected_shot_number != "xxx":
                    asset_item.setHidden(True)

            if asset.type != self.selected_department_name and self.selected_department_name != "All":
                asset_item.setHidden(True)

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

    def create_new_version(self):
        if self.selected_asset.version == "out":
            self.Lib.message_box(self, text="You can't create a new version from a published asset")
            return


        old_version_path = self.selected_asset.full_path

        new_version = str(int(self.selected_asset.version) + 1).zfill(2)
        print(self.selected_asset.extension)
        return
        asset = self.Asset(self, 0, self.selected_asset.project, self.selected_asset.sequence, self.selected_asset.shot, self.selected_asset.name, "", self.selected_asset.extension, self.selected_asset.type, new_version, self.selected_asset.comments,
                           self.selected_asset.tags, self.selected_asset.dependency, self.selected_asset.last_access, self.selected_asset.creator)
        asset.add_asset_to_db()

        shutil.copy(old_version_path, asset.full_path)

    def publish_asset(self):
        subprocess.Popen([self.blender_path, "-b", "-P", "H:\\01-NAD\\_pipeline\\_utilities\\_asset_manager\\lib\\software_scripts\\blender_export_obj_from_scene.py", "--", self.selected_asset.full_path, self.selected_asset.full_path.replace("01.blend", "out.obj")], shell=True)

    def update_thumbnail(self):
        if self.selected_asset.type == "mod":
            if self.selected_asset.version != "out":
                self.Lib.message_box(self, text="You can only create a thumbnail from published asset")
            else:
                dialog = QtGui.QDialog(self)
                dialog.setWindowTitle("Select options")
                dialog_main_layout = QtGui.QVBoxLayout(dialog)

                checkbox_full = QtGui.QCheckBox("Single image (Full Resolution Render)", dialog)
                checkbox_quad = QtGui.QCheckBox("Four images (Quad View)", dialog)
                checkbox_turn = QtGui.QCheckBox("Turntable (video)", dialog)

                create_btn = QtGui.QPushButton("Start!", dialog)
                create_btn.clicked.connect(dialog.accept)

                dialog_main_layout.addWidget(checkbox_full)
                dialog_main_layout.addWidget(checkbox_quad)
                dialog_main_layout.addWidget(checkbox_turn)
                dialog_main_layout.addWidget(create_btn)

                dialog.exec_()

                if dialog.result() == 0:
                    return

                if checkbox_full.isChecked():
                    self.Lib.create_thumbnails(self, self.selected_asset.full_path, "full", "300", "50")
                if checkbox_quad.isChecked():
                    self.Lib.create_thumbnails(self, self.selected_asset.full_path, "quad", "150", "50")
                if checkbox_turn.isChecked():
                    self.Lib.create_thumbnails(self, self.selected_asset.full_path, "turn", "50", "100")

    def switch_thumbnail_display(self, type=""):
        if not self.selected_asset:
            return

        if not self.selected_asset.extension == "obj":
            return

        if type == "full":
            qpixmap = QtGui.QPixmap(self.selected_asset.full_path.replace(".obj", "_full.jpg"))
            qpixmap = qpixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
            self.assetImg.setData(self.selected_asset)
            self.assetImg.setPixmap(qpixmap)

        elif type == "quad":
            if not os.path.isfile(self.selected_asset.full_path.replace(".obj", "_quad.jpg")):
                self.update_thumbnail()
                return
            qpixmap = QtGui.QPixmap(self.selected_asset.full_path.replace(".obj", "_quad.jpg"))
            qpixmap = qpixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
            self.assetImg.setData(self.selected_asset)
            self.assetImg.setPixmap(qpixmap)

        elif type == "turn":
            if not os.path.isfile(self.selected_asset.full_path.replace(".obj", "_turn.mp4")):
                self.update_thumbnail()
                return
            subprocess.Popen(["Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_soft\\MPC\\mpc-hc.exe", "H:\\01-NAD\\_pipeline\\test_project_files\\assets\\mod\\nat_xxx_xxxx_mod_colonneRomaine_out_turn.mp4", "/fullscreen", ])

    def load_asset(self):
        if self.selected_asset.type == "ref":
            os.system(self.selected_asset.full_path)

        elif self.selected_asset.type == "mod":
            if self.selected_asset.extension != "obj":
                t = Thread(target=lambda: os.system(self.selected_asset.full_path))
                t.start()

    def create_asset_from_scratch(self):
        if self.selected_department_name == "mod":
            self.create_modeling_asset_from_scratch()

    def create_modeling_asset_from_scratch(self):

        dialog = QtGui.QDialog(self)
        self.Lib.apply_style(self, dialog)

        dialog.setWindowTitle("Enter a name")
        dialog_main_layout = QtGui.QVBoxLayout(dialog)

        software_combobox = QtGui.QComboBox(dialog)
        software_combobox.addItems(["Blender", "Maya", "Softimage", "Cinema 4D", "Houdini"])

        name_line_edit = QtGui.QLineEdit()
        name_line_edit.setPlaceholderText("Please enter a name...")
        name_line_edit.returnPressed.connect(dialog.accept)

        dialog_main_layout.addWidget(software_combobox)
        dialog_main_layout.addWidget(name_line_edit)


        dialog.exec_()
        if dialog.result() == 0:
            return

        selected_software = str(software_combobox.currentText()).lower().replace(" ", "")
        if selected_software == "blender":
            extension = "blend"
        elif selected_software == "maya":
            extension = "ma"
        elif selected_software == "softimage":
            extension = "scn"
        elif selected_software == "cinema4d":
            extension = "c4d"
        elif selected_software == "houdini":
            extension = "hip"

        asset_name = str(name_line_edit.text())
        asset_name = self.Lib.normalize_str(self, asset_name)
        asset_name = self.Lib.convert_to_camel_case(self, asset_name)

        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", extension, "mod", "01", [], [], "", "", self.username)
        asset.add_asset_to_db()
        shutil.copy(self.NEF_folder + "\\" + selected_software + "." + extension, asset.full_path)

        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "obj", "mod", "out", [], [], "", "", self.username)
        asset.add_asset_to_db()
        shutil.copy(self.NEF_folder + "\\default_cube.obj", asset.full_path)

        shutil.copy(self.cur_dir + "media\\default_cube.jpg", asset.full_path.replace(".obj", "_full.jpg"))

        #os.system("setx HOUDINI_USER_PREF_DIR ''")
        subprocess.Popen([self.houdini_batch_path, self.cur_path + "\\lib\\software_scripts\\houdini_create_modeling_hda.py",
                          asset.full_path + "*" + asset_name], shell=True)
        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "mod", "out", [], [], "", "", self.username)
        asset.add_asset_to_db()
        #os.system("setx HOUDINI_USER_PREF_DIR H:\\01-NAD\\Divers\\Houdini\\houdini__HVER__")

        self.load_all_assets_for_first_time()
        self.load_assets_from_selected_seq_shot_dept()



