#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import subprocess
import os
import shutil
from PIL import Image
import urllib
from functools import partial
import pafy
import time
import re

from lib.module import Lib
from lib.comments import CommentWidget


class ReferenceTab(object):
    def __init__(self):

        self.first_thumbnail_load = True
        self.compression_level = 60
        self.keep_size = False

        self.referenceThumbListWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.referenceThumbListWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

        self.allTagsTreeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        self.seqReferenceList.itemClicked.connect(self.seqReferenceList_Clicked)
        self.shotReferenceList.itemClicked.connect(self.shotReferenceList_Clicked)
        self.referenceThumbListWidget.itemSelectionChanged.connect(self.referenceThumbListWidget_itemSelectionChanged)
        self.referenceThumbListWidget.itemDoubleClicked.connect(self.reference_doubleClicked)
        self.filterByNameLineEdit.textChanged.connect(self.filter_reference_by_name)
        self.filterByTagsListWidget.itemSelectionChanged.connect(self.filter_reference_by_tags)
        self.createReferenceFromWebBtn.clicked.connect(self.create_reference_from_web)
        self.createReferencesFromFilesBtn.clicked.connect(self.create_reference_from_files)
        self.createReferencesFromScreenshotBtn.clicked.connect(self.create_reference_from_screenshot)
        self.keepQualityCheckBox.stateChanged.connect(self.change_quality)
        self.openRefInKuadroBtn.clicked.connect(self.load_ref_in_kuadro)
        self.openRefInPhotoshopBtn.clicked.connect(self.load_ref_in_photoshop)
        self.addTagsBtn.clicked.connect(self.add_tags_to_selected_references)
        self.allTagsTreeWidget.doubleClicked.connect(self.add_tags_to_selected_references)
        self.removeTagsBtn.clicked.connect(self.remove_tags_from_selected_references)
        self.existingTagsListWidget.doubleClicked.connect(self.remove_tags_from_selected_references)
        self.biggerRefPushButton_01.clicked.connect(partial(self.change_reference_thumb_size, 1))
        self.biggerRefPushButton_02.clicked.connect(partial(self.change_reference_thumb_size, 2))
        self.biggerRefPushButton_03.clicked.connect(partial(self.change_reference_thumb_size, 3))
        self.biggerRefPushButton_04.clicked.connect(partial(self.change_reference_thumb_size, 4))
        self.changeRefSeqShotBtn.clicked.connect(self.change_seq_shot_layout)
        self.showUrlImageBtn.clicked.connect(self.show_url_image)
        self.hideReferenceOptionsFrameBtn.clicked.connect(self.hide_reference_options_frame)

        icon = QtGui.QIcon(
            "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\thumbnail.png")
        self.biggerRefPushButton_01.setIcon(icon)
        self.biggerRefPushButton_02.setIcon(icon)
        self.biggerRefPushButton_03.setIcon(icon)
        self.biggerRefPushButton_04.setIcon(icon)
        self.biggerRefPushButton_01.setIconSize(QtCore.QSize(8, 8))
        self.biggerRefPushButton_02.setIconSize(QtCore.QSize(16, 16))
        self.biggerRefPushButton_03.setIconSize(QtCore.QSize(24, 24))
        self.biggerRefPushButton_04.setIconSize(QtCore.QSize(30, 30))

    def seqReferenceList_Clicked(self):

        # If no thumbnail is loaded, load all reference thumbnails for first load.
        if self.referenceThumbListWidget.count() == 0:
            self.load_reference_thumbnails(self.first_thumbnail_load)

        self.selected_sequence_name = str(self.seqReferenceList.selectedItems()[0].text())

        # Add shots to shot list and shot creation list
        if self.selected_sequence_name == "All":
            self.selected_sequence_name = "xxx"
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")

        elif self.selected_sequence_name == "None":
            self.selected_sequence_name = "xxx"
            self.shotReferenceList.clear()
            self.shotReferenceList.addItem("None")

        else:
            self.shotReferenceList.clear()
            shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
                                        (self.selected_project_name, self.selected_sequence_name,)).fetchall()
            self.shotReferenceList.addItem("None")
            shots = [i[0] for i in shots]
            shots = sorted(shots)
            [self.shotReferenceList.addItem(shot) for shot in shots]


        # Filter thumbnails based on which sequence was clicked
        all_references = []
        all_tags = []
        for i in xrange(self.referenceThumbListWidget.count()):
            all_references.append(self.referenceThumbListWidget.item(i))

        for ref in all_references:
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()
            ref_seq = ref_data[0]
            ref_tags = ref_data[5]
            if str(self.seqReferenceList.selectedItems()[
                       0].text()) == "All":  # If "All" is selected, show all thumbnails
                all_tags.append(ref_tags)
                self.referenceThumbListWidget.setItemHidden(ref, False)
            else:  # Else, show thumbnails for selected sequence only
                if ref_seq == self.selected_sequence_name:
                    all_tags.append(ref_tags)
                    self.referenceThumbListWidget.setItemHidden(ref, False)
                else:
                    self.referenceThumbListWidget.setItemHidden(ref, True)

        self.add_tags_to_filter_tags_list(all_tags)

    def shotReferenceList_Clicked(self):

        if str(self.shotReferenceList.selectedItems()[0].text()) == "None":
            self.selected_shot_number = "xxxx"
        else:
            self.selected_shot_number = str(self.shotReferenceList.selectedItems()[0].text())

        # Filter thumbnails based on which shot was clicked
        all_references = []
        all_tags = []
        for i in xrange(self.referenceThumbListWidget.count()):
            all_references.append(self.referenceThumbListWidget.item(i))

        for ref in all_references:
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()
            ref_seq = ref_data[0]
            ref_shot = ref_data[1]
            ref_tags = ref_data[5]
            if str(self.shotReferenceList.selectedItems()[
                       0].text()) == "None":  # If "None" is selected, show all thumbnails
                if ref_seq == self.selected_sequence_name:
                    all_tags.append(ref_tags)
                    self.referenceThumbListWidget.setItemHidden(ref, False)
                else:
                    self.referenceThumbListWidget.setItemHidden(ref, True)
            else:  # Else, show thumbnails for selected sequence only
                if ref_shot == self.selected_shot_number and ref_seq == self.selected_sequence_name:
                    all_tags.append(ref_tags)
                    self.referenceThumbListWidget.setItemHidden(ref, False)
                else:
                    self.referenceThumbListWidget.setItemHidden(ref, True)

        self.add_tags_to_filter_tags_list(all_tags)

    def add_tags_to_selected_references(self):

        # Retrieve selected tags to add
        selected_tags = self.allTagsTreeWidget.selectedItems()
        selected_tags = [str(i.text(0)) for i in selected_tags]

        # Retrieve selected QListWidgetItem
        selected_references = self.referenceThumbListWidget.selectedItems()
        for ref in selected_references:
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()  # Get data associated with QListWidgetItem
            ref_sequence_name = str(ref_data[0])
            ref_shot_number = str(ref_data[1])
            ref_name = str(ref_data[2])
            ref_path = str(ref_data[3])
            ref_version = str(ref_data[4])
            ref_tags = ref_data[5]

            if ref_tags and "," in ref_tags:
                ref_tags = ref_data[5].split(",")
            else:
                ref_tags = [ref_tags]

            tags_to_add = sorted(list(set(ref_tags + selected_tags)))
            tags_to_add = filter(None, tags_to_add)
            tags_to_add = ",".join(tags_to_add)

            # Update reference QListWidgetItem data
            data = (ref_sequence_name, ref_shot_number, ref_name, ref_path, ref_version, tags_to_add)
            ref.setData(QtCore.Qt.UserRole, data)

            self.cursor.execute(
                '''UPDATE assets SET asset_tags=? WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_version=?''',
                (tags_to_add, ref_sequence_name, ref_shot_number, ref_name, ref_version,))

        self.db.commit()

        self.referenceThumbListWidget_itemSelectionChanged()
        self.reload_filter_by_tags_list()

    def add_tags_to_filter_tags_list(self, tags):

        all_tags = tags

        all_tags = filter(None, all_tags)
        all_tags = ",".join(all_tags)
        all_tags = all_tags.split(",")
        all_tags = sorted(list(set(all_tags)))

        self.filterByTagsListWidget.clear()
        for tag in all_tags:
            tag_frequency = self.tags_frequency[tag]  # Get the frequency of current tag (ex: 1, 5, 15)
            tag_frequency = Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 10,
                                          30)  # Fit frequency in the 10-30 range
            font = QtGui.QFont()
            font.setPointSize(tag_frequency)

            item = QtGui.QListWidgetItem(tag)
            item.setFont(font)

            self.filterByTagsListWidget.addItem(item)

    def create_reference_from_web(self):

        # Check if URL is valid
        URL = str(self.referenceWebLineEdit.text())
        if len(URL) < 3:
            self.message_box(text="Please enter a valid URL")
            return

        asset_name_dialog = QtGui.QDialog()
        asset_name_dialog.setWindowTitle("Asset name")
        Lib.apply_style(self, asset_name_dialog)
        main_layout = QtGui.QVBoxLayout(asset_name_dialog)

        lbl = QtGui.QLabel("Type a name for the asset and press enter:", asset_name_dialog)
        lineEdit = QtGui.QLineEdit(asset_name_dialog)
        lineEdit.returnPressed.connect(asset_name_dialog.close)

        main_layout.addWidget(lbl)
        main_layout.addWidget(lineEdit)

        asset_name_dialog.exec_()

        # Convert asset name
        asset_name = unicode(lineEdit.text())
        asset_name = Lib.normalize_str(self, asset_name)
        asset_name = Lib.convert_to_camel_case(self, asset_name)


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
            if selected_sequence == "All" or selected_sequence == "None":
                selected_sequence = "xxx"
            asset_filename += selected_sequence + "_"
        except:
            self.message_box(text="Please select a sequence first")
            return

        # Check if a shot is selected
        try:
            selected_shot = str(self.shotReferenceList.selectedItems()[0].text())
            if selected_shot == "None":
                selected_shot = "xxxx"
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

        # Create reference from video
        if "youtube" in URL or "vimeo" in URL:
            self.ref_type = "video"
            if "youtube" in URL.lower():
                video = pafy.new(URL)
                thumbnail_url = str(video.thumb).replace("default", "sddefault")
                stream_link = video.streams[0].url

            elif "vimeo" in URL.lower():
                stream_link = URL
                id = re.search(r'[0-9]{3,12}', URL).group(0)
                fetch_thumbnail = urllib.urlopen("https://vimeo.com/api/v2/video/{0}.xml".format(id))
                page_source = fetch_thumbnail.read()
                start = '<thumbnail_large>'
                end = '</thumbnail_large>'
                thumbnail_url = re.search('%s(.*)%s' % (start, end), page_source).group(1)

            urllib.urlretrieve(thumbnail_url, self.selected_project_path + asset_filename)
            downloaded_img = Image.open(self.selected_project_path + asset_filename)
            image_width = downloaded_img.size[0]
            if self.keepSizeCheckBox.checkState() == 0:
                if image_width > 1920:
                    image_width = 1920
            Lib.compress_image(self, self.selected_project_path + asset_filename, image_width, self.compression_level)
            Lib.add_watermark(self, self.selected_project_path + asset_filename, "VIDEO",
                              self.selected_project_path + asset_filename)



        else:  # Create image reference
            self.ref_type = "image"
            urllib.urlretrieve(URL, self.selected_project_path + asset_filename)
            downloaded_img = Image.open(self.selected_project_path + asset_filename)
            image_width = downloaded_img.size[0]
            if self.keepSizeCheckBox.checkState() == 0:
                if image_width > 1920:
                    image_width = 1920
            Lib.compress_image(self, self.selected_project_path + asset_filename, image_width, self.compression_level)

        new_item = QtGui.QListWidgetItem()
        new_item.setIcon(QtGui.QIcon(self.selected_project_path + asset_filename))

        # Add reference to database
        if self.ref_type == "video":
            self.cursor.execute(
                '''INSERT INTO assets(project_name, sequence_name, shot_number, asset_name, asset_path, asset_type, asset_version, asset_dependency, asset_tags, creator) VALUES(?,?,?,?,?,?,?,?,?,?)''',
                (self.selected_project_name, selected_sequence, selected_shot, asset_name, asset_filename, "ref",
                 last_version, stream_link, "video", self.username))

            self.add_log_entry("{0} added a reference from web (video format)".format(self.members[self.username]))

            new_item.setData(QtCore.Qt.UserRole,
                             [str(selected_sequence), str(selected_shot), str(asset_name), str(asset_filename),
                              str(last_version), "video"])

        elif self.ref_type == "image":
            self.cursor.execute(
                '''INSERT INTO assets(project_name, sequence_name, shot_number, asset_name, asset_path, asset_type, asset_version, creator) VALUES(?,?,?,?,?,?,?,?)''',
                (self.selected_project_name, selected_sequence, selected_shot, asset_name, asset_filename, "ref",
                 last_version, self.username))

            self.add_log_entry("{0} added a reference from web".format(self.members[self.username]))

            new_item.setData(QtCore.Qt.UserRole,
                             [str(selected_sequence), str(selected_shot), str(asset_name), str(asset_filename),
                              str(last_version), ""])

        self.db.commit()

        self.referenceThumbListWidget.addItem(new_item)

        self.referenceThumbListWidget.scrollToItem(new_item)
        self.referenceThumbListWidget.clearSelection()
        self.referenceThumbListWidget.setItemSelected(new_item, True)

    def create_reference_from_files(self):

        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            self.message_box(text="Please select a project first")
            return

        asset_filename = "\\assets\\ref\\" + self.selected_project_shortname + "_"

        # Check if a sequence is selected
        try:
            selected_sequence = str(self.seqReferenceList.selectedItems()[0].text())
            if selected_sequence == "All":
                selected_sequence = "xxx"
            asset_filename += selected_sequence + "_"
        except:
            self.message_box(text="Please select a sequence first")
            return

        # Check if a shot is selected
        try:
            selected_shot = str(self.shotReferenceList.selectedItems()[0].text())
            if selected_shot == "None":
                selected_sequence = "xxxx"
            asset_filename += selected_shot + "_"
        except:
            selected_shot = "xxxx"
            asset_filename += "xxxx_"


        # Ask for user to select files
        selected_files_path = QtGui.QFileDialog.getOpenFileNames(self, 'Select Files',
                                                                 'Z:\\Groupes-cours\\NAND999-A15-N01\\Nature',
                                                                 "Images Files (*.jpg *.png *bmp)")

        if len(selected_files_path) < 1:
            return


        # Get file name
        selected_files_name = []
        files_name = []
        for path in selected_files_path:
            file_name = unicode(path.split("\\")[-1].split(".")[0])
            file_name = Lib.normalize_str(self, file_name)
            file_name = Lib.convert_to_camel_case(self, file_name)
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



        # Rename images
        for i, path in enumerate(selected_files_path):
            if not os.path.isfile(self.selected_project_path + selected_files_name[i]):
                # Backup file
                file_name, file_extension = os.path.splitext(path)
                backup_path = path.replace(file_extension, "") + "_backup" + ".jpg"
                shutil.copy(path, backup_path)

                # Rename file and place it in correct folder
                os.rename(path, self.selected_project_path + selected_files_name[i])

                # Update progress bar

        # Compress images
        for path in selected_files_name:
            img = Image.open(self.selected_project_path + path)
            image_width = img.size[0]
            if self.keepSizeCheckBox.checkState() == 0:
                if image_width > 1920:
                    image_width = 1920
            Lib.compress_image(self, self.selected_project_path + path, image_width, self.compression_level)


        # Add reference to database
        number_of_refs_added = 0
        for i, path in enumerate(selected_files_name):
            number_of_refs_added += 1
            last_version = path.split("\\")[-1].split(".")[0].split("_")[-1]

            self.cursor.execute(
                '''INSERT INTO assets(project_name, sequence_name, shot_number, asset_name, asset_path, asset_type, asset_version, creator) VALUES(?,?,?,?,?,?,?,?)''',
                (self.selected_project_name, selected_sequence, selected_shot, files_name[i], path, "ref", last_version,
                 self.username))

            new_item = QtGui.QListWidgetItem()
            new_item.setIcon(QtGui.QIcon(self.selected_project_path + path))
            new_item.setData(QtCore.Qt.UserRole,
                             [str(selected_sequence), str(selected_shot), str(files_name[i]), str(path),
                              str(last_version), ""])

            self.referenceThumbListWidget.addItem(new_item)

        self.add_log_entry(
            "{0} added {1} references from files".format(self.members[self.username], number_of_refs_added))

        self.db.commit()

        self.referenceThumbListWidget.scrollToItem(new_item)
        self.referenceThumbListWidget.setItemSelected(new_item, True)

    def create_reference_from_screenshot(self):

        asset_name_dialog = QtGui.QDialog()
        asset_name_dialog.setWindowTitle("Asset name")
        Lib.apply_style(self, asset_name_dialog)
        main_layout = QtGui.QVBoxLayout(asset_name_dialog)

        lbl = QtGui.QLabel("Type a name for the asset and press enter:", asset_name_dialog)
        lineEdit = QtGui.QLineEdit(asset_name_dialog)
        lineEdit.returnPressed.connect(asset_name_dialog.close)

        main_layout.addWidget(lbl)
        main_layout.addWidget(lineEdit)

        asset_name_dialog.exec_()

        # Convert asset name
        asset_name = unicode(lineEdit.text())
        asset_name = Lib.normalize_str(self, asset_name)
        asset_name = Lib.convert_to_camel_case(self, asset_name)

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
            if selected_sequence == "All" or selected_sequence == "None":
                selected_sequence = "xxx"
            asset_filename += selected_sequence + "_"
        except:
            self.message_box(text="Please select a sequence first")
            return

        # Check if a shot is selected
        try:
            selected_shot = str(self.shotReferenceList.selectedItems()[0].text())
            if selected_shot == "None":
                selected_shot = "xxxx"
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

        # Create reference from capture
        Lib.take_screenshot(self, path=self.selected_project_path + asset_filename)
        downloaded_img = Image.open(self.selected_project_path + asset_filename)
        image_width = downloaded_img.size[0]
        Lib.compress_image(self, self.selected_project_path + asset_filename, image_width, self.compression_level)

        new_item = QtGui.QListWidgetItem()
        new_item.setIcon(QtGui.QIcon(self.selected_project_path + asset_filename))

        # Add reference to database
        self.cursor.execute(
            '''INSERT INTO assets(project_name, sequence_name, shot_number, asset_name, asset_path, asset_type, asset_version, creator) VALUES(?,?,?,?,?,?,?,?)''',
            (self.selected_project_name, selected_sequence, selected_shot, asset_name, asset_filename, "ref",
             last_version, self.username))

        self.add_log_entry("{0} added a reference from web".format(self.members[self.username]))

        new_item.setData(QtCore.Qt.UserRole,
                         [str(selected_sequence), str(selected_shot), str(asset_name), str(asset_filename),
                          str(last_version), ""])

        self.db.commit()

        self.referenceThumbListWidget.addItem(new_item)

        self.referenceThumbListWidget.scrollToItem(new_item)
        self.referenceThumbListWidget.clearSelection()
        self.referenceThumbListWidget.setItemSelected(new_item, True)

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

    def remove_selected_references(self):

        # Retrieve selected references
        selected_references = self.referenceThumbListWidget.selectedItems()

        # Delete references on database and on disk
        number_of_refs_removed = 0
        for ref in selected_references:
            number_of_refs_removed += 1
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()
            ref_sequence = str(ref_data[0])
            ref_shot_number = str(ref_data[1])
            ref_path = str(ref_data[3])
            ref_name = str(ref_data[2])
            ref_version = str(ref_data[4])

            os.remove(self.selected_project_path + str(ref_path))
            self.cursor.execute(
                '''DELETE FROM assets WHERE asset_name=? AND asset_version=? AND asset_type="ref" AND sequence_name=? AND shot_number=?''',
                (ref_name, ref_version, ref_sequence, ref_shot_number,))

            self.db.commit()

            self.referenceThumbListWidget.takeItem(self.referenceThumbListWidget.row(ref))

        if number_of_refs_removed > 1:
            self.add_log_entry(
                "{0} deleted {1} reference(s)".format(self.members[self.username], number_of_refs_removed))
        else:
            self.add_log_entry("{0} deleted {1} reference".format(self.members[self.username], number_of_refs_removed))

    def remove_tags_from_selected_references(self):
        # Retrieve selected tags to remove
        selected_tags = self.existingTagsListWidget.selectedItems()
        selected_tags = [str(i.text()) for i in selected_tags]

        # Retrieve selected references thumbnails names
        selected_references = self.referenceThumbListWidget.selectedItems()
        for ref in selected_references:
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()
            ref_sequence_name = ref_data[0]
            ref_shot_number = ref_data[1]
            ref_name = ref_data[2]
            ref_version = ref_data[4]
            ref_tags = ref_data[5]

            if ref_tags and "," in ref_tags:
                ref_tags = ref_data[5].split(",")
            else:
                ref_tags = [ref_tags]

            tags_to_add = list(set(ref_tags) - set(selected_tags))
            tags_to_add = filter(None, tags_to_add)
            tags_to_add = ",".join(tags_to_add)

            # Update reference QListWidgetItem data
            data = (ref_sequence_name, ref_shot_number, ref_name, ref_data[3], ref_version, tags_to_add)
            ref.setData(QtCore.Qt.UserRole, data)

            self.cursor.execute(
                '''UPDATE assets SET asset_tags=? WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_version=?''',
                (tags_to_add, ref_sequence_name, ref_shot_number, ref_name, ref_version,))

        self.db.commit()

        self.referenceThumbListWidget_itemSelectionChanged()
        self.reload_filter_by_tags_list()

    def load_reference_thumbnails(self, first_load=False):

        # Show progress bar dialog
        dialog = QtGui.QDialog()
        dialog.setWindowTitle("Please wait...")
        main_layout = QtGui.QVBoxLayout(dialog)

        mainLbl = QtGui.QLabel("Loading thumbnails:", self)
        progressBar = QtGui.QProgressBar(self)

        main_layout.addWidget(mainLbl)
        main_layout.addWidget(progressBar)

        Lib.apply_style(self, dialog)

        dialog.show()
        dialog.repaint()

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

        if selected_sequence == "None": selected_sequence = "xxx"
        if selected_shot == "None": selected_shot = "xxxx"

        # Load all thumbnails for first load, no matter what sequence is selected.
        if first_load == True:
            selected_sequence = "All"

        # Get reference paths from database based on selected sequence and shot
        if selected_sequence == "All" and selected_shot == "xxxx":
            references_list = self.cursor.execute(
                '''SELECT sequence_name, shot_number, asset_name, asset_path, asset_version, asset_tags FROM assets''').fetchall()
        elif selected_sequence == "xxx" and selected_shot != "xxxx":
            references_list = self.cursor.execute(
                '''SELECT sequence_name, shot_number, asset_name, asset_path, asset_version, asset_tags FROM assets WHERE shot_number=?''',
                (selected_shot,)).fetchall()
        elif selected_sequence != "xxx" and selected_shot == "xxxx":
            references_list = self.cursor.execute(
                '''SELECT sequence_name, shot_number, asset_name, asset_path, asset_version, asset_tags FROM assets WHERE sequence_name=?''',
                (selected_sequence,)).fetchall()
        elif selected_sequence == "xxx" and selected_shot == "xxxx":
            references_list = self.cursor.execute(
                '''SELECT sequence_name, shot_number, asset_name, asset_path, asset_version, asset_tags FROM assets WHERE sequence_name=? AND shot_number=?''',
                ("xxx", "xxxx",)).fetchall()
        else:
            references_list = self.cursor.execute(
                '''SELECT sequence_name, shot_number, asset_name, asset_path, asset_version, asset_tags FROM assets WHERE sequence_name=? AND shot_number=?''',
                (selected_sequence, selected_shot,)).fetchall()

        # references_list = (u'mus', u'xxxx', u'musee', u'\\assets\\ref\\nat_mus_xxxx_ref_musee_01.jpg', u'01', u'lighting,tree,architecture')

        all_tags = []

        progressBar.setMaximum(len(references_list))

        # Load thumbnails
        if len(references_list) > 0:

            for i, reference in enumerate(references_list):
                reference_path = self.selected_project_path + reference[3]
                reference_name = reference[2]
                reference_tags = reference[5]

                all_tags.append(reference_tags)

                reference_list_item = QtGui.QListWidgetItem(reference_name)
                reference_list_item.setIcon(QtGui.QIcon(reference_path))
                reference_list_item.setData(QtCore.Qt.UserRole, reference)

                if os.path.isfile(reference_path):
                    self.referenceThumbListWidget.addItem(reference_list_item)

                progressBar.setValue(i)

        all_tags = filter(None, all_tags)
        all_tags = ",".join(all_tags)
        all_tags = all_tags.split(",")
        all_tags = sorted(list(set(all_tags)))

        self.filterByTagsListWidget.clear()
        for tag in all_tags:
            tag_frequency = self.tags_frequency[tag]  # Get the frequency of current tag (ex: 1, 5, 15)
            tag_frequency = Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 10,
                                          30)  # Fit frequency in the 10-30 range
            font = QtGui.QFont()
            font.setPointSize(tag_frequency)

            item = QtGui.QListWidgetItem(tag)
            item.setFont(font)

            self.filterByTagsListWidget.addItem(item)

        # Close progress bar dialog
        dialog.close()
        self.first_thumbnail_load = False

    def reload_filter_by_tags_list(self):

        all_references = []
        for i in xrange(self.referenceThumbListWidget.count()):
            all_references.append(self.referenceThumbListWidget.item(i))

        all_tags = self.get_all_tags_from_loaded_references(all_references)

        self.filterByTagsListWidget.clear()
        for tag in all_tags:
            tag_frequency = self.tags_frequency[tag]  # Get the frequency of current tag (ex: 1, 5, 15)
            tag_frequency = Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 10,
                                          30)  # Fit frequency in the 10-30 range
            font = QtGui.QFont()
            font.setPointSize(tag_frequency)

            item = QtGui.QListWidgetItem(tag)
            item.setFont(font)

            self.filterByTagsListWidget.addItem(item)

    def referenceThumbListWidget_itemSelectionChanged(self):

        self.selected_references = self.referenceThumbListWidget.selectedItems()

        all_tags = self.get_all_tags_from_loaded_references(self.selected_references)

        # Add tags to existing tags list
        self.existingTagsListWidget.clear()
        for tag in all_tags:
            self.existingTagsListWidget.addItem(tag)

    def get_all_tags_from_loaded_references(self, references_list):

        """This function gets tags from a list of QListWidgetItem.

        :param references_list: list of QListWidgetItems
        :return: list of tags from QListWidgetItems. Ex: ["lighting", "character", "architecture"]
        """

        all_tags = []

        for ref in references_list:
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()
            ref_tags = str(ref_data[5])
            all_tags.append(ref_tags)
            all_tags = filter(None, all_tags)
            all_tags = ",".join(all_tags)  # convert all_tags = ["", "architecture", "architecture,lighting"] to all_tags = "architecture,architecture,lighting"
            all_tags = all_tags.split(
                ",")  # convert all_tags = "architecture,architecture,lighting" to ["architecture", "architecture", "lighting"]
            all_tags = sorted(list(set(all_tags)))  # sort list and remove duplicates

        return all_tags

    def change_reference_thumb_size(self, size):

        icon_size = QtCore.QSize(128 * size, 128 * size)
        self.referenceThumbListWidget.setIconSize(icon_size)

        try:
            selected_reference = self.referenceThumbListWidget.selectedItems()[0]
            self.referenceThumbListWidget.scrollToItem(selected_reference, QtGui.QAbstractItemView.EnsureVisible)
        except:
            pass

    def filter_reference_by_tags(self):

        # Get all selected tags from the filter tags list
        selected_tags = self.filterByTagsListWidget.selectedItems()
        selected_tags = [str(i.text()) for i in selected_tags]

        # Get all references currently loaded in the referenceThumbListWidget view
        all_references = []
        for i in xrange(self.referenceThumbListWidget.count()):
            all_references.append(self.referenceThumbListWidget.item(i))

        # If no tag is selected, unhide all references
        if not selected_tags:
            [ref.setHidden(False) for ref in all_references]
            self.seqReferenceList_Clicked()
            return

        # Loop over all references and set them to hidden if any selected tag can't be found in reference's tags
        for ref in all_references:
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()
            ref_sequence = ref_data[0]
            ref_tags = ref_data[5]
            if ref_tags == None:
                ref.setHidden(True)
                continue

            if "," in ref_tags:
                ref_tags = ref_tags.split(
                    ",")  # Convert string to list (ex: "character, lighting" to ["character", "statue"]
            else:
                ref_tags = ref_tags.split()

            ref_tags = [str(i) for i in ref_tags]

            if self.selected_sequence_name == "xxx":  # If selected sequence is all, filter only by selected tags
                if set(ref_tags).isdisjoint(selected_tags):  # Can't find any selected tag in reference tags : hide item
                    ref.setHidden(True)
                else:
                    ref.setHidden(False)
            else:  # If selected sequence is something else than all, filter by selected tags and by sequence name
                if not set(ref_tags).isdisjoint(
                        selected_tags) and self.selected_sequence_name == ref_sequence:  # If current reference is in selected sequence and has tags from selected tags, then don't hide it
                    ref.setHidden(False)
                else:
                    ref.setHidden(True)

    def filter_reference_by_name(self):

        filter_str = unicode(self.filterByNameLineEdit.text())
        filter_str = Lib.normalize_str(self, filter_str)
        filter_str = filter_str.lower()

        if "*" in filter_str:
            filter_str = filter_str.replace("*", ".*")
            r = re.compile(filter_str)
            for i in xrange(0, self.referenceThumbListWidget.count()):
                item_text = str(self.referenceThumbListWidget.item(i).text()).lower()
                if r.match(item_text):
                    self.referenceThumbListWidget.setItemHidden(self.referenceThumbListWidget.item(i), False)
                else:
                    self.referenceThumbListWidget.setItemHidden(self.referenceThumbListWidget.item(i), True)
        else:

            for i in xrange(0, self.referenceThumbListWidget.count()):
                item_text = str(self.referenceThumbListWidget.item(i).text()).lower()
                if filter_str in item_text:
                    self.referenceThumbListWidget.setItemHidden(self.referenceThumbListWidget.item(i), False)
                else:
                    self.referenceThumbListWidget.setItemHidden(self.referenceThumbListWidget.item(i), True)

    def load_ref_in_kuadro(self):

        os.system("taskkill /im kuadro.exe /f")

        references_to_load = []

        for ref in self.selected_references:
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()
            ref_path = ref_data[3]
            references_to_load.append(self.selected_project_path + ref_path)

        references_to_load = " ".join(references_to_load)

        subprocess.Popen(["Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_soft\\kuadro.exe",
                          [references_to_load]], close_fds=True)

    def load_ref_in_photoshop(self):

        references_to_load = []

        for ref in self.selected_references:
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()
            ref_path = str(ref_data[3])
            references_to_load.append(self.selected_project_path + ref_path)

        for ref_path in references_to_load:
            subprocess.Popen([self.photoshop_path, ref_path])

    def reference_doubleClicked(self):

        selected_ref = self.referenceThumbListWidget.selectedItems()[0]
        ref_data = selected_ref.data(QtCore.Qt.UserRole).toPyObject()
        ref_sequence_name = str(ref_data[0])
        ref_shot_number = str(ref_data[1])
        ref_name = str(ref_data[2])
        ref_path = str(ref_data[3])
        ref_version = str(ref_data[4])
        ref_tags = str(ref_data[5])

        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:  # Renaming reference
            self.old_reference_name = self.referenceThumbListWidget.selectedItems()[0]
            self.old_reference_name = self.old_reference_name.data(QtCore.Qt.UserRole).toPyObject()[2]

            self.rename_dialog = QtGui.QDialog()
            self.rename_dialog.setWindowIcon(self.app_icon)
            self.rename_dialog.setWindowTitle("Rename reference")

            Lib.apply_style(self, self.rename_dialog)

            self.horizontalLayout = QtGui.QVBoxLayout(self.rename_dialog)

            self.reference_new_name = QtGui.QLineEdit()
            self.reference_new_name.setText(self.old_reference_name)
            self.horizontalLayout.addWidget(self.reference_new_name)

            self.acceptBtn = QtGui.QPushButton("Accept")
            self.horizontalLayout.addWidget(self.acceptBtn)

            self.acceptBtn.clicked.connect(self.rename_reference)

            self.rename_dialog.exec_()

        elif QtGui.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:  # Viewing comments
            comment_dialog = CommentWidget(self, 1, "ref", ref_name, ref_sequence_name, ref_shot_number, ref_version,
                                           ref_path)

        else:  # Opening video / image in chrome / windows image view

            isVideo = self.cursor.execute(
                '''SELECT asset_dependency FROM assets WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_path=? AND asset_version=? AND asset_tags=?''',
                (ref_sequence_name, ref_shot_number, ref_name, ref_path, ref_version, ref_tags,)).fetchone()
            try:
                subprocess.Popen(["C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe", isVideo[0]])
                return
            except:
                # Open image in windows viewer
                os.system(self.selected_project_path + ref_path)

        return

    def rename_reference(self):

        new_name = unicode(self.reference_new_name.text())
        new_name = Lib.normalize_str(self, new_name)
        new_name = Lib.convert_to_camel_case(self, new_name)

        if len(new_name) >= 3:
            self.rename_dialog.close()
        else:
            return

        selected_reference = self.referenceThumbListWidget.selectedItems()[0]

        ref_data = selected_reference.data(QtCore.Qt.UserRole).toPyObject()
        ref_sequence_name = ref_data[0]
        ref_shot_number = ref_data[1]
        ref_name = ref_data[2]
        ref_path = ref_data[3]
        ref_version = ref_data[4]
        ref_tags = ref_data[5]

        if self.old_reference_name == new_name:
            return

        new_path = ref_path.replace(self.old_reference_name, new_name)

        new_version = ref_version
        # Check if file exist, if yes, increment new_version and change new_path based on new_version.
        while os.path.isfile(self.selected_project_path + new_path):
            fileName, fileExtension = os.path.splitext(new_path)
            current_version = int(fileName.split("_")[-1])
            new_version = str(current_version + 1).zfill(2)
            new_path = new_path.replace("_" + str(current_version).zfill(2), "_" + new_version)

        os.rename(self.selected_project_path + ref_path, self.selected_project_path + new_path)

        self.cursor.execute(
            '''UPDATE assets SET asset_name=?, asset_path=?, asset_version=? WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_version=?''',
            (new_name, new_path, new_version, ref_sequence_name, ref_shot_number, ref_name, ref_version,))

        self.db.commit()

        # Update reference QListWidgetItem data
        data = (ref_sequence_name, ref_shot_number, new_name, new_path, ref_version, ref_tags)
        selected_reference.setData(QtCore.Qt.UserRole, data)

        selected_reference.setText(new_name)

    def change_seq_shot_layout(self):
        self.change_dialog = QtGui.QDialog()
        self.change_dialog.setWindowTitle("Change Sequence / Shot")
        self.change_dialog.resize(300, 200)

        Lib.apply_style(self, self.change_dialog)

        # Create main layout
        main_layout = QtGui.QVBoxLayout(self.change_dialog)

        # Create seq and shot combo box
        self.seq_combobox = QtGui.QComboBox()
        self.seq_combobox.addItem("All")
        self.seq_combobox.addItems([str(i[0]) for i in self.sequences])

        self.shot_combobox = QtGui.QComboBox()
        self.shot_combobox.addItem("None")

        # Create accept button
        apply_btn = QtGui.QPushButton("Accept")

        # Create labels
        sequence_lbl = QtGui.QLabel("Sequence Name:")
        shot_lbl = QtGui.QLabel("Shot Number:")

        # Add widgets to layout
        main_layout.addWidget(sequence_lbl)
        main_layout.addWidget(self.seq_combobox)
        main_layout.addWidget(shot_lbl)
        main_layout.addWidget(self.shot_combobox)
        main_layout.addWidget(apply_btn)

        # Connect the widgets to the functions
        apply_btn.clicked.connect(self.change_seq_shot)
        self.seq_combobox.currentIndexChanged.connect(self.filter_shots_from_sequences)

        # Execute the QDialog
        self.change_dialog.exec_()

    def change_seq_shot(self):
        self.change_dialog.close()

        selected_sequence = str(self.seq_combobox.currentText())
        selected_shot = str(self.shot_combobox.currentText())
        selected_references = self.referenceThumbListWidget.selectedItems()

        if selected_sequence == "All":
            selected_sequence = "xxx"

        if selected_shot == "None":
            selected_shot = "xxxx"

        for ref in selected_references:
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()
            ref_sequence_name = str(ref_data[0])
            ref_shot_number = str(ref_data[1])
            ref_name = str(ref_data[2])
            ref_path = str(ref_data[3])
            ref_version = str(ref_data[4])
            ref_tags = str(ref_data[5])

            new_path = ref_path
            new_path = ref_path.replace("_" + ref_sequence_name + "_" + str(ref_shot_number),
                                        "_" + selected_sequence + "_" + selected_shot)
            new_version = ref_version

            while os.path.isfile(self.selected_project_path + new_path):
                fileName, fileExtension = os.path.splitext(new_path)
                current_version = int(fileName.split("_")[-1])
                new_version = str(current_version + 1).zfill(2)
                new_path = new_path.replace("_" + str(current_version).zfill(2), "_" + new_version)

            os.rename(self.selected_project_path + ref_path, self.selected_project_path + new_path)

            self.cursor.execute(
                '''UPDATE assets SET sequence_name=?, shot_number=?, asset_path=?, asset_version=? WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_version=?''',
                (selected_sequence, selected_shot, new_path, new_version, ref_sequence_name, ref_shot_number, ref_name,
                 ref_version,))

            # Update reference QListWidgetItem data
            data = (selected_sequence, selected_shot, ref_name, new_path, new_version, ref_tags)
            ref.setData(QtCore.Qt.UserRole, data)

            if selected_sequence == "xxx" and ref_sequence_name == "xxx":  # If new sequence and old sequence is still "All", then leave the ref on None (= don't hide it)
                self.referenceThumbListWidget.setItemHidden(ref, False)
            else:
                self.referenceThumbListWidget.setItemHidden(ref, True)

        self.referenceThumbListWidget.clearSelection()
        self.db.commit()

    def filter_shots_from_sequences(self):
        selected_sequence_name = str(self.seq_combobox.currentText())

        # Add shots to shot list and shot creation list
        if selected_sequence_name == "All":
            self.shot_combobox.addItem("None")

        else:
            shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''',
                                        (self.selected_project_name, selected_sequence_name,)).fetchall()
            self.shot_combobox.clear()
            self.shot_combobox.addItem("None")
            shots = [i[0] for i in shots]
            shots = sorted(shots)
            [self.shot_combobox.addItem(shot) for shot in shots]

    def show_url_image(self):

        URL = str(self.referenceWebLineEdit.text())

        if len(URL) < 5:
            Lib.message_box(self, text="Please enter a valid URL")
            return

        eye_icon = QtGui.QPixmap(
            "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\eye_icon_closed.png")
        eye_icon = QtGui.QIcon(eye_icon)
        self.showUrlImageBtn.setIcon(eye_icon)
        self.showUrlImageBtn.repaint()

        QDialog = QtGui.QDialog()
        QDialog.setWindowTitle("URL Preview")
        QDialog.setMaximumSize(600, 600)
        Lib.apply_style(self, QDialog)

        data = urllib.urlopen(URL).read()
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(data)
        pixmap = pixmap.scaled(600, 600, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        label = QtGui.QLabel()
        label.setPixmap(pixmap)

        layout = QtGui.QHBoxLayout(QDialog)

        layout.addWidget(label)

        QDialog.resize(600, 600)

        eye_icon = QtGui.QPixmap(
            "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\eye_icon.png")
        eye_icon = QtGui.QIcon(eye_icon)
        self.showUrlImageBtn.setIcon(eye_icon)
        self.showUrlImageBtn.repaint()

        QDialog.exec_()

    def change_quality(self):
        if self.keepQualityCheckBox.checkState() == 2:
            self.compression_level = 70
        elif self.keepQualityCheckBox.checkState() == 0:
            self.compression_level = 40

    def hide_reference_options_frame(self):
        if self.referenceOptionsFrame.isHidden():
            self.referenceOptionsFrame.show()
        else:
            self.referenceOptionsFrame.hide()
