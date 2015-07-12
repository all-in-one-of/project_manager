#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore

class TaskCommentWidget(QtGui.QDialog):

    def __init__(self, task_id):
        super(TaskCommentWidget, self).__init__()

        self.task_id = task_id
        self.setWindowTitle("Comments for task #" + self.task_id)



