#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
from PyQt4.phonon import Phonon
import subprocess
from functools import partial
import os
import shutil
from threading import Thread
from datetime import datetime
import time
from glob import glob

from ui.add_assets_to_layout import Ui_addAssetsToLayoutWidget

class AssetLoader(object):

    def __init__(self):

        self.favorite_icon = QtGui.QIcon(self.cur_path + "\\media\\favorite.png")
        self.unfavorite_icon = QtGui.QIcon(self.cur_path + "\\media\\unfavorite.png")
        self.comment_icon = QtGui.QIcon(self.cur_path + "\\media\\comment.png")
        self.comment_disabled_icon = QtGui.QIcon(self.cur_path + "\\media\\comment_disabled.png")
        self.publish_icon = QtGui.QIcon(self.cur_path + "\\media\\publish.png")
        self.publish_disabled_icon = QtGui.QIcon(self.cur_path + "\\media\\publish_disabled.png")
        self.new_version_icon = QtGui.QIcon(self.cur_path + "\\media\\new_version.png")
        self.new_version_disabled_icon = QtGui.QIcon(self.cur_path + "\\media\\new_version_disabled.png")
        self.load_asset_icon = QtGui.QIcon(self.cur_path + "\\media\\load_asset.png")
        self.load_asset_disabled_icon = QtGui.QIcon(self.cur_path + "\\media\\load_asset_disabled.png")
        self.import_high_res_obj_icon = QtGui.QIcon(self.cur_path + "\\media\\import_layout_asset.png")

        self.showAssetCommentBtn.setIcon(self.comment_disabled_icon)
        self.publishBtn.setIcon(self.publish_disabled_icon)
        self.createVersionBtn.setIcon(self.new_version_disabled_icon)
        self.loadAssetBtn.setIcon(self.load_asset_disabled_icon)
        self.importIntoSceneBtn.setIcon(self.import_high_res_obj_icon)
        self.importIntoSceneBtn.hide()


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
        self.selected_department_name = "mod"
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
        self.shotList.itemDoubleClicked.connect(self.shotList_DoubleClicked)
        self.assetList.itemClicked.connect(self.assetList_Clicked)
        self.versionList.itemDoubleClicked.connect(self.versionList_DoubleClicked)
        self.versionList.itemClicked.connect(self.versionList_Clicked)
        self.connect(self.versionList, QtCore.SIGNAL('arrow_key_pressed'), self.versionList_Clicked)
        self.connect(self.versionList, QtCore.SIGNAL('delete_selected_asset_version'), self.remove_version)


        self.usernameAdminComboBox.currentIndexChanged.connect(self.change_username)

        # Connect the buttons
        self.showAssetCommentBtn.clicked.connect(self.show_comments)
        self.addRemoveAssetAsFavoriteBtn.clicked.connect(self.change_favorite_state)
        self.addRemoveAssetAsFavoriteBtn.setIcon(self.unfavorite_icon)
        self.addRemoveAssetAsFavoriteBtn.setIconSize(QtCore.QSize(24, 24))

        self.addProjectBtn.clicked.connect(self.add_project)
        self.addSequenceBtn.clicked.connect(self.add_sequence)
        self.addShotBtn.clicked.connect(self.add_shot)

        self.thumbFullBtn.clicked.connect(partial(self.switch_thumbnail_display, "full"))
        self.thumbTurnBtn.clicked.connect(partial(self.switch_thumbnail_display, "turn"))
        self.loadObjInGplayBtn.clicked.connect(self.load_obj_in_gplay)

        self.seqFilterClearBtn.clicked.connect(partial(self.clear_filter, "seq"))
        self.assetFilterClearBtn.clicked.connect(partial(self.clear_filter, "asset"))
        self.updateThumbBtn.clicked.connect(self.update_thumbnail)
        self.loadAssetBtn.clicked.connect(self.load_asset)
        self.importIntoSceneBtn.clicked.connect(self.import_into_scene)

        self.createAssetFromScratchBtn.clicked.connect(self.create_asset_from_scratch)
        self.createAssetFromScratchAssetBtn.clicked.connect(self.create_asset_from_asset)
        self.deleteAssetBtn.clicked.connect(self.delete_asset)

        self.createVersionBtn.clicked.connect(self.create_new_version)
        self.publishBtn.clicked.connect(self.publish_asset)

        self.showPlayBlastBtn.clicked.connect(self.show_anm_playblast)
        self.showPlayBlastBtn.hide()

    def show_comments(self):
        if self.selected_asset == None:
            return
        self.CommentsFrame.show()
        self.commentLineEdit.setFocus()
        self.CommentWidget.load_comments(self)

    def change_favorite_state(self):

        if self.selected_asset == None:
            return

        selected_asset_publish = self.cursor.execute('''SELECT asset_id FROM assets WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_type=? AND asset_version="out"''', (self.selected_asset.sequence, self.selected_asset.shot, self.selected_asset.name, self.selected_asset.type, )).fetchone()
        selected_asset_publish_id = selected_asset_publish[0]

        is_asset_favorited = self.cursor.execute('''SELECT * FROM favorited_assets WHERE asset_id=? AND member=?''', (selected_asset_publish_id, self.username,)).fetchone()
        if is_asset_favorited == None: # Asset is not already favorited by member
            self.cursor.execute('''INSERT INTO favorited_assets(asset_id, member) VALUES(?,?)''', (selected_asset_publish_id, self.username,))
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
        self.cursor.execute('''INSERT INTO shots(project_name, sequence_name, shot_number, frame_start, frame_end) VALUES (?, ?, ?, ?, ?)''',
                            (self.selected_project_name, self.selected_sequence_name, shot_number, "1", "1"))

        self.db.commit()

        # Add shot to GUI
        self.shotList.addItem(shot_number)
        self.seqList_Clicked()

    def load_all_assets_for_first_time(self):
        '''
        Add all assets from selected project. Only run once to rebuild assets objects from Asset class.
        '''
        self.assets = {}
        assets_list = []
        self.versions = []
        self.assetList.clear()
        self.versionList.clear()

        self.departmentList.clearSelection()
        self.assetList.clearSelection()
        self.versionList.clearSelection()

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
            publish_from_version = asset[15]

            # Create ListWidget Item
            asset_item = QtGui.QListWidgetItem(asset_name)

            # Create asset object and attach it to the ListWidgetItem
            asset = self.Asset(self, asset_id, project_name, sequence_name, shot_number, asset_name, asset_path, asset_extension, asset_type, asset_version, asset_tags, asset_dependency, last_access, last_publish, creator, number_of_publishes, publish_from_version)
            asset_item.setData(QtCore.Qt.UserRole, asset)

            # Dictionary of asset objects associated with listwidget item (Exemple Class Asset -> ListWidgetItem)
            # Useful to have access to both the asset object and its associated ListWidgetItem.
            self.assets[asset] = asset_item

            # Append each item's sequence, shot, name and type to a list to only add first version of an asset to assetList
            assets_list.append((asset.sequence, asset.shot, asset.name, asset.type))
            if asset.version != "out" and asset.type != "ref":
                # If there's less than 2 entries for an asset, add it to the assetList.
                # If there's more than 2 entries, it means that current loop is on the version 02 or more of an asset.
                # Therefore, its first version is already in the assetList and you don't need to add the other versions too.
                if assets_list.count((asset.sequence, asset.shot, asset.name, asset.type)) < 2:
                    self.assetList.addItem(asset_item)
                    asset_item.setHidden(True) # Hide item by default

                # Add all versions to version List.
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
        self.shots_framerange = {}
        for seq in self.sequences:
            shots = (self.cursor.execute('''SELECT shot_number, frame_start, frame_end FROM shots WHERE project_name=? AND sequence_name=?''', (self.selected_project_name, seq[0],))).fetchall()
            self.shots[str(seq[0])] = [str(shot[0]) for shot in shots]
            for shot in shots:
                self.shots_framerange[str(seq[0]) + "-" + str(shot[0])] = (shot[1], shot[2])

        # Populate the sequences and shots lists
        self.seqList.clear()
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

        self.selected_shot_number = "xxxx"

        self.selected_sequence_name = str(self.seqList.selectedItems()[0].text())
        if self.selected_sequence_name == "None":
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

    def shotList_DoubleClicked(self):

        if self.selected_shot_number == "All" or self.selected_shot_number == "xxxx":
            return

        framerange = self.cursor.execute('''SELECT frame_start, frame_end FROM shots WHERE project_name=? AND sequence_name=? AND shot_number=?''', (self.selected_project_name, self.selected_sequence_name, self.selected_shot_number,)).fetchone()
        start_frame = framerange[0]
        end_frame = framerange[1]

        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Change Framerange")
        dialog.setMinimumWidth(200)
        layout = QtGui.QGridLayout(dialog)

        start_spinbox = QtGui.QSpinBox()
        end_spinbox = QtGui.QSpinBox()

        start_spinbox.setMinimum(1)
        start_spinbox.setMaximum(10000)
        end_spinbox.setMinimum(1)
        end_spinbox.setMaximum(10000)

        start_spinbox.setValue(start_frame)
        end_spinbox.setValue(end_frame)

        if self.username != "thoudon" or self.username != "lclavet":
            update_btn = QtGui.QPushButton("Update Framerange", dialog)
            update_btn.clicked.connect(dialog.accept)
            layout.addWidget(start_spinbox, 0, 0)
            layout.addWidget(end_spinbox, 0, 1)
            layout.addWidget(update_btn, 1, 0, 2, 2)
        else:
            start_spinbox.setDisabled(True)
            end_spinbox.setDisabled(True)
            layout.addWidget(start_spinbox, 0, 0)
            layout.addWidget(end_spinbox, 0, 1)



        dialog.exec_()

        if dialog.result() == 0:
            return

        new_start_frame = start_spinbox.value()
        new_end_frame = end_spinbox.value()

        self.cursor.execute('''UPDATE shots SET frame_start=?, frame_end=? WHERE project_name=? AND sequence_name=? AND shot_number=?''', (new_start_frame, new_end_frame, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number,))
        self.db.commit()

    def departmentList_Clicked(self):

        # Hide load obj buttons
        self.importIntoSceneBtn.hide()

        # Reset last publish and last access text
        self.lastAccessLbl.setText("Last accessed by: ...")
        self.lastPublishedLbl.setText("Last published by: ...")

        self.selected_department_name = str(self.departmentList.selectedItems()[0].text())
        self.selected_department_name = self.departments_shortname[self.selected_department_name]

        qpixmap = QtGui.QPixmap(self.no_img_found)
        qpixmap = qpixmap.scaledToWidth(300, QtCore.Qt.SmoothTransformation)
        self.assetImg.setData(self.no_img_found)
        self.assetImg.setPixmap(qpixmap)

        self.updateThumbBtn.hide()

        if self.selected_department_name == "ref":
            self.loadObjInGplayBtn.hide()
            self.showPlayBlastBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "mod":
            self.loadObjInGplayBtn.show()
            self.showPlayBlastBtn.hide()
            self.thumbDisplayTypeFrame.show()

        elif self.selected_department_name == "tex":
            self.loadObjInGplayBtn.hide()
            self.showPlayBlastBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "rig":
            self.loadObjInGplayBtn.hide()
            self.showPlayBlastBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "anm":
            self.showPlayBlastBtn.show()
            self.loadObjInGplayBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "sim":
            self.loadObjInGplayBtn.hide()
            self.showPlayBlastBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "shd":
            self.loadObjInGplayBtn.hide()
            self.showPlayBlastBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "lay":
            self.loadObjInGplayBtn.hide()
            self.showPlayBlastBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "dmp":
            self.loadObjInGplayBtn.hide()
            self.showPlayBlastBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "cmp":
            self.loadObjInGplayBtn.hide()
            self.showPlayBlastBtn.hide()
            self.thumbDisplayTypeFrame.hide()

        elif self.selected_department_name == "rdr":
            self.loadObjInGplayBtn.hide()
            self.showPlayBlastBtn.hide()
            self.thumbDisplayTypeFrame.hide()
            self.selected_department_name = "lay"

        else:
            self.loadObjInGplayBtn.hide()
            self.showPlayBlastBtn.hide()
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
            if selected_asset.name == asset.name and asset.type == self.selected_department_name:
                version.setHidden(False)
                version.setSelected(True)
            else:
                version.setHidden(True)

        self.updateThumbBtn.show()
        self.versionList_Clicked()

    def versionList_Clicked(self):

        # If user press arrow key in a tab other than Asset Loader, don't do anything
        current_tab_text = self.Tabs.tabText(self.Tabs.currentIndex())
        if current_tab_text != "Asset Loader":
            return

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
        elif self.selected_asset.type == "anm":
            if not os.path.isfile(self.selected_asset.anim_playblast_path.replace("mp4", "jpg")):
                img_path, width = self.no_img_found, 300
            else:
                if os.path.isfile(self.selected_asset.anim_playblast_path.replace("mp4", "jpg")):
                    img_path, width = self.selected_asset.anim_playblast_path.replace("mp4", "jpg"), 500

            qpixmap = QtGui.QPixmap(img_path)
            qpixmap = qpixmap.scaledToWidth(width, QtCore.Qt.SmoothTransformation)
            self.assetImg.setData(img_path)
            self.assetImg.setPixmap(qpixmap)

        elif self.selected_asset.type == "lay" and self.selected_asset.extension == "hda" and self.selected_asset.version != "out":
            if not os.path.isfile(self.selected_asset.full_img_path):
                img_path, width = self.no_img_found, 300
            else:
                img_path, width = self.selected_asset.full_img_path, 500

            qpixmap = QtGui.QPixmap(img_path)
            qpixmap = qpixmap.scaledToWidth(width, QtCore.Qt.SmoothTransformation)
            self.assetImg.setData(img_path)
            self.assetImg.setPixmap(qpixmap)

        else:
            qpixmap = QtGui.QPixmap(self.no_img_found)
            qpixmap = qpixmap.scaledToWidth(300, QtCore.Qt.SmoothTransformation)
            self.assetImg.setData(self.no_img_found)
            self.assetImg.setPixmap(qpixmap)


        if self.selected_asset.type == "mod" or self.selected_asset.type == "anm" or self.selected_asset.type == "lay":
            self.importIntoSceneBtn.show()
        else:
            self.importIntoSceneBtn.hide()

        # Set labels
        self.lastAccessLbl.setText("Last accessed by: " + self.selected_asset.last_access)

        # Set favorite button state
        selected_asset_publish = self.cursor.execute('''SELECT asset_id FROM assets WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_type=? AND asset_version="out"''', (self.selected_asset.sequence, self.selected_asset.shot, self.selected_asset.name, self.selected_asset.type,)).fetchone()
        if not selected_asset_publish == None:
            selected_asset_publish_id = selected_asset_publish[0]
        else:
            selected_asset_publish_id = 0

        is_asset_favorited = self.cursor.execute('''SELECT * FROM favorited_assets WHERE asset_id=? AND member=?''', (selected_asset_publish_id, self.username,)).fetchone()
        if is_asset_favorited == None:
            self.addRemoveAssetAsFavoriteBtn.setIcon(self.unfavorite_icon)
        else:
            self.addRemoveAssetAsFavoriteBtn.setIcon(self.favorite_icon)

        # Set comment icon to enabled
        self.showAssetCommentBtn.setIcon(self.comment_icon)

        # Set publish icon to enabled
        self.publishBtn.setIcon(self.publish_icon)

        # Set create new version icon to enabled
        self.createVersionBtn.setIcon(self.new_version_icon)

        # Set load asset icon to enabled
        self.loadAssetBtn.setIcon(self.load_asset_icon)

        # Set last publish comment
        publish_comments = self.cursor.execute('''SELECT publish_time, publish_comment, publish_creator FROM publish_comments WHERE asset_id=?''', (self.selected_asset.id,)).fetchall()
        comments = ""
        for comment in reversed(publish_comments):
            publish_time = comment[0]
            publish_comment = comment[1]
            publish_creator = comment[2]
            comments += u"{0} (by {1}): {2}\n\n".format(publish_time, self.members[publish_creator], publish_comment)

        self.lastPublishComment.setText(comments)

        # Set last publish label
        if self.selected_asset.type != "lay" and self.selected_asset.type != "shd" and self.selected_asset.extension != "hipnc" and self.selected_asset.type != "cam" and self.selected_asset.type:

            asset_published = self.Asset(self, self.selected_asset.dependency)
            asset_published.get_infos_from_id()
            self.update_last_published_time_lbl(asset_published)

    def update_last_published_time_lbl(self, asset_published=None):

        # Set last published date label
        day_today = datetime.now()
        number_of_days_since_last_publish = day_today - asset_published.last_publish_as_date
        number_of_days_since_last_publish = number_of_days_since_last_publish.days

        if number_of_days_since_last_publish == 0:
            number_of_days_since_last_publish = "today"
        elif number_of_days_since_last_publish > 7:
            number_of_days_since_last_publish = str(number_of_days_since_last_publish) + " days ago. You should publish a new version!"
            self.lastPublishedLbl.setStyleSheet("color: red;")
        else:
            number_of_days_since_last_publish = str(number_of_days_since_last_publish) + " days ago"

        publish_from_version_asset_id = asset_published.publish_from_version
        publish_from_version = self.cursor.execute('''SELECT asset_version FROM assets WHERE asset_id=?''', (publish_from_version_asset_id,)).fetchone()
        if publish_from_version == None or publish_from_version == "":
            publish_from_version = "01"
        else:
            publish_from_version = publish_from_version[0]
        self.lastPublishedLbl.setText("Last published by: {0} ({1}) from version {2}".format(asset_published.last_publish, number_of_days_since_last_publish, publish_from_version, ))

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
            if asset.sequence != self.selected_sequence_name:
                asset_item.setHidden(True)

            if asset.shot != self.selected_shot_number and self.selected_shot_number != "xxxx":
                asset_item.setHidden(True)

            if asset.type != self.selected_department_name:
                asset_item.setHidden(True)

            # If asset is a houdini modeling, only show it when user clicks on modeling dep and not on layout
            if self.selected_department_name == "mod" and self.selected_sequence_name == asset.sequence and asset.extension == "hda" and asset.type == "lay" and asset.version != "out":
                asset_item.setHidden(False)
            elif self.selected_department_name == "lay" and self.selected_sequence_name == asset.sequence and asset.extension == "hda" and asset.type == "lay" and asset.version != "out":
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

        old_version_path = self.selected_asset.full_path
        new_version = str(int(self.selected_asset.version) + 1).zfill(2)

        asset = self.Asset(self, 0, self.selected_asset.project, self.selected_asset.sequence, self.selected_asset.shot, self.selected_asset.name, "", self.selected_asset.extension, self.selected_asset.type, new_version, self.selected_asset.tags, self.selected_asset.dependency, self.selected_asset.last_access, self.selected_asset.last_publish, self.selected_asset.creator, self.selected_asset.number_of_publishes)
        asset.add_asset_to_db()

        if self.selected_asset.type == "tex":
            # Get path of selected texture asset folder
            texture_project_path = self.Lib.get_mari_project_path_from_asset_name(self, self.selected_asset.name, self.selected_asset.version)
            # Switch cache directory location to user H
            self.Lib.switch_mari_cache(self, "home")
            # Remove folder if it already exists
            if os.path.isdir("H:/mari_cache_tmp_synthese/" + texture_project_path):
                shutil.rmtree("H:/mari_cache_tmp_synthese/" + texture_project_path)
            # Copy texture asset folder from Z to H
            shutil.copytree("Z:/Groupes-cours/NAND999-A15-N01/Nature/tex/" + texture_project_path, "H:/mari_cache_tmp_synthese/" + texture_project_path)

            # Start mari process
            self.mari_process = QtCore.QProcess(self)
            self.mari_process.waitForFinished()
            self.mari_process.readyRead.connect(self.mari_process_read_data)
            self.mari_process.finished.connect(partial(self.create_new_tex_version_finished, texture_project_path, asset))
            self.mari_process.start(self.mari_path, ["-t", self.cur_path + "\\lib\\software_scripts\\mari_create_new_version.py"])
            return


        if self.selected_asset.version == "out":
            self.Lib.message_box(self, text="You can't create a new version from a published asset")
            return

        try:
            shutil.copy(old_version_path, asset.full_path)
        except:
            asset.remove_asset_from_db()
            return

        version_item = QtGui.QListWidgetItem(asset.version + " (" + asset.extension + ")")
        version_item.setData(QtCore.Qt.UserRole, asset)
        self.versions.append(version_item)
        self.versionList.addItem(version_item)
        self.versionList.setItemSelected(version_item, True)
        self.versionList_Clicked()

    def create_new_tex_version_finished(self, existing_project_path, asset):
        self.mari_process.kill()

        # Remove folder for current version of texture asset
        shutil.rmtree("H:/mari_cache_tmp_synthese/" + existing_project_path)

        # Get folder path of new texture asset version
        paths = glob("H:/mari_cache_tmp_synthese/*")
        paths = [i.replace("\\", "/") for i in paths]
        paths = [i for i in paths if not "SINGLE" in i and not "Generic" in i]

        # Copy folder of new texture asset version back to the tex folder
        shutil.move(paths[0], "Z:/Groupes-cours/NAND999-A15-N01/Nature/tex/" + paths[0].split("/")[-1])

        # Add item to version list
        version_item = QtGui.QListWidgetItem(asset.version + " (" + asset.extension + ")")
        version_item.setData(QtCore.Qt.UserRole, asset)
        self.versions.append(version_item)
        self.versionList.addItem(version_item)
        self.versionList.setItemSelected(version_item, True)
        self.versionList_Clicked()

        self.Lib.message_box(self, type="info", text="New version successfully created!")

    def remove_version(self):

        # Confirm dialog
        confirm_dialog = QtGui.QMessageBox()
        reply = confirm_dialog.question(self, 'Delete selected version', "Are you sure ?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        self.Lib.apply_style(self, confirm_dialog)
        if reply != QtGui.QMessageBox.Yes:
            return

        self.selected_asset.remove_asset_from_db()
        for item in self.versionList.selectedItems():
            self.versionList.takeItem(self.versionList.row(item))

    def publish_asset(self):

        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Add a comment")
        self.Lib.apply_style(self, dialog)

        dialog_layout = QtGui.QVBoxLayout(dialog)

        publish_comment_text_edit = QtGui.QTextEdit(dialog)
        publish_accept_btn = QtGui.QPushButton("Publish asset!", dialog)
        publish_accept_btn.clicked.connect(dialog.accept)

        dialog_layout.addWidget(publish_comment_text_edit)
        dialog_layout.addWidget(publish_accept_btn)
        dialog.exec_()

        if dialog.result() == 0:
            return

        # Add publish comment to database
        publish_comment = unicode(self.utf8_codec.fromUnicode(publish_comment_text_edit.toPlainText()), 'utf-8')
        self.cursor.execute('''INSERT INTO publish_comments(asset_id, publish_comment, publish_time, publish_creator) VALUES(?,?,?,?)''', (self.selected_asset.id, publish_comment, datetime.now().strftime("%d/%m/%Y at %H:%M"), self.username))
        self.db.commit()

        # Update last publish time
        self.selected_asset.change_last_publish()
        if self.selected_asset.type == "mod":
            if self.selected_asset.extension == "blend":
                self.publish_process = QtCore.QProcess(self)
                self.publish_process.finished.connect(self.publish_process_finished)
                self.publish_process.start(self.blender_path, ["-b", "-P", self.cur_path + "\\lib\\software_scripts\\blender_export_obj_from_scene.py", "--", self.selected_asset.full_path, self.selected_asset.obj_path])
            elif self.selected_asset.extension == "ma":
                self.publish_process = QtCore.QProcess(self)
                self.publish_process.finished.connect(self.publish_process_finished)
                self.publish_process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_export_obj_from_scene.py", self.selected_asset.full_path, self.selected_asset.obj_path])
            elif self.selected_asset.extension == "scn":
                self.publish_process = QtCore.QProcess(self)
                self.publish_process.finished.connect(self.publish_process_finished)
                self.publish_process.start(self.softimage_batch_path, ["-processing", "-script", self.cur_path + "\\lib\\software_scripts\\softimage_export_obj_from_scene.py", "-main", "export_obj", "-args", "-file_path", self.selected_asset.full_path, "-export_path", self.selected_asset.obj_path])
            elif self.selected_asset.extension == "hda":
                self.publish_process = QtCore.QProcess(self)
                self.publish_process.finished.connect(self.publish_process_finished)
                self.publish_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_export_mod_from_mod.py", self.selected_asset.full_path])

            self.cursor.execute('''UPDATE assets SET publish_from_version=? WHERE asset_path=?''', (self.selected_asset.id, self.selected_asset.obj_path.replace(self.selected_project_path, ""),))
            self.db.commit()

        elif self.selected_asset.type == "rig":
            shutil.copy2(self.selected_asset.full_path, self.selected_asset.rig_out_path)
            self.publish_process_finished()

        elif self.selected_asset.type == "anm":
            # Get frame range from selected shot
            framerange = self.shots_framerange[self.selected_asset.sequence + "-" + self.selected_asset.shot]
            start_frame = framerange[0]
            end_frame = framerange[1]

            self.publish_process = QtCore.QProcess(self)
            self.publish_process.finished.connect(self.publish_process_finished)
            self.publish_process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_export_anm_as_alembic.py", self.selected_asset.full_path.replace("\\", "/"), self.selected_asset.anim_out_path.replace("\\", "/"), str(start_frame), str(end_frame)])

            self.cursor.execute('''UPDATE assets SET publish_from_version=? WHERE asset_path=?''', (self.selected_asset.id, self.selected_asset.anim_out_path.replace(self.selected_project_path, ""),))
            self.db.commit()

        elif self.selected_asset.type == "cam":
            # Get frame range from selected shot
            framerange = self.shots_framerange[self.selected_asset.sequence + "-" + self.selected_asset.shot]
            start_frame = str(framerange[0])
            end_frame = str(framerange[1])

            export_path = str(self.selected_asset.full_path.replace("_" + self.selected_asset.version + ".", "_out.").replace(".hda", ".abc").replace("\\", "/"))
            hda_path = str(self.selected_asset.full_path.replace("\\", "/"))
            camera_name = str(self.selected_asset.name)

            self.publish_process = QtCore.QProcess(self)
            self.publish_process.finished.connect(self.publish_process_finished)
            self.publish_process.waitForFinished()
            self.publish_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_export_cam_from_lay.py", export_path, hda_path, camera_name, start_frame, end_frame])

    def publish_process_finished(self):

        # If published asset was of type mod, normalize its scale
        if self.selected_asset.type == "mod" or (self.selected_asset.type == "lay" and self.selected_asset.extension == "hda" and self.selected_asset.version != "out"):
            self.normalize_mod_scale_process = QtCore.QProcess(self)
            self.normalize_mod_scale_process.waitForFinished()
            print(self.selected_asset.obj_path)
            self.normalize_mod_scale_process.start(self.blender_path, ["-b", "-P", self.cur_path + "\\lib\\software_scripts\\blender_normalize_mod_scale.py", "--", self.selected_asset.obj_path])

        # Check if current asset has been favorited by someone.
        favorited_by = self.cursor.execute('''SELECT member FROM favorited_assets WHERE asset_id=?''', (self.selected_asset.id,)).fetchall()
        if favorited_by != None:
            favorited_by = [i[0] for i in favorited_by]
        else:
            favorited_by = []

        # Add log entry saying that the asset has been published.
        log_entry = self.LogEntry(self, 0, self.selected_asset.id, [], favorited_by, self.username, "", "publish", "{0} has published a new version of asset {1} ({2}).".format(self.members[self.username], self.selected_asset.name, self.departments_longname[self.selected_asset.type]), datetime.now().strftime("%d/%m/%Y at %H:%M"))
        log_entry.add_log_to_database()
        self.Lib.message_box(self, text="Asset has been successfully published!", type="info")

        # Confirm dialog
        confirm_dialog = QtGui.QMessageBox()
        reply = confirm_dialog.question(self, 'Create thumbnail?', "Do you want to update the thumbnails?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        self.Lib.apply_style(self, confirm_dialog)
        if reply == QtGui.QMessageBox.No:
            return

        self.update_thumbnail()

    def update_thumbnail(self):
        if self.selected_asset.type == "mod":

            dialog = QtGui.QDialog(self)
            dialog.setWindowTitle("Select options")
            dialog_main_layout = QtGui.QVBoxLayout(dialog)

            checkbox_full = QtGui.QCheckBox("Single image (Full Resolution Render)", dialog)
            if not os.path.isfile(self.selected_asset.full_img_path): # If full don't exist, set checkbox to true
                checkbox_full.setCheckState(2)
            checkbox_turn = QtGui.QCheckBox("Turntable (video)", dialog)
            if not os.path.isfile(self.selected_asset.turn_vid_path): # If turn don't exist, set checkbox to true
                checkbox_turn.setCheckState(2)

            create_btn = QtGui.QPushButton("Start!", dialog)
            create_btn.clicked.connect(dialog.accept)

            dialog_main_layout.addWidget(checkbox_full)
            dialog_main_layout.addWidget(checkbox_turn)
            dialog_main_layout.addWidget(create_btn)

            dialog.exec_()

            if dialog.result() == 0:
                return

            thumbs_to_create = ""
            if checkbox_full.isChecked():
                thumbs_to_create += "full"
            if checkbox_turn.isChecked():
                thumbs_to_create += "turn"

            self.Lib.create_thumbnails(self, self.selected_asset.obj_path, thumbs_to_create, self.selected_asset.version)

        elif self.selected_asset.type == "anm":

            shots = (self.cursor.execute('''SELECT frame_start, frame_end FROM shots WHERE project_name=? AND sequence_name=? AND shot_number=?''', (self.selected_project_name, self.selected_asset.sequence, self.selected_asset.shot, ))).fetchall()
            start_frame = str(shots[0][0])
            end_frame = str(shots[0][1])
            self.i = 0
            self.thumbnailProgressBar.show()
            self.thumbnailProgressBar.setMaximum(int(end_frame) - int(start_frame))
            self.thumbnailProgressBar.setValue(0)
            self.maya_playblast = QtCore.QProcess(self)
            self.maya_playblast.finished.connect(partial(self.create_mov_from_playblast, start_frame, end_frame))
            self.maya_playblast.readyRead.connect(self.playblast_ready_read)
            self.maya_playblast.waitForFinished()
            self.maya_playblast.start("C:/Program Files/Autodesk/Maya2015/bin/Render.exe", ["-r", "hw2", "-s", start_frame, "-e", end_frame, self.selected_asset.full_path])

        elif self.selected_asset.type == "cam":
            associated_hip_scene = self.cursor.execute('''SELECT asset_path FROM assets WHERE asset_id=?''', (self.selected_asset.dependency,)).fetchone()[0]
            associated_hip_scene = self.selected_project_path + associated_hip_scene

            self.houdini_flipbook_process = QtCore.QProcess(self)
            self.houdini_flipbook_process.waitForFinished()
            self.houdini_flipbook_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_flipbook.py", self.selected_asset.full_path.replace("\\", "/"), camera_asset.full_path.replace("\\", "/"), selected_shot])

    def create_mov_from_playblast(self, start_frame, end_frame):
        file_sequence = "H:/" + self.selected_asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + ".%04d.jpg"
        movie_path = "H:/" + self.selected_asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + "_playblast.mp4"

        subprocess.call([self.cur_path_one_folder_up + "\\_soft\\ffmpeg\\ffmpeg.exe", "-start_number", start_frame, "-i", file_sequence, "-vcodec", "libx264", "-y", "-r", "24", movie_path])

        thumb_filename = os.path.split(self.selected_asset.full_path)[0] + "\\.playblast\\" + self.selected_asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + ".mp4"
        shutil.copy(movie_path, thumb_filename)

        os.remove(movie_path)
        for i in range(int(start_frame), int(end_frame) + 1):
            if i == int(start_frame):
                shutil.copy("H:/" + self.selected_asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + "." + str(i).zfill(4) + ".jpg", os.path.split(self.selected_asset.full_path)[0] + "\\.playblast\\" + self.selected_asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + ".jpg")
            os.remove("H:/" + self.selected_asset.path.replace("\\assets\\anm\\", "").replace(".ma", "") + "." + str(i).zfill(4) + ".jpg")

        self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.maximum())
        self.Lib.message_box(self, type="info", text="Successfully created playblast!")

    def playblast_ready_read(self):
        while self.maya_playblast.canReadLine():
            self.i += 1
            self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.value() + 1)
            hue = self.fit_range(self.i, 0, self.thumbnailProgressBar.maximum(), 0, 76)
            self.thumbnailProgressBar.setStyleSheet("QProgressBar::chunk {background-color: hsl(" + str(hue) + ", 255, 205);}")
            out = self.maya_playblast.readLine()
            print(out)

    def show_anm_playblast(self):
        subprocess.Popen([self.cur_path_one_folder_up + "/_soft/DJView/bin/djv_view.exe", self.selected_asset.anim_playblast_path])

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

        elif type == "turn":
            result = self.check_thumbnails_conditions(type="turn")
            if result == True:
                subprocess.Popen([self.cur_path_one_folder_up + "/_soft/DJView/bin/djv_view.exe", self.selected_asset.turn_vid_path])

    def check_thumbnails_conditions(self, type=""):
        '''
        When user clicks on full, quad or turn to show given view, this function check if the asset has already been published at least once, if
        there is already a thumbnail or not, and if there's a new published version from which user can make a new thumbnail.
        '''

        if type == "full":
            path = self.selected_asset.full_img_path
            type_full_text = "full resolution image"
        elif type == "turn":
            path = self.selected_asset.turn_vid_path
            type_full_text = "turntable"


        # Asset has never been published, ask for first publish.
        publish_asset = self.Asset(self, self.selected_asset.dependency)
        publish_asset.get_infos_from_id()
        if publish_asset.number_of_publishes == 0:
            result = self.Lib.message_box(self, type="warning", text="This asset has never been published. Do you want to publish it?", no_button=True)
            if result == 0:
                return False
            else:
                self.publish_asset()
                return False

        # There's a new published version, ask if user wants to create a new thumbnail
        if os.path.isfile(path):
            publish_asset_id = self.selected_asset.dependency
            publish_asset = self.Asset(self, publish_asset_id)
            publish_asset.get_infos_from_id()
            last_publish_time = publish_asset.last_publish_as_date
            last_modified_img_time = self.Lib.modification_date(self, path)
            if last_publish_time > last_modified_img_time:
                result = self.Lib.thumbnail_creation_box(self, text="There's a new publish available. Do you want to create a thumbnail for it?")
                if result == 1:
                    os.remove(path)
                    self.update_thumbnail()
                    return False

        # Thumbnail has never been created for asset, ask if user wants to create a thumbnail
        if not os.path.isfile(path):
            result = self.Lib.message_box(self, type="warning", text="There is no {0} for this asset. Do you want to create one?".format(type_full_text), no_button=True)
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
                t = Thread(target=lambda: subprocess.Popen([self.softimage_path, "-w", "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/_prefs/softimage/nature", self.selected_asset.full_path]))
                t.start()
            elif self.selected_asset.extension == "hda":
                process = QtCore.QProcess(self)
                process.start(self.houdini_path, [self.selected_asset.full_path])

        elif self.selected_asset.type == "shd":
            process = QtCore.QProcess(self)
            process.start(self.houdini_path, [self.selected_asset.main_hda_path.replace("\\", "/")])

        elif self.selected_asset.type == "lay":
            try:
                selected_dep = str(self.departmentList.selectedItems()[0].text())
            except:
                selected_dep = ""
            if selected_dep != "Rendering":
                shutil.copy2(self.selected_asset.full_path, self.selected_asset.full_path.replace(".hipnc", "_" + self.username + "_laytmp.hipnc"))
                process = QtCore.QProcess(self)
                process.finished.connect(partial(self.load_asset_finished, self.selected_asset.full_path.replace(".hipnc", "_" + self.username + "_laytmp.hipnc")))
                process.start(self.houdini_path, [self.selected_asset.full_path.replace("\\", "/").replace(".hipnc", "_" + self.username + "_laytmp.hipnc")])
            else:
                process = QtCore.QProcess(self)
                process.start(self.houdini_path, [self.selected_asset.full_path.replace("\\", "/")])

        elif self.selected_asset.type == "rig" or self.selected_asset.type == "anm":
            process = QtCore.QProcess(self)
            process.start(self.maya_path, [self.selected_asset.full_path.replace("\\", "/")])

        elif self.selected_asset.type == "cam":
            associated_hip_scene = self.cursor.execute('''SELECT asset_path FROM assets WHERE asset_id=?''', (self.selected_asset.dependency, )).fetchone()[0]
            associated_hip_scene = self.selected_project_path + associated_hip_scene
            shutil.copy2(associated_hip_scene, associated_hip_scene.replace(".hipnc", "_" + self.username + "_camtmp.hipnc"))
            process = QtCore.QProcess(self)
            process.finished.connect(partial(self.load_asset_finished, associated_hip_scene.replace(".hipnc", "_" + self.username + "_camtmp.hipnc")))
            process.start(self.houdini_path, [associated_hip_scene.replace("\\", "/").replace(".hipnc", "_" + self.username + "_camtmp.hipnc")])

        elif self.selected_asset.type == "tex":
            texture_project_path = self.Lib.get_mari_project_path_from_asset_name(self, self.selected_asset.name, self.selected_asset.version)
            self.Lib.switch_mari_cache(self, "home")
            if os.path.isdir("H:/mari_cache_tmp_synthese/" + texture_project_path):
                shutil.rmtree("H:/mari_cache_tmp_synthese/" + texture_project_path)
            shutil.copytree("Z:/Groupes-cours/NAND999-A15-N01/Nature/tex/" + texture_project_path, "H:/mari_cache_tmp_synthese/" + texture_project_path)

            self.mari_open_asset_process = QtCore.QProcess(self)
            self.mari_open_asset_process.finished.connect(partial(self.mari_finished, texture_project_path))
            self.mari_open_asset_process.start(self.mari_path, [])

    def load_asset_finished(self, file_to_remove=None):
        if file_to_remove != None:
            if os.path.isfile(file_to_remove):
                os.remove(file_to_remove)

    def mari_finished(self, texture_project_path):
        self.mari_open_asset_process.kill()
        time.sleep(2)
        self.Lib.switch_mari_cache(self, "user")
        shutil.rmtree("Z:/Groupes-cours/NAND999-A15-N01/Nature/tex/" + texture_project_path)
        shutil.move("H:/mari_cache_tmp_synthese/" + texture_project_path, "Z:/Groupes-cours/NAND999-A15-N01/Nature/tex/" + texture_project_path)

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

    def import_into_scene(self):
        if self.selected_asset == None:
            return

        if self.selected_asset.type == "mod":
            self.import_obj_into_scene()

        elif self.selected_asset.type == "anm":

            self.create_from_asset_dialog = QtGui.QDialog(self)
            self.Lib.apply_style(self, self.create_from_asset_dialog)

            self.create_from_asset_dialog.setWindowTitle("Choose which asset to import")
            self.create_from_asset_dialog_main_layout = QtGui.QHBoxLayout(self.create_from_asset_dialog)

            camBtn = QtGui.QPushButton("Camera", self.create_from_asset_dialog)
            layBtn = QtGui.QPushButton("Layout", self.create_from_asset_dialog)

            camBtn.clicked.connect(self.create_from_asset_dialog.reject)
            layBtn.clicked.connect(self.create_from_asset_dialog.accept)

            self.create_from_asset_dialog_main_layout.addWidget(camBtn)
            self.create_from_asset_dialog_main_layout.addWidget(layBtn)

            self.create_from_asset_dialog.exec_()

            if self.create_from_asset_dialog.result() == 0:
                self.import_cam_into_anm()
                return

            all_layout_scene = []
            for asset in self.assets:
                if asset.type == "lay" and asset.extension == "hipnc":
                    all_layout_scene.append(asset)

            dialog = QtGui.QDialog(self)
            dialog.setWindowTitle("Please choose a layout scene")
            layout = QtGui.QVBoxLayout(dialog)

            listwidget = QtGui.QListWidget(dialog)

            for asset in all_layout_scene:
                item = QtGui.QListWidgetItem("Sequence: {0} | Shot: {1} | Name: {2}".format(asset.sequence, asset.shot, asset.name))
                item.setData(QtCore.Qt.UserRole, asset)
                listwidget.addItem(item)

            acceptBtn = QtGui.QPushButton("Select layout scene", dialog)
            acceptBtn.clicked.connect(dialog.accept)

            layout.addWidget(listwidget)
            layout.addWidget(acceptBtn)

            dialog.exec_()

            if dialog.result() == 0:
                return


            selected_scene = listwidget.selectedItems()[0]
            self.selected_layout_asset = selected_scene.data(QtCore.Qt.UserRole).toPyObject()

            AddAssetsToAnimWindow(self)
        elif self.selected_asset.type == "lay":
            AddAssetsToLayoutWindow(self)

    def import_cam_into_anm(self):
        self.create_from_asset_dialog.close()
        all_cameras = []
        for asset in self.assets:
            if asset.type == "cam" and asset.extension == "abc":
                all_cameras.append(asset)

        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Please choose a camera")
        layout = QtGui.QVBoxLayout(dialog)

        listwidget = QtGui.QListWidget(dialog)

        for asset in all_cameras:
            item = QtGui.QListWidgetItem("Sequence: {0} | Shot: {1}".format(asset.sequence, asset.shot, asset.name))
            item.setData(QtCore.Qt.UserRole, asset)
            listwidget.addItem(item)

        acceptBtn = QtGui.QPushButton("Import selected camera", dialog)
        acceptBtn.clicked.connect(dialog.accept)

        layout.addWidget(listwidget)
        layout.addWidget(acceptBtn)

        dialog.exec_()

        if dialog.result() == 0:
            return

        selected_camera = listwidget.selectedItems()[0]
        self.selected_camera_asset = selected_camera.data(QtCore.Qt.UserRole).toPyObject()

        self.import_cam_process = QtCore.QProcess(self)
        self.import_cam_process.finished.connect(lambda: self.Lib.message_box(self, type="info", text="Successfully imported Camera into scene!"))
        self.import_cam_process.waitForFinished()
        self.import_cam_process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_import_cam_into_anm.py", self.selected_asset.full_path, self.selected_camera_asset.full_path])

    def import_obj_into_scene(self):
        if "lowres" in self.selected_asset.name:
            obj_file = self.selected_asset.obj_path.replace("-lowres", "")
        else:
            # Ask for user to select files
            obj_file = QtGui.QFileDialog.getOpenFileName(self, 'Select OBJ', 'H:/', "3D Model (*.obj)")

            if len(obj_file) < 1:
                return

        if self.selected_asset.extension == "blend":
            self.import_obj_process = QtCore.QProcess(self)
            self.import_obj_process.finished.connect(lambda: self.Lib.message_box(self, type="info", text="Successfully imported OBJ file!"))
            self.import_obj_process.waitForFinished()
            self.import_obj_process.start(self.blender_path, ["-b", "-P", self.cur_path + "\\lib\\software_scripts\\blender_import_obj_into_scene.py", "--", self.selected_asset.full_path, obj_file])
        elif self.selected_asset.extension == "ma":
            self.import_obj_process = QtCore.QProcess(self)
            self.import_obj_process.finished.connect(lambda: self.Lib.message_box(self, type="info", text="Successfully imported OBJ file!"))
            self.import_obj_process.waitForFinished()
            self.import_obj_process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_import_obj_into_scene.py", self.selected_asset.full_path, obj_file])
        elif self.selected_asset.extension == "scn":
            self.import_obj_process = QtCore.QProcess(self)
            self.import_obj_process.finished.connect(lambda: self.Lib.message_box(self, type="info", text="Successfully imported OBJ file!"))
            self.import_obj_process.start(self.softimage_batch_path, ["-processing", "-script", self.cur_path + "\\lib\\software_scripts\\softimage_import_obj_into_scene.py", "-main", "import_obj", "-args", "-file_path", self.selected_asset.full_path, "-obj_path", obj_file])

    def create_asset_from_scratch(self):

        if self.selected_department_name == "lay":
            if self.selected_sequence_name == "xxx":
                self.Lib.message_box(self, type="error", text="You must select a sequence to create a layout")
                return

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
                extension = "hda"

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
            self.create_mod_asset_from_scratch(asset_name, extension, selected_software)
        elif self.selected_department_name == "lay":
            self.create_lay_asset_from_scratch(asset_name)

    def create_asset_from_asset(self):
        if self.selected_department_name == "mod" or (self.selected_asset.type == "lay" and self.selected_asset.extension == "hda" and self.selected_asset.version != "out"):
            if self.selected_asset == None: return
            if "lowres" in self.selected_asset.name:
                self.Lib.message_box(self, type="error", text="You can't create an asset from a low-res asset. Please select the corresponding high-res asset.")
                return
            self.create_from_asset_dialog = QtGui.QDialog(self)
            self.Lib.apply_style(self, self.create_from_asset_dialog)

            self.create_from_asset_dialog.setWindowTitle("Choose which asset to create")
            self.create_from_asset_dialog_main_layout = QtGui.QHBoxLayout(self.create_from_asset_dialog)

            rigBtn = QtGui.QPushButton("Rig", self.create_from_asset_dialog)
            texBtn = QtGui.QPushButton("Tex", self.create_from_asset_dialog)

            rigBtn.clicked.connect(self.create_rig_asset_from_mod)
            texBtn.clicked.connect(self.create_tex_asset_from_mod)

            self.create_from_asset_dialog_main_layout.addWidget(rigBtn)
            self.create_from_asset_dialog_main_layout.addWidget(texBtn)

            self.create_from_asset_dialog.exec_()

        elif self.selected_department_name == "rig":
            AnimSceneChooser(self)

        elif self.selected_department_name == "lay":
            if self.selected_asset == None: return
            self.create_from_asset_dialog = QtGui.QDialog(self)
            self.Lib.apply_style(self, self.create_from_asset_dialog)

            self.create_from_asset_dialog.setWindowTitle("Enter a name")
            self.create_from_asset_dialog_main_layout = QtGui.QHBoxLayout(self.create_from_asset_dialog)

            cameraBtn = QtGui.QPushButton("Camera", self.create_from_asset_dialog)
            lightingBtn = QtGui.QPushButton("Lighting", self.create_from_asset_dialog)

            cameraBtn.clicked.connect(self.create_cam_asset_from_lay)
            lightingBtn.clicked.connect(self.create_lgt_asset_from_lay)

            self.create_from_asset_dialog_main_layout.addWidget(cameraBtn)
            self.create_from_asset_dialog_main_layout.addWidget(lightingBtn)

            self.create_from_asset_dialog.exec_()

    def create_rig_asset_from_mod(self):

        self.create_from_asset_dialog.close()

        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, self.selected_asset.name, "", "ma", "rig", "01", [], self.selected_asset.id, "", "", self.username)
        asset.add_asset_to_db()

        obj_path = str(self.selected_asset.obj_path).replace("\\", "/")
        file_export = os.path.splitext(obj_path)[0].replace("mod", "rig").replace("out", "01") + ".ma"
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(partial(self.asset_creation_finished, asset))
        self.process.waitForFinished()
        self.process.start(self.maya_batch_path, [self.cur_path + "\\lib\\software_scripts\\maya_import_obj_as_reference.py", obj_path, file_export])

    def create_tex_asset_from_mod(self):

        self.create_from_asset_dialog.close()

        obj_publish_path = self.Asset(self, self.selected_asset.dependency)
        obj_publish_path.get_infos_from_id()

        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, self.selected_asset.name, "", "mari", "tex", "01", [], obj_publish_path.id, "", "", self.username)
        asset.add_asset_to_db()

        self.Lib.switch_mari_cache(self, "server")
        self.mari_process = QtCore.QProcess(self)
        self.mari_process.readyRead.connect(self.mari_process_read_data)
        self.mari_process.finished.connect(partial(self.asset_creation_finished, asset))
        self.mari_process.waitForFinished()
        self.mari_process.start(self.mari_path, ["-t", self.cur_path + "\\lib\\software_scripts\\mari_create_project.py", self.selected_asset.name, "01", obj_publish_path.full_path])

    def mari_process_read_data(self):
        while self.mari_process.canReadLine():
            out = self.mari_process.readLine()
            if "Welcome to Mari 2.6v2!  Type help() to get started." in out:
                self.mari_process.kill()

    def create_cam_asset_from_lay(self):

        self.create_from_asset_dialog.close()

        # if selected sequence has no shots, abort
        shots = self.shots[self.selected_sequence_name]
        if len(shots) == 0:
            self.Lib.message_box(self, type="error", text="You can't create a camera for a sequence without any shot")
            return

        # Create shot list selection dialog
        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Choose a shot")
        self.Lib.apply_style(self, dialog)

        layout = QtGui.QVBoxLayout(dialog)

        shotLbl = QtGui.QLabel("Shot list:", self)
        shotListWidget = QtGui.QListWidget(self)
        createCamBtn = QtGui.QPushButton("Create asset", self)
        createCamBtn.clicked.connect(dialog.accept)

        existing_cam_shots = self.cursor.execute('''SELECT shot_number FROM assets WHERE asset_type="cam" AND sequence_name=?''', (self.selected_sequence_name,)).fetchall()
        if len(existing_cam_shots) > 0:
            existing_cam_shots = [str(i[0]) for i in existing_cam_shots]

        shots = self.shots[self.selected_sequence_name]
        shots_with_no_cam = list(set(shots) - set(existing_cam_shots))

        if len(shots_with_no_cam) == 0:
            self.Lib.message_box(self, type="warning", text="There's already a camera for every shot in this sequence")
            return

        shotListWidget.addItems(QtCore.QStringList(shots_with_no_cam))
        shotListWidget.setCurrentRow(0)
        selected_shot = shots[0]

        layout.addWidget(shotLbl)
        layout.addWidget(shotListWidget)
        layout.addWidget(createCamBtn)

        dialog.exec_()

        if dialog.result() == 0:
            return

        # Get selected item
        selected_shot = shotListWidget.selectedItems()[0]
        selected_shot = str(selected_shot.text())

        camera_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, selected_shot, "cam-" + selected_shot, "", "hda", "cam", "01", [], self.selected_asset.id, "", "", self.username)
        camera_asset.add_asset_to_db()

        camera_asset_publish = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, selected_shot, "cam-" + selected_shot, "", "abc", "cam", "out", [], camera_asset.id, "", "", self.username)
        camera_asset_publish.add_asset_to_db()

        shutil.copy(self.NEF_folder + "\\camera.abc", camera_asset_publish.full_path)

        # Create HDA associated to modeling scene
        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.finished.connect(partial(self.asset_creation_finished, camera_asset))
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_import_cam_into_lay.py", self.selected_asset.full_path.replace("\\", "/"), camera_asset.full_path.replace("\\", "/"), selected_shot])

    def create_lgt_asset_from_lay(self):

        self.create_from_asset_dialog.close()

        # if selected sequence has no shots, abort
        shots = self.shots[self.selected_sequence_name]
        if len(shots) == 0:
            self.Lib.message_box(self, type="error", text="You can't create a light for a sequence without any shot")
            return

        # Create shot list selection dialog
        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Choose a shot")
        self.Lib.apply_style(self, dialog)

        layout = QtGui.QVBoxLayout(dialog)

        shotLbl = QtGui.QLabel("Shot list:", self)
        shotListWidget = QtGui.QListWidget(self)
        createLgtBtn = QtGui.QPushButton("Create asset", self)
        createLgtBtn.clicked.connect(dialog.accept)

        existing_lights_shots = self.cursor.execute('''SELECT shot_number FROM assets WHERE asset_type="lgt" AND sequence_name=?''', (self.selected_sequence_name, )).fetchall()
        if len(existing_lights_shots) > 0:
            existing_lights_shots = [str(i[0]) for i in existing_lights_shots]

        shots = self.shots[self.selected_sequence_name]
        shots_with_no_lights = list(set(shots) - set(existing_lights_shots))

        if len(shots_with_no_lights) == 0:
            self.Lib.message_box(self, type="warning", text="There's already a light for every shot in this sequence")
            return

        shotListWidget.addItems(QtCore.QStringList(shots_with_no_lights))
        shotListWidget.setCurrentRow(0)
        selected_shot = shots[0]

        layout.addWidget(shotLbl)
        layout.addWidget(shotListWidget)
        layout.addWidget(createLgtBtn)

        dialog.exec_()

        if dialog.result() == 0:
            return

        # Get selected item
        selected_shot = shotListWidget.selectedItems()[0]
        selected_shot = str(selected_shot.text())

        light_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, selected_shot, "lighting-" + selected_shot, "", "hda", "lgt", "01", [], self.selected_asset.id, "", "", self.username)
        light_asset.add_asset_to_db()

        # Create HDA associated to modeling scene
        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.finished.connect(partial(self.asset_creation_finished, light_asset))
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_import_lgt_into_lay.py", self.selected_asset.full_path.replace("\\", "/"), light_asset.full_path.replace("\\", "/"), selected_shot])

    def create_mod_asset_from_scratch(self, asset_name="", extension=None, selected_software=None):

        if selected_software == "houdini":
            # Create modeling scene asset
            asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "mod", "01", [], "", "", "", self.username)
            asset.add_asset_to_db()

            # Create main HDA database entry
            main_hda_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "lay", "out", [], asset.id, "", "", self.username)
            main_hda_asset.add_asset_to_db()

            # Create shading HDA database entry
            shading_hda_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "shd", "01", [], main_hda_asset.id, "", "", self.username)
            shading_hda_asset.add_asset_to_db()

            # Create default publish cube (obj)
            obj_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "obj", "mod", "out", [], asset.id, "", "", self.username)
            obj_asset.add_asset_to_db()
            shutil.copy(self.NEF_folder + "\\default_cube.obj", obj_asset.full_path)

            # Create default lowres publish cube (obj)
            obj_lowres_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name + "-lowres", "", "obj", "mod", "out", [], asset.id, "", "", self.username)
            obj_lowres_asset.add_asset_to_db()
            shutil.copy(self.NEF_folder + "\\default_cube.obj", obj_lowres_asset.full_path)

            # Add publish obj as dependency to main asset
            asset.change_dependency(obj_asset.id)

            # Create modeling HDA
            self.houdini_hda_process = QtCore.QProcess(self)
            self.houdini_hda_process.readyRead.connect(self.readdata)
            self.houdini_hda_process.waitForFinished()
            self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_modeling_hda_for_houdini.py", asset.name, asset.obj_path, asset.full_path])

            # Create HDA associated to modeling scene
            self.houdini_hda_process = QtCore.QProcess(self)
            self.houdini_hda_process.finished.connect(partial(self.asset_creation_finished, main_hda_asset))
            self.houdini_hda_process.readyRead.connect(self.readdata)
            self.houdini_hda_process.waitForFinished()
            self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_modeling_hda.py", main_hda_asset.full_path, shading_hda_asset.full_path, main_hda_asset.obj_path, asset_name])

        else:
            # Create modeling scene asset
            asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", extension, "mod", "01", [], "", "", "", self.username)
            asset.add_asset_to_db()
            shutil.copy(self.NEF_folder + "\\" + selected_software + "." + extension, asset.full_path)

            # Create low res modeling scene asset
            asset_low_res = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name + "-lowres", "", extension, "mod", "01", [], "", "", "", self.username)
            asset_low_res.add_asset_to_db()
            shutil.copy(self.NEF_folder + "\\" + selected_software + "." + extension, asset_low_res.full_path)

            # Create default publish cube (obj)
            obj_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "obj", "mod", "out", [], asset.id, "", "", self.username)
            obj_asset.add_asset_to_db()
            shutil.copy(self.NEF_folder + "\\default_cube.obj", obj_asset.full_path)

            # Create default lowres publish cube (obj)
            obj_lowres_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name + "-lowres", "", "obj", "mod", "out", [], asset_low_res.id, "", "", self.username)
            obj_lowres_asset.add_asset_to_db()
            shutil.copy(self.NEF_folder + "\\default_cube.obj", obj_lowres_asset.full_path)

            # Add publish obj as dependency to main asset
            asset.change_dependency(obj_asset.id)

            # Add publish obj as dependency to main asset
            asset_low_res.change_dependency(obj_lowres_asset.id)

            # Create main HDA database entry
            main_hda_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "lay", "out", [], asset.id, "", "", self.username)
            main_hda_asset.add_asset_to_db()

            # Create shading HDA database entry
            shading_hda_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hda", "shd", "01", [], main_hda_asset.id, "", "", self.username)
            shading_hda_asset.add_asset_to_db()

            # Create HDA associated to modeling scene
            self.houdini_hda_process = QtCore.QProcess(self)
            self.houdini_hda_process.finished.connect(partial(self.asset_creation_finished, asset))
            self.houdini_hda_process.waitForFinished()
            self.houdini_hda_process.start(self.houdini_batch_path, [self.cur_path + "\\lib\\software_scripts\\houdini_create_modeling_hda.py", main_hda_asset.full_path, shading_hda_asset.full_path, main_hda_asset.obj_path, asset_name])

    def readdata(self):
        while self.houdini_hda_process.canReadLine():
            out = self.houdini_hda_process.readLine()
            print(out)

    def create_lay_asset_from_scratch(self, asset_name):

        # Create modeling scene asset
        asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, asset_name, "", "hipnc", "lay", "01", [], "", "", "", self.username)
        asset.add_asset_to_db()
        shutil.copy(self.NEF_folder + "\\houdini.hipnc", asset.full_path)

        self.asset_creation_finished(asset)

    def asset_creation_finished(self, asset):

        if self.selected_department_name == "mod" and asset.type == "rig":
            # Create default publish scene for rig asset
            out_rig_asset = self.Asset(self, 0, self.selected_project_name, self.selected_sequence_name, self.selected_shot_number, self.selected_asset.name, "", "ma", "rig", "out", [], asset.id, "", "", self.username)
            out_rig_asset.add_asset_to_db()
            shutil.copy(asset.full_path, out_rig_asset.full_path)

        # Reload assets
        self.load_all_assets_for_first_time()
        self.load_assets_from_selected_seq_shot_dept()

        # Update last access
        asset.change_last_access()
        self.lastAccessLbl.setText("Last accessed by: " + asset.last_access)


        # Add Log Entry
        log_entry = self.LogEntry(self, 0, asset.id, [], [], self.username, "", "asset", "{0} has created a new {1} asset ({2}).".format(self.members[self.username], self.departments_longname[asset.type], asset.name), datetime.now().strftime("%d/%m/%Y at %H:%M"))
        log_entry.add_log_to_database()

        # Show info message
        self.Lib.message_box(self, type="info", text="Asset has been succesfully created!")

    def add_assets_to_layout(self):
        AddAssetsToLayoutWindow(self)

