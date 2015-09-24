#!/usr/bin/env python
# coding=utf-8

import sys
import os
import subprocess

from datetime import date
from datetime import datetime
from dateutil import relativedelta

import sqlite3
import time
import threading
from PyQt4 import QtGui, QtCore

class Monitoring(object):
    def __init__(self):
        pass


    def initialize_slave(self):
        print("Successfully started slave on computer #" + self.computer_id)

        self.get_classroom_from_id()

        self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()
        if self.computer_status == None:
            self.cursor.execute('''INSERT INTO computers(computer_id, classroom, status, scene_path, seq, shot, last_active, rendered_frames, current_frame) VALUES(?,?,?,?,?,?,?,?,?)''',
                                (self.computer_id, self.classroom, "Idle", "---", "---", "---", "---", "0", "0"))
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
        sequence = self.cursor.execute('''SELECT seq FROM computers WHERE computer_id=?''', (str(self.computer_id), )).fetchone()[0]
        shot = self.cursor.execute('''SELECT shot FROM computers WHERE computer_id=?''', (str(self.computer_id), )).fetchone()[0]
        shot = str(shot)
        first_frame = self.cursor.execute('''SELECT frame_start FROM shots WHERE sequence_name=? AND shot_number=?''', (sequence, shot,)).fetchone()[0]
        last_frame = self.cursor.execute('''SELECT frame_end FROM shots WHERE sequence_name=? AND shot_number=?''', (sequence, shot,)).fetchone()[0]

        render_path = self.selected_project_path + "\\assets\\rdr\\" + sequence

        rendered_frames = self.cursor.execute('''SELECT rendered_frames FROM computers WHERE seq=? AND shot=?''', (sequence, shot, )).fetchall()
        rendered_frames = list(sum(rendered_frames, ()))

        print(rendered_frames)
        current_frames = self.cursor.execute('''SELECT current_frame FROM computers WHERE seq=? AND shot=?''', (sequence, shot, )).fetchall()
        current_frames = [i[0] for i in current_frames]
        print(current_frames)

        return

        p = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.13/bin/mantra.exe", "-f", "Z:/Groupes-cours/NAND999-A15-N01/pub/assets/rdr/prk/prk.1001.ifd"], stdout=subprocess.PIPE)
        p.wait()
        for line in p.stdout:
            print(line)







        #while self.computer_status == "Rendering":
        #    print("Computer is rendering...")
        #    self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()[0]
        #    time.sleep(2)

        #self.check_status()

    def ada(self):
        while self.mantra_process.canReadLine():
            print(self.mantra_process.readLine())

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
