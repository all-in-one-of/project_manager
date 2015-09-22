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

            status_item = QtGui.QTableWidgetItem()
            status_item.setText(str(status))
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if status == "Idle":
                status_item.setBackground(QtGui.QColor(253, 179, 20))
            elif status == "Rendering":
                status_item.setBackground(QtGui.QColor(135, 45, 44))
            self.renderTableWidget.setItem(0, 7, status_item)

            self.renderTableWidget.resizeColumnsToContents()


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
            self.renderTableWidget.setItem(item.row(), 7, status_item)

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
            self.renderTableWidget.setItem(item.row(), 7, status_item)

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
            item = QtGui.QListWidgetItem("None")
            item.setData(QtCore.Qt.UserRole, seq)
            self.shotListWidget.addItem(item)
            for shot in shots:
                item = QtGui.QListWidgetItem(shot)
                item.setData(QtCore.Qt.UserRole, seq)
                self.shotListWidget.addItem(item)

        change_seq_shot_btn = QtGui.QPushButton("Change Sequence and Shot", dialog)

        layout.addWidget(seqLbl, 0, 0)
        layout.addWidget(shotLbl, 0, 1)
        layout.addWidget(self.seqListWidget, 1, 0)
        layout.addWidget(self.shotListWidget, 1, 1)
        layout.addWidget(change_seq_shot_btn, 2, 0, 2, 2)

        self.seqListWidget.setCurrentRow(0)
        self.filter_shots_based_on_sequence()

        dialog.exec_()

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
