#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
import subprocess
import os
import shutil
from PIL import Image
import urllib
from lib.module import Lib

class ReferenceTab(object):

    def __init__(self):
        self.referenceThumbListWidget.itemSelectionChanged.connect(self.referenceThumbListWidget_itemSelectionChanged)
        self.referenceThumbListWidget.itemDoubleClicked.connect(self.rename_reference_layout)
        self.filterByTagsListWidget.itemSelectionChanged.connect(self.filter_reference_by_tags)
        self.createReferenceFromWebBtn.clicked.connect(self.create_reference_from_web)
        self.createReferencesFromFilesBtn.clicked.connect(self.create_reference_from_files)
        self.removeRefsBtn.clicked.connect(self.remove_selected_references)
        self.openRefInKuadroBtn.clicked.connect(self.load_ref_in_kuadro)
        self.openRefInPhotoshopBtn.clicked.connect(self.load_ref_in_photoshop)
        self.addTagsBtn.clicked.connect(self.add_tags_to_selected_references)
        self.allTagsListWidget.doubleClicked.connect(self.add_tags_to_selected_references)
        self.removeTagsBtn.clicked.connect(self.remove_tags_from_selected_references)
        self.existingTagsListWidget.doubleClicked.connect(self.remove_tags_from_selected_references)
        self.referenceThumbSizeSlider.sliderMoved.connect(self.change_reference_thumb_size)
        self.changeRefSeqShotBtn.clicked.connect(self.change_seq_shot_layout)
        self.showUrlImageBtn.clicked.connect(self.show_url_image)

    def add_tags_to_selected_references(self):

        # Retrieve selected tags to add
        selected_tags = self.allTagsListWidget.selectedItems()
        selected_tags = [str(i.text()) for i in selected_tags]

        # Retrieve selected QListWidgetItem
        selected_references = self.referenceThumbListWidget.selectedItems()
        for ref in selected_references:
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()  # Get data associated with QListWidgetItem
            ref_sequence_name = ref_data[0]
            ref_shot_number = ref_data[1]
            ref_name = ref_data[2]
            ref_path = ref_data[3]
            ref_version = ref_data[4]
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

    def create_reference_from_web(self):


        asset_name = unicode(self.referenceNameLineEdit.text())
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


        # Fetch image from web and compress it
        URL = str(self.referenceWebLineEdit.text())
        if len(URL) > 0:
            urllib.urlretrieve(URL, self.selected_project_path + asset_filename)
            downloaded_img = Image.open(self.selected_project_path + asset_filename)
            image_width = downloaded_img.size[0]
            if image_width > 1920: image_width = 1920
            Lib.compress_image(self, self.selected_project_path + asset_filename, image_width, 75)


        # Add reference to database
        self.cursor.execute(
            '''INSERT INTO assets(project_name, sequence_name, shot_number, asset_name, asset_path, asset_type, asset_version, creator) VALUES(?,?,?,?,?,?,?,?)''',
            (self.selected_project_name, selected_sequence, selected_shot, asset_name, asset_filename, "ref",
             last_version,
             self.username))

        self.db.commit()

        self.add_log_entry("{0} added a reference from web".format(self.members[self.username]))


        self.load_reference_thumbnails()

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
            Lib.compress_image(self, self.selected_project_path + path, image_width, 75)


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

    def remove_selected_references(self):

        # Retrieve selected references
        selected_references = self.referenceThumbListWidget.selectedItems()

        # Delete references on database and on disk
        number_of_refs_removed = 0
        for ref in selected_references:
            number_of_refs_removed += 1
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()
            ref_sequence = ref_data[0]
            ref_shot_number = ref_data[1]
            ref_path = ref_data[3]
            ref_name = ref_data[2]
            ref_version = ref_data[4]

            os.remove(self.selected_project_path + str(ref_path))
            self.cursor.execute(
                '''DELETE FROM assets WHERE asset_name=? AND asset_version=? AND asset_type="ref" AND sequence_name=? AND shot_number=?''',
                (ref_name, ref_version, ref_sequence, ref_shot_number,))

        if number_of_refs_removed > 1:
            self.add_log_entry(
                "{0} deleted {1} reference(s)".format(self.members[self.username], number_of_refs_removed))
        else:
            self.add_log_entry("{0} deleted {1} reference".format(self.members[self.username], number_of_refs_removed))

        self.db.commit()
        self.load_reference_thumbnails()

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

    def load_reference_thumbnails(self):

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
                '''SELECT sequence_name, shot_number, asset_name, asset_path, asset_version, asset_tags FROM assets''').fetchall()
        elif selected_sequence == "All" and selected_shot != "None":
            references_list = self.cursor.execute(
                '''SELECT sequence_name, shot_number, asset_name, asset_path, asset_version, asset_tags FROM assets WHERE shot_number=?''',
                (selected_shot,)).fetchall()
        elif selected_sequence != "All" and selected_shot == "None":
            references_list = self.cursor.execute(
                '''SELECT sequence_name, shot_number, asset_name, asset_path, asset_version, asset_tags FROM assets WHERE sequence_name=?''',
                (selected_sequence,)).fetchall()
        else:
            references_list = self.cursor.execute(
                '''SELECT sequence_name, shot_number, asset_name, asset_path, asset_version, asset_tags FROM assets WHERE sequence_name=? AND shot_number=?''',
                (selected_sequence, selected_shot,)).fetchall()

        # references_list = (u'mus', u'xxxx', u'musee', u'\\assets\\ref\\nat_mus_xxxx_ref_musee_01.jpg', u'01', u'lighting,tree,architecture')

        all_tags = []

        # Load thumbnails
        if len(references_list) > 0:

            for i, reference in enumerate(references_list):
                reference_path = self.selected_project_path + reference[3]
                reference_name = reference[2] + "_" + reference[4]
                reference_tags = reference[5]

                all_tags.append(reference_tags)

                reference_list_item = QtGui.QListWidgetItem()
                reference_list_item.setIcon(QtGui.QIcon(reference_path))
                reference_list_item.setData(QtCore.Qt.UserRole, reference)

                self.referenceThumbListWidget.addItem(reference_list_item)


        all_tags = filter(None, all_tags)
        all_tags = ",".join(all_tags)
        all_tags = all_tags.split(",")
        all_tags = sorted(list(set(all_tags)))
        self.filterByTagsListWidget.clear()
        [self.filterByTagsListWidget.addItem(tag) for tag in all_tags]

    def reload_filter_by_tags_list(self):

        all_references = []
        for i in xrange(self.referenceThumbListWidget.count()):
            all_references.append(self.referenceThumbListWidget.item(i))

        all_tags = self.get_all_tags_from_loaded_references(all_references)

        self.filterByTagsListWidget.clear()
        [self.filterByTagsListWidget.addItem(tag) for tag in all_tags]

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
            ref_tags = ref_data[5]
            all_tags.append(ref_tags)
            all_tags = filter(None, all_tags)
            all_tags = ",".join(
                all_tags)  # convert all_tags = ["", "architecture", "architecture,lighting"] to all_tags = "architecture,architecture,lighting"
            all_tags = all_tags.split(
                ",")  # convert all_tags = "architecture,architecture,lighting" to ["architecture", "architecture", "lighting"]
            all_tags = sorted(list(set(all_tags)))  # sort list and remove duplicates

        return all_tags

    def change_reference_thumb_size(self):

        slider_size = self.referenceThumbSizeSlider.value()
        icon_size = QtCore.QSize(slider_size, slider_size)
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
            return

        # Loop over all references and set them to hidden if any selected tag can't be found in reference's tags
        for ref in all_references:
            ref_data = ref.data(QtCore.Qt.UserRole).toPyObject()
            ref_tags = ref_data[5]
            if ref_tags == None:
                ref.setHidden(True)
                continue

            if "," in ref_tags:
                ref_tags = ref_tags.split(",")  # Convert string to list (ex: "character, lighting" to ["character", "statue"]

            if set(ref_tags).isdisjoint(selected_tags):
                ref.setHidden(True)
            else:
                ref.setHidden(False)

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
            ref_path = ref_data[3]
            references_to_load.append(self.selected_project_path + ref_path)

        for ref_path in references_to_load:
            subprocess.Popen([self.photoshop_path, ref_path])

    def rename_reference_layout(self):
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

        self.load_reference_thumbnails()

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
            ref_shot_number = ref_data[1]
            ref_name = ref_data[2]
            ref_path = ref_data[3]
            ref_version = ref_data[4]
            ref_tags = ref_data[5]

            new_path = ref_path.replace("_" + ref_sequence_name + "_" + str(ref_shot_number), "_" + selected_sequence + "_" + selected_shot)

            new_version = ref_version
            while os.path.isfile(self.selected_project_path + new_path):
                fileName, fileExtension = os.path.splitext(new_path)
                current_version = int(fileName.split("_")[-1])
                new_version = str(current_version + 1).zfill(2)
                new_path = new_path.replace("_" + str(current_version).zfill(2), "_" + new_version)


            os.rename(self.selected_project_path + ref_path, self.selected_project_path + new_path)

            self.cursor.execute(
                    '''UPDATE assets SET sequence_name=?, shot_number=?, asset_path=?, asset_version=? WHERE sequence_name=? AND shot_number=? AND asset_name=? AND asset_version=?''',
                    (selected_sequence, selected_shot, new_path, new_version, ref_sequence_name, ref_shot_number, ref_name, ref_version,))

            # Update reference QListWidgetItem data
            data = (selected_sequence, selected_shot, ref_name, ref_path, ref_version, ref_tags)
            ref.setData(QtCore.Qt.UserRole, data)

        self.db.commit()
        self.load_reference_thumbnails()

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

        eye_icon = QtGui.QPixmap("H:\\01-NAD\\_pipeline\\_utilities\\_asset_manager\\media\\eye_icon_closed.png")
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

        eye_icon = QtGui.QPixmap("H:\\01-NAD\\_pipeline\\_utilities\\_asset_manager\\media\\eye_icon.png")
        eye_icon = QtGui.QIcon(eye_icon)
        self.showUrlImageBtn.setIcon(eye_icon)
        self.showUrlImageBtn.repaint()

        QDialog.exec_()










