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
from lib.module import Lib


class TaskManager(object):

    def __init__(self):



        self.tm_departments = {"Script": 0, "Storyboard": 1, "References": 2, "Concepts": 3, "Modeling": 4, "Texturing": 5,
                            "Rigging": 6, "Animation": 7, "Simulation": 8, "Shading": 9, "Layout": 10,
                            "DMP": 11, "Compositing": 12, "Editing": 13, "RnD": 14}

        self.status = {"Ready to Start": 0, "In Progress": 1, "On Hold": 2, "Waiting for Approval": 3, "Retake": 4,
                       "Done": 5}

        self.members_id = {"achaput": 0, "costiguy": 1, "cgonnord": 2, "dcayerdesforges": 3,
                           "earismendez": 4, "erodrigue": 5, "jberger": 6, "lgregoire": 7,
                           "lclavet": 8, "mchretien": 9, "mbeaudoin": 10,
                           "mroz": 11, "obolduc": 12, "slachapelle": 13, "thoudon": 14,
                           "vdelbroucq": 15, "yjobin": 16, "yshan": 17}

        # The itemChanged signal connection of the QTableWidget is fired every time
        # an item changes on the tablewidget. Therefore whenever we're adding an entry to the tablewidget, the itemChanged
        # slot is fired. The item_added variable is used to know when the user adds a row and when a user update a row
        # if item_added is set to true, then the user is simply adding a row and not updating it.
        # Therefore, the update_task function is disabled when the item_added variable is set to true.

        self.item_added = False
        self.tmTableWidget.setStyleSheet("color: white;")
        self.tmAddTaskBtn.clicked.connect(self.add_task)
        self.tmRemoveTaskBtn.clicked.connect(self.remove_task)

        self.tmFilterByDeptComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByStatusComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByMemberComboBox.currentIndexChanged.connect(self.filter)
        self.tmBidOperationComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByBidComboBox.valueChanged.connect(self.filter)

        self.tmFilterByDeptComboBox.addItem("None")
        self.tmFilterByDeptComboBox.addItems(self.tm_departments.keys())
        self.tmFilterByStatusComboBox.addItem("None")
        self.tmFilterByStatusComboBox.addItems(self.status.keys())
        self.tmFilterByMemberComboBox.addItem("None")
        self.tmFilterByMemberComboBox.addItems(sorted(self.members.values()))

    def add_tasks_from_database(self):

        for i in reversed(xrange(self.tmTableWidget.rowCount())):
            self.tmTableWidget.removeRow(i)


        all_tasks = self.cursor.execute('''SELECT * FROM tasks''').fetchall()

        self.widgets = {}

        inversed_index = len(all_tasks) - 1


        # Add existing tasks to task table
        for i, task in enumerate(reversed(all_tasks)):

            self.tmTableWidget.insertRow(0)

            # Adding tasks description
            task_description = task[3] #Ex: Ajouter références pour le musée
            task_description_item = QtGui.QTableWidgetItem()
            task_description_item.setText(task_description)
            self.tmTableWidget.setItem(0, 0, task_description_item)
            self.widgets[str(inversed_index) + ":0"] = task_description_item


            # Adding department combo boxes
            task_department = task[4] #Ex: Compositing
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Script", "Storyboard", "References", "Concepts", "Modeling", "Texturing",
                            "Rigging", "Animation", "Simulation", "Shading", "Layout",
                            "DMP", "Compositing", "Editing", "RnD"])
            combo_box.setCurrentIndex(self.tm_departments[task_department])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 1, combo_box)
            self.widgets[str(inversed_index) + ":1"] = combo_box

            # Adding task status
            task_status = task[5] #Ex: En cours
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Ready to Start", "In Progress", "On Hold", "Waiting for Approval", "Retake", "Done"])
            combo_box.setCurrentIndex(self.status[task_status])
            combo_box.setEditable(False)
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.change_cell_status_color(combo_box, task_status)
            self.tmTableWidget.setCellWidget(0, 2, combo_box)
            self.widgets[str(inversed_index) + ":2"] = combo_box

            # Adding assigned to
            task_assignation = task[6] #Ex: Amélie
            combo_box = QtGui.QComboBox()
            combo_box.addItems(
                [u"Amelie", u"Chloe", u"Christopher", u"David", u"Edwin", u"Etienne", u"Jeremy",
                 u"Laurence", u"Louis-Philippe", u"Marc-Antoine", u"Mathieu", u"Maxime", u"Olivier", u"Simon", u"Thibault",
                 u"Valentin", u"Yann", u"Yi"])
            combo_box.setCurrentIndex(self.members_id[task_assignation])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 3, combo_box)
            self.widgets[str(inversed_index) + ":3"] = combo_box


            # Adding task start
            task_date_start = task[7]
            date_start = QtCore.QDate.fromString(task_date_start, 'dd/MM/yyyy')
            date_start_edit = QtGui.QDateEdit()
            date_start_edit.setDate(date_start)
            date_start_edit.setDisplayFormat("dd/MM/yyyy")
            date_start_edit.setFrame(False)
            self.set_calendar(date_start_edit)
            self.tmTableWidget.setCellWidget(0, 4, date_start_edit)
            self.widgets[str(inversed_index) + ":4"] = date_start_edit


            # Adding task end
            task_date_end = task[8]
            date_end = QtCore.QDate.fromString(task_date_end, 'dd/MM/yyyy')
            date_end_edit = QtGui.QDateEdit()
            date_end_edit.setDate(date_end)
            date_end_edit.setDisplayFormat("dd/MM/yyyy")
            date_end_edit.setFrame(False)
            self.set_calendar(date_end_edit)
            self.tmTableWidget.setCellWidget(0, 5, date_end_edit)
            self.widgets[str(inversed_index) + ":5"] = date_end_edit


            # Adding days left
            days_left = str(date_start.daysTo(date_end))
            days_left_item = QtGui.QTableWidgetItem()
            days_left_item.setText(days_left)
            days_left_item.setTextAlignment(QtCore.Qt.AlignCenter)
            days_left_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tmTableWidget.setItem(0, 6, days_left_item)
            self.widgets[str(inversed_index) + ":6"] = days_left_item

            # Adding task bid
            task_bid = task[9]
            task_bid_item = QtGui.QSpinBox()
            task_bid_item.setValue(int(task_bid))
            task_bid_item.setAlignment(QtCore.Qt.AlignCenter)
            task_bid_item.setFrame(False)
            task_bid_item.setMaximum(500)
            task_bid_item.setMinimum(1)
            task_bid_item.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
            task_bid_item.valueChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 7, task_bid_item)
            self.widgets[str(inversed_index) + ":7"] = task_bid_item

            inversed_index -= 1


        self.tmTableWidget.cellChanged.connect(self.update_tasks)

    def update_tasks(self, value):

        if self.item_added == True:
            return

        # Get which item was clicked and its value
        clicked_widget = self.sender()
        clicked_widget_value = value

        # Get index from clicked_widget position
        if type(clicked_widget) == QtGui.QTableWidget:
            widget_row_index = clicked_widget_value
        else:
            widget_index = self.tmTableWidget.indexAt(clicked_widget.pos())
            widget_row_index = widget_index.row()


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

        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            Lib.message_box(self, text="Please select a project first")
            return

        self.item_added = True

        number_of_rows_to_add = self.tmNbrOfRowsToAddSpinBox.value()
        today_date = time.strftime("%d/%m/%Y", time.gmtime())

        for i in xrange(number_of_rows_to_add):
            self.cursor.execute(
                '''INSERT INTO tasks(project_name, task_description, task_department, task_status, task_assignation, task_start, task_end, task_bid) VALUES (?,?,?,?,?,?,?,?)''',
                (self.selected_project_name, "", "Script", "Ready to Start", u"achaput", today_date, today_date, "1"))

        self.db.commit()
        self.add_tasks_from_database()
        self.item_added = False

    def remove_task(self):

        selected_rows = self.tmTableWidget.selectedItems()
        for row in selected_rows:
            row_to_delete = row.row() + 1
            self.cursor.execute('''DELETE FROM tasks WHERE rowid = ? ''', (row_to_delete,))

        self.db.commit()
        self.item_added = True
        self.add_tasks_from_database()

    def filter(self):

        number_of_rows = self.tmTableWidget.rowCount()
        for row_index in xrange(number_of_rows):
            # Retrieve text / value of filter widgets
            department_filter = self.tmFilterByDeptComboBox.currentText()
            status_filter = self.tmFilterByStatusComboBox.currentText()
            member_filter = self.tmFilterByMemberComboBox.currentText()
            bid_filter = self.tmFilterByBidComboBox.value()
            bid_operation = self.tmBidOperationComboBox.currentText()

            # Retrieve value of current row items
            department = self.tmTableWidget.cellWidget(row_index, 1).currentText()
            status = self.tmTableWidget.cellWidget(row_index, 2).currentText()
            member = self.tmTableWidget.cellWidget(row_index, 3).currentText()
            bid = self.tmTableWidget.cellWidget(row_index, 7).value()

            # If filters are set to default value, set the filters variables to the current row values
            if department_filter == "None": department_filter = department
            if status_filter == "None" : status_filter = status
            if member_filter == "None" : member_filter = member
            if bid_filter == 0: bid_filter = bid

            if str(bid_operation) == ">":
                if department_filter == department and status_filter == status and member_filter == member and bid_filter <= bid:
                    self.tmTableWidget.showRow(row_index)
                else:
                    self.tmTableWidget.hideRow(row_index)

            elif str(bid_operation) == "<":
                if department_filter == department and status_filter == status and member_filter == member and bid_filter >= bid:
                    self.tmTableWidget.showRow(row_index)
                else:
                    self.tmTableWidget.hideRow(row_index)

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

        if task_status == "Ready to Start":
            cell_item.setStyleSheet("background-color: #872d2c;")
        elif task_status == "In Progress":
            cell_item.setStyleSheet("background-color: #3292d5;")
        elif task_status == "On Hold":
            cell_item.setStyleSheet("background-color: #eb8a18;")
        elif task_status == "Waiting for Approval":
            cell_item.setStyleSheet("background-color: #eb8a18")
        elif task_status == "Retake":
            cell_item.setStyleSheet("background-color: #872d2c")
        elif task_status == "Done":
            cell_item.setStyleSheet("background-color: #4b4b4b;")


