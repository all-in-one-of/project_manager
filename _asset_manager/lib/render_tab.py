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
import time

from random import randint

class RenderTab(object):
    def __init__(self):

        self.tmSequenceFilterFrame_2.hide()
        self.tmShotFilterFrame_2.hide()
        self.rdrDoneFilterFrame.hide()


        self.startRenderBtn.clicked.connect(self.start_render_on_selected_computers)
        self.stopRenderBtn.clicked.connect(self.stop_rendering_on_selected_computers)
        self.logOutBtn.clicked.connect(self.log_out_selected_computers)


        self.addJobBtn.clicked.connect(self.add_job)
        self.removeSelectedJobsBtn.clicked.connect(self.remove_selected_jobs)
        self.updateJobsBtn.clicked.connect(self.update_jobs)

        self.deleteSelectedFramesBtn.clicked.connect(self.delete_selected_frames)

        self.removeSelectedComputersBtn.clicked.connect(self.remove_selected_computers)

        self.render_db_path = "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_database/rendering.sqlite"
        self.render_db = sqlite3.connect(self.render_db_path, check_same_thread=False, timeout=60.0)
        self.render_cursor = self.render_db.cursor()

        self.add_jobs_from_database()
        self.add_frames_from_database()
        self.add_computers_from_database()

    def add_jobs_from_database(self):
        for i in reversed(xrange(self.jobsTableWidget.rowCount())):
            self.jobsTableWidget.removeRow(i)

        all_jobs = self.render_cursor.execute('''SELECT * FROM jobs''').fetchall()

        # Add existing tasks to task table
        for row_index, jobs in enumerate(reversed(all_jobs)):

            self.jobsTableWidget.insertRow(0)

            id = jobs[0]
            ifd_path = jobs[1]
            priority = jobs[2]
            resolution = jobs[3]
            sampling = jobs[4]

            if id == None: id = ""
            if ifd_path == None: ifd_path = ""
            if priority == None: priority = ""
            if resolution == None: resolution = ""
            if sampling == None: sampling = ""

            id_item = QtGui.QTableWidgetItem()
            id_item.setText(str(id))
            id_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.jobsTableWidget.setItem(0, 0, id_item)

            ifd_item = QtGui.QTableWidgetItem()
            ifd_item.setText(str(ifd_path))
            ifd_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.jobsTableWidget.setItem(0, 1, ifd_item)

            priority_item = QtGui.QTableWidgetItem()
            priority_item.setText(str(priority))
            priority_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.jobsTableWidget.setItem(0, 2, priority_item)

            resolution_item = QtGui.QTableWidgetItem()
            resolution_item.setText(str(resolution))
            resolution_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.jobsTableWidget.setItem(0, 3, resolution_item)

            sampling_item = QtGui.QTableWidgetItem()
            sampling_item.setText(str(sampling))
            sampling_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.jobsTableWidget.setItem(0, 4, sampling_item)

            self.jobsTableWidget.horizontalHeader().setResizeMode(4, QtGui.QHeaderView.Stretch)
            #self.jobsTableWidget.resizeColumnsToContents()

    def add_frames_from_database(self):
        for i in reversed(xrange(self.renderedFramesTableWidget.rowCount())):
            self.renderedFramesTableWidget.removeRow(i)

        all_frames = self.render_cursor.execute('''SELECT * FROM rendered_frames''').fetchall()

        # Add existing tasks to task table
        for row_index, frame in enumerate(reversed(all_frames)):

            self.renderedFramesTableWidget.insertRow(0)

            sequence = frame[1]
            frame = frame[2]


            if sequence == None: sequence = ""
            if frame == None: frame = ""

            sequence_item = QtGui.QTableWidgetItem()
            sequence_item.setText(str(sequence))
            sequence_item.setTextAlignment(QtCore.Qt.AlignCenter)
            sequence_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderedFramesTableWidget.setItem(0, 0, sequence_item)

            frame_item = QtGui.QTableWidgetItem()
            frame_item.setText(str(frame))
            frame_item.setTextAlignment(QtCore.Qt.AlignCenter)
            frame_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderedFramesTableWidget.setItem(0, 1, frame_item)

    def add_computers_from_database(self):


        for i in reversed(xrange(self.renderTableWidget.rowCount())):
            self.renderTableWidget.removeRow(i)

        all_computers = self.render_cursor.execute('''SELECT * FROM computers''').fetchall()

        for computer in all_computers:
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M")
            current_time_datetime = datetime.strptime(current_time, '%d/%m/%Y %H:%M')

            last_active = computer[4]
            last_active_datetime = datetime.strptime(last_active, '%d/%m/%Y %H:%M')

            time_difference = current_time_datetime - last_active_datetime
            if time_difference.seconds > 1000:
                pass
                #self.render_cursor.execute('''DELETE FROM computers WHERE computer_id=?''', (computer[0], ))

        self.render_db.commit()

        all_computers = self.render_cursor.execute('''SELECT * FROM computers''').fetchall()

        # Add existing tasks to task table
        for row_index, computer in enumerate(reversed(all_computers)):

            self.renderTableWidget.insertRow(0)

            computer_id = computer[0]
            classroom = computer[1]
            status = computer[2]
            current_frame = computer[3]
            last_active = computer[4]

            if computer_id == None: computer_id = ""
            if classroom == None: classroom = ""
            if status == None: status = ""
            if current_frame == None: current_frame = ""
            if last_active == None: last_active = ""

            computer_id_item = QtGui.QTableWidgetItem()
            computer_id_item.setText(str(computer_id))
            computer_id_item.setTextAlignment(QtCore.Qt.AlignCenter)
            computer_id_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 0, computer_id_item)

            classroom_item = QtGui.QTableWidgetItem()
            classroom_item.setText(str(classroom))
            classroom_item.setTextAlignment(QtCore.Qt.AlignCenter)
            classroom_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 1, classroom_item)

            current_frame_item = QtGui.QTableWidgetItem()
            current_frame_item.setText(str(current_frame))
            current_frame_item.setTextAlignment(QtCore.Qt.AlignCenter)
            current_frame_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 2, current_frame_item)

            last_active_item = QtGui.QTableWidgetItem()
            last_active_item.setText(str(last_active))
            last_active_item.setTextAlignment(QtCore.Qt.AlignCenter)
            last_active_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.renderTableWidget.setItem(0, 3, last_active_item)

            status_item = QtGui.QTableWidgetItem()
            status_item.setText(str(status))
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if status == "idle":
                status_item.setBackground(QtGui.QColor(253, 179, 20))
            elif status == "rendering":
                status_item.setBackground(QtGui.QColor(216, 72, 72))
            self.renderTableWidget.setItem(0, 4, status_item)

            self.renderTableWidget.horizontalHeader().setResizeMode(4, QtGui.QHeaderView.Stretch)
            #self.renderTableWidget.resizeColumnsToContents()

    def start_render_on_selected_computers(self):
        selected_items = self.renderTableWidget.selectedItems()
        for item in selected_items:
            id = self.renderTableWidget.item(item.row(), 0).text()
            computer_id = self.renderTableWidget.item(item.row(), 1).text()
            self.render_cursor.execute('''UPDATE computers SET status="start" WHERE computer_id=?''', (str(computer_id), ))
            self.render_db.commit()

            status_item = QtGui.QTableWidgetItem()
            status_item.setText("Rendering")
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            status_item.setBackground(QtGui.QColor(216, 72, 72))
            self.renderTableWidget.setItem(item.row(), 6, status_item)
            self.repaint()
            time.sleep(4)

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

    def add_job(self):
        self.jobsTableWidget.insertRow(0)

    def remove_selected_jobs(self):
        selected_items = self.jobsTableWidget.selectedItems()

        for item in selected_items:
            self.render_cursor.execute('''DELETE FROM jobs WHERE id=?''', (str(item.text()), ))

        self.render_db.commit()
        self.add_jobs_from_database()

    def update_jobs(self):
        row_count = self.jobsTableWidget.rowCount()
        items = []

        for row in xrange(0, row_count):
            ifd_path = self.jobsTableWidget.item(row, 0)
            ifd_path = str(ifd_path.text())
            priority = self.jobsTableWidget.item(row, 1)
            priority = str(priority.text())
            resolution = self.jobsTableWidget.item(row, 2)
            resolution = str(resolution.text())
            sampling = self.jobsTableWidget.item(row, 3)
            sampling = str(sampling.text())

            items.append((ifd_path, priority, resolution, sampling))

        self.render_cursor.execute('''DELETE FROM jobs''')
        self.render_db.commit()

        for item in items:
            self.render_cursor.execute('''INSERT INTO jobs(ifd_path, priority, resolution, sampling) VALUES(?,?,?,?)''', (item[0], item[1], item[2], item[3],))

        self.render_db.commit()
        self.add_jobs_from_database()

    def delete_selected_frames(self):
        selected_items = self.renderedFramesTableWidget.selectedItems()

        for item in selected_items:
            seq = self.renderedFramesTableWidget.item(item.row(), 0)
            seq = str(seq.text())
            frame = self.renderedFramesTableWidget.item(item.row(), 1)
            frame = str(frame.text())
            self.render_cursor.execute('''DELETE FROM rendered_frames WHERE seq=? AND frame=?''', (seq, frame,))

        self.render_db.commit()
        self.add_frames_from_database()

    def remove_selected_computers(self):
        selected_items = self.renderTableWidget.selectedItems()

        for item in selected_items:
            id = self.renderTableWidget.item(item.row(), 0)
            id = str(id.text())
            self.render_cursor.execute('''DELETE FROM computers WHERE computer_id=?''', (id,))

        self.render_db.commit()
        self.add_computers_from_database()