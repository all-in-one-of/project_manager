#  ___    ___    ___  ___ ___  ____    __ __  ___  __   __
# (   )  (   )  / _ \(_  v  _)(   _)  (_ v _)/ _ \(  | |  )
#  | |    | |__( (_) ) \   /   | E_     \ / ( (_) )| |_| |
# (___)  (_____)\___/   \_/   (____)   (___) \___/ (_____)

# THIBAULT



# SCRIPT BY THE ONE AND ONLY RODRIGUOOOOOOOOOOOOOOOOOOOOOOOO





import mari, os, hashlib
import PythonQt.QtGui as gui
import PythonQt.QtCore as core
import subprocess


class MariExportManager(gui.QDialog):
    def __init__(self):
        super(MariExportManager, self).__init__()
        self.ui_n_stuff()
        self.show()


    def ui_n_stuff(self):
        # Variables necessaires
        self.geo_list = mari.geo.list()
        obj = mari.geo.current()
        obj_name = str(obj.name())
        obj_name = obj_name.split("_")[0]

        self.path_export = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\assets\\tex\\" + obj_name + "\\"

        self.nomenclature = "$CHANNEL.png"

        # Construire la fenetre et le layout de base
        self.setWindowTitle("Export Manager")
        main_layout = gui.QHBoxLayout(self)

        close_layout = gui.QVBoxLayout(self)


        # Layout pour section du top
        top_group = gui.QGroupBox()
        top_group_layout = gui.QVBoxLayout()
        top_group.setLayout(top_group_layout)

        # Layout pour section du bot
        bottom_group = gui.QGroupBox()
        bottom_group_layout = gui.QVBoxLayout()
        bottom_group.setLayout(bottom_group_layout)


        # Ajouter Group Widget au main Layout
        main_layout.addWidget(top_group)
        main_layout.addWidget(bottom_group)


        # Channel Header, Label et Widgets
        channel_label = gui.QLabel("<strong>Channels To Export</strong>")
        channel_layout = gui.QVBoxLayout()
        channel_header_layout = gui.QHBoxLayout()

        # Layout Channel
        channel_header_layout.addWidget(channel_label)
        channel_header_layout.addStretch()
        channel_layout.addLayout(channel_header_layout)

        top_group_layout.addLayout(channel_layout)

        # -----------------------------BUTTON & WIDGETS---------------------------------

        # Repopulate the earth
        chan_dict = {}
        self.checkbox_dict = {}
        checkbox_liste = []

        checkbox_group = gui.QGroupBox()
        checkbox_group_layout = gui.QVBoxLayout()
        checkbox_group.setLayout(checkbox_group_layout)
        top_group_layout.addWidget(checkbox_group)

        # Label & Checkbox builder
        geo_dict = {}
        for geo in self.geo_list:  # Iterating over each object (geo = Cube, Sphere, Torus)

            obj_label = gui.QLabel(str(geo.name()))
            checkbox_group_layout.addWidget(obj_label)

            for channel in geo.channelList():  # Iterating over each channel (channel = Diffuse, Spec, Bump...)
                checkbox = gui.QCheckBox(str(channel.name()))
                checkbox_group_layout.addWidget(checkbox)
                self.checkbox_dict[checkbox] = channel


        # Path Layout
        path_layout = gui.QHBoxLayout()

        # Ajouter un label, bouton et text field pour le path
        path_label = gui.QLabel('Path:')  # Label avant le lineEdit
        path_line_edit = gui.QLineEdit(self.path_export)  # Texte sur la ligne
        path_line_edit.setDisabled(1)
        path_line_edit.setReadOnly(1)  # Read Only mode, can select can't change
        path_pixmap = gui.QPixmap(mari.resources.path(mari.resources.ICONS) + '/ExportImages.png')
        icon = gui.QIcon(path_pixmap)
        path_button = gui.QPushButton(icon, "")

        path_layout.addWidget(path_label)
        path_layout.addWidget(path_line_edit)
        path_layout.addWidget(path_button)

        bottom_group_layout.addLayout(path_layout)



        # Select All & Select None Button
        sel_all = gui.QPushButton("Select All")
        sel_none = gui.QPushButton("Select None")
        top_group_layout.addWidget(sel_all)
        top_group_layout.addWidget(sel_none)

        sel_all.connect("clicked()", self.select_all)  # Connect button to fonction
        sel_none.connect("clicked()", self.select_none)  # Connect button to fonction


        # Export All & Export Button
        export_all = gui.QPushButton("Export All")
        export_selected = gui.QPushButton("Export Selected")
        bottom_group_layout.addWidget(export_all)
        bottom_group_layout.addWidget(export_selected)

        export_all.connect("clicked()", self.export_all_fc)  # Connect button to fonction
        export_selected.connect("clicked()", self.export_selected_fc)  # Connect button to fonction

        # Close button
        close_btn = gui.QPushButton("Close")
        close_layout.addWidget(close_btn)
        main_layout.addLayout(close_layout, stretch=1)

        close_btn.connect("clicked()", self.reject)  # Connect button to fonction


    def select_all(self):
        # Fonction pour bouton Select all --- All Checkbox == 1
        for key, value in self.checkbox_dict.items():
            key.setChecked(1)  # 1 = Checked


    def select_none(self):
        # Fonction pour bouton Select none --- All Checkbox == 0
        for key, value in self.checkbox_dict.items():
            key.setChecked(0)  # 0 = Not Checked


    def export_all_fc(self):
        # Export All maps peu importe les Checkbox
        print "EXPORTING THESE MAPS(ALL)"
        for obj in self.geo_list:
            mari.geo.setCurrent(obj)
            channelList = obj.channelList()
            for chan in channelList:
                print chan
                chan.exportImagesFlattened(self.path_export + self.nomenclature)
                proc = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.13/bin/icp.exe", self.path_export + self.nomenclature.replace("$CHANNEL", chan.name()), self.path_export + self.nomenclature.replace(".png", ".rat").replace("$CHANNEL", chan.name())])
                proc.wait()
                proc = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.13/bin/icp.exe", self.path_export + self.nomenclature.replace("$CHANNEL", chan.name()), self.path_export + self.nomenclature.replace(".png", ".jpg").replace("$CHANNEL", chan.name())])
                proc.wait()
                os.remove(self.path_export + self.nomenclature.replace("$CHANNEL", chan.name()))

        canvas = mari.canvases.current()
        camera_front = mari.actions.find('/Mari/Canvas/Camera/Camera Front')
        camera_side = mari.actions.find('/Mari/Canvas/Camera/Camera Left')
        camera_top = mari.actions.find('/Mari/Canvas/Camera/Camera Top')
        camera_list = [camera_front, camera_side, camera_top]
        print("2")
        for cameras in camera_list:
            # Se promener a travers les cameras
            cameras.trigger()
            # Refresh le canvas
            canvas.repaint()
            # Frame All
            frame_all = mari.actions.find('/Mari/Canvas/Camera/View All')
            frame_all.trigger()
            # Disable le HUD
            """Ne semble pas fonctionner avec le captureImage"""
            hud_enabled = canvas.getDisplayProperty("HUD/RenderHud")
            if hud_enabled == 1:
                canvas.setDisplayProperty("HUD/RenderHud", False)
            # Prendre Screenshot
            snapAction = mari.actions.find('/Mari/Canvas/Take Screenshot')
            snapAction.trigger()
            # Reenable le HUD
            canvas.setDisplayProperty("HUD/RenderHud", True)

        print "Exporting finished."

    def export_selected_fc(self):
        # Export SELECTED maps selon les Checkbox
        print "EXPORTING THESE MAPS(SELECTED)"
        for key in self.checkbox_dict.keys():
            if key.checkState() == 2:
                chan = self.checkbox_dict[key]
                print chan
                chan.exportImagesFlattened(self.path_export + self.nomenclature)
                proc = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.13/bin/icp.exe", self.path_export + self.nomenclature.replace("$CHANNEL", chan.name()), self.path_export + self.nomenclature.replace(".png", ".rat").replace("$CHANNEL", chan.name())])
                proc.wait()
                proc = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.13/bin/icp.exe", self.path_export + self.nomenclature.replace("$CHANNEL", chan.name()), self.path_export + self.nomenclature.replace(".png", ".jpg").replace("$CHANNEL", chan.name())])
                proc.wait()
                os.remove(self.path_export + self.nomenclature.replace("$CHANNEL", chan.name()))

        canvas = mari.canvases.current()
        camera_front = mari.actions.find('/Mari/Canvas/Camera/Camera Front')
        camera_side = mari.actions.find('/Mari/Canvas/Camera/Camera Left')
        camera_top = mari.actions.find('/Mari/Canvas/Camera/Camera Top')
        camera_list = [camera_front, camera_side, camera_top]
        print("2")
        for cameras in camera_list:
            # Se promener a travers les cameras
            cameras.trigger()
            # Refresh le canvas
            canvas.repaint()
            # Frame All
            frame_all = mari.actions.find('/Mari/Canvas/Camera/View All')
            frame_all.trigger()
            # Disable le HUD
            """Ne semble pas fonctionner avec le captureImage"""
            hud_enabled = canvas.getDisplayProperty("HUD/RenderHud")
            if hud_enabled == 1:
                canvas.setDisplayProperty("HUD/RenderHud", False)
            # Prendre Screenshot
            snapAction = mari.actions.find('/Mari/Canvas/Take Screenshot')
            snapAction.trigger()
            # Reenable le HUD
            canvas.setDisplayProperty("HUD/RenderHud", True)

        print "Exporting finished."

            # object = "Cube"
            # channel = "Diffuse"
            # geo_dict = {"Cube":objet cube}
