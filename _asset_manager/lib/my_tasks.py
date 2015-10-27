#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import operator

class MyTasks(object):

    def __init__(self):
        self.mt_departments = {"Misc": 0, "Script": 1, "Storyboard": 2, "References": 3, "Concepts": 4, "Modeling": 5, "Texturing": 6,
                            "Rigging": 7, "Animation": 8, "Simulation": 9, "Shading": 10, "Camera": 11, "Lighting": 12, "Layout": 13,
                            "DMP": 14, "Compositing": 15, "Editing": 16, "RnD": 17}

        self.mt_status = {"Ready to Start": 0, "In Progress": 1, "On Hold": 2, "Waiting for Approval": 3, "Retake": 4}

        self.members_id = {"costiguy": 0, "cgonnord": 1,
                           "erodrigue": 2, "jberger": 3, "lgregoire": 4,
                           "lclavet": 5, "mbeaudoin": 6,
                           "mroz": 7, "obolduc": 8, "slachapelle": 9, "thoudon": 10,
                           "vdelbroucq": 11, "yjobin": 12, "yshan": 13, "acorbin": 14}

        self.mt_task_priority_dic = {"High": 0, "Default": 1, "Low": 2}

        self.mt_item_added = False
        self.mtTableWidget.setStyleSheet("color: black;")

        self.mtTableWidget.itemDoubleClicked.connect(self.mtTableWidget_DoubleClicked)

        self.mtFilterBySequenceComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterByShotComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterByDeptComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterByStatusComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtMeOnlyCheckBox.stateChanged.connect(self.mt_meCheckBox_Clicked)
        self.mtFilterByMemberComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterByMemberComboBox.setEnabled(False)
        self.mtBidOperationComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterByBidComboBox.valueChanged.connect(self.mt_filter)
        self.mtDaysLeftComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterByDaysLeftSpinBox.valueChanged.connect(self.mt_filter)

        self.mtFilterBySequenceComboBox.addItem("None")
        self.mtFilterBySequenceComboBox.currentIndexChanged.connect(self.mt_load_shots)

        self.mtFilterByShotComboBox.addItem("None")
        self.mtFilterByDeptComboBox.addItem("None")
        self.mtFilterByDeptComboBox.addItems(self.mt_departments.keys())
        self.mtFilterByStatusComboBox.addItem("None")
        self.mtFilterByStatusComboBox.addItems(self.mt_status.keys())
        self.mtFilterByMemberComboBox.addItem("None")
        self.mtFilterByMemberComboBox.addItems(sorted(self.members.values()))
        self.mtFilterByMemberComboBox.setCurrentIndex(self.mtFilterByMemberComboBox.findText(self.members[self.username]))

        self.mtHideDoneCheckBox.setCheckState(QtCore.Qt.Checked)
        self.mtHideDoneCheckBox.clicked.connect(self.mt_filter)

        self.mt_load_sequences()

        self.mt_add_tasks_from_database()

    def mt_add_tasks_from_database(self):

        for i in reversed(xrange(self.mtTableWidget.rowCount())):
            self.mtTableWidget.removeRow(i)


        all_tasks = self.cursor.execute('''SELECT * FROM tasks''').fetchall()
        self.mt_widgets = {}

        inversed_index = len(all_tasks) - 1

        # Add existing tasks to task table
        for row_index, task in enumerate(reversed(all_tasks)):
            self.mtTableWidget.insertRow(0)

            id = task[0]
            project_name = task[1]
            sequence_name = task[2]
            shot_number = task[3]
            asset_id = task[4]
            description = task[5]
            department = task[6]
            status = task[7]
            assignation = task[8]
            end = task[9]
            bid = task[10]
            confirmation = task[11]
            priority = task[12]

            if id == None: id = ""
            if project_name == None: project_name = ""
            if sequence_name == None: sequence_name = ""
            if shot_number == None: shot_number = ""
            if asset_id == None: asset_id = ""
            if description == None: description = ""
            if department == None: department = ""
            if status == None: status = ""
            if assignation == None: assignation = ""
            if end == None: end = ""
            if bid == None: bid = ""
            if confirmation == None: confirmation = ""
            if priority == None: priority = ""

            task = self.Task(self, id, project_name, sequence_name, shot_number, asset_id, description, department,
                             status, assignation, end, bid, confirmation, priority)

            # Adding tasks id
            number_of_comments = self.cursor.execute('''SELECT asset_id FROM comments WHERE comment_type="task" AND asset_id=?''', (task.id,)).fetchall()
            task_id_item = QtGui.QTableWidgetItem()
            task_id_item.setData(QtCore.Qt.UserRole, task)
            task_id_item.setText(str(task.id))
            task_id_item.setTextAlignment(QtCore.Qt.AlignCenter)
            task_id_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            if len(number_of_comments) > 0:
                task_id_item.setBackground(QtGui.QColor(189, 255, 0))

            self.mtTableWidget.setItem(0, 0, task_id_item)
            self.mt_widgets[str(inversed_index) + ":0"] = task_id_item

            # Adding tasks description
            task_description_item = QtGui.QTableWidgetItem()
            task_description_item.setText(task.description)
            task_description_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 1, task_description_item)
            self.mt_widgets[str(inversed_index) + ":1"] = task_description_item

            # Adding department
            task_department_item = QtGui.QTableWidgetItem()
            task_department_item.setText(task.department)
            task_department_item.setTextAlignment(QtCore.Qt.AlignCenter)
            task_department_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 2, task_department_item)
            self.mt_widgets[str(inversed_index) + ":2"] = task_department_item

            # Adding task status
            if task.status == "Done":
                task_status_item = QtGui.QTableWidgetItem()
                task_status_item.setText(task.status)
                task_status_item.setTextAlignment(QtCore.Qt.AlignCenter)
                task_status_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.mtTableWidget.setItem(0, 3, task_status_item)
                self.mt_widgets[str(inversed_index) + ":3"] = task_status_item
            else:
                status_combobox = QtGui.QComboBox()
                status_combobox.addItems(["Ready to Start", "In Progress", "On Hold", "Waiting for Approval", "Retake"])
                status_combobox.setCurrentIndex(self.mt_status[task.status])
                status_combobox.currentIndexChanged.connect(self.mt_update_tasks)
                if task.assignation != self.username:
                    status_combobox.setDisabled(True)
                self.change_cell_status_color(status_combobox, task.status)
                self.mtTableWidget.setCellWidget(0, 3, status_combobox)
                self.mt_widgets[str(inversed_index) + ":3"] = status_combobox

            # Adding assigned to
            task_assignation_item = QtGui.QTableWidgetItem()
            task_assignation_item.setText(self.members[task.assignation])
            task_assignation_item.setTextAlignment(QtCore.Qt.AlignCenter)
            task_assignation_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 4, task_assignation_item)
            self.mt_widgets[str(inversed_index) + ":4"] = task_assignation_item

            # Adding task end
            date_start = QtCore.QDate.currentDate()
            date_end = QtCore.QDate.fromString(task.end, 'dd/MM/yyyy')
            date_end_item = QtGui.QTableWidgetItem()
            date_end_item.setText(task.end)
            date_end_item.setTextAlignment(QtCore.Qt.AlignCenter)
            date_end_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 5, date_end_item)
            self.mt_widgets[str(inversed_index) + ":5"] = date_end_item

            # Adding days left
            days_left = str(date_start.daysTo(date_end))
            days_left_item = QtGui.QTableWidgetItem()
            days_left_item.setText(days_left)
            days_left_item.setTextAlignment(QtCore.Qt.AlignCenter)
            days_left_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 6, days_left_item)
            self.mt_widgets[str(inversed_index) + ":6"] = days_left_item

            # Adding task bid
            task_bid_item = QtGui.QTableWidgetItem()
            task_bid_item.setText(task.bid)
            task_bid_item.setTextAlignment(QtCore.Qt.AlignCenter)
            task_bid_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 7, task_bid_item)
            self.mt_widgets[str(inversed_index) + ":7"] = task_bid_item

            # Adding sequence name
            sequence_item = QtGui.QTableWidgetItem()
            sequence_item.setText(task.sequence)
            sequence_item.setTextAlignment(QtCore.Qt.AlignCenter)
            sequence_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 8, sequence_item)
            self.mt_widgets[str(inversed_index) + ":8"] = sequence_item

            # Adding shot number
            shot_item = QtGui.QTableWidgetItem()
            shot_item.setText(task.sequence)
            shot_item.setTextAlignment(QtCore.Qt.AlignCenter)
            shot_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 9, shot_item)
            self.mt_widgets[str(inversed_index) + ":9"] = shot_item

            # Adding assets
            asset_item = QtGui.QTableWidgetItem()
            asset_item.setTextAlignment(QtCore.Qt.AlignCenter)
            asset_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            asset_item.setText(str(task.asset_id))
            self.mtTableWidget.setItem(0, 10, asset_item)
            self.mt_widgets[str(inversed_index) + ":10"] = asset_item

            # Adding task priority
            priority_combobox = QtGui.QComboBox()
            priority_combobox.addItems(["High", "Default", "Low"])
            priority_combobox.setCurrentIndex(self.mt_task_priority_dic[task.priority])
            priority_combobox.currentIndexChanged.connect(self.mt_update_tasks)
            priority_combobox.setEnabled(False)
            self.change_cell_status_color(priority_combobox, task.priority)
            self.mtTableWidget.setCellWidget(0, 11, priority_combobox)
            self.mt_widgets[str(inversed_index) + ":11"] = priority_combobox

            # If hide done checkbox is checked and current task is done, hide it
            if self.mtHideDoneCheckBox.isChecked():
                if task.status == "Done":
                    self.mtTableWidget.hideRow(0)

            # If task is not confirmed, hide it:
            if task.confirmation == "0":
                self.mtTableWidget.hideRow(0)

            inversed_index -= 1

        self.mtTableWidget.cellChanged.connect(self.mt_update_tasks)
        self.mtTableWidget.resizeColumnsToContents()
        self.mtTableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

        self.mt_item_added = False
        self.mt_filter()

    def mt_update_tasks(self, value):
        if self.mt_item_added == True:
            return

        # Get which item was clicked and its value
        clicked_widget = self.sender()
        clicked_widget_value = value

        # Get index from clicked_widget position
        if type(clicked_widget) == QtGui.QTableWidget:
            widget_index = self.mtTableWidget.indexAt(clicked_widget.pos())
            widget_row_index = clicked_widget_value
            widget_row_column = widget_index.column()
        else:
            widget_index = self.mtTableWidget.indexAt(clicked_widget.pos())
            widget_row_index = widget_index.row()
            widget_row_column = widget_index.column()

        # Get widgets and their values from row index
        task_id_widget = self.mt_widgets[str(widget_row_index) + ":0"]
        task_id = str(task_id_widget.text())

        task_status_widget = self.mt_widgets[str(widget_row_index) + ":3"]
        task_status = str(task_status_widget.currentText())

        task = self.Task(self, task_id)
        task.get_infos_from_id()

        if task_status != task.status: task.change_status(task_status)

        self.change_cell_status_color(task_status_widget, task_status)

    def mt_filter(self):
        number_of_rows = self.mtTableWidget.rowCount()
        for row_index in xrange(number_of_rows):

            # Retrieve text / value of filter widgets
            sequence_filter = str(self.mtFilterBySequenceComboBox.currentText())
            shot_filter = str(self.mtFilterByShotComboBox.currentText())
            department_filter = self.mtFilterByDeptComboBox.currentText()
            status_filter = self.mtFilterByStatusComboBox.currentText()
            member_filter = self.mtFilterByMemberComboBox.currentText()
            daysleft_filter = self.mtFilterByDaysLeftSpinBox.value()
            daysleft_operation = self.mtDaysLeftComboBox.currentText()
            bid_filter = self.mtFilterByBidComboBox.value()
            bid_operation = self.mtBidOperationComboBox.currentText()

            if self.mtMeOnlyCheckBox.checkState():
                member_filter = self.members[self.username]

            # Retrieve value of current row items
            task_id = str(self.mtTableWidget.item(row_index, 0).text())
            task = self.Task(self, task_id)
            task.get_infos_from_id()

            # If task is not confirmed, hide it:
            if task.confirmation == "0" and task.status != "Done":
                self.mtTableWidget.hideRow(row_index)
                continue

            # If filters are set to default value, set the filters variables to the current row values
            if sequence_filter == "None": sequence_filter = task.sequence
            if shot_filter == "None": shot_filter = task.shot
            if department_filter == "None": department_filter = task.department
            if status_filter == "None" : status_filter = task.status
            if member_filter == "None" : member_filter = task.assignation
            for shortname, longname in self.members.iteritems():
                if longname == member_filter:
                    member_filter = shortname

            days_left = QtCore.QDate.currentDate().daysTo(QtCore.QDate.fromString(task.end, "dd/MM/yyyy"))
            if daysleft_filter == 0:
                daysleft_filter = days_left

            if bid_filter == 0: bid_filter = task.bid

            if str(bid_operation) == ">=": bid_result = operator.le(int(bid_filter), int(task.bid))
            elif str(bid_operation) == "<=": bid_result = operator.ge(int(bid_filter), int(task.bid))

            if str(daysleft_operation) == ">=": days_left_result = operator.le(int(daysleft_filter), int(days_left))
            elif str(daysleft_operation) == "<=": days_left_result = operator.ge(int(daysleft_filter), int(days_left))

            if sequence_filter == task.sequence and shot_filter == task.shot and department_filter == task.department and status_filter == task.status and str(member_filter) == str(task.assignation) and bid_result and days_left_result:
                if self.mtHideDoneCheckBox.isChecked():
                    if task.status == "Done":
                        self.mtTableWidget.hideRow(row_index)
                    else:
                        self.mtTableWidget.showRow(row_index)
                else:
                    self.mtTableWidget.showRow(row_index)
            else:
                self.mtTableWidget.hideRow(row_index)

        self.mtTableWidget.resizeColumnsToContents()
        self.mtTableWidget.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

    def mt_refresh_tasks_list(self):
        self.mt_item_added = True
        self.mt_add_tasks_from_database()

    def mt_load_sequences(self):
        current_project = str(self.projectList.currentText())
        if current_project == "None":
            return

        self.mt_sequences = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''', (current_project,)).fetchall()
        self.mt_sequences = [str(i[0]) for i in self.mt_sequences]

        self.mtFilterBySequenceComboBox.clear()
        self.mtFilterBySequenceComboBox.addItem("None")
        for seq in self.mt_sequences:
            self.mtFilterBySequenceComboBox.addItem(seq)

    def mt_load_shots(self):
        current_sequence = str(self.mtFilterBySequenceComboBox.currentText())
        if current_sequence == "None":
            return

        shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE sequence_name=?''', (current_sequence,)).fetchall()
        shots = [str(i[0]) for i in shots]

        self.mtFilterByShotComboBox.clear()
        self.mtFilterByShotComboBox.addItem("None")
        for shot in shots:
            self.mtFilterByShotComboBox.addItem(shot)

    def mt_meCheckBox_Clicked(self):

        if self.mtMeOnlyCheckBox.checkState():
            index = self.mtFilterByMemberComboBox.findText(self.members[self.username])
            self.mtFilterByMemberComboBox.setCurrentIndex(index)
            self.mtFilterByMemberComboBox.setEnabled(False)
        else:
            self.mtFilterByMemberComboBox.setCurrentIndex(0)
            self.mtFilterByMemberComboBox.setEnabled(True)

        self.mt_filter()

    def open_tasks_as_desktop_widgets(self):
        all_tasks = self.cursor.execute('''SELECT * FROM tasks WHERE task_assignation=?''', (self.username,)).fetchall()
        self.tasks = {}
        for i, task in enumerate(all_tasks):
            self.tasks[task] = self.Lib.DesktopWidget(task[5], task[6], task[7], task[9], task[10], task[11])
            self.tasks[task].show()

            self.tasks[task].move(10, 10 + (i * 60))

    def mtTableWidget_DoubleClicked(self, value):

        row = value.row()
        column = value.column()
        if column != 10:
            # Show comments for clicked task
            task_item = self.mtTableWidget.item(row, 0)
            self.selected_asset = task_item.data(QtCore.Qt.UserRole).toPyObject()
            if self.selected_asset == None:
                return  # User clicked on the days left cell

            self.commentLineEdit.setFocus()
            self.CommentWidget.load_comments(self)
            if column == 1:

                description_widget = self.mt_widgets["{0}:{1}".format(row, column)]

                dialog = QtGui.QDialog(self)
                dialog.setWindowTitle("Task Description")
                self.Lib.apply_style(self, dialog)

                layout = QtGui.QHBoxLayout(dialog)

                text_edit = QtGui.QTextEdit(dialog)
                text_edit.setEnabled(False)
                text_edit.setText(description_widget.text())
                layout.addWidget(text_edit)

                dialog.exec_()

        else:
            # Go to asset in asset loader
            asset_id_line_edit = self.widgets[str(row) + ":10"]
            for asset, asset_item in self.assets.items():
                asset_id = str(asset_id_line_edit.text())
                asset_item.setHidden(False)
                if asset_id == str(asset.id):
                    asset_item.setHidden(False)
                else:
                    asset_item.setHidden(True)

            self.Tabs.setCurrentWidget(self.Tabs.widget(0))

