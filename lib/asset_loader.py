#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import subprocess
from functools import partial
import os
import shutil
from threading import Thread
import datetime

from ui.add_assets_to_layout_tmp import Ui_addAssetsToLayoutWidget

class AssetLoader(object):
    def __init__(self):

        self.favorite_icon = QtGui.QIcon(self.cur_path + "\\media\\favorite.png")
        self.unfavorite_icon = QtGui.QIcon(self.cur_path + "\\media\\unfavorite.png")

        self.addAssetsToLayoutBtn.hide()

        self.assets = {}
        self.selected_asset = None
        self.thumbDisplayTypeFrame.hide()
        self.loadObjInGplayBtn.hide()
        self.updateThumbBtn.hide()

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
        self.assetList.itemClicked.connect(self.assetList_Clicked)
        self.versionList.itemDoubleClicked.connect(self.versionList_DoubleClicked)
        self.versionList.itemClicked.connect(self.versionList_Clicked)

        self.usernameAdminComboBox.currentIndexChanged.connect(self.change_username)

        # Connect the buttons
        self.showAssetCommentBtn.clicked.connect(self.show_comments)
        self.addRemoveAssetAsFavoriteBtn.clicked.connect(self.change_favorite_state)
        self.addRemoveAssetAsFavoriteBtn.setIcon(self.unfavorite_icon)
        self.addRemoveAssetAsFavoriteBtn.setIconSize(QtCore.QSize(24, 24))

        self.addAssetsToLayoutBtn.clicked.connect(self.add_assets_to_layout)


        self.addProjectBtn.clicked.connect(self.add_project)
        self.addSequenceBtn.clicked.connect(self.add_sequence)
        self.addShotBtn.clicked.connect(self.add_shot)

        self.thumbFullBtn.clicked.connect(partial(self.switch_thumbnail_display, "full"))
        self.thumbQuadBtn.clicked.connect(partial(self.switch_thumbnail_display, "quad"))
        self.thumbTurnBtn.clicked.connect(partial(self.switch_thumbnail_display, "turn"))
        self.loadObjInGplayBtn.clicked.connect(self.load_obj_in_gplay)

        self.seqFilterClearBtn.clicked.connect(partial(self.clear_filter, "seq"))
        self.assetFilterClearBtn.clicked.connect(partial(self.clear_filter, "asset"))
        self.updateThumbBtn.clicked.connect(self.update_thumbnail)
        self.loadAssetBtn.clicked.connect(self.load_asset)
        self.createAssetFromScratchBtn.clicked.connect(self.create_asset_from_scratch)
        self.createAssetFromScratchAssetBtn.clicked.connect(self.create_asset_from_asset)
        self.deleteAssetBtn.clicked.connect(self.delete_asset)

        self.createVersionBtn.clicked.connect(self.create_new_version)
        self.publishBtn.clicked.connect(self.publish_asset)

    def show_comments(self):
        if self.selected_asset == None:
            return
        self.CommentsFrame.show()
        self.commentLineEdit.setFocus()
        self.CommentWidget.load_comments(self)

    def change_favorite_state(self):
        if self.selected_asset == None:
            return

        is_asset_favorited = self.cursor.execute('''SELECT * FROM favorited_assets WHERE asset_id=? AND member=?''', (self.selected_asset.id, self.username,)).fetchone()
        if is_asset_favorited == None: # Asset is not already favorited by member
            self.cursor.execute('''INSERT INTO favorited_assets(asset_id, member) VALUES(?,?)''', (self.selected_asset.id, self.username,))
            self.db.commit()
            self.addRemoveAssetAsFavoriteBtn.setIcon(self.favorite_icon)
        else:
            self.cursor.execute('''DELETE FROM favorited_assets WHERE asset_id=? AND member=?''', (is_asset_favorited[0], is_asset_favorited[1],))
            self.db.commit()
            self.addRemoveAssetAsFavoriteBtn.setIcon(self.unfavorite_icon)

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
            asset_tags = asset[9]
            asset_dependency = asset[10]
            last_access = asset[11]
            last_publish = asset[12]
            creator = asset[13]
            number_of_publishes = asset[14]


            asset_item = QtGui.QListWidgetItem(asset_name)
            asset = self.Asset(self, asset_id, project_name, sequence_name, shot_number, asset_name, asset_path, asset_extension, asset_type, asset_version, asset_tags, asset_dependency, last_access, last_publish, creator, number_of_publishes)
            asset_item.setData(QtCore.Qt.UserRole, asset)
            self.assets[asset] = asset_item
            if asset.version != "out" and asset.type != "ref":
                self.assetList.addItem(asset_item)
                version_item = QtGui.QListWidgetItem(asset.version + " (" + asset.extension + ")")
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

        qpixmap = QtGui.QPixmap(self.no_img_found)
        qpixmap = qpixmap.scaledToWidth(300, QtCore.Qt.SmoothTransformation)
        self.assetImg.setData(self.no_img_found)
        self.assetImg.setPixmap(qpixmap)

        self.addAssetsToLayoutBtn.hide()
        self.updateThumbBtn.hide()

        if self.selected_department_name == "ref":
            self.loadObjInGplayBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "mod":
            self.loadObjInGplayBtn.show()
            self.thumbDisplayTypeFrame.show()

        elif self.selected_department_name == "tex":
            self.loadObjInGplayBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "rig":
            self.loadObjInGplayBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "anm":
            self.loadObjInGplayBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "sim":
            self.loadObjInGplayBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "shd":
            self.loadObjInGplayBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "lay":
            self.loadObjInGplayBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "dmp":
            self.loadObjInGplayBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "cmp":
            self.loadObjInGplayBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        self.verticalLayout_4.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        self.gridLayout_6.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        self.addRemoveAssetAsFavoriteBtn.setIcon(self.unfavorite_icon)
        self.load_assets_from_selected_seq_shot_dept()

    def assetList_Clicked(self):

        selected_asset = self.assetList.selectedItems()[0]
        selected_asset = selected_asset.data(QtCore.Qt.UserRole).toPyObject()
        for version in self.versions:
            asset = version.data(QtCore.Qt.UserRole).toPyObject()
            if self.selected_department_name == "All":
                if selected_asset.name == asset.name:
                    version.setHidden(False)
                    version.setSelected(True)
                else:
                    version.setHidden(True)
            else:
                if selected_asset.name == asset.name and asset.type == self.selected_department_name:
                    version.setHidden(False)
                    version.setSelected(True)
                else:
                    version.setHidden(True)

        self.updateThumbBtn.show()
        self.versionList_Clicked()

    def versionList_Clicked(self):
        selected_version = self.versionList.selectedItems()[0]
        self.selected_asset = selected_version.data(QtCore.Qt.UserRole).toPyObject()

        # Set pixmap
        if self.selected_asset.type == "mod":
            if not os.path.isfile(self.selected_asset.full_img_path):
                img_path, width = self.no_img_found, 300
            else:
                img_path, width = self.selected_asset.full_img_path, 500

            qpixmap = QtGui.QPixmap(img_path)
            qpixmap = qpixmap.scaledToWidth(width, QtCore.Qt.SmoothTransformation)
            self.assetImg.setData(img_path)
            self.assetImg.setPixmap(qpixmap)
            self.update_last_published_time_lbl()
        else:
            qpixmap = QtGui.QPixmap(self.no_img_found)
            qpixmap = qpixmap.scaledToWidth(300, QtCore.Qt.SmoothTransformation)
            self.assetImg.setData(self.no_img_found)
            self.assetImg.setPixmap(qpixmap)


        if self.selected_asset.type == "lay":
            if self.username == "thoudon" or self.username == "lclavet":
                self.addAssetsToLayoutBtn.show()

        # Set labels
        self.lastAccessLbl.setText("Last accessed by: " + self.selected_asset.last_access)

        # Set favorite button state
        is_asset_favorited = self.cursor.execute('''SELECT * FROM favorited_assets WHERE asset_id=? AND member=?''', (self.selected_asset.id, self.username,)).fetchone()
        if is_asset_favorited == None:
            self.addRemoveAssetAsFavoriteBtn.setIcon(self.unfavorite_icon)
        else:
            self.addRemoveAssetAsFavoriteBtn.setIcon(self.favorite_icon)

    def update_last_published_time_lbl(self, asset=None):
        if asset == None:
            asset = self.selected_asset

        if asset.type == "mod":
            # Set last published date label
            day_today = datetime.datetime.now()
            number_of_days_since_last_publish = day_today - self.selected_asset.last_publish_as_date
            number_of_days_since_last_publish = number_of_days_since_last_publish.days

            if number_of_days_since_last_publish == 0:
                number_of_days_since_last_publish = "today"
            elif number_of_days_since_last_publish > 7:
                number_of_days_since_last_publish = str(number_of_days_since_last_publish) + " days ago. You should publish a new version!"
                self.lastPublishedLbl.setStyleSheet("color: red;")
            else:
                number_of_days_since_last_publish = str(number_of_days_since_last_publish) + " days ago"

            self.lastPublishedLbl.setText("Last published by: {0} ({1})".format(self.selected_asset.last_publish, number_of_days_since_last_publish))

    def versionList_DoubleClicked(self):
        selected_version = self.versionList.selectedItems()[0]
        self.selected_asset = selected_version.data(QtCore.Qt.UserRole).toPyObject()
        subprocess.Popen(r'explorer /select,' + str(self.selected_asset.full_path))

    def load_assets_from_selected_seq_shot_dept(self):
        # Hide all versions
        [version.setHidden(True) for version in self.versions]

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
        asset = self.Asset(self, 0, self.selected_asset.project, self.selected_asset.sequence, self.selected_asset.shot, self.selected_asset.name, "", self.selected_asset.extension, self.selected_asset.type, new_version, self.selected_asset.tags, self.selected_asset.dependency, self.selected_asset.last_access, self.selected_asset.creator, self.selected_asset.number_of_publishes)
        asset.add_asset_to_db()

        shutil.copy(old_version_path, asset.full_path)
        version_item = QtGui.QListWidgetItem(asset.version + " (" + asset.extension + ")")
        version_item.setData(QtCore.Qt.UserRole, asset)
        self.versions.append(version_item)
        self.versionList.addItem(version_item)

    def publish_asset(self):

        self.selected_asset.change_last_publish()
        if self.selected_asset.type == "mod":
            if self.selected_asset.extension == "blend":
                self.publish_process = QtCore.QProcess(self)
                self.publish_process.finished.connect(self.publish_process_finished)
                self.publish_process.start(self.blender_path, ["-b", "-P", "H:\\01-NAD\\_pipeline\\_utilities\\_asset_manager\\lib\\software_scripts\\blender_export_obj_from_scene.py", "--", self.selected_asset.full_path, self.selected_asset.obj_path])
            elif self.selected_asset.extension == "ma":
                self.publish_process = QtCore.QProcess(self)
                self.publish_process.finished.connect(self.publish_process_finished)
                self.publish_process.readyReadStandardOutput.connect(self.read_data)
                self.publish_process.start(self.maya_batch_path, ["H:\\01-NAD\\_pipeline\\_utilities\\_asset_manager\\lib\\software_scripts\\maya_export_obj_from_scene.py", self.selected_asset.full_path, self.selected_asset.obj_path])
            elif self.selected_asset.extension == "scn":
                self.publish_process = QtCore.QProcess(self)
                self.publish_process.finished.connect(self.publish_process_finished)
                self.publish_process.readyReadStandardOutput.connect(self.read_data)
                self.publish_process.start(self.softimage_batch_path, ["-processing", "-script", "H:\\01-NAD\\_pipeline\\_utilities\\_asset_manager\\lib\\software_scripts\\softimage_export_obj_from_scene.py", "-main", "export_obj", "-args", "-file_path", self.selected_asset.full_path, "-export_path", self.selected_asset.obj_path])

    def publish_process_finished(self):
        # Check if current asset has been favorited by someone.
        favorited_by = self.cursor.execute('''SELECT member FROM favorited_assets WHERE asset_id=?''', (self.selected_asset.id,)).fetchall()
        if favorited_by != None:
            favorited_by = [i[0] for i in favorited_by]
        else:
            favorited_by = []

        # Add log entry saying that the asset has been published.
        self.Lib.add_entry_to_log(self, "All", favorited_by, self.selected_asset.id, "publish", "Asset {0} of type {1} has been published by {2}".format(self.selected_asset.name, self.selected_asset.type, self.selected_asset.last_publish))
        self.update_last_published_time_lbl()
        self.Lib.message_box(self, text="Asset has been successfully published!", type="info")

    def update_thumbnail(self):
        if self.selected_asset.type == "mod":

            dialog = QtGui.QDialog(self)
            dialog.setWindowTitle("Select options")
            dialog_main_layout = QtGui.QVBoxLayout(dialog)

            checkbox_full = QtGui.QCheckBox("Single image (Full Resolution Render)", dialog)
            if not os.path.isfile(self.selected_asset.full_img_path): # If full don't exist, set checkbox to true
                checkbox_full.setCheckState(2)
            checkbox_quad = QtGui.QCheckBox("Four images (Quad View)", dialog)
            if not os.path.isfile(self.selected_asset.quad_img_path): # If quad don't exist, set checkbox to true
                checkbox_quad.setCheckState(2)
            checkbox_turn = QtGui.QCheckBox("Turntable (video)", dialog)
            if not os.path.isfile(self.selected_asset.turn_vid_path): # If turn don't exist, set checkbox to true
                checkbox_turn.setCheckState(2)

            create_btn = QtGui.QPushButton("Start!", dialog)
            create_btn.clicked.connect(dialog.accept)

            dialog_main_layout.addWidget(checkbox_full)
            dialog_main_layout.addWidget(checkbox_quad)
            dialog_main_layout.addWidget(checkbox_turn)
            dialog_main_layout.addWidget(create_btn)

            dialog.exec_()

            if dialog.result() == 0:
                return

            thumbs_to_create = ""
            if checkbox_full.isChecked():
                thumbs_to_create += "full"
            if checkbox_quad.isChecked():
                thumbs_to_create += "quad"
            if checkbox_turn.isChecked():
                thumbs_to_create += "turn"

            self.Lib.create_thumbnails(self, self.selected_asset.obj_path, thumbs_to_create)

    def switch_thumbnail_display(self, type=""):
        if not self.selected_asset:
            return

        if type == "full":
            result = self.check_thumbnails_conditions(type="full")
            if result == True:
                qpixmap = QtGui.QPixmap(self.selected_asset.full_img_path)
                qpixmap = qpixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
                self.assetImg.setData(self.selected_asset.full_img_path)
                self.assetImg.setPixmap(qpixmap)

        elif type == "quad":
            result = self.check_thumbnails_conditions(type="quad")
            if result == True:
                qpixmap = QtGui.QPixmap(self.selected_asset.quad_img_path)
                qpixmap = qpixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
                self.assetImg.setData(self.selected_asset.quad_img_path)
                self.assetImg.setPixmap(qpixmap)

        elif type == "turn":
            result = self.check_thumbnails_conditions(type="turn")
            if result == True:
                subprocess.Popen(["Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_soft\\MPC\\mpc-hc.exe", self.selected_asset.turn_vid_path, "/fullscreen"])

    def check_thumbnails_conditions(self, type=""):
        '''
        When user clicks on full, quad or turn to show given view, this function check if the asset has already been published at least once, if
        there is already a thumbnail or not, and if there's a new published version from which user can make a new thumbnail.
        '''

        if type == "full":
            path = self.selected_asset.full_img_path
        elif type == "quad":
            path = self.selected_asset.quad_img_path
        elif type == "turn":
            path = self.selected_asset.turn_vid_path

        # Asset has never been published, ask for first publish.
        if self.selected_asset.number_of_publishes == 0:
            result = self.Lib.message_box(self, type="warning", text="This asset has never been published. Do you want to publish it?", no_button=True)
            if result == 0:
                return False
            else:
                self.publish_asset()
                return False

        # There's a new published version, ask if user wants to create a new thumbnail
        if os.path.isfile(path):
            last_publish_time = self.selected_asset.last_publish_as_date
            last_modified_img_time = self.Lib.modification_date(self, path)
            if last_publish_time > last_modified_img_time:
                result = self.Lib.thumbnail_creation_box(self, text="There's a new publish available. Do you want to create a thumbnail for it?")
                if result == 1:
                    os.remove(path)
                    self.update_thumbnail()
                    return False

        # Thumbnail has never been created for asset, ask if user wants to create a thumbnail
        if not os.path.isfile(path):
            result = self.Lib.message_box(self, type="warning", text="There is no thumbnail for this asset. Do you want to create one?", no_button=True)
            if result == 0:
                return False
            else:
                self.update_thumbnail()
                return False

        return True

    def load_obj_in_gplay(self):
        subprocess.Popen(["Z:\\RFRENC~1\\Outils\\SPCIFI~1\\Houdini\\HOUDIN~1.13\\bin\\gplay.exe", self.selected_asset.obj_path], shell=True)

    def load_asset(self):
        self.selected_asset.change_last_access()
        self.lastAccessLbl.setText("Last accessed by: " + self.selected_asset.last_access)

        if self.selected_asset.type == "ref":
            os.system(self.selected_asset.full_path)

        elif self.selected_asset.type == "mod":
            if self.selected_asset.extension == "blend":
                t = Thread(target=lambda: subprocess.Popen([self.blender_path, self.selected_asset.full_path]))
                t.start()
            elif self.selected_asset.extension == "ma":
                t = Thread(target=lambda: subprocess.Popen([self.maya_path, self.selected_asset.full_path]))
                t.start()
            elif self.selected_asset.extension == "scn":
                t = Thread(target=lambda: subprocess.Popen([self.softimage_path, self.selected_asset.full_path]))
                t.start()

        elif self.selected_asset.type == "shd":
            process = QtCore.QProcess(self)
            process.start(self.houdini_path, [self.selected_asset.main_hda_path])

        elif self.selected_asset.type == "lay":
            process = QtCore.QProcess(self)
            process.start(self.houdini_path, [self.selected_asset.full_path])

        elif self.selected_asset.type == "rig":
            process = QtCore.QProcess(self)
            process.start(self.maya_path, [self.selected_asset.full_path])

    def delete_asset(self):
        dependencies = self.cursor.execute('''SELECT asset_id FROM assets WHERE asset_dependency=?''', (str(self.selected_asset.id),)).fetchall()
        for asset_id in dependencies:
            asset = self.Asset(self, int(asset_id[0]))
            asset.get_infos_from_id()
            asset.remove_asset_from_db()

        self.selected_asset.remove_asset_from_db()

        # Remove item from asset widget list
        for item in self.assetList.selectedItems():
            self.assetList.takeItem(self.assetList.row(item))

        self.load_all_assets_for_first_time()

        # Hide all versions
        [version.setHidden(True) for version in self.versions]

    def create_asset_from_scratch(self):
        # Create soft selection and asset name dialog
        dialog = QtGui.QDialog(self)
        self.Lib.apply_style(self, dialog)

        dialog.setWindowTitle("Enter a name")
        dialog_main_layout = QtGui.QVBoxLayout(dialog)


        if self.selected_department_name == "mod":
            software_combobox = QtGui.QComboBox(dialog)
            software_combobox.addItems(["Blender", "Maya", "Softimage", "Cinema 4D", "Houdini"])
            dialog_main_layout.addWidget(software_combobox)

        name_line_edit = QtGui.QLineEdit()
        name_line_edit.setPlaceholderText("Please enter a name...")
        name_line_edit.returnPressed.connect(dialog.accept)


        dialog_main_layout.addWidget(name_line_edit)

        dialog.exec_()
        if dialog.result() == 0:
            return

        if self.selected_department_name == "mod":
            # Get selected software and associated extension
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

        # Get asset name
        asset_name = unicode(name_line_edit.text())
        asset_name = self.Lib.normalize_str(self, asset_name)
        asset_name = asset_name_tmp = self.Lib.convert_to_camel_case(self, asset_name)

        # If an asset with given name already exists, change asset name to "assetname-version" (ex: colonne-01) until no asset with given name exists
        version = 1
        all_assets_name = self.cursor.execute('''SELECT asset_name FROM assets''').fetchall()
        all_assets_name = [str(i[0]) for i in all_assets_name]
        while asset_name_tmp in all_assets_name:
            all_assets_name = self.cursor.execute('''SELECT asset_name FROM assets''').fetchall()
            all_assets_name = [str(i[0]) for i in all_assets_name]
            asset_name_tmp = asset_name + "-" + str(version).zfill(2)
            version += 1

        asset_name = asset_name_tmp

        if self.selected_department_name == "mod":
            self.create_modeling_asset_from_scratch(asset_name, extension, selected_software)
        elif self.selected_department_name == "lay":
            self.create_layout_asset_from_scratch(asset_name)

    def create_asset_from_asset(self):
        if self.selected_department_name == "mod":
            if self.selected_asset == None: return
            if self.selected_asset.type != "mod": return
            self.create_from_asset_dialog = QtGui.QDialog(self)
            self.Lib.apply_style(self, self.create_from_asset_dialog)

            self.create_from_asset_dialog.setWindowTitle("Enter a name")
            self.create_from_asset_dialog_main_layout = QtGui.QHBoxLayout(self.create_from_asset_dialog)

            rigBtn = QtGui.QPushButton("Rig", self.create_from_asset_dialog)
            texBtn = QtGui.QPushButton("Tex", self.create_from_asset_dialog)

            rigBtn.clicked.connect(self.create_rig_asset_from_mod)
            texBtn.clicked.connect(self.create_tex_asset_from_mod)

            self.create_from_asset_dialog_main_layout.addWidget(rigBtn)
            self.create_from_asset_dialog_main_layout.addWidget(texBtn)

            self.create_from_asset_dialog.exec_()

    def create_rig_asset_from_mod(self):

        self.create_from_asset_dialog.close()

        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, self.selected_asset.name, "", "ma", "rig", "01", [], "", "", "", self.username)
        asset.add_asset_to_db()

        obj_path = str(self.selected_asset.obj_path)
        file_export = str(self.selected_asset.full_path)
        file_export = os.path.splitext(file_export)[0].replace("mod", "rig").replace("out", "01") + ".ma"
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(partial(self.asset_creation_finished, asset))
        self.process.waitForFinished()
        self.process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_import_obj_as_reference.py", obj_path, file_export])

    def create_tex_asset_from_mod(self):
        self.create_from_asset_dialog.close()
        print("Tex")

    def create_modeling_asset_from_scratch(self, asset_name="", extension=None, selected_software=None):

        # Create modeling scene asset
        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", extension, "mod", "01", [], "", "", "", self.username)
        asset.add_asset_to_db()
        main_id = asset.id
        shutil.copy(self.NEF_folder + "\\" + selected_software + "." + extension, asset.full_path)

        # Create default publish cube (obj)
        obj_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "obj", "mod", "out", [], main_id, "", "", self.username)
        obj_asset.add_asset_to_db()
        shutil.copy(self.NEF_folder + "\\default_cube.obj", obj_asset.full_path)

        # Create main HDA database entry
        main_hda_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "lay", "out", [], main_id, "", "", self.username)
        main_hda_asset.add_asset_to_db()

        # Create shading HDA database entry
        shading_hda_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "shd", "01", [], main_id, "", "", self.username)
        shading_hda_asset.add_asset_to_db()

        # Create HDA associated to modeling scene
        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.finished.connect(partial(self.asset_creation_finished, asset))
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_modeling_hda.py", main_hda_asset.full_path, shading_hda_asset.full_path, main_hda_asset.obj_path, asset_name])

    def create_layout_asset_from_scratch(self, asset_name):

        # Create modeling scene asset
        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hipnc", "lay", "01", [], "", "", "", self.username)
        asset.add_asset_to_db()
        shutil.copy(self.NEF_folder + "\\houdini.hipnc", asset.full_path)

        self.asset_creation_finished(asset)

    def asset_creation_finished(self, asset):
        # Reload assets
        self.load_all_assets_for_first_time()
        self.load_assets_from_selected_seq_shot_dept()

        # Update last access
        asset.change_last_access()
        self.lastAccessLbl.setText("Last accessed by: " + asset.last_access)

        # Update last publish
        self.update_last_published_time_lbl(asset)

        # Show info message
        self.Lib.message_box(self, type="info", text="Asset has been succesfully created!")

    def add_assets_to_layout(self):

        AddAssetsToLayoutWindow(self)