class AnimSceneChooser(QtGui.QDialog):
    def __init__(self, main):
        super(AnimSceneChooser, self).__init__()
        self.main = main

        self.setWindowTitle("Choose a sequence and a shot")
        self.main.Lib.apply_style(self.main, self)

        layout = QtGui.QGridLayout(self)

        seqLbl = QtGui.QLabel("Sequence:", self)
        shotLbl = QtGui.QLabel("Shot:", self)

        self.seqListWidget = QtGui.QListWidget(self)
        self.shotListWidget = QtGui.QListWidget(self)

        self.seqListWidget.itemClicked.connect(self.filter_shots_based_on_sequence)
        self.shotListWidget.itemClicked.connect(self.shot_list_clicked)

        seqList = QtCore.QStringList()
        [seqList.append(i) for i in self.main.shots.keys()]
        self.seqListWidget.addItems(seqList)

        for seq, shots in self.main.shots.items():
            item = QtGui.QListWidgetItem("None")
            item.setData(QtCore.Qt.UserRole, seq)
            self.shotListWidget.addItem(item)
            for shot in shots:
                item = QtGui.QListWidgetItem(shot)
                item.setData(QtCore.Qt.UserRole, seq)
                self.shotListWidget.addItem(item)

        createAnimSceneBtn = QtGui.QPushButton("Create animation asset", self)
        createAnimSceneBtn.clicked.connect(self.create_anm_from_rig)


        layout.addWidget(seqLbl, 0, 0)
        layout.addWidget(shotLbl, 0, 1)
        layout.addWidget(self.seqListWidget, 1, 0)
        layout.addWidget(self.shotListWidget, 1, 1)
        layout.addWidget(createAnimSceneBtn, 2, 0, 2, 2)

        self.seqListWidget.setCurrentRow(0)
        self.filter_shots_based_on_sequence()

        self.exec_()

    def filter_shots_based_on_sequence(self):
        self.selected_sequence = self.seqListWidget.selectedItems()[0]
        self.selected_sequence = str(self.selected_sequence.text())

        for i in xrange(0, self.shotListWidget.count()):
            seq_from_shot = self.shotListWidget.item(i).data(QtCore.Qt.UserRole).toPyObject()
            if seq_from_shot == self.selected_sequence:
                self.shotListWidget.item(i).setHidden(False)
            else:
                self.shotListWidget.item(i).setHidden(True)

    def shot_list_clicked(self):
        self.selected_shot = self.shotListWidget.selectedItems()[0]
        self.selected_shot = str(self.selected_shot.text())
        if self.selected_shot == "None":
            self.selected_shot = "xxxx"

    def create_anm_from_rig(self):

        asset = self.main.Asset(self.main, 0, self.main.selected_project_name, self.selected_sequence, self.selected_shot, self.main.selected_asset.name, "", "ma", "anm", "01", [], "", "", "", self.main.username)
        asset.add_asset_to_db()

        alembic_publish_asset = self.main.Asset(self.main, 0, self.main.selected_project_name, self.selected_sequence, self.selected_shot, self.main.selected_asset.name, "", "abc", "anm", "out", [], asset.id, "", "", self.main.username)
        alembic_publish_asset.add_asset_to_db()

        asset.change_dependency(alembic_publish_asset.id)

        process = QtCore.QProcess(self)
        process.waitForFinished()
        process.start(self.main.maya_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\maya_import_rig_as_reference.py", self.main.selected_asset.rig_out_path, asset.full_path])

        hda_layout_asset = self.main.cursor.execute('''SELECT asset_path FROM assets WHERE asset_name=? AND asset_extension="hda" AND asset_type="lay"''', (asset.name,)).fetchone()

        hda_process = QtCore.QProcess(self)
        hda_process.finished.connect(partial(self.create_abc, asset))
        hda_process.waitForFinished()
        hda_process.start(self.main.houdini_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\houdini_update_hda_from_abc.py", alembic_publish_asset.full_path.replace("\\", "/"), alembic_publish_asset.name, (self.main.selected_project_path + hda_layout_asset[0]).replace("\\", "/")])


    def create_abc(self, asset):
        self.publish_process = QtCore.QProcess(self)
        self.publish_process.finished.connect(partial(self.main.asset_creation_finished, asset))
        self.publish_process.start(self.main.maya_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\maya_export_anm_as_alembic.py", asset.full_path.replace("\\", "/"), asset.anim_out_path.replace("\\", "/"), "1", "2"])

class AddAssetsToLayoutWindow(QtGui.QDialog, Ui_addAssetsToLayoutWidget):
    def __init__(self, main):
        super(AddAssetsToLayoutWindow, self).__init__()

        self.main = main

        # Initialize the guis
        self.add_assets_layout = self.setupUi(self)
        self.main.Lib.apply_style(self.main, self)

        # Connections
        self.availableAssetsListWidget.doubleClicked.connect(self.add_asset_to_list)
        self.assetsToAddListWidget.doubleClicked.connect(self.remove_asset_from_list)
        self.availableAssetsListWidget.setDragEnabled(False)
        self.assetsToAddListWidget.setDragEnabled(False)

        self.addAssetBtn.clicked.connect(self.add_asset_to_list)
        self.removeAssetBtn.clicked.connect(self.remove_asset_from_list)
        self.addAssetsToLayoutBtn.clicked.connect(self.add_assets_to_layout)

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
        # Remove whitespace, new line, and other special characters from assets paths.
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
            if not asset_id in self.assets_in_layout_db_id: # if asset is not already in layout scene, add it
                asset_object = self.main.Asset(self.main, asset_id) # Get layout hda digital asset
                asset_object.get_infos_from_id()

                # Get first modeling scene (Ex: \assets\mod\nat_xxx_xxxx_mod_boubou_blend_01.blend)
                first_modeling_scene_asset = self.main.Asset(self.main, asset_object.dependency)
                first_modeling_scene_asset.get_infos_from_id()

                # Get associated publish obj asset (Ex: \assets\mod\nat_xxx_xxxx_mod_boubou_out.obj)
                out_obj_asset = self.main.Asset(self.main, first_modeling_scene_asset.dependency)
                out_obj_asset.get_infos_from_id()

                # If asset has never been published, skip
                if out_obj_asset.number_of_publishes == 0:
                    continue

                # Get version from which the last publish was made (Ex: \assets\mod\nat_xxx_xxxx_mod_boubou_05.blend)
                last_published_asset = self.main.Asset(self.main, out_obj_asset.publish_from_version)
                last_published_asset.get_infos_from_id()

                item = QtGui.QListWidgetItem(asset_object.name)
                # Get thumbnail from last published scene (Full thumbnail of version 05 (which is the version from which the last publish was made for example))
                if not os.path.isfile(last_published_asset.full_img_path):
                    item.setIcon(QtGui.QIcon(self.main.no_img_found))
                else:
                    item.setIcon(QtGui.QIcon(last_published_asset.full_img_path))
                item.setData(QtCore.Qt.UserRole, (asset_object, last_published_asset.full_img_path))
                self.availableAssetsListWidget.addItem(item)

        self.exec_()

    def add_asset_to_list(self):
        for asset in self.availableAssetsListWidget.selectedItems():
            selected_asset_item = asset
            selected_asset = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            selected_asset_img = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[1]

            # Create listwidget item from selected asset
            item = QtGui.QListWidgetItem(selected_asset.name)
            item.setIcon(QtGui.QIcon(selected_asset_img))
            item.setData(QtCore.Qt.UserRole, (selected_asset, selected_asset_img))

            # Add item to right list
            self.assetsToAddListWidget.addItem(item)

            # Remove item from left list
            self.availableAssetsListWidget.takeItem(self.availableAssetsListWidget.row(asset))

    def remove_asset_from_list(self):
        for asset in self.assetsToAddListWidget.selectedItems():
            selected_asset_item = asset
            selected_asset = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            selected_asset_img = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[1]

            # Create listwidget item from selected asset
            item = QtGui.QListWidgetItem(selected_asset.name)
            item.setIcon(QtGui.QIcon(selected_asset_img))
            item.setData(QtCore.Qt.UserRole, (selected_asset, selected_asset_img))

            # Add item to right list
            self.availableAssetsListWidget.addItem(item)

            # Remove item from left list
            self.assetsToAddListWidget.takeItem(self.assetsToAddListWidget.row(asset))

    def add_assets_to_layout(self):
        assets_list = []
        for i in xrange(self.assetsToAddListWidget.count()):
            list_item = self.assetsToAddListWidget.item(i)
            asset = list_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            asset.print_asset()
            assets_list.append(asset.full_path.replace("\\", "/"))
            self.main.cursor.execute('''INSERT INTO assets_in_layout(asset_id, layout_id) VALUES(?,?)''', (asset.id, self.main.selected_asset.id,))
            self.main.db.commit()

        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.finished.connect(self.process_finished)
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.main.houdini_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\houdini_import_multiple_hdas_into_layout.py", self.main.selected_asset.full_path.replace("\\", "/"), "|".join(assets_list)])

    def process_finished(self):
        self.main.Lib.message_box(self.main, type="info", text="Assets have been succesfully imported into layout scene!")
        self.houdini_hda_process.kill()
        self.assetsToAddListWidget.clear()

class AddAssetsToAnimWindow(QtGui.QDialog, Ui_addAssetsToLayoutWidget):
    def __init__(self, main):
        super(AddAssetsToAnimWindow, self).__init__()

        self.main = main

        # Initialize the guis
        self.add_assets_layout = self.setupUi(self)
        self.main.Lib.apply_style(self.main, self)

        self.setWindowTitle("Add/remove assets to/from animation scene")
        self.addAssetsToLayoutBtn.setText("Add/remove assets to/from animation scene")

        # Connections
        self.availableAssetsListWidget.setDragEnabled(False)
        self.assetsToAddListWidget.setDragEnabled(False)
        self.availableAssetsListWidget.doubleClicked.connect(self.add_asset_to_list)
        self.assetsToAddListWidget.doubleClicked.connect(self.remove_asset_from_list)

        self.addAssetBtn.clicked.connect(self.add_asset_to_list)
        self.removeAssetBtn.clicked.connect(self.remove_asset_from_list)
        self.addAssetsToLayoutBtn.clicked.connect(self.add_remove_assets_to_anim)

        self.assets_in_anim = []
        self.assets_not_in_layout_db = []
        self.assets_in_layout_db = []

        self.get_assets_from_anim = QtCore.QProcess(self)
        self.get_assets_from_anim.readyRead.connect(self.get_assets_from_process_output)
        self.get_assets_from_anim.finished.connect(self.finished)
        self.get_assets_from_anim.start(self.main.maya_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\maya_get_assets_from_anm.py", self.main.selected_asset.full_path])

    def get_assets_from_process_output(self):
        while self.get_assets_from_anim.canReadLine():
            out = str(self.get_assets_from_anim.readLine())
            self.assets_in_anim.append(out)

    def finished(self):

        # Remove line breaks ("\n") from list
        self.assets_in_anim = [i.replace("\n", "").replace("HighRes", "") for i in self.assets_in_anim]

        # Get all layout assets from selected layout scene
        assets_id_from_db = self.main.cursor.execute('''SELECT asset_id FROM assets_in_layout WHERE layout_id=?''', (self.main.selected_layout_asset.id,)).fetchall()
        assets_id_from_db = [i[0] for i in assets_id_from_db]

        layout_assets = []
        for id in assets_id_from_db:
            try:
                asset = self.main.Asset(self.main, id)
                asset.get_infos_from_id()
                layout_assets.append(asset)
            except:
                pass

        # Go through each asset and check if it is already in anim scene
        for asset in layout_assets:
            asset_filename = asset.path.split("\\")[-1].replace(".hda", "") # Get asset_filename (Ex: nat_xxx_xxxx_lay_pipe_out from \assets\lay\nat_xxx_xxxx_lay_pipe_out.hda)
            if not asset_filename in self.assets_in_anim:
                # Asset is not in anim scene, add it to assets_not_in_layout_db list
                self.assets_not_in_layout_db.append(asset)
            else:
                self.assets_in_layout_db.append(asset)


        # Add assets to list widget
        for asset in self.assets_not_in_layout_db:
            # Get version from which the modeling asset was published
            obj_asset_path = asset.full_path.replace("lay", "mod").replace("hda", "obj") # Get path of obj from modeling (Ex: \assets\mod\nat_xxx_xxxx_mod_pipe_out.obj)
            obj_asset_id = self.main.cursor.execute('''SELECT asset_id FROM assets WHERE asset_path=?''', (obj_asset_path.replace(self.main.selected_project_path, ""), )).fetchone()
            obj_asset = self.main.Asset(self.main, obj_asset_id[0])
            obj_asset.get_infos_from_id()

            # If asset has never been published, skip
            if obj_asset.number_of_publishes == 0:
                continue

            published_from_version = obj_asset.publish_from_version # Published_from_version = id of asset from which the modeling was published
            last_published_asset = self.main.Asset(self.main, published_from_version)
            last_published_asset.get_infos_from_id()

            item = QtGui.QListWidgetItem(asset.name)
            # Get thumbnail from last published scene (Full thumbnail of version 05 (which is the version from which the last publish was made for example))
            if not os.path.isfile(last_published_asset.full_img_path):
                item.setIcon(QtGui.QIcon(self.main.no_img_found))
            else:
                item.setIcon(QtGui.QIcon(last_published_asset.full_img_path))
            item.setData(QtCore.Qt.UserRole, (asset, last_published_asset.full_img_path))
            self.availableAssetsListWidget.addItem(item)


        for asset in self.assets_in_layout_db:
            # Get version from which the modeling asset was published
            obj_asset_path = asset.full_path.replace("lay", "mod").replace("hda", "obj")  # Get path of obj from modeling (Ex: \assets\mod\nat_xxx_xxxx_mod_pipe_out.obj)
            obj_asset_id = self.main.cursor.execute('''SELECT asset_id FROM assets WHERE asset_path=?''', (obj_asset_path.replace(self.main.selected_project_path, ""),)).fetchone()
            obj_asset = self.main.Asset(self.main, obj_asset_id[0])
            obj_asset.get_infos_from_id()

            # If asset has never been published, skip
            if obj_asset.number_of_publishes == 0:
                continue

            published_from_version = obj_asset.publish_from_version  # Published_from_version = id of asset from which the modeling was published
            last_published_asset = self.main.Asset(self.main, published_from_version)
            last_published_asset.get_infos_from_id()

            item = QtGui.QListWidgetItem(asset.name)
            # Get thumbnail from last published scene (Full thumbnail of version 05 (which is the version from which the last publish was made for example))
            if not os.path.isfile(last_published_asset.full_img_path):
                item.setIcon(QtGui.QIcon(self.main.no_img_found))
                item.setData(QtCore.Qt.UserRole, (asset, self.main.no_img_found))
            else:
                item.setIcon(QtGui.QIcon(last_published_asset.full_img_path))
                item.setData(QtCore.Qt.UserRole, (asset, last_published_asset.full_img_path))
            self.assetsToAddListWidget.addItem(item)

        self.exec_()

    def add_asset_to_list(self):
        for asset in self.availableAssetsListWidget.selectedItems():
            selected_asset_item = asset
            selected_asset = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            selected_asset_img = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[1]

            # Create listwidget item from selected asset
            item = QtGui.QListWidgetItem(selected_asset.name)
            item.setIcon(QtGui.QIcon(selected_asset_img))
            item.setData(QtCore.Qt.UserRole, (selected_asset, selected_asset_img))

            # Add item to right list
            self.assetsToAddListWidget.addItem(item)

            # Remove item from left list
            self.availableAssetsListWidget.takeItem(self.availableAssetsListWidget.row(asset))

    def remove_asset_from_list(self):
        for asset in self.assetsToAddListWidget.selectedItems():
            selected_asset_item = asset
            selected_asset = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[0]
            selected_asset_img = selected_asset_item.data(QtCore.Qt.UserRole).toPyObject()[1]

            # Create listwidget item from selected asset
            item = QtGui.QListWidgetItem(selected_asset.name)
            item.setIcon(QtGui.QIcon(selected_asset_img))
            item.setData(QtCore.Qt.UserRole, (selected_asset, selected_asset_img))

            # Add item to right list
            self.availableAssetsListWidget.addItem(item)

            # Remove item from left list
            self.assetsToAddListWidget.takeItem(self.assetsToAddListWidget.row(asset))

    def add_remove_assets_to_anim(self):
        self.assets_to_add = []
        for i in xrange(self.assetsToAddListWidget.count()):
            item_to_add = self.assetsToAddListWidget.item(i)
            asset = item_to_add.data(QtCore.Qt.UserRole).toPyObject()[0]
            self.assets_to_add.append(asset.full_path.replace("\\", "/"))

        self.assets_to_remove = []
        for i in xrange(self.availableAssetsListWidget.count()):
            item_to_add = self.availableAssetsListWidget.item(i)
            asset = item_to_add.data(QtCore.Qt.UserRole).toPyObject()[0]
            self.assets_to_remove.append(asset.full_path.replace("\\", "/"))

        self.houdini_hda_process = QtCore.QProcess(self)
        self.houdini_hda_process.finished.connect(self.houdini_process_finished)
        #self.houdini_hda_process.readyRead.connect(self.readydata)
        self.houdini_hda_process.waitForFinished()
        self.houdini_hda_process.start(self.main.houdini_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\houdini_export_mod_in_place_from_lay.py", self.main.selected_layout_asset.full_path, "|".join(self.assets_to_add)])

    def houdini_process_finished(self):
        self.maya_ref_process = QtCore.QProcess(self)
        self.maya_ref_process.finished.connect(self.maya_process_finished)
        self.maya_ref_process.readyRead.connect(self.readydata)
        self.maya_ref_process.waitForFinished()
        self.maya_ref_process.start(self.main.maya_batch_path, [self.main.cur_path + "\\lib\\software_scripts\\maya_import_obj_from_lay_as_ref.py", self.main.selected_asset.full_path, "|".join(self.assets_to_remove), "|".join(self.assets_to_add)])


    def maya_process_finished(self):
        self.main.Lib.message_box(self.main, type="info", text="Assets have been succesfully imported/removed into/from layout scene!")
        #self.houdini_hda_process.kill()
        #self.maya_ref_process.kill()


    def readydata(self):
        while self.maya_ref_process.canReadLine():
            out = self.maya_ref_process.readLine()
            print(out)