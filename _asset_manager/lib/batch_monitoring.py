#!/usr/bin/env python
# coding=utf-8

import sys
import os
import subprocess

import socket

from datetime import date
from datetime import datetime
from dateutil import relativedelta

import sqlite3
import time
import threading
from PyQt4 import QtGui, QtCore

class Monitoring(QtGui.QWidget):
    def __init__(self):

        self.computer_id = socket.gethostname()
        self.get_classroom_from_id()
        self.today = time.strftime("%d/%m/%Y", time.gmtime())

        self.db_path = "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_database/rendering.sqlite"
        self.db_path = "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_database/pub.sqlite"

        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()

        self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()
        if self.computer_status == None:
            self.cursor.execute('''INSERT INTO computers(computer_id, classroom, status, scene_path, seq, shot, last_active, rendered_frames, current_frame) VALUES(?,?,?,?,?,?,?,?,?,?)''', (self.computer_id, self.classroom, "Idle", "---", "---", "---", "---", "0", "0"))
            self.db.commit()

        self.check_status()

    def check_status(self):
        self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()[0]
        while self.computer_status == "Idle":
            print("Computer is idle...")
            last_active = datetime.now().strftime("%d/%m/%Y %H:%M")
            self.cursor.execute('''UPDATE computers SET last_active=? WHERE computer_id=?''', (last_active, self.computer_id, ))
            self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()[0]
            self.db.commit()
            time.sleep(2)

        self.start_render()


    def start_render(self):
        p = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.13/bin/hython.exe", "H:/01-NAD/_pipeline/_utilities/_asset_manager/lib/software_scripts/houdini_start_render.py",
                              "Z:/Groupes-cours/NAND999-A15-N01/pub/assets/lay/pub_prk_xxxx_lay_parkingLayout_01.hipnc", "1002"], stdout=subprocess.PIPE)
        for line in p.stdout:
            print(line)

        while self.computer_status == "Rendering":
            print("Computer is rendering...")
            self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()[0]
            time.sleep(2)

        self.check_status()

    def get_classroom_from_id(self):
        if self.computer_id.split("-")[0] == "320":
            self.classroom = "Prod-4"
        elif self.computer_id.split("-")[0] == "326":
            self.classroom = "Prod-1,2,3"
        elif self.computer_id.split("-")[0] == "328":
            self.classroom = "Debevec"
        elif self.computer_id.split("-")[0] == "336":
            self.classroom = "Evans"
        elif self.computer_id.split("-")[0] == "337":
            self.classroom = "Sutherland"
        elif self.computer_id.split("-")[0] == "338":
            self.classroom = "Gouraud"
        else:
            self.classroom = "Unknown"
