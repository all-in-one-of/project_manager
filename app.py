#!/usr/bin/env python
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
import socket
from thibh import screenshot
import urllib
import sip

from PyQt4 import QtGui, QtCore, Qt
from ui.main_window import Ui_Form


class Main(QtGui.QWidget, Ui_Form):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_Form.__init__(self)

        Form = self.setupUi(self)
        Form.center_window()

        # Create Favicon
        app_icon = QtGui.QIcon()
        app_icon.addFile("H:\\01-NAD\\Session-06\\_pipeline\\PyQt_test\\project_manager\\media\\favicon.png",
                         QtCore.QSize(16, 16))
        Form.setWindowIcon(app_icon)


        # Set the StyleSheet
        css = QtCore.QFile("H:\\01-NAD\\Session-06\\_pipeline\\PyQt_test\\project_manager\\media\\style.css")
        css.open(QtCore.QIODevice.ReadOnly)
        if css.isOpen():
            Form.setStyleSheet(QtCore.QVariant(css.readAll()).toString())
        css.close()

        # Override StyleSheet
        self.publishBtn.setStyleSheet("background-color: #77D482;")
        self.loadBtn.setStyleSheet(
            "QPushButton {background-color: #77B0D4;} QPushButton:hover {background-color: #1BCAA7;}")

        # Database Setup
        self.db_path = "H:\\01-NAD\\Session-06\\_pipeline\\_utilities\\_database\\db.sqlite"
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()

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



        # Global Variables
        self.screenshot_dir = "H:\\01-NAD\\Session-06\\_pipeline\\_utilities\\_database\\screenshots\\"
        self.username = socket.gethostname()

        pixmap = QtGui.QPixmap(self.screenshot_dir + "default\\no_img.png").scaled(1000, 200, QtCore.Qt.KeepAspectRatio,
                                                                                   QtCore.Qt.SmoothTransformation)
        self.assetImg.setPixmap(pixmap)


        # Connect the filter textboxes
        self.seqFilter.textChanged.connect(partial(self.filterList_textChanged, "sequence"))
        self.assetFilter.textChanged.connect(partial(self.filterList_textChanged, "asset"))

        # Connect the lists
        self.projectList.itemClicked.connect(self.projectList_Clicked)
        self.departmentList.itemClicked.connect(self.departmentList_Clicked)
        self.seqList.itemClicked.connect(self.seqList_Clicked)
        self.assetList.itemClicked.connect(self.assetList_Clicked)

        self.departmentCreationList.itemClicked.connect(self.departmentCreationList_Clicked)


        # Connect the buttons
        self.seqFilterClearBtn.clicked.connect(partial(self.clear_filter, "seq"))
        self.assetFilterClearBtn.clicked.connect(partial(self.clear_filter, "asset"))
        self.loadBtn.clicked.connect(self.load_asset)
        self.openInExplorerBtn.clicked.connect(self.open_in_explorer)
        self.addCommentBtn.clicked.connect(self.add_comment)
        self.updateThumbBtn.clicked.connect(self.update_thumb)

        self.savePrefBtn.clicked.connect(self.save_prefs)

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
        self.selected_project = str(self.projectList.selectedItems()[0].text())
        self.selected_project_id = str(self.cursor.execute('''SELECT project_id FROM projects WHERE project_name=?''',
                                                           (self.selected_project,)).fetchone()[0])

        # Query the departments associated with the project
        self.departments = (self.cursor.execute('''SELECT DISTINCT asset_type FROM assets WHERE project_id=?''',
                                                (self.selected_project_id,))).fetchall()

        # Populate the departments list
        self.departmentList.clear()
        self.departmentList.addItem("All")
        [self.departmentList.addItem(department[0]) for department in self.departments]

        # Query the sequences associated with the project
        self.sequences = (self.cursor.execute('''SELECT DISTINCT sequence_name FROM sequences WHERE project_id=?''',
                                              (self.selected_project_id,))).fetchall()

        # Populate the sequences lists
        self.seqList.clear()
        self.seqList.addItem("All")
        self.seqCreationList.clear()
        self.seqCreationList.addItem("All")
        [self.seqList.addItem(sequence[0]) for sequence in self.sequences]
        [self.seqCreationList.addItem(sequence[0]) for sequence in self.sequences]


        # Populate the assets list
        self.all_assets = self.cursor.execute('''SELECT * FROM assets WHERE project_id=?''',
                                              (self.selected_project_id,))
        self.add_assets_to_asset_list(self.all_assets)

    def departmentList_Clicked(self):
        self.selected_department = str(self.departmentList.selectedItems()[0].text())

        if len(self.seqList.selectedItems()) == 0:
            if self.selected_department == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_id=?''', (self.selected_project_id,))
            else:
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_id=? AND asset_type=?''',
                                             (self.selected_project_id, self.selected_department,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)

        else:

            if self.selected_department == "All" and self.selected_sequence == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_id=?''', (self.selected_project_id,))
            elif self.selected_department == "All" and self.selected_sequence != "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_id=? AND sequence_id=?''',
                                             (self.selected_project_id, self.selected_sequence_id))
            elif self.selected_department != "All" and self.selected_sequence == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_id=? AND asset_type=?''',
                                             (self.selected_project_id, self.selected_department))
            else:
                self.selected_sequence_id = str(
                    self.cursor.execute('''SELECT sequence_id FROM sequences WHERE sequence_name=?''',
                                        (self.selected_sequence,)).fetchone()[0])
                assets = self.cursor.execute(
                    '''SELECT * FROM assets WHERE project_id=? AND sequence_id=? AND asset_type=?''',
                    (self.selected_project_id, self.selected_sequence_id, self.selected_department,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)

    def seqList_Clicked(self):
        self.selected_sequence = str(self.seqList.selectedItems()[0].text())
        if not self.selected_sequence == "All":
            self.selected_sequence_id = str(
                self.cursor.execute('''SELECT sequence_id FROM sequences WHERE sequence_name=?''',
                                    (self.selected_sequence,)).fetchone()[0])

        if len(self.departmentList.selectedItems()) == 0:
            if self.selected_sequence == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_id=?''', (self.selected_project_id,))
            else:
                self.selected_sequence_id = str(
                    self.cursor.execute('''SELECT sequence_id FROM sequences WHERE sequence_name=?''',
                                        (self.selected_sequence,)).fetchone()[0])
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_id=? AND sequence_id=?''',
                                             (self.selected_project_id, self.selected_sequence_id,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)
        else:
            if self.selected_department == "All" and self.selected_sequence == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_id=?''', (self.selected_project_id,))
            elif self.selected_department == "All" and self.selected_sequence != "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_id=? AND sequence_id=?''',
                                             (self.selected_project_id, self.selected_sequence_id))
            elif self.selected_department != "All" and self.selected_sequence == "All":
                assets = self.cursor.execute('''SELECT * FROM assets WHERE project_id=? AND asset_type=?''',
                                             (self.selected_project_id, self.selected_department))
            else:
                self.selected_sequence_id = str(
                    self.cursor.execute('''SELECT sequence_id FROM sequences WHERE sequence_name=?''',
                                        (self.selected_sequence,)).fetchone()[0])
                assets = self.cursor.execute(
                    '''SELECT * FROM assets WHERE project_id=? AND sequence_id=? AND asset_type=?''',
                    (self.selected_project_id, self.selected_sequence_id, self.selected_department,))

            # Add assets to asset list
            self.add_assets_to_asset_list(assets)

    def assetList_Clicked(self):

        self.selected_asset_type = str(self.assetList.selectedItems()[0].text()).split("_")[0]
        self.selected_asset_name = str(self.assetList.selectedItems()[0].text()).split("_")[1]
        self.selected_asset_version = str(self.assetList.selectedItems()[0].text()).split("_")[2]
        self.selected_asset_path = self.cursor.execute(
            '''SELECT asset_path FROM assets WHERE project_id=? AND asset_type=? AND asset_name=? AND asset_version=?''',
            (self.selected_project_id, self.selected_asset_type, self.selected_asset_name,
             self.selected_asset_version)).fetchone()[0]

        if self.selected_asset_path.endswith(".jpg") or self.selected_asset_path.endswith(".png"):

            self.fileTypeLbl.setText("Image (" + os.path.splitext(self.selected_asset_path)[-1] + ")")

            for i in reversed(range(self.actionFrameLayout.count())):  # Delete all items from layout
                self.actionFrameLayout.itemAt(i).widget().close()

            # Create action interface
            self.loadInKuadroBtn = QtGui.QPushButton(self.actionFrame)
            self.actionFrameLayout.addWidget(self.loadInKuadroBtn)
            self.loadInKuadroBtn.setText("Load in Kuadro")
            self.loadInKuadroBtn.clicked.connect(partial(self.load_asset, "Kuadro"))

        elif self.selected_asset_path.endswith(".mb") or self.selected_asset_path.endswith(".ma"):
            self.fileTypeLbl.setText("Maya (" + os.path.splitext(self.selected_asset_path)[-1] + ")")

        elif self.selected_asset_path.endswith(".obj"):
            self.fileTypeLbl.setText("Geometry (" + os.path.splitext(self.selected_asset_path)[-1] + ")")


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
            '''SELECT asset_comment FROM assets WHERE project_id=? AND asset_type=? AND asset_name=? AND asset_version=?''',
            (self.selected_project_id, self.selected_asset_type, self.selected_asset_name,
             self.selected_asset_version)).fetchone()[0]
        if asset_comment:
            self.commentTxt.setText(asset_comment)

    def departmentCreationList_Clicked(self):
        '''Filter the softwareCreationList based on the type of department selected.
        ex. if "Concept" is selected, only show Photoshop.
        '''

        selected_department = str(self.departmentCreationList.selectedItems()[0].text())

        if selected_department == "Concept":
            self.softwareCreationList.setItemHidden(self.seqList.item(i), False)
            self.softwareCreationList.setItemHidden("Houdini", False)
        elif selected_department == "Modeling":
            pass
        elif selected_department == "Layout":
            pass

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

    def load_asset(self, action):

        if action == "Kuadro":

            if not QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
                os.system("taskkill /im kuadro.exe /f")
            subprocess.Popen(
                ["H:\\01-NAD\\Session-06\\_pipeline\\_utilities\\_soft\\kuadro.exe", self.selected_asset_path])
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

    def add_assets_to_asset_list(self, assets_list):
        """
        Add assets from assets_list to self.assetList

        """

        self.assetList.clear()
        for asset in assets_list:
            self.assetList.addItem(asset[5] + "_" + asset[3] + "_" + str(asset[6]))

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
        screenshot.take(self.screenshot_dir, self.asset_name)

        pixmap = QtGui.QPixmap(self.screenshot_dir + self.asset_name + ".jpg").scaled(1000, 200,
                                                                                      QtCore.Qt.KeepAspectRatio,
                                                                                      QtCore.Qt.SmoothTransformation)
        self.assetImg.setPixmap(pixmap)


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
                              "H:\\01-NAD\\Session-06\\_pipeline\\_utilities\\software_scripts\\blender\\blender_obj_load.py",
                              self.asset])
        elif software == "c4d":
            subprocess.Popen(["H:\\Programmes\\Cinema 4D R16\\CINEMA 4D.exe", self.asset])



























        # Main Loop


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
