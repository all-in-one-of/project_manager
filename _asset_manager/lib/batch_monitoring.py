#!/usr/bin/env python
# coding=utf-8

import sys
import os
import subprocess

import socket

import sqlite3
import time
from threading import Thread
from PyQt4 import QtGui, QtCore

class Monitoring(QtGui.QWidget):
    def __init__(self):
        super(Monitoring, self).__init__()

        self.db_path = "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_database/rendering.sqlite"
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()

        self.today = time.strftime("%d/%m/%Y", time.gmtime())

        self.computer_id = socket.gethostname()

        self.cursor.execute('''''')

        self.thread = StartRendering(self, working_seconds_for_today, idle_seconds_for_today)
        self.connect(self.thread, QtCore.SIGNAL("change_background_color"), self.change_background_color)
        self.connect(self.thread, QtCore.SIGNAL("add_to_db"), self.add_to_db)




class StartRendering(QtCore.QThread):
    def __init__(self, gui, working_seconds_for_today, idle_seconds_for_today):
        super(StartRendering, self).__init__()

        self.gui = gui

        self.bg_red = False
        self.positions = []
        self.pos_x = 0
        self.idle_seconds = 0
        self.idle_minutes = 0
        self.timer_seconds = 0
        self.timer_minutes = 0

        self.total_working_seconds = int(working_seconds_for_today)
        self.total_idle_seconds = int(idle_seconds_for_today)

        self.seconds_before_adding = 4

        self.t = threading.Thread(target=self.working_timer)
        self.t.daemon = True
        self.t.start()

    def working_timer(self):

        idle_time = self.get_idle_duration()
        if self.idle_minutes >= 3:
            self.emit(QtCore.SIGNAL("change_background_color"), "black")
            self.timer_seconds = 0
            self.timer_minutes = 0
            self.gui.nbr_of_breaks += 1
            self.emit(QtCore.SIGNAL("add_to_db"), "break")

        self.idle_minutes = 0
        self.idle_seconds = 0

        while idle_time <= 1:
            idle_time = self.get_idle_duration()
            self.total_working_seconds += 1
            self.timer_seconds += 1
            self.add_minutes()
            self.gui.timerLbl.setText(
                "Working for: {0}:{1}".format(str(self.timer_minutes).zfill(2), str(self.timer_seconds).zfill(2)))
            if self.timer_minutes >= 30:
                self.emit(QtCore.SIGNAL("change_background_color"), "red")

            time.sleep(1)

        self.idle_timer()


app = QtGui.QApplication([])
Monitoring()
app.exec_()
