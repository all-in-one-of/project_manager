#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore, Qt
from thibh import modules
import re
import subprocess
import os
import shutil
from PIL import Image
import time


class TaskManager(object):

    def __init__(self):
        self.departments = {"Script": 0, "Storyboard": 1, "References": 2, "Concepts": 3, "Modeling": 4, "Texturing": 5,
                            "Rigging": 6, "Animation": 7, "Simulation": 8, "Shading": 9, "Layout": 10,
                            "Digital Matte Painting": 11, "Compositing": 12, "Editing": 13, "RnD": 14}

        self.status = {"Ready to start": 0, "Waiting to start": 1, "In Progress": 2, "On Hold": 3, "Final": 4}

        self.members = {"achaput":0, "costiguy":1, "cgonnord":2, "dcayerdesforges":3,
                        "earismendez":4, "erodrigue":5, "jberger":6, "lgregoire":7,
                        "lclavet":8, "mchretien":9, "mbeaudoin":10,
                        "mroz":11, "obolduc":12, "slachapelle":13, "thoudon":14,
                        "yjobin":15, "yshan":16, "vdelbroucq":17}

    def add_tasks_from_database(self):

        all_tasks = self.cursor.execute('''SELECT * FROM tasks''').fetchall()

        # Add existing tasks to task table
        for i, task in enumerate(all_tasks):
            self.taskManagerTableWidget.insertRow(0)

            # Adding tasks description
            task_description = task[1] #Ex: Ajouter références pour le musée
            task_description_item = QtGui.QTableWidgetItem()
            task_description_item.setText(task_description)
            self.taskManagerTableWidget.setItem(0, 0, task_description_item)


            # Adding department combo boxes
            task_department = task[2] #Ex: Compositing
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Script", "Storyboard", "References", "Concepts", "Modeling", "Texturing",
                            "Rigging", "Animation", "Simulation", "Shading", "Layout",
                            "Digital Matte Painting", "Compositing", "Editing", "RnD"])
            combo_box.setCurrentIndex(self.departments[task_department])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.taskManagerTableWidget.setCellWidget(0, 1, combo_box)

            # Adding task status
            task_status = task[3] #Ex: En cours
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Ready to start", "Waiting to start", "In Progress", "On Hold", "Final"])
            combo_box.setCurrentIndex(self.status[task_status])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.change_cell_status_color(combo_box, task_status)
            self.taskManagerTableWidget.setCellWidget(0, 2, combo_box)

            # Adding assigned to
            task_assignation = task[4] #Ex: Amélie
            combo_box = QtGui.QComboBox()
            combo_box.addItems(
                [u"Amélie", u"Chloé", u"Christopher", u"David", u"Edwin", u"Étienne", u"Jeremy",
                 u"Laurence", u"Louis-Philippe", u"Marc-Antoine", u"Mathieu", u"Maxime", u"Olivier", u"Simon", u"Thibault",
                 u"Yann", u"Yi", u"Valentin"])
            combo_box.setCurrentIndex(self.members[task_assignation])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.taskManagerTableWidget.setCellWidget(0, 3, combo_box)


            # Adding task start
            task_date_start = task[5]
            date_start = QtCore.QDate.fromString(task_date_start, 'dd/MM/yyyy')
            date_start_edit = QtGui.QDateEdit()
            date_start_edit.setDate(date_start)
            date_start_edit.setDisplayFormat("dd/MM/yyyy")
            self.set_calendar(date_start_edit)
            self.taskManagerTableWidget.setCellWidget(0, 4, date_start_edit)


            # Adding task end
            task_date_end = task[6]
            date_end = QtCore.QDate.fromString(task_date_end, 'dd/MM/yyyy')
            date_end_edit = QtGui.QDateEdit()
            date_end_edit.setDate(date_end)
            date_end_edit.setDisplayFormat("dd/MM/yyyy")
            self.set_calendar(date_end_edit)
            self.taskManagerTableWidget.setCellWidget(0, 5, date_end_edit)


            # Adding days left
            days_left = str(date_start.daysTo(date_end))
            days_left_item = QtGui.QTableWidgetItem()
            days_left_item.setText(days_left)
            days_left_item.setTextAlignment(QtCore.Qt.AlignCenter)
            days_left_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.taskManagerTableWidget.setItem(0, 6, days_left_item)

        self.taskManagerTableWidget.itemChanged.connect(self.update_tasks)
        self.taskManagerAddRowBtn.clicked.connect(self.add_task)

    def update_tasks(self, test):
        clicked_widget = self.sender()
        if type(clicked_widget) == QtGui.QComboBox:
            print(clicked_widget.currentIndex())
            print(clicked_widget.currentText())

        elif type(clicked_widget) == QtGui.QDateEdit:
            print(clicked_widget)







    def set_calendar(self, QDateEdit):
        QDateEdit.setCalendarPopup(True)
        calendar_widget = QtGui.QCalendarWidget()
        calendar_widget.setFirstDayOfWeek(QtCore.Qt.Monday)
        calendar_widget.showToday()
        calendar_widget.setStyleSheet("background-color: white;")
        QDateEdit.setCalendarWidget(calendar_widget)
        QDateEdit.dateChanged.connect(self.update_tasks)

    def calendar_widget(self):
        calendar_widget = QtGui.QCalendarWidget()
        calendar_widget.setFirstDayOfWeek(Qt.Monday)

    def add_task(self):

        self.taskManagerTableWidget.insertRow(0)

        # Adding tasks description
        task_description_item = QtGui.QTableWidgetItem()
        self.taskManagerTableWidget.setItem(0, 0, task_description_item)


        # Adding department combo boxes
        combo_box = QtGui.QComboBox()
        combo_box.addItems(["Script", "Storyboard", "References", "Concepts", "Modeling", "Texturing",
                        "Rigging", "Animation", "Simulation", "Shading", "Layout",
                        "Digital Matte Painting", "Compositing", "Editing", "RnD"])
        self.taskManagerTableWidget.setCellWidget(0, 1, combo_box)

        # Adding task status
        combo_box = QtGui.QComboBox()
        combo_box.addItems(["Ready to start", "Waiting to start", "In Progress", "On Hold", "Final"])
        self.taskManagerTableWidget.setCellWidget(0, 2, combo_box)

        # Adding assigned to
        combo_box = QtGui.QComboBox()
        combo_box.addItems(
            [u"Amélie", u"Chloé", u"Christopher", u"David", u"Edwin", u"Étienne", u"Jeremy",
             u"Laurence", "Louisu-Philippe", "Marcu-Antoine", u"Mathieu", u"Maxime", u"Olivier", u"Simon", u"Thibault",
             u"Yann", u"Yi", u"Valentin"])
        self.taskManagerTableWidget.setCellWidget(0, 3, combo_box)


        # Adding task start
        today_date = time.strftime("%d/%m/%Y")
        today_date = QtCore.QDate.fromString(today_date, "dd/MM/yyyy")
        date_start_edit = QtGui.QDateEdit()
        date_start_edit.setDate(today_date)
        date_start_edit.setDisplayFormat("dd/MM/yyyy")
        self.set_calendar(date_start_edit)

        self.taskManagerTableWidget.setCellWidget(0, 4, date_start_edit)


        # Adding task end
        date_end_edit = QtGui.QDateEdit()
        date_end_edit.setDate(today_date)
        date_end_edit.setDisplayFormat("dd/MM/yyyy")
        self.set_calendar(date_end_edit)
        self.taskManagerTableWidget.setCellWidget(0, 5, date_end_edit)


        # Adding days left
        days_left_item = QtGui.QTableWidgetItem()
        days_left_item.setText("0")
        days_left_item.setTextAlignment(QtCore.Qt.AlignCenter)
        days_left_item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.taskManagerTableWidget.setItem(0, 6, days_left_item)

    def change_cell_status_color(self, cell_item, task_status):
        if task_status == "Ready to start":
            cell_item.setStyleSheet("background-color: blue;")
        elif task_status == "Waiting to start":
            cell_item.setStyleSheet("background-color: dark-blue;")
        elif task_status == "In Progress":
            cell_item.setStyleSheet("background-color: yellow;")
        elif task_status == "On Hold":
            cell_item.setStyleSheet("background-color: orange;")
        elif task_status == "Final":
            cell_item.setStyleSheet("background-color: green;")


