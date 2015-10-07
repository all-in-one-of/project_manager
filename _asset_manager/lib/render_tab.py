#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import operator
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pyperclip as clipboard
from operator import itemgetter
import sqlite3

from random import randint

class RenderTab(object):

    def __init__(self):

        self.startRenderBtn.clicked.connect(self.start_render_on_selected_computers)
        self.stopRenderBtn.clicked.connect(self.stop_rendering_on_selected_computers)
        self.logOutBtn.clicked.connect(self.log_out_selected_computers)

        self.add_computers_from_database()

    def add_computers_from_database(self):
        self.render_db_path = "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_database/rendering.sqlite"
        self.render_db = sqlite3.connect(self.render_db_path, check_same_thread=False, timeout=30.0)
        self.render_cursor = self.render_db.cursor()

        for i in reversed(xrange(self.renderTableWidget.rowCount())):
            self.renderTableWidget.removeRow(i)

        all_computers = self.render_cursor.execute('''SELECT * FROM computers''').fetchall()

        for computer in all_computers:
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
            current_time_datetime = datetime.strptime(current_time, '%d/%m/%Y %H:%M')

            last_active = computer[5]
            last_active_datetime = datetime.strptime(last_active, '%d/%m/%Y %H:%M')

            time_difference = current_time_datetime - last_active_datetime
            if time_difference.seconds > 1000:
                self.render_cursor.execute('''DELETE FROM computers WHERE computer_id=?''', (computer[0], ))

        self.render_db.commit()

        all_computers = self.render_cursor.execute('''SELECT * FROM computers''').fetchall()

        # Add existing tasks to task table
        for row_index, computer in enumerate(reversed(all_computers)):

            self.renderTableWidget.insertRow(0)

            computer_id = computer[0]
            classroom = computer[1]
            status = computer[2]
            rendered_frames = computer[3]
            current_frame = computer[4]
            last_active = computer[5]

            if computer_id == None: computer_id = ""
            if classroom == None: classroom = ""
            if status == None: status = ""
            if rendered_frames == None: rendered_frames = ""
            if current_frame == None: current_frame = ""
            if last_active == None: last_active = ""

            id_item = QtGui.QTableWidgetItem()
            id_item.setText("0")
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

            rendered_frames_item = QtGui.QTableWidgetItem()
            rendered_frames_item.setText(str(rendered_frames))
            rendered_frames_item.setTextAlignment(QtCore.Qt.AlignCenter)
            rendered_frames_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 3, rendered_frames_item)

            current_frame_item = QtGui.QTableWidgetItem()
            current_frame_item.setText(str(current_frame))
            current_frame_item.setTextAlignment(QtCore.Qt.AlignCenter)
            current_frame_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 4, current_frame_item)

            last_active_item = QtGui.QTableWidgetItem()
            last_active_item.setText(str(last_active))
            last_active_item.setTextAlignment(QtCore.Qt.AlignCenter)
            last_active_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 5, last_active_item)

            status_item = QtGui.QTableWidgetItem()
            status_item.setText(str(status))
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if status == "idle":
                status_item.setBackground(QtGui.QColor(253, 179, 20))
            elif status == "rendering":
                status_item.setBackground(QtGui.QColor(216, 72, 72))
            self.renderTableWidget.setItem(0, 6, status_item)

            self.tmTableWidget.horizontalHeader().setResizeMode(6, QtGui.QHeaderView.Stretch)
            self.renderTableWidget.resizeColumnsToContents()

    def start_render_on_selected_computers(self):
        selected_items = self.renderTableWidget.selectedItems()
        for item in selected_items:
            id = self.renderTableWidget.item(item.row(), 0).text()
            computer_id = self.renderTableWidget.item(item.row(), 1).text()
            print(computer_id)
            self.render_cursor.execute('''UPDATE computers SET status="start" WHERE computer_id=?''', (str(computer_id), ))

            status_item = QtGui.QTableWidgetItem()
            status_item.setText("Rendering")
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            status_item.setBackground(QtGui.QColor(216, 72, 72))
            self.renderTableWidget.setItem(item.row(), 6, status_item)

        self.render_db.commit()

    def stop_rendering_on_selected_computers(self):
        selected_items = self.renderTableWidget.selectedItems()
        for item in selected_items:
            id = self.renderTableWidget.item(item.row(), 0).text()
            computer_id = self.renderTableWidget.item(item.row(), 1).text()
            self.render_cursor.execute('''UPDATE computers SET status="stop" WHERE computer_id=?''', (str(computer_id),))

            status_item = QtGui.QTableWidgetItem()
            status_item.setText("Idle")
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            status_item.setBackground(QtGui.QColor(253, 179, 20))
            self.renderTableWidget.setItem(item.row(), 6, status_item)

        self.render_db.commit()

    def log_out_selected_computers(self):
        selected_items = self.renderTableWidget.selectedItems()
        for item in selected_items:
            id = self.renderTableWidget.item(item.row(), 0).text()
            computer_id = self.renderTableWidget.item(item.row(), 1).text()
            self.render_cursor.execute('''UPDATE computers SET status="logout" WHERE computer_id=?''', (str(computer_id),))

            status_item = QtGui.QTableWidgetItem()
            status_item.setText("Logging Out")
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            status_item.setBackground(QtGui.QColor(253, 179, 20))
            self.renderTableWidget.setItem(item.row(), 6, status_item)

        self.render_db.commit()


