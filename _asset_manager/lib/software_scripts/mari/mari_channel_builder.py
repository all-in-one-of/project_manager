#!/usr/bin/env python
# coding=utf-8

# coding=utf-8

import mari, os, hashlib
import PythonQt.QtGui as gui
import PythonQt.QtCore as core
import sys


class MariChannelBuilder(gui.QDialog):
    def __init__(self):
        super(MariChannelBuilder, self).__init__()
        self.ui_variables()
        self.setMaximumSize(100, 100)
        self.show()

    def ui_variables(self):
        # -----------------------------Boring stuff (AKA VARIABLES ET FONCTIONS)-----------------
        self.geo_list = mari.geo.list()
        self.sel_obj = mari.geo.current()
        self.chk_dict = {}
        self.chk_liste = []
        self.maps_combobox_list = []
        self.build_all_checkbox_value = 0
        self.build_selected_checkbox_value = 0
        diff_chk = gui.QCheckBox("Diffuse", self)
        bump_chk = gui.QCheckBox("Bump", self)
        disp_chk = gui.QCheckBox("Displacement", self)
        spec_chk = gui.QCheckBox("Specular", self)
        norm_chk = gui.QCheckBox("Normal", self)
        roug_chk = gui.QCheckBox("Roughness", self)
        refl_chk = gui.QCheckBox("Reflection", self)
        refr_chk = gui.QCheckBox("Refraction", self)
        fres_chk = gui.QCheckBox("Fresnel", self)
        mask_chk = gui.QCheckBox("Mask", self)
        self.chk_liste = [diff_chk, bump_chk, disp_chk, spec_chk, norm_chk, roug_chk, refl_chk, refr_chk, fres_chk,
                          mask_chk]
        self.chk_liste_name = ["diff_chk", "bump_chk", "disp_chk", "spec_chk", "norm_chk", "roug_chk", "refl_chk",
                               "refr_chk", "fres_chk", "mask_chk"]



        # -----------------------------Base Layout----------------------------------------------
        self.setWindowTitle("Channel Builder")
        main_layout = gui.QHBoxLayout(self)

        # Map Checkbox Layout
        left_group = gui.QGroupBox(self)
        self.channel_layout = gui.QGridLayout()
        left_group.setLayout(self.channel_layout)
        self.lbl = gui.QLabel("<b>Channels To Build</b>")
        self.channel_layout.addWidget(self.lbl)
        self.channel_layout.setColumnMinimumWidth(1, 5)

        # Middle Layout
        self.mid_group = gui.QGroupBox(self)
        self.mid_group_layout = gui.QVBoxLayout(self)
        self.mid_group.setLayout(self.mid_group_layout)

        # Add Layout to main
        main_layout.addWidget(left_group)
        main_layout.addWidget(self.mid_group)



        # -----------------------------Buttons, Checkbox, and stuff.... you know....------------
        # Add Checkbox pour Map et Set to layout
        temp = 0
        for checkbox in self.chk_liste:
            self.size_for_map = gui.QComboBox()
            self.size_for_map.insertItem(0, "1024", )
            self.size_for_map.insertItem(1, "2048", )
            self.size_for_map.insertItem(2, "4096", )
            self.size_for_map.insertItem(3, "8192", )
            # self.size_for_map.insertItem(4, "16384", )    #PEUT-ETRE DISPONIBLE UN JOUR QUI SAIT ;_;
            self.channel_layout.addWidget(self.chk_liste[temp])
            self.channel_layout.addWidget(self.size_for_map)
            temp_name = self.chk_liste_name[temp]
            temp = temp + 1
            self.chk_dict[temp_name] = self.size_for_map
            self.maps_combobox_list.append(self.size_for_map)

        # Select All & Select None
        sel_all = gui.QPushButton("Select All")
        sel_none = gui.QPushButton("Select None")
        self.channel_layout.addWidget(sel_all)
        self.channel_layout.addWidget(sel_none)

        sel_all.connect("clicked()", self.select_all)
        sel_none.connect("clicked()", self.select_none)

        # Build Selected
        build_selected = gui.QPushButton("Build Selected")  # Bouton Build Selected
        self.build_selected_same_size_chkbox = gui.QCheckBox("Use same size for all maps?")
        self.build_selected_size_combobox = gui.QComboBox()
        self.build_selected_groupbox = gui.QGroupBox(self)  # Creation du cadre
        self.build_selected_layout = gui.QGridLayout(self)  # Layout du cadre
        self.build_selected_groupbox.setLayout(self.build_selected_layout)  # Attribuer le layout au cadre

        self.build_selected_layout.addWidget(build_selected)  # Ajouter bouton au layout

        self.build_selected_layout.addWidget(self.build_selected_same_size_chkbox)  # Ajouter checkbox au layout

        self.build_selected_layout.addWidget(self.build_selected_size_combobox)  # AJouter combobox au layout
        self.build_selected_size_combobox.insertItem(0, "1024", )  # Ajouter resolution 1024
        self.build_selected_size_combobox.insertItem(1, "2048", )  # Ajouter resolution 2048
        self.build_selected_size_combobox.insertItem(2, "4096", )  # Ajouter resolution 4096
        self.build_selected_size_combobox.insertItem(3, "8192", )  # Ajouter resolution 8192
        self.build_selected_size_combobox.setDisabled(1)

        self.mid_group_layout.addWidget(self.build_selected_groupbox)  # Ajouter le cadre au layout du milieu

        build_selected.connect("clicked()", self.build_selected_fc)
        self.build_selected_same_size_chkbox.connect("clicked()", self.lock_build_selected_combobox)


        # Build All
        build_all = gui.QPushButton("Build All")  # Bouton Build All
        self.build_all_same_size_chkbox = gui.QCheckBox("Use same size for all maps?")
        self.build_all_size_combobox = gui.QComboBox()
        self.build_all_groupbox = gui.QGroupBox(self)  # Création du cadre
        self.build_all_layout = gui.QGridLayout(self)  # Layout du cadre
        self.build_all_groupbox.setLayout(self.build_all_layout)  # Attribuer le layout au cadre

        self.build_all_layout.addWidget(build_all)  # Ajouter le bouton au layout

        self.build_all_layout.addWidget(self.build_all_same_size_chkbox)  # Ajouter le checkbox au layout

        self.build_all_layout.addWidget(self.build_all_size_combobox)  # Ajouter la combobox au layout
        self.build_all_size_combobox.insertItem(0, "1024", )  # Ajouter resolution 1024
        self.build_all_size_combobox.insertItem(1, "2048", )  # Ajouter resolution 2048
        self.build_all_size_combobox.insertItem(2, "4096", )  # Ajouter resolution 4096
        self.build_all_size_combobox.insertItem(3, "8192", )  # Ajouter resolution 8192
        self.build_all_size_combobox.setDisabled(1)

        self.mid_group_layout.addWidget(self.build_all_groupbox)  # Ajouter le cadre au Layout du milieu

        build_all.connect("clicked()", self.build_all_fc)  # Connect bouton a fonction
        self.build_all_same_size_chkbox.connect("clicked()", self.lock_build_all_combobox)





    def lock_build_all_combobox(self):
        """Fonction pour barrer la ComboBox(Build All) quand non necessaire"""
        if self.build_all_size_combobox.isEnabled() == 0:
            self.build_all_size_combobox.setEnabled(1)
        elif self.build_all_size_combobox.isEnabled() == 1:
            self.build_all_size_combobox.setDisabled(1)

    def lock_build_selected_combobox(self):
        """Fonction pour barrer la ComboBox(Build Selected) quand non necessaire"""
        if self.build_selected_size_combobox.isEnabled() == 0:
            self.build_selected_size_combobox.setEnabled(1)
        elif self.build_selected_size_combobox.isEnabled() == 1:
            self.build_selected_size_combobox.setDisabled(1)

    def select_all(self):
        '''Fonction pour selectionner tout'''
        for checkbox in self.chk_liste:
            checkbox.setChecked(1)

    def select_none(self):
        '''Fonction pour déselectionner tout'''
        for checkbox in self.chk_liste:
            checkbox.setChecked(0)

    def build_all_fc(self):
        """Fonction pour créer l'entierete des maps"""
        if self.build_all_same_size_chkbox.checkState() == 0:
            # """Diffuse"""
            self.build_all_diff_size = self.maps_combobox_list[0].currentText
            self.sel_obj.createChannel("diff", int(self.build_all_diff_size), int(self.build_all_diff_size), 8)

            # """Bump"""
            self.build_all_bump_size = self.maps_combobox_list[1].currentText
            self.sel_obj.createChannel("bump", int(self.build_all_bump_size), int(self.build_all_bump_size), 8)

            # """Displacement"""
            self.build_all_disp_size = self.maps_combobox_list[2].currentText
            self.sel_obj.createChannel("disp", int(self.build_all_disp_size), int(self.build_all_disp_size), 8)

            # """Specular"""
            self.build_all_spec_size = self.maps_combobox_list[3].currentText
            self.sel_obj.createChannel("spec", int(self.build_all_spec_size), int(self.build_all_spec_size), 8)

            # """Normal"""
            self.build_all_norm_size = self.maps_combobox_list[4].currentText
            self.sel_obj.createChannel("norm", int(self.build_all_norm_size), int(self.build_all_norm_size), 8)

            # """Roughness"""
            self.build_all_roug_size = self.maps_combobox_list[5].currentText
            self.sel_obj.createChannel("roug", int(self.build_all_roug_size), int(self.build_all_roug_size), 8)

            # """Reflection"""
            self.build_all_refl_size = self.maps_combobox_list[6].currentText
            self.sel_obj.createChannel("refl", int(self.build_all_refl_size), int(self.build_all_refl_size), 8)

            # """Refraction"""
            self.build_all_refr_size = self.maps_combobox_list[7].currentText
            self.sel_obj.createChannel("refr", int(self.build_all_refr_size), int(self.build_all_refr_size), 8)

            # """Fresnel"""
            self.build_all_frnl_size = self.maps_combobox_list[8].currentText
            self.sel_obj.createChannel("frnl", int(self.build_all_frnl_size), int(self.build_all_frnl_size), 8)

            # """Mask"""
            self.build_all_mask_size = self.maps_combobox_list[9].currentText
            self.sel_obj.createChannel("mask", int(self.build_all_mask_size), int(self.build_all_mask_size), 8)


        else:
            self.build_all_same_size = int(self.build_all_size_combobox.currentText)
            self.sel_obj.createChannel("diff", self.build_all_same_size, self.build_all_same_size, 8)
            self.sel_obj.createChannel("bump", self.build_all_same_size, self.build_all_same_size, 8)
            self.sel_obj.createChannel("disp", self.build_all_same_size, self.build_all_same_size, 8)
            self.sel_obj.createChannel("spec", self.build_all_same_size, self.build_all_same_size, 8)
            self.sel_obj.createChannel("norm", self.build_all_same_size, self.build_all_same_size, 8)
            self.sel_obj.createChannel("roug", self.build_all_same_size, self.build_all_same_size, 8)
            self.sel_obj.createChannel("refl", self.build_all_same_size, self.build_all_same_size, 8)
            self.sel_obj.createChannel("refr", self.build_all_same_size, self.build_all_same_size, 8)
            self.sel_obj.createChannel("frnl", self.build_all_same_size, self.build_all_same_size, 8)
            self.sel_obj.createChannel("mask", self.build_all_same_size, self.build_all_same_size, 8)

    def build_selected_fc(self):
        """Fonction pour crer les maps selectionner seulement"""
        if self.build_selected_same_size_chkbox.checkState() == 0:  # Build selected SANS SAME SIZE CHECKBOX
            # """Diffuse"""
            if self.chk_liste[0].checkState() == 2:
                self.build_selected_diff_size = int(self.maps_combobox_list[0].currentText)
                self.sel_obj.createChannel("diff", self.build_selected_diff_size, self.build_selected_diff_size, 8)
            else:
                pass

            # """Bump"""
            if self.chk_liste[1].checkState() == 2:
                self.build_selected_bump_size = int(self.maps_combobox_list[1].currentText)
                self.sel_obj.createChannel("bump", self.build_selected_bump_size, self.build_selected_bump_size, 8)
            else:
                pass

            # """Displacement"""
            if self.chk_liste[2].checkState() == 2:
                self.build_selected_disp_size = int(self.maps_combobox_list[2].currentText)
                self.sel_obj.createChannel("disp", self.build_selected_disp_size, self.build_selected_disp_size, 8)
            else:
                pass

            # """Specular"""
            if self.chk_liste[3].checkState() == 2:
                self.build_selected_spec_size = int(self.maps_combobox_list[3].currentText)
                self.sel_obj.createChannel("spec", self.build_selected_spec_size, self.build_selected_spec_size, 8)
            else:
                pass

            # """Normal"""
            if self.chk_liste[4].checkState() == 2:
                self.build_selected_norm_size = int(self.maps_combobox_list[4].currentText)
                self.sel_obj.createChannel("norm", self.build_selected_norm_size, self.build_selected_norm_size, 8)
            else:
                pass

            # """Roughness"""
            if self.chk_liste[5].checkState() == 2:
                self.build_selected_roug_size = int(self.maps_combobox_list[5].currentText)
                self.sel_obj.createChannel("roug", self.build_selected_roug_size, self.build_selected_roug_size, 8)
            else:
                pass

            # """Reflection"""
            if self.chk_liste[6].checkState() == 2:
                self.build_selected_refl_size = int(self.maps_combobox_list[6].currentText)
                self.sel_obj.createChannel("refl", self.build_selected_refl_size, self.build_selected_refl_size, 8)
            else:
                pass

            # """Refraction"""
            if self.chk_liste[7].checkState() == 2:
                self.build_selected_refr_size = int(self.maps_combobox_list[7].currentText)
                self.sel_obj.createChannel("refr", self.build_selected_refr_size, self.build_selected_refr_size, 8)
            else:
                pass

            # """Fresnel"""
            if self.chk_liste[8].checkState() == 2:
                self.build_selected_frnl_size = int(self.maps_combobox_list[8].currentText)
                self.sel_obj.createChannel("frnl", self.build_selected_frnl, self.build_selected_frnl, 8)
            else:
                pass

            # """Mask"""
            if self.chk_liste[9].checkState() == 2:
                self.build_selected_mask_size = int(self.maps_combobox_list[9].currentText)
                self.sel_obj.createChannel("mask", self.build_selected_mask_size, self.build_selected_mask_size, 8)
            else:
                pass


        else:  # Build selected avec SAME SIZE CHECKBOX
            self.build_selected_same_size = int(self.build_selected_size_combobox.currentText)
            # """Diffuse"""
            if self.chk_liste[0].checkState() == 2:
                self.sel_obj.createChannel("diff", self.build_selected_same_size, self.build_selected_same_size, 8)
            else:
                pass

            # """Bump"""
            if self.chk_liste[1].checkState() == 2:
                self.sel_obj.createChannel("bump", self.build_selected_same_size, self.build_selected_same_size, 8)
            else:
                pass

            # """Displacement"""
            if self.chk_liste[2].checkState() == 2:
                self.sel_obj.createChannel("disp", self.build_selected_same_size, self.build_selected_same_size, 8)
            else:
                pass

            # """Specular"""
            if self.chk_liste[3].checkState() == 2:
                self.sel_obj.createChannel("spec", self.build_selected_same_size, self.build_selected_same_size, 8)
            else:
                pass

            # """Normal"""
            if self.chk_liste[4].checkState() == 2:
                self.sel_obj.createChannel("norm", self.build_selected_same_size, self.build_selected_same_size, 8)
            else:
                pass

            # """Roughness"""
            if self.chk_liste[5].checkState() == 2:
                self.sel_obj.createChannel("roug", self.build_selected_same_size, self.build_selected_same_size, 8)
            else:
                pass

            # """Reflection"""
            if self.chk_liste[6].checkState() == 2:
                self.sel_obj.createChannel("refl", self.build_selected_same_size, self.build_selected_same_size, 8)
            else:
                pass

            # """Refraction"""
            if self.chk_liste[7].checkState() == 2:
                self.sel_obj.createChannel("refr", self.build_selected_same_size, self.build_selected_same_size, 8)
            else:
                pass

            # """Fresnel"""
            if self.chk_liste[8].checkState() == 2:
                self.sel_obj.createChannel("frnl", self.build_selected_same_size, self.build_selected_same_size, 8)
            else:
                pass

            # """Mask"""
            if self.chk_liste[9].checkState() == 2:
                self.sel_obj.createChannel("mask", self.build_selected_same_size, self.build_selected_same_size, 8)
            else:
                pass

