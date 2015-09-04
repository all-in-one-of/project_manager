#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import subprocess
import os
from PIL import Image
import urllib
from functools import partial
import re
import pafy
from collections import Counter
import shutil
import webbrowser
import datetime


class ReferenceTab(object):
    def __init__(self):
        self.compression_level = 60
        self.keep_size = False
        self.last_asset_name = ""

        eye_icon = QtGui.QPixmap(self.cur_path + "\\media\\eye_icon.png")
        eye_icon = QtGui.QIcon(eye_icon)
        self.showUrlImageBtn.setIcon(eye_icon)

        self.ref_selected_sequence_name = "xxx"
        self.ref_selected_shot_number = "xxxx"
        self.ref_selected_filter_tags = [""]
        self.all_references_ListWidgetItems = []
        self.images_with_no_tags_state = 0
        self.images_with_comments_state = 0
        self.nbrOfRefLoadedLbl.setText("Showing 0 out of 0")
        self.nbr_of_visible_images = 0

        self.ref_assets_instances = []

        self.allTagsTreeWidget.sortItems(0, QtCore.Qt.AscendingOrder)
        self.seqReferenceList.itemClicked.connect(self.ref_sequence_list_clicked)
        self.shotReferenceList.itemClicked.connect(self.ref_shot_list_clicked)
        self.referenceThumbListWidget.itemSelectionChanged.connect(self.referenceThumbListWidget_itemSelectionChanged)
        self.referenceThumbListWidget.itemDoubleClicked.connect(self.reference_doubleClicked)
        self.filterByNameLineEdit.textChanged.connect(self.ref_filter_by_name)
        self.filterByTagsListWidget.itemClicked.connect(self.ref_filter_by_tags_clicked)
        self.clearFilterByTagsSelectionBtn.clicked.connect(self.clear_filter_by_tags_selection)
        self.reloadFilterByTagsBtn.clicked.connect(self.load_filter_by_tags_list)
        self.createReferenceFromWebBtn.clicked.connect(self.create_reference_from_web)
        self.referenceWebLineEdit.returnPressed.connect(self.create_reference_from_web)
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
        self.changeRefSeqShotBtn.clicked.connect(self.ref_change_seq_shot)
        self.showUrlImageBtn.clicked.connect(self.show_url_image)
        self.hideReferenceOptionsFrameBtn.clicked.connect(self.hide_reference_options_frame)
        self.filterByNoTagsCheckBox.stateChanged.connect(self.ref_filter_images_with_no_tags_clicked)
        self.filterByCommentsCheckBox.stateChanged.connect(self.ref_filter_images_with_comments_clicked)
        self.refShowNamesCheckBox.stateChanged.connect(self.toggle_thumbnail_text)
        self.refShowSequencesCheckBox.stateChanged.connect(self.toggle_thumbnail_text)
        self.createMoodboardFromImagesBtn.clicked.connect(self.create_moodboard_from_images)
        self.connect(self.referenceThumbListWidget, QtCore.SIGNAL('delete_selected_reference'), self.remove_selected_references)
        self.connect(self.referenceThumbListWidget, QtCore.SIGNAL('referenceThumbListWidget_simple_view'), self.reference_open_ref_in_windows_viewer)

        resize_icon = QtGui.QIcon(self.cur_path + "\\media\\thumbnail.png")
        self.biggerRefPushButton_01.setIcon(resize_icon)
        self.biggerRefPushButton_02.setIcon(resize_icon)
        self.biggerRefPushButton_03.setIcon(resize_icon)
        self.biggerRefPushButton_04.setIcon(resize_icon)
        self.biggerRefPushButton_01.setIconSize(QtCore.QSize(8, 8))
        self.biggerRefPushButton_02.setIconSize(QtCore.QSize(16, 16))
        self.biggerRefPushButton_03.setIconSize(QtCore.QSize(24, 24))
        self.biggerRefPushButton_04.setIconSize(QtCore.QSize(30, 30))

        # Tags Manager Buttons
        self.addTagBtn.clicked.connect(self.add_tag_to_tags_manager)
        self.addTagLineEdit.returnPressed.connect(self.add_tag_to_tags_manager)
        self.removeSelectedTagsBtn.clicked.connect(self.remove_selected_tags_from_tags_manager)

        # Tags setup
        self.setup_tags()

    def ref_load_all_references(self):
        '''Load all references when clicking sequence for the first time'''

        if len(self.seqReferenceList.selectedItems()) == 0:
            self.seqReferenceList.setCurrentRow(0)
            self.shotReferenceList.setCurrentRow(0)

        # Show progress bar dialog
        dialog = QtGui.QDialog()
        dialog.setWindowTitle("Please wait...")
        main_layout = QtGui.QVBoxLayout(dialog)

        mainLbl = QtGui.QLabel("Loading thumbnails:", self)
        progressBar = QtGui.QProgressBar(self)

        main_layout.addWidget(mainLbl)
        main_layout.addWidget(progressBar)

        self.Lib.apply_style(self, dialog)

        dialog.show()
        dialog.repaint()

        ref_all_references_assets = self.cursor.execute(
            '''SELECT * FROM assets WHERE project_name=? AND asset_type=?''',
            (self.selected_project_name, "ref")).fetchall()
        progressBar.setMaximum(len(ref_all_references_assets))

        self.references = []

        for i, ref in enumerate(ref_all_references_assets):
            id = ref[0]
            project_name = ref[1]
            sequence_name = ref[2]
            shot_number = ref[3]
            name = ref[4]
            path = ref[5]
            extension = ref[6]
            type = ref[7]
            version = ref[8]
            tags = ref[9]
            dependency = ref[10]
            last_access = ref[11]
            last_publish = ref[12]
            creator = ref[13]
            if id == None: id = ""
            if project_name == None: project_name = ""
            if sequence_name == None: sequence_name = ""
            if shot_number == None: shot_number = ""
            if name == None: name = ""
            if path == None: path = ""
            if extension == None: extension = ""
            if type == None: type = ""
            if version == None: version = ""
            if tags == None: tags = ""
            if dependency == None: dependency = ""
            if last_access == None: last_access = ""
            if last_publish == None: last_publish = ""
            if creator == None: creator = ""

            asset = self.Asset(self, id, project_name, sequence_name, shot_number, name, path, extension, type, version,
                          tags, dependency, last_access, last_publish, creator)
            self.ref_assets_instances.append(asset)
            ref_item = QtGui.QListWidgetItem()
            ref_item.setIcon(QtGui.QIcon(asset.full_path.replace(".jpg", "_thumb.jpg")))
            ref_item.setData(QtCore.Qt.UserRole, asset)

            if os.path.isfile(asset.full_path):  # Check if image exists to prevent errors
                self.references.append((ref_item, asset))
                self.all_references_ListWidgetItems.append(ref_item)
                self.referenceThumbListWidget.addItem(ref_item)

            progressBar.setValue(i)
            hue = self.fit_range(i, 0, progressBar.maximum(), 0, 76)
            progressBar.setStyleSheet("QProgressBar::chunk {background-color: hsl(" + str(hue) + ", 255, 205);} QProgressBar{ text-align: center;}")
            mainLbl.setText("Adding image #" + str(i))
            self.nbr_of_visible_images += 1
            dialog.repaint()

        self.nbrOfRefLoadedLbl.setText("Showing {0} out of {1}".format(self.nbr_of_visible_images, len(self.all_references_ListWidgetItems)))
        mainLbl.setText("Refreshing view, please wait...")
        dialog.repaint()
        dialog.close()

        self.load_filter_by_tags_list()

    def ref_filter_references(self):
        '''Filter references by sequence / shot / tags'''
        [ref.setHidden(False) for ref in self.all_references_ListWidgetItems]

        # Filter by sequence
        all_references = self.get_all_visible_references()

        self.nbr_of_visible_images = len(self.all_references_ListWidgetItems)

        for ref in all_references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            if self.seqReferenceList.selectedItems()[0].text() == "All":
                continue
            elif self.seqReferenceList.selectedItems()[0].text() == "None":
                if asset.sequence != "xxx":
                    ref.setHidden(True)
                    self.nbr_of_visible_images -= 1
            elif self.seqReferenceList.selectedItems()[0].text() != "None":
                if asset.sequence != self.ref_selected_sequence_name:
                    ref.setHidden(True)
                    self.nbr_of_visible_images -= 1

        # Filter by shot
        all_references = self.get_all_visible_references()

        for ref in all_references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            if self.shotReferenceList.selectedItems()[0].text() != "None":
                if asset.shot != self.ref_selected_shot_number:
                    ref.setHidden(True)
                    self.nbr_of_visible_images -= 1

        # Filter by tags
        all_references = self.get_all_visible_references()

        for ref in all_references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            if len(self.filterByTagsListWidget.selectedItems()) > 0:
                if not set(self.ref_selected_filter_tags).issubset(set(asset.tags)):
                    ref.setHidden(True)
                    self.nbr_of_visible_images -= 1

        # Show only assets with no tags if checkbox is checked
        if self.images_with_no_tags_state == 2:
            all_references = self.get_all_visible_references()
            for ref in all_references:
                asset = ref.data(QtCore.Qt.UserRole).toPyObject()
                if len(asset.tags) != 0:
                    ref.setHidden(True)
                    self.nbr_of_visible_images -= 1

        # Show only assets with comments if checkbox is checked
        if self.images_with_comments_state == 2:
            all_references = self.get_all_visible_references()
            for ref in all_references:
                asset = ref.data(QtCore.Qt.UserRole).toPyObject()

                if asset.nbr_of_comments == 0:
                    ref.setHidden(True)
                    self.nbr_of_visible_images -= 1




        # If no tags is selected in filter tags list, refresh filter tags list
        if len(self.filterByTagsListWidget.selectedItems()) == 0:
            self.load_filter_by_tags_list()

        self.nbrOfRefLoadedLbl.setText("Showing {0} out of {1}".format(self.nbr_of_visible_images, len(self.all_references_ListWidgetItems)))

    def ref_filter_by_name(self):
        '''Filter references by name'''
        all_visible_references = self.get_all_visible_references()
        for ref in all_visible_references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            if len(self.filterByNameLineEdit.text()) > 0:
                filter_str = unicode(self.filterByNameLineEdit.text())
                filter_str = self.Lib.normalize_str(self, filter_str)
                filter_str = filter_str.lower()
                if "*" in filter_str:
                    filter_str = filter_str.replace("*", ".*")
                    r = re.compile(filter_str)
                    if not r.match(asset.name):
                        ref.setHidden(True)
                        self.nbr_of_visible_images -= 1
                    else:
                        ref.setHidden(False)
                else:
                    if not filter_str in asset.name:
                        ref.setHidden(True)
                        self.nbr_of_visible_images -= 1
                    else:
                        ref.setHidden(False)
            else:
                self.ref_filter_references()

        self.nbrOfRefLoadedLbl.setText("Showing {0} out of {1}".format(self.nbr_of_visible_images, len(self.all_references_ListWidgetItems)))

    def ref_sequence_list_clicked(self):
        '''Set variables, load shots from selected reference and filter references'''

        # If reference thumb list widget is empty, load all references for the first time
        if self.referenceThumbListWidget.count() == 0: self.ref_load_all_references()

        # Set selected reference name variable
        self.ref_selected_sequence_name = str(self.seqReferenceList.selectedItems()[0].text())
        if self.ref_selected_sequence_name == "All" or self.ref_selected_sequence_name == "None" :
            self.ref_selected_sequence_name = "xxx"

        # Add shots to shot list and shot creation list
        self.shotReferenceList.clear()
        self.shotReferenceList.addItem("None")
        if not self.ref_selected_sequence_name == "xxx":
            [self.shotReferenceList.addItem(shot) for shot in self.shots[self.ref_selected_sequence_name]]
        self.shotReferenceList.setCurrentRow(0)

        # Filter references
        self.ref_filter_references()

    def ref_shot_list_clicked(self):
        '''Set variables and filter references'''
        self.ref_selected_shot_number = str(self.shotReferenceList.selectedItems()[0].text())
        if self.ref_selected_shot_number == "None": self.ref_selected_shot_number = "xxxx"
        self.ref_filter_references()

    def ref_filter_by_tags_clicked(self):
        '''Set variables and filter references'''
        self.ref_selected_filter_tags = self.filterByTagsListWidget.selectedItems()
        self.ref_selected_filter_tags = [str(i.text()) for i in self.ref_selected_filter_tags]
        self.ref_filter_references()

    def ref_filter_images_with_no_tags_clicked(self):
        '''Set variable and filter references'''
        self.images_with_no_tags_state = self.filterByNoTagsCheckBox.checkState()
        self.ref_filter_references()

    def ref_filter_images_with_comments_clicked(self):
        '''Set variable and filter references'''
        self.images_with_comments_state = self.filterByCommentsCheckBox.checkState()
        self.ref_filter_references()

    def load_filter_by_tags_list(self):
        '''Add tags to filterByTagsList based on visible references'''
        all_visible_references  = self.get_all_visible_references()
        all_tags_from_visible_references = sorted(self.get_all_tags_from_references(all_visible_references))

        self.filterByTagsListWidget.clear()
        for tag in all_tags_from_visible_references:
            tag_frequency = self.tags_frequency[tag]  # Get the frequency of current tag (ex: 1, 5, 15)
            tag_frequency = self.Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 10, 30)  # Fit frequency in the 10-30 range
            font = QtGui.QFont()
            font.setPointSize(tag_frequency)
            item = QtGui.QListWidgetItem(tag)
            item.setFont(font)
            self.filterByTagsListWidget.addItem(item)

    def get_all_visible_references(self):
        '''
        Get all references currently visible in the reference list widget
        :return: list of all visible references
        '''
        all_visible_references = []
        self.nbr_of_visible_images = 0

        for ref in self.all_references_ListWidgetItems:
            if not ref.isHidden():
                all_visible_references.append(ref)
                self.nbr_of_visible_images += 1

        return all_visible_references

    def get_all_tags_from_references(self, references):
        '''
        Get all tags from references
        :param references: list of references list widget item
        :return: list of tags from list of reference
        '''
        all_tags_from_references = []

        for ref in references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            all_tags_from_references.append(asset.tags)

        all_tags_from_references = list(set(sum(all_tags_from_references, []))) # Convert into one single list and remove duplicates
        all_tags_from_references = filter(None, all_tags_from_references) # Remove empty entries

        return all_tags_from_references

    def referenceThumbListWidget_itemSelectionChanged(self):
        '''
        Add tags to existing tags list so user can remove them
        '''
        self.selected_references = self.referenceThumbListWidget.selectedItems()

        try:
            selected_reference = self.referenceThumbListWidget.selectedItems()[0]
            self.selected_asset = selected_reference.data(QtCore.Qt.UserRole).toPyObject()
            self.CommentWidget.load_comments(self)
        except:
            pass

        all_tags = self.get_all_tags_from_references(self.selected_references)


        # Add tags to existing tags list
        self.existingTagsListWidget.clear()
        for tag in sorted(all_tags):
            self.existingTagsListWidget.addItem(tag)

    def remove_selected_references(self):
        '''
        Remove selected reference from database and reference list widget
        '''
        # Confirm dialog
        confirm_dialog = QtGui.QMessageBox()
        reply = confirm_dialog.question(self, 'Delete selected references', "Are you sure ?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        self.Lib.apply_style(self, confirm_dialog)
        if reply != QtGui.QMessageBox.Yes:
            return

        # Retrieve selected references
        selected_references = self.referenceThumbListWidget.selectedItems()

        # Delete references on database and on disk
        for ref in selected_references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            asset.remove_asset_from_db()
            self.Lib.remove_log_entry_from_asset_id(self, asset.id, "image")
            del asset
            self.all_references_ListWidgetItems.remove(ref)
            self.referenceThumbListWidget.takeItem(self.referenceThumbListWidget.row(ref))

    def reference_open_ref_in_windows_viewer(self):
        selected_reference = self.referenceThumbListWidget.selectedItems()[0]
        self.selected_asset = selected_reference.data(QtCore.Qt.UserRole).toPyObject()

        if "vimeo" in self.selected_asset.dependency or "youtube" in self.selected_asset.dependency:
            subprocess.Popen(["C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe", self.selected_asset.dependency])
        else:
            # Open image in windows viewer
            webbrowser.open(self.selected_asset.full_path)

    def reference_doubleClicked(self):
        subprocess.Popen(r'explorer /select,' + str(self.selected_asset.full_path))

    def rename_reference(self, asset):
        '''
        Rename reference
        '''
        rename_dialog = QtGui.QDialog()
        rename_dialog.setWindowIcon(self.app_icon)
        rename_dialog.setWindowTitle("Rename reference")

        self.Lib.apply_style(self, rename_dialog)

        horizontalLayout = QtGui.QVBoxLayout(rename_dialog)

        reference_new_name = QtGui.QLineEdit()
        reference_new_name.returnPressed.connect(rename_dialog.accept)
        reference_new_name.selectAll()
        reference_new_name.setText(asset.name)
        horizontalLayout.addWidget(reference_new_name)

        rename_dialog.exec_()

        if rename_dialog.result() == 0:
            return

        new_name = unicode(reference_new_name.text())
        new_name = self.Lib.normalize_str(self, new_name)
        new_name = self.Lib.convert_to_camel_case(self, new_name)

        if len(new_name) <= 3:
            self.Lib.message_box(self, text="Please enter a name with more than 3 letters")
            return

        if asset.name == new_name:
            return

        asset.change_name(new_name)

        selected_reference = self.referenceThumbListWidget.selectedItems()[0]
        selected_reference.setText(new_name)

    def ref_change_seq_shot(self):
        '''
        Change sequence and shot for selected references
        '''
        # Create the change seq shot dialog
        change_dialog = QtGui.QDialog()
        change_dialog.setWindowTitle("Change Sequence / Shot")
        change_dialog.setMinimumWidth(200)
        self.Lib.apply_style(self, change_dialog)

        # Create main layout
        main_layout = QtGui.QVBoxLayout(change_dialog)

        # Create seq and shot combo box
        self.change_ref_seq_combobox = QtGui.QComboBox()
        self.change_ref_seq_combobox.addItem("All")
        self.change_ref_seq_combobox.addItems([str(i[0]) for i in self.sequences])
        self.change_ref_shot_combobox = QtGui.QComboBox()
        self.change_ref_shot_combobox.addItem("None")

        # Create accept button
        apply_btn = QtGui.QPushButton("Accept")

        # Create labels
        sequence_lbl = QtGui.QLabel("Sequence Name:")
        shot_lbl = QtGui.QLabel("Shot Number:")

        # Add widgets to layout
        main_layout.addWidget(sequence_lbl)
        main_layout.addWidget(self.change_ref_seq_combobox)
        main_layout.addWidget(shot_lbl)
        main_layout.addWidget(self.change_ref_shot_combobox)
        main_layout.addWidget(apply_btn)

        # Connect the widgets to the functions
        apply_btn.clicked.connect(change_dialog.accept)
        self.change_ref_seq_combobox.currentIndexChanged.connect(self.ref_change_seq_shot_filter_shots)

        # Execute the QDialog
        change_dialog.exec_()

        # If user close dialog, return
        if change_dialog.result() == 0:
            return

        # Get selected references and change seq shot
        selected_references = self.referenceThumbListWidget.selectedItems()
        selected_sequence = str(self.change_ref_seq_combobox.currentText())
        selected_shot = str(self.change_ref_shot_combobox.currentText())
        if selected_sequence == "All": selected_sequence = "xxx"
        if selected_shot == "None": selected_shot = "xxxx"

        for ref in selected_references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            asset.change_sequence(selected_sequence)
            asset.change_shot(selected_shot)

        # Filter references and clear selection
        self.ref_filter_references()
        self.referenceThumbListWidget.clearSelection()

    def ref_change_seq_shot_filter_shots(self):
        '''
        Add shots based on what sequence was clicked on the ref_change_seq_shot layout
        '''
        selected_sequence_name = str(self.change_ref_seq_combobox.currentText())

        # Add shots to shot list and shot creation list
        self.change_ref_shot_combobox.clear()
        self.change_ref_shot_combobox.addItem("None")
        if selected_sequence_name != "All":
            [self.change_ref_shot_combobox.addItem(shot) for shot in self.shots[selected_sequence_name]]

    def add_tags_to_selected_references(self):
        # Retrieve selected tags to add
        selected_tags = self.allTagsTreeWidget.selectedItems()
        selected_tags = [str(i.text(0)) for i in selected_tags]

        # Retrieve selected QListWidgetItem
        selected_references = self.referenceThumbListWidget.selectedItems()
        for ref in selected_references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            asset.add_tags(selected_tags)

        self.referenceThumbListWidget_itemSelectionChanged() # Reload tags from selected references

    def remove_tags_from_selected_references(self):
        # Retrieve selected tags to remove
        selected_tags = self.existingTagsListWidget.selectedItems()
        selected_tags = [str(i.text()) for i in selected_tags]

        # Retrieve selected QListWidgetItem
        selected_references = self.referenceThumbListWidget.selectedItems()
        for ref in selected_references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            asset.remove_tags(selected_tags)

        self.referenceThumbListWidget_itemSelectionChanged()  # Reload tags from selected references

    def create_reference_from_web(self):
        # If reference thumb list widget is empty, load all references for the first time
        if self.referenceThumbListWidget.count() == 0: self.ref_load_all_references()
        self.referenceThumbListWidget.clearSelection()

        # Check if a sequence is selected
        selected_sequence, selected_shot = self.Lib.reference_check_if_projSeqShot_is_selected(self)
        if selected_sequence == None: return

        # Check if URL is valid
        URL = str(self.referenceWebLineEdit.text())
        if len(URL) < 3:
            self.message_box(text="Please enter a valid URL")
            return

        # Open name dialog
        asset_name = self.asset_name_dialog()
        if asset_name == None: return

        # Instanciate asset
        asset = self.Asset(self, 0, self.selected_project_name, self.ref_selected_sequence_name, self.ref_selected_shot_number, asset_name, "", "jpg", "ref", "01", "", "", "", "", self.username)
        asset.add_asset_to_db()
        self.ref_assets_instances.append(asset)

        # Create reference from video
        if "youtube" in URL or "vimeo" in URL:
            if "youtube" in URL.lower():
                stream_link = URL
                video = pafy.new(URL)
                thumbnail_url = str(video.thumb).replace("default", "sddefault")

            elif "vimeo" in URL.lower():
                stream_link = URL
                id = re.search(r'[0-9]{3,12}', URL).group(0)
                fetch_thumbnail = urllib.urlopen("https://vimeo.com/api/v2/video/{0}.xml".format(id))
                page_source = fetch_thumbnail.read()
                start = '<thumbnail_large>'
                end = '</thumbnail_large>'
                thumbnail_url = re.search('%s(.*)%s' % (start, end), page_source).group(1)

            # Download video thumbnail
            urllib.urlretrieve(thumbnail_url, asset.full_path)
            try:
                downloaded_img = Image.open(asset.full_path)
            except:
                self.Lib.message_box(self, text="Cannot download file. Try to save it and add it as a file.")
                return
            image_width = downloaded_img.size[0]
            if self.keepSizeCheckBox.checkState() == 0:
                if image_width > 1920:
                    image_width = 1920
            self.Lib.compress_image(self, asset.full_path, image_width, self.compression_level)
            self.Lib.add_watermark(self, asset.full_path, "VIDEO", asset.full_path)
            asset.change_dependency(URL)
            asset.add_tags(["_VIDEO"])

        else:  # Create image reference
            urllib.urlretrieve(URL, asset.full_path)
            try:
                downloaded_img = Image.open(asset.full_path)
            except:
                self.Lib.message_box(self, text="Cannot download file. Try to save it and add it as a file.")
                return
            image_width = downloaded_img.size[0]
            if self.keepSizeCheckBox.checkState() == 0:
                if image_width > 1920:
                    image_width = 1920
            self.Lib.compress_image(self, asset.full_path, image_width, self.compression_level)
            asset.change_dependency(URL)

        # Create low res thumbnail for preview on list widget
        shutil.copy(asset.full_path, asset.full_path.replace(".jpg", "_thumb.jpg"))
        self.Lib.compress_image(self, asset.full_path.replace(".jpg", "_thumb.jpg"), 512, 30)


        # Add Log Entry
        log_entry = self.LogEntry(self, 0, asset.id, [], [], self.username, "", "image", "{0} has added a new image from web named '{1}'.".format(self.members[self.username], asset.name), datetime.datetime.now().strftime("%d/%m/%Y at %H:%M"))
        log_entry.add_log_to_database()

        # Add item to lists
        new_item = QtGui.QListWidgetItem()
        new_item.setData(QtCore.Qt.UserRole, asset)
        new_item.setIcon(QtGui.QIcon(asset.full_path.replace(".jpg", "_thumb.jpg")))
        self.all_references_ListWidgetItems.append(new_item)
        self.referenceThumbListWidget.addItem(new_item)
        self.references.append((new_item, asset))

        self.toggle_thumbnail_text()
        self.referenceThumbListWidget.scrollToItem(new_item)
        self.referenceThumbListWidget.setItemSelected(new_item, True)

        self.referenceWebLineEdit.clear()

    def create_reference_from_files(self):
        '''
        Create references from selected files
        '''

        # If reference thumb list widget is empty, load all references for the first time
        if self.referenceThumbListWidget.count() == 0: self.ref_load_all_references()

        self.referenceThumbListWidget.clearSelection()

        selected_sequence, selected_shot = self.Lib.reference_check_if_projSeqShot_is_selected(self)
        if selected_sequence == None: return

        # Ask for user to select files
        selected_files = QtGui.QFileDialog.getOpenFileNames(self, 'Select Files', 'H:/', "Images Files (*.jpg *.png)")

        if len(selected_files) < 1:
            return

        # Show progress bar dialog
        dialog = QtGui.QDialog()
        dialog.setWindowTitle("Please wait...")
        main_layout = QtGui.QVBoxLayout(dialog)

        mainLbl = QtGui.QLabel("Adding images:", self)
        progressBar = QtGui.QProgressBar(self)
        progressBar.setMaximum(len(selected_files))

        main_layout.addWidget(mainLbl)
        main_layout.addWidget(progressBar)

        self.Lib.apply_style(self, dialog)

        dialog.show()
        dialog.repaint()


        # Add each file
        assets = []
        for i, file_path in enumerate(selected_files):
            progressBar.setValue(i)
            dialog.repaint()

            file_path = unicode(file_path)
            file_path = os.path.abspath(file_path)

            # Convert file name to normalized camel case name
            asset_name = unicode(file_path.split("\\")[-1].split(".")[0])
            asset_name = self.Lib.normalize_str(self, asset_name)
            asset_name = self.Lib.convert_to_camel_case(self, asset_name)

            # Create asset
            asset = self.Asset(self, 0, self.selected_project_name, self.ref_selected_sequence_name, self.ref_selected_shot_number, asset_name, "", "jpg", "ref", "01", "", "", "", "", self.username)
            asset.add_asset_to_db()
            self.ref_assets_instances.append(asset)
            assets.append(asset)

            # Rename file and place it in correct folder
            os.rename(file_path, asset.full_path)

            # Compress image
            img = Image.open(asset.full_path)
            image_width = img.size[0]
            if self.keepSizeCheckBox.checkState() == 0:
                if image_width > 1920:
                    image_width = 1920
            self.Lib.compress_image(self, asset.full_path, image_width, self.compression_level)

            # Create low res thumbnail for preview on list widget		+
            shutil.copy(asset.full_path, asset.full_path.replace(".jpg", "_thumb.jpg"))
            self.Lib.compress_image(self, asset.full_path.replace(".jpg", "_thumb.jpg"), 512, 30)

            # Add Log Entry
            log_entry = self.LogEntry(self, 0, asset.id, [], [], self.username, "", "image", "{0} has added a new image from files named '{1}'.".format(self.members[self.username], asset.name), datetime.datetime.now().strftime("%d/%m/%Y at %H:%M"))
            log_entry.add_log_to_database()

            # Add reference to reference list
            new_item = QtGui.QListWidgetItem()
            new_item.setIcon(QtGui.QIcon(asset.full_path.replace(".jpg", "_thumb.jpg")))
            new_item.setData(QtCore.Qt.UserRole, asset)

            self.referenceThumbListWidget.addItem(new_item)
            self.all_references_ListWidgetItems.append(new_item)
            self.referenceThumbListWidget.setItemSelected(new_item, True)
            self.references.append((new_item, asset))


        dialog.repaint()
        dialog.close()

        self.toggle_thumbnail_text()
        self.referenceThumbListWidget.scrollToItem(new_item)

    def create_reference_from_screenshot(self):
        '''
        Create reference from screenshot
        '''

        # If reference thumb list widget is empty, load all references for the first time
        if self.referenceThumbListWidget.count() == 0: self.ref_load_all_references()
        self.referenceThumbListWidget.clearSelection()

        selected_sequence, selected_shot = self.Lib.reference_check_if_projSeqShot_is_selected(self)
        if selected_sequence == None: return

        self.referenceThumbListWidget.clearSelection()

        asset_name = ""
        # Check if a name is defined for the asset
        while len(asset_name) <= 3:
            asset_name = self.asset_name_dialog()
            if asset_name == None: return
            if len(asset_name) > 3: break
            self.message_box(text="Please enter a name with more than 3 characters for the asset")


        asset = self.Asset(self, 0, self.selected_project_name, self.ref_selected_sequence_name, self.ref_selected_shot_number, asset_name, "", "jpg", "ref", "01", "", "", "", "", self.username)
        asset.add_asset_to_db()
        self.ref_assets_instances.append(asset)

        # Create reference from capture
        self.Lib.take_screenshot(self, path=asset.full_path, user_selection=True)
        downloaded_img = Image.open(asset.full_path)
        image_width = downloaded_img.size[0]
        self.Lib.compress_image(self, asset.full_path, image_width, self.compression_level)

        # Create low res thumbnail for preview on list widget
        shutil.copy(asset.full_path, asset.full_path.replace(".jpg", "_thumb.jpg"))
        self.Lib.compress_image(self, asset.full_path.replace(".jpg", "_thumb.jpg"), 512, 30)

        # Add Log Entry
        log_entry = self.LogEntry(self, 0, asset.id, [], [], self.username, "", "image", "{0} has created a new image from screenshot named '{1}'.".format(self.members[self.username], asset.name), datetime.datetime.now().strftime("%d/%m/%Y at %H:%M"))
        log_entry.add_log_to_database()

        # Add reference to reference list
        new_item = QtGui.QListWidgetItem()
        new_item.setIcon(QtGui.QIcon(asset.full_path.replace(".jpg", "_thumb.jpg")))
        new_item.setData(QtCore.Qt.UserRole, asset)

        self.referenceThumbListWidget.addItem(new_item)
        self.all_references_ListWidgetItems.append(new_item)
        self.references.append((new_item, asset))

        self.toggle_thumbnail_text()
        self.referenceThumbListWidget.scrollToItem(new_item)
        self.referenceThumbListWidget.clearSelection()
        self.referenceThumbListWidget.setItemSelected(new_item, True)

    def create_moodboard_from_images(self):
        image_list = []
        selected_items = self.referenceThumbListWidget.selectedItems()

        for selected_item in selected_items:
            asset = selected_item.data(QtCore.Qt.UserRole).toPyObject()
            image_list.append(asset.full_path)

        self.Moodboard_Creator(self, image_list)

    def asset_name_dialog(self):

        # Enter asset name dialog
        asset_name_dialog = QtGui.QDialog()
        asset_name_dialog.setWindowTitle("Asset name")
        self.Lib.apply_style(self, asset_name_dialog)
        main_layout = QtGui.QVBoxLayout(asset_name_dialog)

        lbl = QtGui.QLabel("Type a name for the asset and press enter:", asset_name_dialog)
        lineEdit = QtGui.QLineEdit(self.last_asset_name, asset_name_dialog)
        lineEdit.selectAll()
        lineEdit.returnPressed.connect(asset_name_dialog.accept)

        main_layout.addWidget(lbl)
        main_layout.addWidget(lineEdit)


        asset_name_dialog.exec_()
        if asset_name_dialog.result() == 0:
            return None

        # Convert asset name
        asset_name = self.last_asset_name = unicode(lineEdit.text())
        asset_name = self.Lib.normalize_str(self, asset_name)
        asset_name = self.Lib.convert_to_camel_case(self, asset_name)

        return asset_name

    def load_ref_in_kuadro(self):
        os.system("taskkill /im kuadro.exe /f")

        references_to_load = []

        for ref in self.selected_references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            references_to_load.append(asset.full_path)

        references_to_load = " ".join(references_to_load)
        subprocess.Popen([self.cur_path_one_folder_up + "\\_soft\\PureRef.exe",
                          [references_to_load]], close_fds=True)

    def load_ref_in_photoshop(self):

        references_to_load = []

        for ref in self.selected_references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            references_to_load.append(asset.full_path)

        for ref_path in references_to_load:
            subprocess.Popen([self.photoshop_path, ref_path])

    def show_url_image(self):

        URL = str(self.referenceWebLineEdit.text())

        if len(URL) < 5:
            self.Lib.message_box(self, text="Please enter a valid URL")
            return

        eye_icon = QtGui.QPixmap(
            self.cur_path + "\\media\\eye_icon_closed.png")
        eye_icon = QtGui.QIcon(eye_icon)
        self.showUrlImageBtn.setIcon(eye_icon)
        self.showUrlImageBtn.repaint()

        QDialog = QtGui.QDialog()
        QDialog.setWindowTitle("URL Preview")
        QDialog.setMaximumSize(600, 600)
        self.Lib.apply_style(self, QDialog)

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
            self.cur_path + "\\media\\eye_icon.png")
        eye_icon = QtGui.QIcon(eye_icon)
        self.showUrlImageBtn.setIcon(eye_icon)
        self.showUrlImageBtn.repaint()

        QDialog.exec_()

    def change_quality(self):
        if self.keepQualityCheckBox.checkState() == 2:
            self.compression_level = 80
        elif self.keepQualityCheckBox.checkState() == 0:
            self.compression_level = 60

    def hide_reference_options_frame(self):
        if self.referenceOptionsFrame.isHidden():
            self.referenceOptionsFrame.show()
        else:
            self.referenceOptionsFrame.hide()

    def change_reference_thumb_size(self, size):
        '''
        Change reference thumbnail size
        :param size: New size of icon
        '''
        icon_size = QtCore.QSize(128 * size, 128 * size)
        self.referenceThumbListWidget.setIconSize(icon_size)

        # Check if an image is selected, if yes, scroll the view to ensure reference is visible
        selected_reference = self.referenceThumbListWidget.selectedItems()
        if len(selected_reference) > 0:
            self.referenceThumbListWidget.scrollToItem(selected_reference[0], QtGui.QAbstractItemView.EnsureVisible)

    def toggle_thumbnail_text(self):
        '''
        Toggle visibility of names/sequence under reference thumbnails
        '''
        all_references = self.all_references_ListWidgetItems
        for ref in all_references:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()

            if (self.refShowNamesCheckBox.checkState() and self.refShowSequencesCheckBox.checkState()) == 2:
                thumb_text = "{0} ({1})".format(asset.name, asset.sequence)
            elif self.refShowNamesCheckBox.checkState() == 2 and self.refShowSequencesCheckBox.checkState() == 0:
                thumb_text = "{0}".format(asset.name)
            elif self.refShowNamesCheckBox.checkState() == 0 and self.refShowSequencesCheckBox.checkState() == 2:
                thumb_text = "{0}".format(asset.sequence)
            elif self.refShowNamesCheckBox.checkState() == 0 and self.refShowSequencesCheckBox.checkState() == 0:
                thumb_text = ""

            ref.setText(thumb_text)

    def refresh_reference_list(self):
        '''
        Get all assets IDs from database and compare them to the current asset ID loaded to see if there are
        new asset in database or assets which have been removed
        '''
        all_references_id_loaded = self.cursor.execute('''SELECT asset_id FROM assets WHERE project_name=? AND asset_type=?''', (self.selected_project_name, "ref")).fetchall()
        all_references_id_loaded = [int(i[0]) for i in all_references_id_loaded]

        all_references_id = []
        for ref in self.all_references_ListWidgetItems:
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            all_references_id.append(asset.id)

        if all_references_id_loaded > all_references_id:
            self.id_to_load_or_remove = self.Lib.get_diff_between_lists(self, all_references_id, all_references_id_loaded)
            self.load_new_references("add")
        elif all_references_id_loaded < all_references_id:
            self.id_to_load_or_remove = self.Lib.get_diff_between_lists(self, all_references_id, all_references_id_loaded)
            self.load_new_references("remove")

    def load_new_references(self, operation):
        '''
        If operation is add, add new assets from database to reference view.
        If operation is remove, remove assets which are no longer in database from reference view.
        '''
        if operation == "add":
            for id in self.id_to_load_or_remove:
                ref_all_references_assets = self.cursor.execute('''SELECT * FROM assets WHERE project_name=? AND asset_type=? AND asset_id=?''',(self.selected_project_name, "ref", id)).fetchall()

                for i, ref in enumerate(ref_all_references_assets):
                    id = ref[0]
                    project_name = ref[1]
                    sequence_name = ref[2]
                    shot_number = ref[3]
                    name = ref[4]
                    path = ref[5]
                    extension = ref[6]
                    type = ref[7]
                    version = ref[8]
                    tags = ref[9]
                    dependency = ref[10]
                    last_access = ref[11]
                    last_publish = ref[12]
                    creator = ref[13]
                    if id == None: id = ""
                    if project_name == None: project_name = ""
                    if sequence_name == None: sequence_name = ""
                    if shot_number == None: shot_number = ""
                    if name == None: name = ""
                    if path == None: path = ""
                    if extension == None: extension = ""
                    if type == None: type = ""
                    if version == None: version = ""
                    if tags == None: tags = ""
                    if dependency == None: dependency = ""
                    if last_access == None: last_access = ""
                    if last_publish == None: last_publish = ""
                    if creator == None: creator = ""

                    asset = self.Asset(self, id, project_name, sequence_name, shot_number, name, path, extension, type, version,
                                  tags, dependency, last_access, last_publish, creator)

                    self.ref_assets_instances.append(asset)
                    ref_item = QtGui.QListWidgetItem(asset.name)
                    ref_item.setIcon(QtGui.QIcon(asset.full_path.replace(".jpg", "_thumb.jpg")))
                    ref_item.setData(QtCore.Qt.UserRole, asset)

                    if os.path.isfile(asset.full_path):  # Check if image exists to prevent errors
                        self.all_references_ListWidgetItems.append(ref_item)
                        self.referenceThumbListWidget.addItem(ref_item)

        elif operation == "remove":
            for id in self.id_to_load_or_remove:
                for ref in self.all_references_ListWidgetItems:
                    asset = ref.data(QtCore.Qt.UserRole).toPyObject()
                    if asset.id == id:
                        self.all_references_ListWidgetItems.remove(ref)
                        self.referenceThumbListWidget.takeItem(self.referenceThumbListWidget.row(ref))


        self.load_filter_by_tags_list()

    def print_all_assets(self):
        for ref_object in self.all_references_ListWidgetItems:
            asset = ref_object.data(QtCore.Qt.UserRole).toPyObject()
            print(asset)

        print("##################")

        for i in range(self.referenceThumbListWidget.count()):
            ref = self.referenceThumbListWidget.item(i)
            asset = ref.data(QtCore.Qt.UserRole).toPyObject()
            print(asset)

        print("-----------------")

    def clear_filter_by_tags_selection(self):
        self.filterByTagsListWidget.clearSelection()

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
        tags_frequency_tmp = sum(tags_frequency_tmp, [])  # Join all lists into one list
        tags_frequency_tmp = [str(i) for i in tags_frequency_tmp]  # Convert all items from unicode to string
        self.tags_frequency = Counter(tags_frequency_tmp)  # Create a dictionary from list with number of occurences

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
            tag_frequency = self.tags_frequency[tag_name]  # Get the frequency of current tag (ex: 1, 5, 15)
            tag_frequency = self.Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 10, 30)  # Fit frequency in the 10-30 range
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
                if tag_parent == top_item_name:  # Check if the tag_parent of current child is equal to the current top item
                    tag_frequency = self.tags_frequency[tag_name]  # Get the frequency of current tag (ex: 1, 5, 15)
                    tag_frequency = self.Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 10, 30)  # Fit frequency in the 10-30 range
                    font = QtGui.QFont()
                    font.setPointSize(tag_frequency)
                    child_item = QtGui.QTreeWidgetItem(top_item)
                    child_item.setText(0, tag_name)
                    child_item.setFont(0, font)
                    top_item.addChild(child_item)

        # Add all parents tags to the add tags list
        for tag in parent_tags:
            tag_name = tag[2]
            tag_frequency = self.tags_frequency[tag_name]  # Get the frequency of current tag (ex: 1, 5, 15)
            tag_frequency = self.Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 9, 20)  # Fit frequency in the 9-20 range
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
                if tag_parent == top_item_name:  # Check if the tag_parent of current child is equal to the current top item
                    tag_frequency = self.tags_frequency[tag_name]  # Get the frequency of current tag (ex: 1, 5, 15)
                    tag_frequency = self.Lib.fit_range(self, tag_frequency, 0, self.maximum_tag_occurence, 9, 20)  # Fit frequency in the 9-20 range
                    font = QtGui.QFont()
                    font.setPointSize(tag_frequency)
                    child_item = QtGui.QTreeWidgetItem(top_item)
                    child_item.setText(0, tag_name)
                    child_item.setFont(0, font)
                    top_item.addChild(child_item)