class AddAssetsToLayoutWindow(QtGui.QDialog, Ui_addAssetsToLayoutWidget):
    def __init__(self, main):
        super(AddAssetsToLayoutWindow, self).__init__()

        self.main = main

        # Initialize the guis
        self.add_assets_layout = self.setupUi(self)
        self.main.Lib.apply_style(self.main, self)

        # Connections
        self.availableAssetsListWidget.itemClicked.connect(self.left_list_item_clicked)
        self.assetsToAddListWidget.itemClicked.connect(self.right_list_item_clicked)

        self.addAssetBtn.clicked.connect(self.add_asset_to_list)
        self.removeAssetBtn.clicked.connect(self.remove_asset_from_list)

        self.assets_in_layout = []
        self.assets_in_layout_db = []

        self.get_assets_from_layout = QtCore.QProcess(self)
        self.get_assets_from_layout.readyRead.connect(self.get_assets_from_process_output)
        self.get_assets_from_layout.finished.connect(self.finished)
        self.get_assets_from_layout.start(self.main.houdini_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\houdini_get_assets_in_layout.py", self.main.selected_asset.full_path])

    def get_assets_from_process_output(self):
        while self.get_assets_from_layout.canReadLine():
            out = str(self.get_assets_from_layout.readLine())
            self.assets_in_layout.append(out)

    def finished(self):
        self.assets_in_layout = [i.strip(' \t\n\r') for i in self.assets_in_layout]

        # Get only last three / of all paths (ex: H:/01-NAD/_pipeline/test_project_files/assets/lay/nat_xxx_xxxx_lay_colonne_out.hda = \assets\lay\nat_xxx_xxxx_lay_colonne_out.hda)
        self.assets_in_layout = ["\\" + "\\".join(i.split("/")[-3:len(i.split("/"))]) for i in self.assets_in_layout]
        self.assets_in_layout_db = []
        for asset_path in self.assets_in_layout: # Get database entries from assets path
            asset_from_db = self.main.cursor.execute('''SELECT * FROM assets WHERE asset_path=?''', (asset_path,)).fetchone()
            asset_id = asset_from_db[0]
            asset = self.main.Asset(self.main, asset_id)
            asset.get_infos_from_id()
            self.assets_in_layout_db.append(asset)

        # Get IDs of all assets in layout
        self.assets_in_layout_db_id = [i.id for i in self.assets_in_layout_db]
        # Get all layout assets
        self.all_layout_assets = self.main.cursor.execute('''SELECT * FROM assets WHERE asset_type="lay" AND asset_extension="hda"''').fetchall()


        # Add available assets to left list if they're not already in layout scene
        for asset in self.all_layout_assets:
            asset_id = asset[0]
            asset_name = asset[4]
            if not asset_id in self.assets_in_layout_db_id: # if asset is not already in layout scene, add it
                asset_object = self.main.Asset(self.main, asset_id)
                asset_object.get_infos_from_id()
                item = QtGui.QListWidgetItem(asset_object.name)
                item.setData(QtCore.Qt.UserRole, asset_object)
                self.availableAssetsListWidget.addItem(item)

        self.exec_()

    def left_list_item_clicked(self):
        self.selected_asset = self.availableAssetsListWidget.selectedItems()[0]
        self.selected_asset = self.selected_asset.data(QtCore.Qt.UserRole).toPyObject()
        self.load_image_from_asset()

    def right_list_item_clicked(self):
        self.selected_asset = self.assetsToAddListWidget.selectedItems()[0]
        self.selected_asset = self.selected_asset.data(QtCore.Qt.UserRole).toPyObject()
        self.load_image_from_asset()

    def load_image_from_asset(self):
        replaced_path = self.selected_asset.full_path.replace("lay", "mod").replace(".hda", "_full.jpg")
        thumb_path = os.path.split(replaced_path)[0] + "\\.thumb\\"
        img_path =  os.path.split(replaced_path)[1]
        full_img_path = thumb_path + img_path
        qpixmap = QtGui.QPixmap(full_img_path)
        qpixmap = qpixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
        self.assetPreviewLbl.setPixmap(qpixmap)

    def add_asset_to_list(self):
        # Create listwidget item from selected asset
        item = QtGui.QListWidgetItem(self.selected_asset.name)
        item.setData(QtCore.Qt.UserRole, self.selected_asset)

        # Add item to right list
        self.assetsToAddListWidget.addItem(item)

        # Remove item from left list
        for item in self.availableAssetsListWidget.selectedItems():
            self.availableAssetsListWidget.takeItem(self.availableAssetsListWidget.row(item))

    def remove_asset_from_list(self):
        # Create listwidget item from selected asset
        item = QtGui.QListWidgetItem(self.selected_asset.name)
        item.setData(QtCore.Qt.UserRole, self.selected_asset)

        # Add item to left list
        self.availableAssetsListWidget.addItem(item)

        # Remove item from right list
        for item in self.assetsToAddListWidget.selectedItems():
            self.assetsToAddListWidget.takeItem(self.assetsToAddListWidget.row(item))


