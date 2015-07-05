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

        self.members_id = {"achaput":0, "costiguy":1, "cgonnord":2, "dcayerdesforges":3,
                        "earismendez":4, "erodrigue":5, "jberger":6, "lgregoire":7,
                        "lclavet":8, "mchretien":9, "mbeaudoin":10,
                        "mroz":11, "obolduc":12, "slachapelle":13, "thoudon":14,
                        "vdelbroucq":15, "yjobin":16, "yshan":17}

        # The itemChanged signal connection of the QTableWidget is fired every time
        # an item changes on the tablewidget. Therefore whenever we're adding an entry to the tablewidget, the itemChanged
        # slot is fired. The item_added variable is used to know when the user adds a row and when a user update a row
        # if item_added is set to true, then the user is simply adding a row and not updating it.
        # Therefore, the update_task function is disabled when the item_added variable is set to true.

        self.item_added = False
        self.taskManagerAddTaskBtn.clicked.connect(self.add_task)
        self.taskManagerRemoveTaskBtn.clicked.connect(self.remove_task)

    def add_tasks_from_database(self):

        for i in reversed(xrange(self.taskManagerTableWidget.rowCount())):
            self.taskManagerTableWidget.removeRow(i)


        all_tasks = self.cursor.execute('''SELECT * FROM tasks''').fetchall()

        self.widgets = {}

        inversed_index = len(all_tasks) - 1


        # Add existing tasks to task table
        for i, task in enumerate(reversed(all_tasks)):

            self.taskManagerTableWidget.insertRow(0)

            # Adding tasks description
            task_description = task[0] #Ex: Ajouter références pour le musée
            task_description_item = QtGui.QTableWidgetItem()
            task_description_item.setText(task_description)
            self.taskManagerTableWidget.setItem(0, 0, task_description_item)
            self.widgets[str(inversed_index) + ":0"] = task_description_item


            # Adding department combo boxes
            task_department = task[1] #Ex: Compositing
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Script", "Storyboard", "References", "Concepts", "Modeling", "Texturing",
                            "Rigging", "Animation", "Simulation", "Shading", "Layout",
                            "Digital Matte Painting", "Compositing", "Editing", "RnD"])
            combo_box.setCurrentIndex(self.departments[task_department])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.taskManagerTableWidget.setCellWidget(0, 1, combo_box)
            self.widgets[str(inversed_index) + ":1"] = combo_box

            # Adding task status
            task_status = task[2] #Ex: En cours
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Ready to start", "Waiting to start", "In Progress", "On Hold", "Final"])
            combo_box.setCurrentIndex(self.status[task_status])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.change_cell_status_color(combo_box, task_status)
            self.taskManagerTableWidget.setCellWidget(0, 2, combo_box)
            self.widgets[str(inversed_index) + ":2"] = combo_box

            # Adding assigned to
            task_assignation = task[3] #Ex: Amélie
            combo_box = QtGui.QComboBox()
            combo_box.addItems(
                [u"Amélie", u"Chloé", u"Christopher", u"David", u"Edwin", u"Étienne", u"Jeremy",
                 u"Laurence", u"Louis-Philippe", u"Marc-Antoine", u"Mathieu", u"Maxime", u"Olivier", u"Simon", u"Thibault",
                 u"Valentin", u"Yann", u"Yi"])
            combo_box.setCurrentIndex(self.members_id[task_assignation])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.taskManagerTableWidget.setCellWidget(0, 3, combo_box)
            self.widgets[str(inversed_index) + ":3"] = combo_box


            # Adding task start
            task_date_start = task[4]
            date_start = QtCore.QDate.fromString(task_date_start, 'dd/MM/yyyy')
            date_start_edit = QtGui.QDateEdit()
            date_start_edit.setDate(date_start)
            date_start_edit.setDisplayFormat("dd/MM/yyyy")
            self.set_calendar(date_start_edit)
            self.taskManagerTableWidget.setCellWidget(0, 4, date_start_edit)
            self.widgets[str(inversed_index) + ":4"] = date_start_edit


            # Adding task end
            task_date_end = task[5]
            date_end = QtCore.QDate.fromString(task_date_end, 'dd/MM/yyyy')
            date_end_edit = QtGui.QDateEdit()
            date_end_edit.setDate(date_end)
            date_end_edit.setDisplayFormat("dd/MM/yyyy")
            self.set_calendar(date_end_edit)
            self.taskManagerTableWidget.setCellWidget(0, 5, date_end_edit)
            self.widgets[str(inversed_index) + ":5"] = date_end_edit


            # Adding days left
            days_left = str(date_start.daysTo(date_end))
            days_left_item = QtGui.QTableWidgetItem()
            days_left_item.setText(days_left)
            days_left_item.setTextAlignment(QtCore.Qt.AlignCenter)
            days_left_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.taskManagerTableWidget.setItem(0, 6, days_left_item)
            self.widgets[str(inversed_index) + ":6"] = days_left_item

            # Adding task bid
            task_bid = task[6]
            task_bid_item = QtGui.QSpinBox()
            task_bid_item.setValue(int(task_bid))
            task_bid_item.setAlignment(QtCore.Qt.AlignCenter)
            task_bid_item.valueChanged.connect(self.update_tasks)
            self.taskManagerTableWidget.setCellWidget(0, 7, task_bid_item)
            self.widgets[str(inversed_index) + ":7"] = task_bid_item

            inversed_index -= 1


        self.taskManagerTableWidget.cellChanged.connect(self.update_tasks)


    def update_tasks(self, value):

        if self.item_added == True:
            return

        # Get which item was clicked and its value
        clicked_widget = self.sender()
        clicked_widget_value = value

        # Get index from clicked_widget position
        if type(clicked_widget) == QtGui.QTableWidget:
            widget_row_index = clicked_widget_value
            widget_column_index = None
        else:
            widget_index = self.taskManagerTableWidget.indexAt(clicked_widget.pos())
            widget_row_index = widget_index.row()
            widget_column_index = widget_index.column()


        # Get widgets and their values from row index
        task_description_widget = self.widgets[str(widget_row_index) + ":0"]
        task_description = unicode(task_description_widget.text())

        task_department_widget = self.widgets[str(widget_row_index) + ":1"]
        task_department = str(task_department_widget.currentText())

        task_status_widget = self.widgets[str(widget_row_index) + ":2"]
        task_status = str(task_status_widget.currentText())

        task_assignation_widget = self.widgets[str(widget_row_index) + ":3"]
        task_assignation = unicode(task_assignation_widget.currentText()).encode('UTF-8')
        # Get username from name (Ex: achaput from Amélie)
        for key, val in self.members.items():
            if task_assignation.decode('UTF-8') == val.decode('UTF-8'):
                task_assignation = key

        task_start_widget = self.widgets[str(widget_row_index) + ":4"]
        task_start = str(task_start_widget.date().toString("dd/MM/yyyy"))

        task_end_widget = self.widgets[str(widget_row_index) + ":5"]
        task_end = str(task_end_widget.date().toString("dd/MM/yyyy"))

        task_time_left_widget = self.widgets[str(widget_row_index) + ":6"]

        task_bid_widget = self.widgets[str(widget_row_index) + ":7"]
        task_bid = str(task_bid_widget.value())

        self.cursor.execute(
            '''UPDATE tasks SET task_description=?, task_department=?, task_status=?, task_assignation=?, task_start=?, task_end=?, task_bid=? WHERE rowid=?''',
            (task_description, task_department, task_status, task_assignation, task_start, task_end, task_bid,
             widget_row_index + 1))

        self.calculate_days_left(task_start_widget, task_end_widget, task_time_left_widget)
        self.change_cell_status_color(task_status_widget, task_status)

        self.db.commit()

    def add_task(self, item_added):

        self.item_added = True

        number_of_rows_to_add = self.taskManagerNbrOfRowsToAddSpinBox.value()

        for i in xrange(number_of_rows_to_add):
            self.cursor.execute(
                '''INSERT INTO tasks(task_description, task_department, task_status, task_assignation, task_start, task_end, task_bid) VALUES (?,?,?,?,?,?,?)''',
                ("", "Script", "Waiting to start", u"achaput", "05/07/2015", "05/07/2015", "0"))

        self.db.commit()
        self.add_tasks_from_database()

        self.item_added = False

    def remove_task(self):

        selected_rows = self.taskManagerTableWidget.selectedItems()
        for row in selected_rows:
            row_to_delete = row.row() + 1
            self.cursor.execute('''DELETE FROM tasks WHERE rowid = ? ''', (row_to_delete,))

        self.db.commit()
        self.item_added = True
        self.add_tasks_from_database()

    def calculate_days_left(self, task_start_widget, task_end_widget, task_time_left_widget):

        date_start = task_start_widget.date()
        date_end = task_end_widget.date()
        days_left = str(date_start.daysTo(date_end))
        task_time_left_widget.setText(days_left)

    def set_calendar(self, QDateEdit):
        calendar_widget = QtGui.QCalendarWidget()
        calendar_widget.showToday()
        calendar_widget.setStyleSheet("background-color: white;")
        QDateEdit.setCalendarPopup(True)
        QDateEdit.setCalendarWidget(calendar_widget)
        QDateEdit.dateChanged.connect(self.update_tasks)

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


