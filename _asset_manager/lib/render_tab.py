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
import subprocess
import os
from glob import glob

from random import randint

class RenderTab(object):
    def __init__(self):
        self.startRenderBtn.clicked.connect(self.start_render_on_selected_computers)
        self.stopRenderBtn.clicked.connect(self.stop_rendering_on_selected_computers)
        self.logOutBtn.clicked.connect(self.log_out_selected_computers)

        self.addJobBtn.clicked.connect(self.add_job)
        self.removeSelectedJobsBtn.clicked.connect(self.remove_selected_jobs)
        self.updateJobsBtn.clicked.connect(self.update_jobs)

        self.deleteSelectedFramesBtn.clicked.connect(self.delete_selected_frames)

        self.removeSelectedComputersBtn.clicked.connect(self.remove_selected_computers)

        self.checkFramesIntegrityBtn.clicked.connect(self.check_frames_integrity)

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

        self.all_frames = glob("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendered_frames\\*")
        self.all_frames = [os.path.split(i)[-1] for i in self.all_frames]

        # Add existing tasks to task table
        for row_index, frame in enumerate(reversed(self.all_frames)):

            self.renderedFramesTableWidget.insertRow(0)

            sequence = frame.split("_")[0]
            frame = frame.split("_")[1]

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

        self.all_computers = glob("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_computers\\*")
        self.all_computers = [os.path.split(i)[-1] for i in self.all_computers]
        self.computers = []
        for computer in self.all_computers:
            id = computer.split("_")[0]
            classroom = computer.split("_")[1]
            frame = computer.split("_")[2]
            status = computer.split("_")[3]

            last_active = computer.split("_")[4]
            current_time = datetime.now().strftime("%d-%m-%Y-%Hh%M")
            current_time_datetime = datetime.strptime(current_time, '%d-%m-%Y-%Hh%M')
            last_active_datetime = datetime.strptime(last_active, '%d-%m-%Y-%Hh%M')

            time_difference = current_time_datetime - last_active_datetime
            if time_difference.seconds < 3600:
                self.computers.append((id, classroom, frame, status, last_active))


        idle_computers_number = 0
        rendering_computers_number = 0

        # Add existing tasks to task table
        for row_index, computer in enumerate(reversed(self.computers)):

            self.renderTableWidget.insertRow(0)

            computer_id = computer[0]
            classroom = computer[1]
            current_frame = computer[2]
            status = computer[3]
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
                idle_computers_number += 1
                status_item.setBackground(QtGui.QColor(253, 179, 20))
            elif status == "rendering":
                rendering_computers_number += 1
                status_item.setBackground(QtGui.QColor(216, 72, 72))
            elif status == "start":
                idle_computers_number += 1
                status_item.setBackground(QtGui.QColor(115, 179, 90))
            else:
                idle_computers_number += 1
            self.renderTableWidget.setItem(0, 4, status_item)

            self.renderTableWidget.horizontalHeader().setResizeMode(4, QtGui.QHeaderView.Stretch)
            #self.renderTableWidget.resizeColumnsToContents()

            self.idleComputersLbl.setText("Idle: " + str(idle_computers_number))
            self.renderComputersLbl.setText("Rendering: " + str(rendering_computers_number))
            self.totalComputersLbl.setText("Total: " + str(idle_computers_number + rendering_computers_number))

    def start_render_on_selected_computers(self):
        selected_items = self.renderTableWidget.selectedItems()
        rendering_folder = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_computers\\"
        all_computers = glob(rendering_folder + "*")
        all_computers = [os.path.split(i)[-1] for i in all_computers]
        for item in selected_items:
            computer_id = self.renderTableWidget.item(item.row(), 0).text()
            for computer in all_computers:
                if computer.split("_")[0] == computer_id:
                    id = computer.split("_")[0]
                    classroom = computer.split("_")[1]
                    frame = computer.split("_")[2]
                    last_active = computer.split("_")[4]
                    os.rename(rendering_folder + computer, rendering_folder + "{0}_{1}_{2}_{3}_{4}".format(id, classroom, frame, "start", last_active))


            status_item = QtGui.QTableWidgetItem()
            status_item.setText("Rendering")
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            status_item.setBackground(QtGui.QColor(216, 72, 72))
            self.renderTableWidget.setItem(item.row(), 4, status_item)
            self.repaint()
            time.sleep(4)

    def stop_rendering_on_selected_computers(self):
        selected_items = self.renderTableWidget.selectedItems()
        rendering_folder = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_computers\\"
        all_computers = glob(rendering_folder + "*")
        all_computers = [os.path.split(i)[-1] for i in all_computers]
        for item in selected_items:
            computer_id = self.renderTableWidget.item(item.row(), 0).text()
            for computer in all_computers:
                if computer.split("_")[0] == computer_id:
                    id = computer.split("_")[0]
                    classroom = computer.split("_")[1]
                    frame = computer.split("_")[2]
                    last_active = computer.split("_")[4]
                    os.rename(rendering_folder + computer, rendering_folder + "{0}_{1}_{2}_{3}_{4}".format(id, classroom, frame, "stop", last_active))

            status_item = QtGui.QTableWidgetItem()
            status_item.setText("Idle")
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            status_item.setBackground(QtGui.QColor(253, 179, 20))
            self.renderTableWidget.setItem(item.row(), 4, status_item)

        self.render_db.commit()

    def log_out_selected_computers(self):
        selected_items = self.renderTableWidget.selectedItems()
        rendering_folder = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_computers\\"
        all_computers = glob(rendering_folder + "*")
        all_computers = [os.path.split(i)[-1] for i in all_computers]
        for item in selected_items:
            computer_id = self.renderTableWidget.item(item.row(), 0).text()
            for computer in all_computers:
                if computer.split("_")[0] == computer_id:
                    id = computer.split("_")[0]
                    classroom = computer.split("_")[1]
                    frame = computer.split("_")[2]
                    last_active = computer.split("_")[4]
                    os.rename(rendering_folder + computer, rendering_folder + "{0}_{1}_{2}_{3}_{4}".format(id, classroom, frame, "logout", last_active))

            status_item = QtGui.QTableWidgetItem()
            status_item.setText("Logging Out")
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            status_item.setBackground(QtGui.QColor(253, 179, 20))
            self.renderTableWidget.setItem(item.row(), 4, status_item)

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
            ifd_path = self.jobsTableWidget.item(row, 1)
            ifd_path = str(ifd_path.text())
            priority = self.jobsTableWidget.item(row, 2)
            priority = str(priority.text())
            resolution = self.jobsTableWidget.item(row, 3)
            resolution = str(resolution.text())
            sampling = self.jobsTableWidget.item(row, 4)
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
            try:
                os.remove("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendered_frames\\{0}_{1}".format(seq, frame))
            except:
                pass

        self.add_frames_from_database()

    def remove_selected_computers(self):
        selected_items = self.renderTableWidget.selectedItems()

        rendering_folder = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_computers\\"
        all_computers = glob(rendering_folder + "*")
        all_computers = [os.path.split(i)[-1] for i in all_computers]

        for item in selected_items:
            id = self.renderTableWidget.item(item.row(), 0)
            id = str(id.text())
            for computer in all_computers:
                if computer.split("_")[0] == computer_id:
                    os.remove(rendering_folder + computer)

        self.add_computers_from_database()

    def check_frames_integrity(self):
        all_frames = self.render_cursor.execute('''SELECT * FROM rendered_frames''').fetchall()
        all_frames = [str(i[1]) + ":" + str(i[2]) for i in all_frames]
        all_frames = sorted(list(set(all_frames)))

        success_frames = []

        # Show progress bar dialog
        dialog = QtGui.QDialog()
        dialog.setWindowTitle("Please wait...")
        main_layout = QtGui.QVBoxLayout(dialog)

        mainLbl = QtGui.QLabel("Checking frame #0", self)
        progressBar = QtGui.QProgressBar(self)

        main_layout.addWidget(mainLbl)
        main_layout.addWidget(progressBar)

        self.Lib.apply_style(self, dialog)

        dialog.show()
        dialog.repaint()

        progressBar.setMaximum(len(all_frames))

        for i, frame in enumerate(all_frames):
            seq = frame.split(":")[0]
            frame_number = frame.split(":")[1]
            frame_path = "Z:/Groupes-cours/NAND999-A15-N01/pub/assets/rdr/{0}/{0}.{1}.exr".format(seq, frame_number)
            proc = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.13/bin/iinfo.exe", "-i", frame_path], stdout=subprocess.PIPE)
            lines = ""
            for line in iter(proc.stdout.readline, ''):
                line = line.rstrip()
                lines += line

            if not "File bad" in lines:
                success_frames.append(frame)
            else:
                try:
                    os.remove(frame_path)
                except:
                    pass

            progressBar.setValue(i)
            hue = self.fit_range(i, 0, progressBar.maximum(), 0, 76)
            progressBar.setStyleSheet("QProgressBar::chunk {background-color: hsl(" + str(hue) + ", 255, 205);} QProgressBar{ text-align: center;}")
            mainLbl.setText("Checking frame #" + str(frame_number))
            print("Checking frame #" + str(frame_number))
            dialog.repaint()


        self.render_cursor.execute('''DELETE FROM rendered_frames''')
        self.render_db.commit()

        for frame in success_frames:
            seq = frame.split(":")[0]
            frame_number = frame.split(":")[1]
            self.render_cursor.execute('''INSERT INTO rendered_frames(seq, frame) VALUES(?,?)''', (seq, frame_number, ))

        self.render_db.commit()
        self.add_frames_from_database()

        dialog.repaint()
        dialog.close()

