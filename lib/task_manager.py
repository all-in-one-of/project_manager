#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import operator
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

from random import randint

class TaskManager(object):

    def __init__(self):


        self.tm_departments = {"Script": 0, "Storyboard": 1, "References": 2, "Concepts": 3, "Modeling": 4, "Texturing": 5,
                            "Rigging": 6, "Animation": 7, "Simulation": 8, "Shading": 9, "Layout": 10,
                            "DMP": 11, "Compositing": 12, "Editing": 13, "RnD": 14}

        self.tm_departments_shortname = {"Script": "spt", "Storyboard": "stb", "References": "ref", "Concepts": "cpt",
                                         "Modeling": "mod", "Texturing": "tex", "Rigging": "rig", "Animation": "anm",
                                         "Simulation": "sim", "Shading": "shd", "Layout": "lay", "DMP": "dmp",
                                         "Compositing": "cmp", "Editing": "edt", "RnD": "rnd"}

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
        self.tmTableWidget.itemDoubleClicked.connect(self.tmTableWidget_DoubleClicked)
        self.tmAddTaskBtn.clicked.connect(self.add_task)
        self.tmRemoveTaskBtn.clicked.connect(self.remove_task)
        self.tmCompleteTaskBtn.clicked.connect(self.complete_task)
        self.tmShowBidCurveBtn.clicked.connect(self.show_bid_curve)

        self.tmHideDoneCheckBox.setCheckState(QtCore.Qt.Checked)
        self.tmHideDoneCheckBox.clicked.connect(self.filter)
        self.tmHideConfirmedCheckBox.clicked.connect(self.filter)

        self.tmRemoveTaskBtn.setStyleSheet("QPushButton {background-color: #872d2c;} QPushButton:hover {background-color: #1b81ca;}")
        self.tmCompleteTaskBtn.setStyleSheet("QPushButton {background-color: #98cd00;} QPushButton:hover {background-color: #1b81ca;}")

        self.tmFilterByProjectComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterBySequenceComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByShotComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByDeptComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByStatusComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByMemberComboBox.currentIndexChanged.connect(self.filter)
        self.tmBidOperationComboBox.currentIndexChanged.connect(self.filter)
        self.tmFilterByBidComboBox.valueChanged.connect(self.filter)

        self.tmFilterByProjectComboBox.addItem("None")
        self.tmFilterByProjectComboBox.currentIndexChanged.connect(self.tm_load_sequences)

        self.tmFilterBySequenceComboBox.addItem("None")
        self.tmFilterBySequenceComboBox.currentIndexChanged.connect(self.tm_load_shots)

        self.tmFilterByShotComboBox.addItem("None")
        self.tmFilterByDeptComboBox.addItem("None")
        self.tmFilterByDeptComboBox.addItems(self.tm_departments.keys())
        self.tmFilterByStatusComboBox.addItem("None")
        self.tmFilterByStatusComboBox.addItems(self.status.keys())
        self.tmFilterByMemberComboBox.addItem("None")
        self.tmFilterByMemberComboBox.addItems(sorted(self.members.values()))

        # Add project to project filter combobox
        for project in self.projects:
            self.tmFilterByProjectComboBox.addItem(project)

        self.add_tasks_from_database()

    def add_tasks_from_database(self):

        for i in reversed(xrange(self.tmTableWidget.rowCount())):
            self.tmTableWidget.removeRow(i)


        all_tasks = self.cursor.execute('''SELECT * FROM tasks''').fetchall()

        self.widgets = {}

        inversed_index = len(all_tasks) - 1

        # Add existing tasks to task table
        for row_index, task in enumerate(reversed(all_tasks)):

            self.tmTableWidget.insertRow(0)

            id = task[0]
            project_name = task[1]
            sequence_name = task[2]
            shot_number = task[3]
            asset_id = task[4]
            description = task[5]
            department = task[6]
            status = task[7]
            assignation = task[8]
            start = task[9]
            end = task[10]
            bid = task[11]
            comments = task[12]
            confirmation = task[13]
            if id == None: id = ""
            if project_name == None: project_name = ""
            if sequence_name == None: sequence_name = ""
            if shot_number == None: shot_number = ""
            if asset_id == None: asset_id = ""
            if description == None: description = ""
            if department == None: department = ""
            if status == None: status = ""
            if assignation == None: assignation = ""
            if start == None: start = ""
            if end == None: end = ""
            if bid == None: bid = ""
            if comments == None: comments = ""
            if confirmation == None: confirmation = ""

            task = self.Task(self, id, project_name, sequence_name, shot_number, asset_id, description, department, status, assignation, start, end, bid, comments, confirmation)

            # Adding tasks id
            task_id_item = QtGui.QTableWidgetItem()
            task_id_item.setData(QtCore.Qt.UserRole, task)
            task_id_item.setText(str(task.id))
            task_id_item.setTextAlignment(QtCore.Qt.AlignCenter)
            task_id_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            if task.confirmation == "0":
                task_id_item.setBackground(QtGui.QColor(135, 45, 44))
            else:
                task_id_item.setBackground(QtGui.QColor(152, 205, 0))
            self.tmTableWidget.setItem(0, 0, task_id_item)
            self.widgets[str(inversed_index) + ":0"] = task_id_item

            # Adding tasks description
            task_description_item = QtGui.QTableWidgetItem()
            task_description_item.setText(task.description)
            self.tmTableWidget.setItem(0, 1, task_description_item)
            self.widgets[str(inversed_index) + ":1"] = task_description_item

            # Adding department combo boxes
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Script", "Storyboard", "References", "Concepts", "Modeling", "Texturing",
                            "Rigging", "Animation", "Simulation", "Shading", "Layout",
                            "DMP", "Compositing", "Editing", "RnD"])
            combo_box.setCurrentIndex(self.tm_departments[task.department])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 2, combo_box)
            self.widgets[str(inversed_index) + ":2"] = combo_box

            # Adding task status
            combo_box = QtGui.QComboBox()
            combo_box.addItems(["Ready to Start", "In Progress", "On Hold", "Waiting for Approval", "Retake", "Done"])
            combo_box.setCurrentIndex(self.status[task.status])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.change_cell_status_color(combo_box, task.status)
            self.tmTableWidget.setCellWidget(0, 3, combo_box)
            self.widgets[str(inversed_index) + ":3"] = combo_box

            # Adding assigned to
            combo_box = QtGui.QComboBox()
            combo_box.addItems(
                [u"Amelie", u"Chloe", u"Christopher", u"David", u"Edwin", u"Etienne", u"Jeremy",
                 u"Laurence", u"Louis-Philippe", u"Marc-Antoine", u"Mathieu", u"Maxime", u"Olivier", u"Simon", u"Thibault",
                 u"Valentin", u"Yann", u"Yi"])
            combo_box.setCurrentIndex(self.members_id[task.assignation])
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 4, combo_box)
            self.widgets[str(inversed_index) + ":4"] = combo_box

            # Adding task start
            date_start = QtCore.QDate.fromString(task.start, 'dd/MM/yyyy')
            date_start_edit = QtGui.QDateEdit()
            date_start_edit.setDate(date_start)
            date_start_edit.setDisplayFormat("dd/MM/yyyy")
            date_start_edit.setFrame(False)
            self.set_calendar(date_start_edit)
            self.tmTableWidget.setCellWidget(0, 5, date_start_edit)
            self.widgets[str(inversed_index) + ":5"] = date_start_edit

            # Adding task end
            date_end = QtCore.QDate.fromString(task.end, 'dd/MM/yyyy')
            date_end_edit = QtGui.QDateEdit()
            date_end_edit.setDate(date_end)
            date_end_edit.setDisplayFormat("dd/MM/yyyy")
            date_end_edit.setFrame(False)
            self.set_calendar(date_end_edit)
            self.tmTableWidget.setCellWidget(0, 6, date_end_edit)
            self.widgets[str(inversed_index) + ":6"] = date_end_edit

            # Adding days left
            days_left = str(date_start.daysTo(date_end))
            days_left_item = QtGui.QTableWidgetItem()
            days_left_item.setText(days_left)
            days_left_item.setTextAlignment(QtCore.Qt.AlignCenter)
            days_left_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tmTableWidget.setItem(0, 7, days_left_item)
            self.widgets[str(inversed_index) + ":7"] = days_left_item

            # Adding task bid
            task_bid_item = QtGui.QSpinBox()
            task_bid_item.setValue(int(task.bid))
            task_bid_item.setAlignment(QtCore.Qt.AlignCenter)
            task_bid_item.setFrame(False)
            task_bid_item.setMaximum(500)
            task_bid_item.setMinimum(0)
            task_bid_item.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
            task_bid_item.valueChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 8, task_bid_item)
            self.widgets[str(inversed_index) + ":8"] = task_bid_item

            # Adding sequence name
            all_sequences = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''', (task.project,)).fetchall()
            all_sequences = [str(i[0]) for i in all_sequences]
            all_sequences.insert(0, "xxx")
            combo_box = QtGui.QComboBox()
            combo_box.addItems(all_sequences)
            index = combo_box.findText(task.sequence, QtCore.Qt.MatchFixedString)
            combo_box.setCurrentIndex(index)
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 9, combo_box)
            self.widgets[str(inversed_index) + ":9"] = combo_box

            # Adding shot number
            all_shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''', (task.project, task.sequence)).fetchall()
            all_shots = [str(i[0]) for i in all_shots]
            all_shots.insert(0, "xxxx")
            combo_box = QtGui.QComboBox()
            combo_box.addItems(all_shots)
            index = combo_box.findText(task.shot, QtCore.Qt.MatchFixedString)
            combo_box.setCurrentIndex(index)
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 10, combo_box)
            self.widgets[str(inversed_index) + ":10"] = combo_box

            # Adding assets
            all_assets = self.cursor.execute('''SELECT asset_name FROM assets WHERE sequence_name=? AND shot_number=?''', (task.sequence, task.shot,)).fetchall()
            all_assets = [str(i[0]) for i in all_assets]
            all_assets.insert(0, "xxxxx")
            combo_box = QtGui.QComboBox()
            combo_box.addItems(all_assets)
            if not task.asset_id == 0:
               asset_name_from_id = self.cursor.execute('''SELECT asset_name FROM assets WHERE asset_id=?''', (task.asset_id,)).fetchone()[0]
               index = combo_box.findText(asset_name_from_id, QtCore.Qt.MatchFixedString)
               combo_box.setCurrentIndex(index)
            combo_box.currentIndexChanged.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 11, combo_box)
            self.widgets[str(inversed_index) + ":11"] = combo_box

            # Add confirm task button
            confirm_button = QtGui.QPushButton("Confirm")
            confirm_button.clicked.connect(self.update_tasks)
            self.tmTableWidget.setCellWidget(0, 12, confirm_button)
            self.widgets[str(inversed_index) + ":12"] = confirm_button

            # If hide done checkbox is checked and current task is done, hide it
            if self.tmHideDoneCheckBox.isChecked():
                if task.status == "Done":
                    self.tmTableWidget.hideRow(0)

            inversed_index -= 1


        self.tmTableWidget.cellChanged.connect(self.update_tasks)
        self.tmTableWidget.resizeColumnsToContents()
        self.tmTableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)


        self.item_added = False

    def update_tasks(self, value):
        if self.item_added == True:
            return

        # Get which item was clicked and its value
        clicked_widget = self.sender()
        clicked_widget_value = value

        # Get index from clicked_widget position
        if type(clicked_widget) == QtGui.QTableWidget:
            widget_index = self.tmTableWidget.indexAt(clicked_widget.pos())
            widget_row_index = clicked_widget_value
            widget_row_column = widget_index.column()
        else:
            widget_index = self.tmTableWidget.indexAt(clicked_widget.pos())
            widget_row_index = widget_index.row()
            widget_row_column = widget_index.column()

        # Get widgets and their values from row index
        task_id_widget = self.widgets[str(widget_row_index) + ":0"]
        task_id = str(task_id_widget.text())

        task_description_widget = self.widgets[str(widget_row_index) + ":1"]
        task_description = unicode(task_description_widget.text())

        task_department_widget = self.widgets[str(widget_row_index) + ":2"]
        task_department = str(task_department_widget.currentText())

        task_status_widget = self.widgets[str(widget_row_index) + ":3"]
        task_status = str(task_status_widget.currentText())

        task_assignation_widget = self.widgets[str(widget_row_index) + ":4"]
        task_assignation = unicode(task_assignation_widget.currentText()).encode('UTF-8')
        # Get username from name (Ex: achaput from Amélie)
        for key, val in self.members.items():
            if task_assignation.decode('UTF-8') == val.decode('UTF-8'):
                task_assignation = key

        task_start_widget = self.widgets[str(widget_row_index) + ":5"]
        task_start = str(task_start_widget.date().toString("dd/MM/yyyy"))

        task_end_widget = self.widgets[str(widget_row_index) + ":6"]
        task_end = str(task_end_widget.date().toString("dd/MM/yyyy"))

        task_time_left_widget = self.widgets[str(widget_row_index) + ":7"]

        task_bid_widget = self.widgets[str(widget_row_index) + ":8"]
        task_bid = str(task_bid_widget.value())

        task_sequence_widget = self.widgets[str(widget_row_index) + ":9"]
        task_sequence = str(task_sequence_widget.currentText())

        task_shot_widget = self.widgets[str(widget_row_index) + ":10"]
        task_shot = str(task_shot_widget.currentText())

        task_asset_widget = self.widgets[str(widget_row_index) + ":11"]
        task_asset_name = str(task_asset_widget.currentText())

        task = self.Task(self, task_id)
        task.get_infos_from_id()

        # If clicked widget is a pushbutton, then confirm task
        if type(clicked_widget) == QtGui.QPushButton:
            task.change_confirmation(1)
            task_id_widget.setBackground(QtGui.QColor(152, 205, 0))
            self.add_log_entry(text="Louis-Philippe assigned a new {0} task to {1}".format(task.department, self.members[task.assignation]))
            return

        if task_description != task.description: task.change_description(task_description)
        if task_department != task.department: task.change_department(task_department)
        if task_status != task.status: task.change_status(task_status)
        if task_assignation != task.assignation: task.change_assignation(task_assignation)
        if task_start != task.start: task.change_start(task_start)
        if task_end != task.end: task.change_end(task_end)
        if task_bid != task.bid: task.change_bid(task_bid)

        # Sequence was changed -> Filter shots and assets from sequence and department
        if widget_row_column == 9 or widget_row_column == 2:
            # Get shots from current sequence
            shots_from_sequence = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''', (self.selected_project_name, task_sequence,)).fetchall()
            shots_from_sequence = [str(i[0]) for i in shots_from_sequence]
            shots_from_sequence.insert(0, "xxxx")
            # Add shots to shots combo box
            shot_combobox = self.widgets[str(widget_row_index) + ":10"]
            shot_combobox.clear()
            shot_combobox.addItems(shots_from_sequence)

            # Get assets from current sequence and shot
            assets_from_sequence = self.cursor.execute('''SELECT asset_name FROM assets WHERE project_name=? AND sequence_name=? AND asset_type=?''', (task.project, task_sequence, self.tm_departments_shortname[task.department],)).fetchall()
            assets_from_sequence = [str(i[0]) for i in assets_from_sequence]
            assets_from_sequence.insert(0, "xxxxx")
            # Add assets to asset combo box
            shot_combobox = self.widgets[str(widget_row_index) + ":11"]
            shot_combobox.clear()
            shot_combobox.addItems(assets_from_sequence)

        # Shot was changed -> Filter assets from sequence, shots and department
        elif widget_row_column == 10 or widget_row_column == 2:
            assets_from_shots = self.cursor.execute('''SELECT asset_name FROM assets WHERE project_name=? AND sequence_name=? AND shot_number=? AND asset_type=?''', (task.project, task_sequence, task.shot, self.tm_departments_shortname[task_department])).fetchall()
            assets_from_shots = [str(i[0]) for i in assets_from_shots]
            assets_from_shots.insert(0, "xxxxx")
            shot_combobox = self.widgets[str(widget_row_index) + ":11"]
            shot_combobox.clear()
            shot_combobox.addItems(assets_from_shots)

        task_sequence_widget = self.widgets[str(widget_row_index) + ":9"]
        task_sequence = str(task_sequence_widget.currentText())

        task_shot_widget = self.widgets[str(widget_row_index) + ":10"]
        task_shot = str(task_shot_widget.currentText())

        task_asset_widget = self.widgets[str(widget_row_index) + ":11"]
        task_asset_name = str(task_asset_widget.currentText())

        if task_sequence != task.sequence: task.change_sequence(task_sequence)
        if task_shot != task.shot: task.change_shot(task_shot)

        self.calculate_days_left(task_start_widget, task_end_widget, task_time_left_widget)
        self.change_cell_status_color(task_status_widget, task.status)

    def add_task(self, item_added):

        # Check if a project is selected
        if len(self.projectList.selectedItems()) == 0:
            self.Lib.message_box(self, text="Please select a project first")
            return

        self.item_added = True

        number_of_rows_to_add = self.tmNbrOfRowsToAddSpinBox.value()

        for i in xrange(number_of_rows_to_add):
            task = self.Task(self, 0, self.selected_project_name, "xxx", "xxxx", 0, "", "Script", "Ready to Start", u"achaput", self.today, self.today, "0", "0")
            task.add_task_to_db()

        self.add_tasks_from_database()
        self.item_added = False

    def remove_task(self):

        selected_rows = self.tmTableWidget.selectedItems()
        for row in selected_rows:
            task_id_widget = self.widgets[str(row.row()) + ":0"]
            task_id = str(task_id_widget.text())
            task = self.Task(self, task_id)
            task.get_infos_from_id()
            task.remove_task_from_db()

        self.item_added = True
        self.add_tasks_from_database()

    def complete_task(self):
        selected_rows = self.tmTableWidget.selectedItems()
        bid = 0
        for row in selected_rows:

            # Add bid value from each row
            cur_row_bid = self.widgets[str(row.row()) + ":8"]
            cur_row_bid = cur_row_bid.value()
            bid += cur_row_bid

            # Get task id for current row
            task_id_widget = self.widgets[str(row.row()) + ":0"]
            task_id = str(task_id_widget.text())
            task = self.Task(self, task_id)
            task.get_infos_from_id()
            task.change_confirmation(0)
            task.change_status("Done")


        today_bid = self.cursor.execute('''SELECT bid_log_amount FROM bid_log WHERE bid_log_day=?''', (self.today,)).fetchone()

        # Check if an entry already exists for today. If yes, add the bid to the daily bid. If not, create an entry
        if today_bid:
            today_bid = int(today_bid[0])
            bid += today_bid
            self.cursor.execute('''UPDATE bid_log SET bid_log_amount=? WHERE project_name=? AND bid_log_day=?''', (bid, self.selected_project_name, self.today,))
        else:
            self.cursor.execute('''INSERT INTO bid_log(project_name, bid_log_day, bid_log_amount) VALUES(?,?,?)''', (self.selected_project_name, self.today, bid))


        self.db.commit()
        self.item_added = True
        self.add_tasks_from_database()

    def filter(self):

        number_of_rows = self.tmTableWidget.rowCount()
        for row_index in xrange(number_of_rows):
            # Retrieve text / value of filter widgets
            project_filter = str(self.tmFilterByProjectComboBox.currentText())
            sequence_filter = str(self.tmFilterBySequenceComboBox.currentText())
            shot_filter = str(self.tmFilterByShotComboBox.currentText())
            department_filter = self.tmFilterByDeptComboBox.currentText()
            status_filter = self.tmFilterByStatusComboBox.currentText()
            member_filter = self.tmFilterByMemberComboBox.currentText()
            bid_filter = self.tmFilterByBidComboBox.value()
            bid_operation = self.tmBidOperationComboBox.currentText()

            task_id = str(self.tmTableWidget.item(row_index, 0).text())
            task = self.Task(self, task_id)
            task.get_infos_from_id()

            # If filters are set to default value, set the filters variables to the current row values
            if project_filter == "None": project_filter = task.project
            if sequence_filter == "None": sequence_filter = task.sequence
            if shot_filter == "None": shot_filter = task.shot
            if department_filter == "None": department_filter = task.department
            if status_filter == "None" : status_filter = task.status
            if member_filter == "None" : member_filter = self.members[task.assignation]
            if bid_filter == 0: bid_filter = task.bid


            if str(bid_operation) == ">=": bid_result = operator.le(int(bid_filter), int(task.bid))
            elif str(bid_operation) == "<=": bid_result = operator.ge(int(bid_filter), int(task.bid))

            if project_filter == task.project and sequence_filter == task.sequence and shot_filter == task.shot and department_filter == task.department and status_filter == task.status and member_filter == self.members[task.assignation] and bid_result:
                # Check each row for "Done" and "Confirmed"
                if self.tmHideDoneCheckBox.isChecked() and self.tmHideConfirmedCheckBox.isChecked():
                    if task.status == "Done":
                        self.tmTableWidget.hideRow(row_index)
                        continue
                    if task.confirmation == "1":
                        self.tmTableWidget.hideRow(row_index)
                        continue
                    self.tmTableWidget.showRow(row_index)
                # Check each row for "Done" only
                elif self.tmHideDoneCheckBox.isChecked() and not self.tmHideConfirmedCheckBox.isChecked():
                    if task.status == "Done":
                        self.tmTableWidget.hideRow(row_index)
                        continue
                    self.tmTableWidget.showRow(row_index)
                # Check each row for "Confirmed" only
                elif not self.tmHideDoneCheckBox.isChecked() and self.tmHideConfirmedCheckBox.isChecked():
                    if task.confirmation == "1":
                        self.tmTableWidget.hideRow(row_index)
                        continue
                    self.tmTableWidget.showRow(row_index)
                else:
                    self.tmTableWidget.showRow(row_index)
            else:
                self.tmTableWidget.hideRow(row_index)

        self.tmTableWidget.resizeColumnsToContents()
        self.tmTableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

    def tmTableWidget_DoubleClicked(self, value):
        row = value.row()
        column = value.column()

        task_item = self.tmTableWidget.item(row, column)
        task = task_item.data(QtCore.Qt.UserRole).toPyObject()
        if task == None: return # User clicked on the days left cell

        self.CommentWidget(self, task)




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

    def tm_load_sequences(self):
        current_project = str(self.tmFilterByProjectComboBox.currentText())
        if current_project == "None":
            return

        self.tm_sequences = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''', (current_project,)).fetchall()
        self.tm_sequences = [str(i[0]) for i in self.tm_sequences]

        self.tmFilterBySequenceComboBox.clear()
        self.tmFilterBySequenceComboBox.addItem("None")
        for seq in self.tm_sequences:
            self.tmFilterBySequenceComboBox.addItem(seq)

    def tm_load_shots(self):
        current_sequence = str(self.tmFilterBySequenceComboBox.currentText())
        if current_sequence == "None":
            return

        shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE sequence_name=?''', (current_sequence,)).fetchall()
        shots = [str(i[0]) for i in shots]

        self.tmFilterByShotComboBox.clear()
        self.tmFilterByShotComboBox.addItem("None")
        for shot in shots:
            self.tmFilterByShotComboBox.addItem(shot)

    def show_bid_curve(self):

        d1 = datetime.datetime(2015,07,11)
        d2 = datetime.datetime.now()
        total_days = (d2-d1).days

        bid_log_days = self.cursor.execute('''SELECT bid_log_day FROM bid_log WHERE project_name=? LIMIT ?''', (self.selected_project_name, total_days,)).fetchall()
        bid_log_amounts = self.cursor.execute('''SELECT bid_log_amount FROM bid_log WHERE project_name=? LIMIT ?''', (self.selected_project_name, total_days,)).fetchall()
        bid_log_days = [str(i[0]) for i in bid_log_days]
        bid_log_days = [datetime.datetime.strptime(d,'%d/%m/%Y').date() for d in bid_log_days]
        bid_log_amounts = [int(str(i[0])) for i in bid_log_amounts]

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.ylabel('Number of bidded hours')
        plt.xlabel('Date')
        plt.plot(bid_log_days, bid_log_amounts)
        plt.gcf().autofmt_xdate()
        plt.show()

