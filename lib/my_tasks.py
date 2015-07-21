#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import operator



class MyTasks(object):

    def __init__(self):
        self.mt_departments = {"Script": 0, "Storyboard": 1, "References": 2, "Concepts": 3, "Modeling": 4, "Texturing": 5,
                            "Rigging": 6, "Animation": 7, "Simulation": 8, "Shading": 9, "Layout": 10,
                            "DMP": 11, "Compositing": 12, "Editing": 13, "RnD": 14}

        self.mt_departments_shortname = {"Script": "spt", "Storyboard": "stb", "References": "ref", "Concepts": "cpt",
                                         "Modeling": "mod", "Texturing": "tex", "Rigging": "rig", "Animation": "anm",
                                         "Simulation": "sim", "Shading": "shd", "Layout": "lay", "DMP": "dmp",
                                         "Compositing": "cmp", "Editing": "edt", "RnD": "rnd"}

        self.mt_status = {"Ready to Start": 0, "In Progress": 1, "On Hold": 2, "Waiting for Approval": 3, "Retake": 4}

        self.members_id = {"achaput": 0, "costiguy": 1, "cgonnord": 2, "dcayerdesforges": 3,
                           "earismendez": 4, "erodrigue": 5, "jberger": 6, "lgregoire": 7,
                           "lclavet": 8, "mchretien": 9, "mbeaudoin": 10,
                           "mroz": 11, "obolduc": 12, "slachapelle": 13, "thoudon": 14,
                           "vdelbroucq": 15, "yjobin": 16, "yshan": 17}

        self.mt_item_added = False
        self.mtTableWidget.setStyleSheet("color: white;")

        self.mtFilterByProjectComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterBySequenceComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterByShotComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterByDeptComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterByStatusComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtMeOnlyCheckBox.stateChanged.connect(self.mt_meCheckBox_Clicked)
        self.mtFilterByMemberComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterByMemberComboBox.setEnabled(False)
        self.mtBidOperationComboBox.currentIndexChanged.connect(self.mt_filter)
        self.mtFilterByBidComboBox.valueChanged.connect(self.mt_filter)

        self.mtFilterByProjectComboBox.addItem("None")
        self.mtFilterByProjectComboBox.currentIndexChanged.connect(self.mt_load_sequences)

        self.mtFilterBySequenceComboBox.addItem("None")
        self.mtFilterBySequenceComboBox.currentIndexChanged.connect(self.mt_load_shots)

        self.loadTasksAsWidgetBtn.clicked.connect(self.open_tasks_as_desktop_widgets)
        self.mtRefreshTasksBtn.clicked.connect(self.mt_add_tasks_from_database)

        self.mtFilterByShotComboBox.addItem("None")
        self.mtFilterByDeptComboBox.addItem("None")
        self.mtFilterByDeptComboBox.addItems(self.mt_departments.keys())
        self.mtFilterByStatusComboBox.addItem("None")
        self.mtFilterByStatusComboBox.addItems(self.mt_status.keys())
        self.mtFilterByMemberComboBox.addItem("None")
        self.mtFilterByMemberComboBox.addItems(sorted(self.members.values()))

        self.mtHideDoneCheckBox.setCheckState(QtCore.Qt.Checked)
        self.mtHideDoneCheckBox.clicked.connect(self.mt_filter)

        # Add project to project filter combobox
        for project in self.projects:
            self.mtFilterByProjectComboBox.addItem(project)

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

            # Adding tasks id
            task_id = task[0] #Ex: 1, 5, 8
            task_id_item = QtGui.QTableWidgetItem()
            task_id_item.setText(str(task_id))
            task_id_item.setTextAlignment(QtCore.Qt.AlignCenter)
            task_id_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 0, task_id_item)
            self.mt_widgets[str(inversed_index) + ":0"] = task_id_item

            # Adding tasks description
            task_description = task[5] #Ex: Ajouter références pour le musée
            task_description_item = QtGui.QTableWidgetItem()
            task_description_item.setText(task_description)
            task_description_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 1, task_description_item)
            self.mt_widgets[str(inversed_index) + ":1"] = task_description_item

            # Adding department
            task_department = task[6] #Ex: Compositing
            task_department_item = QtGui.QTableWidgetItem()
            task_department_item.setText(task_department)
            task_department_item.setTextAlignment(QtCore.Qt.AlignCenter)
            task_department_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 2, task_department_item)
            self.mt_widgets[str(inversed_index) + ":2"] = task_department_item

            # Adding task status
            task_status = task[7] #Ex: En cours
            if task_status == "Done":
                task_status_item = QtGui.QTableWidgetItem()
                task_status_item.setText(task_status)
                task_status_item.setTextAlignment(QtCore.Qt.AlignCenter)
                task_status_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
                self.mtTableWidget.setItem(0, 3, task_status_item)
                self.mt_widgets[str(inversed_index) + ":3"] = task_status_item
            else:
                status_combobox = QtGui.QComboBox()
                status_combobox.addItems(["Ready to Start", "In Progress", "On Hold", "Waiting for Approval", "Retake"])
                status_combobox.setCurrentIndex(self.mt_status[task_status])
                status_combobox.currentIndexChanged.connect(self.mt_update_tasks)
                self.change_cell_status_color(status_combobox, task_status)
                self.mtTableWidget.setCellWidget(0, 3, status_combobox)
                self.mt_widgets[str(inversed_index) + ":3"] = status_combobox

            # Adding assigned to
            task_assignation = task[8] #Ex: Amélie
            task_assignation_item = QtGui.QTableWidgetItem()
            task_assignation_item.setText(self.members[task_assignation])
            task_assignation_item.setTextAlignment(QtCore.Qt.AlignCenter)
            task_assignation_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 4, task_assignation_item)
            self.mt_widgets[str(inversed_index) + ":4"] = task_assignation_item

            # Adding task start
            task_date_start = task[9]
            date_start = QtCore.QDate.fromString(task_date_start, 'dd/MM/yyyy')
            date_start_item = QtGui.QTableWidgetItem()
            date_start_item.setText(task_date_start)
            date_start_item.setTextAlignment(QtCore.Qt.AlignCenter)
            date_start_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 5, date_start_item)
            self.mt_widgets[str(inversed_index) + ":5"] = date_start_item

            # Adding task end
            task_date_end = task[10]
            date_end = QtCore.QDate.fromString(task_date_end, 'dd/MM/yyyy')
            date_end_item = QtGui.QTableWidgetItem()
            date_end_item.setText(task_date_end)
            date_end_item.setTextAlignment(QtCore.Qt.AlignCenter)
            date_end_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 6, date_end_item)
            self.mt_widgets[str(inversed_index) + ":6"] = date_end_item

            # Adding days left
            days_left = str(date_start.daysTo(date_end))
            days_left_item = QtGui.QTableWidgetItem()
            days_left_item.setText(days_left)
            days_left_item.setTextAlignment(QtCore.Qt.AlignCenter)
            days_left_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 7, days_left_item)
            self.mt_widgets[str(inversed_index) + ":7"] = days_left_item

            # Adding task bid
            task_bid = task[11] #Ex: 5, 12, 24
            task_bid_item = QtGui.QTableWidgetItem()
            task_bid_item.setText(task_bid)
            task_bid_item.setTextAlignment(QtCore.Qt.AlignCenter)
            task_bid_item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.mtTableWidget.setItem(0, 8, task_bid_item)
            self.mt_widgets[str(inversed_index) + ":8"] = task_bid_item

            # Adding sequence name
            all_sequences = self.cursor.execute('''SELECT sequence_name FROM sequences WHERE project_name=?''', (self.selected_project_name,)).fetchall()
            all_sequences = [str(i[0]) for i in all_sequences]
            all_sequences.insert(0, "xxx")
            task_sequence_name = task[2] #Ex: mus, cri, fru
            combo_box = QtGui.QComboBox()
            combo_box.addItems(all_sequences)
            index = combo_box.findText(task_sequence_name, QtCore.Qt.MatchFixedString)
            combo_box.setCurrentIndex(index)
            combo_box.currentIndexChanged.connect(self.mt_update_tasks)
            self.mtTableWidget.setCellWidget(0, 9, combo_box)
            self.mt_widgets[str(inversed_index) + ":9"] = combo_box

            # Adding shot number
            all_shots = self.cursor.execute('''SELECT shot_number FROM shots WHERE project_name=? AND sequence_name=?''', (self.selected_project_name, task_sequence_name)).fetchall()
            all_shots = [str(i[0]) for i in all_shots]
            all_shots.insert(0, "xxxx")
            task_shot_number = task[3] #Ex: 0010, 0025, 0200
            combo_box = QtGui.QComboBox()
            combo_box.addItems(all_shots)
            index = combo_box.findText(task_shot_number, QtCore.Qt.MatchFixedString)
            combo_box.setCurrentIndex(index)
            combo_box.currentIndexChanged.connect(self.mt_update_tasks)
            self.mtTableWidget.setCellWidget(0, 10, combo_box)
            self.mt_widgets[str(inversed_index) + ":10"] = combo_box

            # Adding assets
            all_assets = self.cursor.execute('''SELECT asset_name FROM assets WHERE project_name=? AND sequence_name=? AND shot_number=?''', (self.selected_project_name, task_sequence_name, task_shot_number)).fetchall()
            all_assets = [str(i[0]) for i in all_assets]
            all_assets.insert(0, "xxxxx")
            task_asset_name = task[4] #Ex: lion, pierrePrecieuse
            combo_box = QtGui.QComboBox()
            combo_box.addItems(all_assets)
            index = combo_box.findText(task_asset_name, QtCore.Qt.MatchFixedString)
            combo_box.setCurrentIndex(index)
            combo_box.currentIndexChanged.connect(self.mt_update_tasks)
            self.mtTableWidget.setCellWidget(0, 11, combo_box)
            self.mt_widgets[str(inversed_index) + ":11"] = combo_box

            # If hide done checkbox is checked and current task is done, hide it
            if self.mtHideDoneCheckBox.isChecked():
                if task_status == "Done":
                    self.mtTableWidget.hideRow(0)

            inversed_index -= 1

        self.mtTableWidget.cellChanged.connect(self.mt_update_tasks)
        self.mtTableWidget.resizeColumnsToContents()

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

        self.cursor.execute(
            '''UPDATE tasks SET task_status=? WHERE task_id=?''',
            (task_status, task_id,))

        self.change_cell_status_color(task_status_widget, task_status)

        self.db.commit()

    def mt_filter(self):

        number_of_rows = self.mtTableWidget.rowCount()
        for row_index in xrange(number_of_rows):
            # Retrieve text / value of filter widgets
            project_filter = str(self.mtFilterByProjectComboBox.currentText())
            sequence_filter = str(self.mtFilterBySequenceComboBox.currentText())
            shot_filter = str(self.mtFilterByShotComboBox.currentText())
            department_filter = self.mtFilterByDeptComboBox.currentText()
            status_filter = self.mtFilterByStatusComboBox.currentText()
            member_filter = self.mtFilterByMemberComboBox.currentText()
            bid_filter = self.mtFilterByBidComboBox.value()
            bid_operation = self.mtBidOperationComboBox.currentText()

            if self.mtMeOnlyCheckBox.checkState():
                member_filter = self.members[self.username]

            # Retrieve value of current row items
            task_id = str(self.mtTableWidget.item(row_index, 0).text())
            project = str(self.cursor.execute('''SELECT project_name FROM tasks WHERE task_id=?''', (task_id,)).fetchone()[0])
            sequence = str(self.mtTableWidget.cellWidget(row_index, 9).currentText())
            shot = str(self.mtTableWidget.cellWidget(row_index, 10).currentText())
            department = str(self.mtTableWidget.item(row_index, 2).text())
            try:
                status = self.mtTableWidget.cellWidget(row_index, 3).currentText()
            except:
                status = str(self.mtTableWidget.item(row_index, 3).text())
            member = str(self.mtTableWidget.item(row_index, 4).text())
            bid = self.mtTableWidget.item(row_index, 8).text()

            # If filters are set to default value, set the filters variables to the current row values
            if project_filter == "None": project_filter = project
            if sequence_filter == "None": sequence_filter = sequence
            if shot_filter == "None": shot_filter = shot
            if department_filter == "None": department_filter = department
            if status_filter == "None" : status_filter = status
            if member_filter == "None" : member_filter = member
            if bid_filter == 0: bid_filter = bid

            if str(bid_operation) == ">=": bid_result = operator.le(bid_filter, bid)
            elif str(bid_operation) == "<=": bid_result = operator.ge(bid_filter, bid)

            if project_filter == project and sequence_filter == sequence and shot_filter == shot and department_filter == department and status_filter == status and member_filter == member and bid_result:
                if self.mtHideDoneCheckBox.isChecked():
                    if status == "Done":
                        self.mtTableWidget.hideRow(row_index)
                    else:
                        self.mtTableWidget.showRow(row_index)
                else:
                    self.mtTableWidget.showRow(row_index)
            else:
                self.mtTableWidget.hideRow(row_index)

    def mt_load_sequences(self):
        current_project = str(self.mtFilterByProjectComboBox.currentText())
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
            self.mtFilterByMemberComboBox.setEnabled(False)
        else:
            self.mtFilterByMemberComboBox.setEnabled(True)

        self.mt_filter()

    def open_tasks_as_desktop_widgets(self):
        all_tasks = self.cursor.execute('''SELECT * FROM tasks WHERE task_assignation=?''', (self.username,)).fetchall()
        self.tasks = {}
        for i, task in enumerate(all_tasks):
            self.tasks[task] = DesktopWidget(task[5], task[6], task[7], task[9], task[10], task[11])
            self.tasks[task].show()

            self.tasks[task].move(10, 10 + (i * 60))


