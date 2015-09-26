#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import operator
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import pyperclip as clipboard
from operator import itemgetter


from random import randint

class RenderTab(object):

    def __init__(self):

        self.startRenderBtn.clicked.connect(self.start_render_on_selected_computers)
        self.stopRenderBtn.clicked.connect(self.stop_rendering_on_selected_computers)

        self.changeSeqBtn.clicked.connect(self.change_sequence_on_selected_computers)

        self.setToIFDBtn.clicked.connect(self.change_to_ifd)
        self.setToMantraBtn.clicked.connect(self.change_to_mantra)

        self.changeResolutionBtn.clicked.connect(self.change_resolution)
        self.changeSamplingBtn.clicked.connect(self.change_sampling)

        self.add_computers_from_database()

    def add_computers_from_database(self):
        for i in reversed(xrange(self.renderTableWidget.rowCount())):
            self.renderTableWidget.removeRow(i)

        all_computers = self.cursor.execute('''SELECT * FROM computers''').fetchall()

        # Add existing tasks to task table
        for row_index, computer in enumerate(reversed(all_computers)):

            self.renderTableWidget.insertRow(0)

            id = computer[0]
            computer_id = computer[1]
            classroom = computer[2]
            status = computer[3]
            scene_path = computer[4]
            seq = computer[5]
            shot = computer[6]
            last_active = computer[7]
            rendered_frames = computer[8]
            current_frame = computer[9]
            ifd = computer[10]
            resolution = computer[11]
            sampling = computer[12]

            if id == None: id = ""
            if computer_id == None: computer_id = ""
            if classroom == None: classroom = ""
            if status == None: status = ""
            if scene_path == None: scene_path = ""
            if seq == None: seq = ""
            if shot == None: shot = ""
            if last_active == None: last_active = ""
            if rendered_frames == None: rendered_frames = ""
            if current_frame == None: current_frame = ""
            if ifd == None: ifd = ""
            if resolution == None: resolution = ""
            if sampling == None: sampling = ""

            id_item = QtGui.QTableWidgetItem()
            id_item.setText(str(id))
            id_item.setTextAlignment(QtCore.Qt.AlignCenter)
            id_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 0, id_item)

            computer_id_item = QtGui.QTableWidgetItem()
            computer_id_item.setText(str(computer_id))
            computer_id_item.setTextAlignment(QtCore.Qt.AlignCenter)
            computer_id_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 1, computer_id_item)

            classroom_item = QtGui.QTableWidgetItem()
            classroom_item.setText(str(classroom))
            classroom_item.setTextAlignment(QtCore.Qt.AlignCenter)
            classroom_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 2, classroom_item)

            seq_item = QtGui.QTableWidgetItem()
            seq_item.setText(str(seq))
            seq_item.setTextAlignment(QtCore.Qt.AlignCenter)
            seq_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 3, seq_item)

            shot_item = QtGui.QTableWidgetItem()
            shot_item.setText(str(shot))
            shot_item.setTextAlignment(QtCore.Qt.AlignCenter)
            shot_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 4, shot_item)

            rendered_frames_item = QtGui.QTableWidgetItem()
            rendered_frames_item.setText(str(rendered_frames))
            rendered_frames_item.setTextAlignment(QtCore.Qt.AlignCenter)
            rendered_frames_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 5, rendered_frames_item)

            current_frame_item = QtGui.QTableWidgetItem()
            current_frame_item.setText(str(current_frame))
            current_frame_item.setTextAlignment(QtCore.Qt.AlignCenter)
            current_frame_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 6, current_frame_item)

            ifd_item = QtGui.QTableWidgetItem()
            ifd_item.setText(str(ifd))
            ifd_item.setTextAlignment(QtCore.Qt.AlignCenter)
            ifd_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 7, ifd_item)

            resolution_item = QtGui.QTableWidgetItem()
            resolution_item.setText(str(resolution))
            resolution_item.setTextAlignment(QtCore.Qt.AlignCenter)
            resolution_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 8, resolution_item)

            sampling_item = QtGui.QTableWidgetItem()
            sampling_item.setText(str(sampling))
            sampling_item.setTextAlignment(QtCore.Qt.AlignCenter)
            sampling_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 9, sampling_item)

            status_item = QtGui.QTableWidgetItem()
            status_item.setText(str(status))
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if status == "Idle":
                status_item.setBackground(QtGui.QColor(253, 179, 20))
            elif status == "Rendering":
                status_item.setBackground(QtGui.QColor(216, 72, 72))
            self.renderTableWidget.setItem(0, 10, status_item)


            self.renderTableWidget.resizeColumnsToContents()
            self.tmTableWidget.horizontalHeader().setResizeMode(10, QtGui.QHeaderView.Stretch)

    def start_render_on_selected_computers(self):
        selected_items = self.renderTableWidget.selectedItems()
        for item in selected_items:
            id = self.renderTableWidget.item(item.row(), 0).text()
            computer_id = self.renderTableWidget.item(item.row(), 1).text()
            self.cursor.execute('''UPDATE computers SET status="Rendering" WHERE computer_id=? AND id=?''', (str(computer_id), str(id), ))

            status_item = QtGui.QTableWidgetItem()
            status_item.setText("Rendering")
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            status_item.setBackground(QtGui.QColor(135, 45, 44))
            self.renderTableWidget.setItem(item.row(), 10, status_item)

        self.db.commit()

    def stop_rendering_on_selected_computers(self):
        selected_items = self.renderTableWidget.selectedItems()
        for item in selected_items:
            id = self.renderTableWidget.item(item.row(), 0).text()
            computer_id = self.renderTableWidget.item(item.row(), 1).text()
            self.cursor.execute('''UPDATE computers SET status="Idle" WHERE computer_id=? AND id=?''', (str(computer_id), str(id),))

            status_item = QtGui.QTableWidgetItem()
            status_item.setText("Idle")
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            status_item.setBackground(QtGui.QColor(253, 179, 20))
            self.renderTableWidget.setItem(item.row(), 10, status_item)

        self.db.commit()

    def change_sequence_on_selected_computers(self):

        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Choose a sequence and a shot")
        self.Lib.apply_style(self, dialog)

        layout = QtGui.QGridLayout(dialog)

        seqLbl = QtGui.QLabel("Sequence:", dialog)
        shotLbl = QtGui.QLabel("Shot:", dialog)

        self.seqListWidget = QtGui.QListWidget(dialog)
        self.shotListWidget = QtGui.QListWidget(dialog)

        self.seqListWidget.itemClicked.connect(self.filter_shots_based_on_sequence)
        self.shotListWidget.itemClicked.connect(self.shot_list_clicked)

        seqList = QtCore.QStringList()
        [seqList.append(i) for i in self.shots.keys()]
        self.seqListWidget.addItems(seqList)

        for seq, shots in self.shots.items():
            for shot in sorted(shots):
                if shot != "xxxx":
                    item = QtGui.QListWidgetItem(shot)
                    item.setData(QtCore.Qt.UserRole, seq)
                    self.shotListWidget.addItem(item)

        change_seq_shot_btn = QtGui.QPushButton("Change Sequence and Shot", dialog)
        change_seq_shot_btn.clicked.connect(dialog.accept)

        layout.addWidget(seqLbl, 0, 0)
        layout.addWidget(shotLbl, 0, 1)
        layout.addWidget(self.seqListWidget, 1, 0)
        layout.addWidget(self.shotListWidget, 1, 1)
        layout.addWidget(change_seq_shot_btn, 2, 0, 2, 2)

        self.seqListWidget.setCurrentRow(0)
        self.filter_shots_based_on_sequence()

        result = dialog.exec_()

        if result == 0:
            return

        selected_items = self.renderTableWidget.selectedItems()

        print(self.render_selected_sequence)
        print(self.render_selected_shot)


        for item in selected_items:

            id = self.renderTableWidget.item(item.row(), 0).text()
            computer_id = self.renderTableWidget.item(item.row(), 1).text()

            # Change sequence
            self.cursor.execute('''UPDATE computers SET seq=? WHERE computer_id=? AND id=?''', (str(self.render_selected_sequence), str(computer_id), str(id), ))

            sequence_item = QtGui.QTableWidgetItem()
            sequence_item.setText(self.render_selected_sequence)
            sequence_item.setTextAlignment(QtCore.Qt.AlignCenter)
            sequence_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(item.row(), 3, sequence_item)


            # Change shot
            self.cursor.execute('''UPDATE computers SET shot=? WHERE computer_id=? AND id=?''', (self.render_selected_shot, str(computer_id), str(id), ))

            shot_item = QtGui.QTableWidgetItem()
            shot_item.setText(self.render_selected_shot)
            shot_item.setTextAlignment(QtCore.Qt.AlignCenter)
            shot_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(item.row(), 4, shot_item)

        self.db.commit()

    def filter_shots_based_on_sequence(self):
        self.render_selected_sequence = self.seqListWidget.selectedItems()[0]
        self.render_selected_sequence = str(self.render_selected_sequence.text())

        for i in xrange(0, self.shotListWidget.count()):
            seq_from_shot = self.shotListWidget.item(i).data(QtCore.Qt.UserRole).toPyObject()
            if seq_from_shot == self.render_selected_sequence:
                self.shotListWidget.item(i).setHidden(False)
            else:
                self.shotListWidget.item(i).setHidden(True)

    def shot_list_clicked(self):
        self.render_selected_shot = self.shotListWidget.selectedItems()[0]
        self.render_selected_shot = str(self.render_selected_shot.text())
        if self.render_selected_shot == "None":
            self.render_selected_shot = "xxxx"







        #
        # selected_items = self.renderTableWidget.selectedItems()
        #
        # all_sequences = self.cursor.execute('''SELECT sequence_name FROM sequences''').fetchall()
        # all_sequences = [i[0] for i in all_sequences]
        #
        # dialog = QtGui.QDialog()
        # dialog.setMinimumWidth(150)
        # self.Lib.apply_style(self, dialog)
        # dialog.setWindowTitle("Select a sequence")
        #
        # layout = QtGui.QVBoxLayout(dialog)
        #
        # combobox = QtGui.QComboBox(dialog)
        # combobox.addItems(QtCore.QStringList(all_sequences))
        #
        # accept_btn = QtGui.QPushButton("Change Sequence")
        # accept_btn.clicked.connect(dialog.accept)
        #
        # layout.addWidget(combobox)
        # layout.addWidget(accept_btn)
        #
        # result = dialog.exec_()
        #
        # if result == 0:
        #     return
        #
        # seq = str(combobox.currentText())
        #
        # for item in selected_items:
        #     id = self.renderTableWidget.item(item.row(), 0).text()
        #     computer_id = self.renderTableWidget.item(item.row(), 1).text()
        #     self.cursor.execute('''UPDATE computers SET seq=? WHERE computer_id=? AND id=?''', (seq, str(computer_id), str(id),))
        #
        #     seq_item = QtGui.QTableWidgetItem()
        #     seq_item.setText(seq)
        #     seq_item.setTextAlignment(QtCore.Qt.AlignCenter)
        #     seq_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        #     self.renderTableWidget.setItem(item.row(), 3, seq_item)
        #
        # self.db.commit()
        #

    def change_to_ifd(self):

        selected_items = self.renderTableWidget.selectedItems()

        for item in selected_items:
            computer_id = self.renderTableWidget.item(item.row(), 1).text()

            # Change sequence
            self.cursor.execute('''UPDATE computers SET ifd="1" WHERE computer_id=?''', (str(computer_id), ))

            ifd_item = QtGui.QTableWidgetItem()
            ifd_item.setText("1")
            ifd_item.setTextAlignment(QtCore.Qt.AlignCenter)
            ifd_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(item.row(), 7, ifd_item)

        self.db.commit()

    def change_to_mantra(self):

        selected_items = self.renderTableWidget.selectedItems()

        for item in selected_items:
            computer_id = self.renderTableWidget.item(item.row(), 1).text()

            # Change sequence
            self.cursor.execute('''UPDATE computers SET ifd="0" WHERE computer_id=?''', (str(computer_id), ))

            ifd_item = QtGui.QTableWidgetItem()
            ifd_item.setText("0")
            ifd_item.setTextAlignment(QtCore.Qt.AlignCenter)
            ifd_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(item.row(), 7, ifd_item)

        self.db.commit()

    def change_resolution(self):
        selected_items = self.renderTableWidget.selectedItems()
        resolution_value = self.resolutionSpinBox.value()

        for item in selected_items:
            computer_id = self.renderTableWidget.item(item.row(), 1).text()

            # Change sequence
            self.cursor.execute('''UPDATE computers SET resolution=? WHERE computer_id=?''', (resolution_value, str(computer_id),))

            resolution_item = QtGui.QTableWidgetItem()
            resolution_item.setText(str(resolution_value))
            resolution_item.setTextAlignment(QtCore.Qt.AlignCenter)
            resolution_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(item.row(), 8, resolution_item)

        self.db.commit()

    def change_sampling(self):
        selected_items = self.renderTableWidget.selectedItems()
        sampling_value = self.samplingSpinBox.value()

        for item in selected_items:
            computer_id = self.renderTableWidget.item(item.row(), 1).text()

            # Change sequence
            self.cursor.execute('''UPDATE computers SET sampling=? WHERE computer_id=?''', (sampling_value, str(computer_id),))

            sampling_item = QtGui.QTableWidgetItem()
            sampling_item.setText(str(sampling_value))
            sampling_item.setTextAlignment(QtCore.Qt.AlignCenter)
            sampling_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(item.row(), 9, sampling_item)

        self.db.commit()