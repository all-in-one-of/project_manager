#!/usr/bin/env python
# coding=utf-8

import sys
import os
import subprocess
import socket
from glob import glob

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
        self.computer_id = socket.gethostname()

        print("Successfully started slave on computer #" + self.computer_id)

        self.get_classroom_from_id()

        self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()

        if self.computer_status == None:
            self.cursor.execute('''INSERT INTO computers(computer_id, classroom, status, rendered_ifd, current_ifd) VALUES(?,?,?,?,?)''',
                                (self.computer_id, self.classroom, "idle", "", ""))
            self.db.commit()
        elif type(self.computer_status) == type(()):
            if self.computer_status[0] == "rendering":
                self.cursor.execute('''UPDATE computers SET status="idle" WHERE computer_id=?''', (self.computer_id,))
                self.db.commit()

        t1 = threading.Thread(target=self.status_check, args=[])
        t1.start()

    def status_check(self):

        print("Checking Status")

        self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()[0]

        if self.computer_status != "rendering":
            while self.computer_status == "idle":
                print("Computer is idle...")
                last_active = datetime.now().strftime("%d/%m/%Y %H:%M")
                self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()[0]
                if self.computer_status == "logout":
                    print("Logging out")

                time.sleep(2)

            # Update status to rendering
            self.cursor.execute('''UPDATE computers SET status="rendering" WHERE computer_id=?''', (self.computer_id,))
            self.db.commit()
            self.computer_status = "rendering"

        time.sleep(2)
        t2 = threading.Thread(target=self.start_render, args=[])
        t2.start()

    def start_render(self):
        all_jobs = self.cursor.execute('''SELECT * FROM jobs''').fetchall()
        all_jobs = sorted(all_jobs, key=lambda x: x[2])
        current_job = all_jobs[0]
        current_seq = current_job[1].split("\\")[-1]

        if current_job[2] < 100:

            rendered_frames = self.cursor.execute('''SELECT rendered_ifd FROM computers''').fetchall()
            rendered_frames = list(sum(rendered_frames, ()))
            rendered_frames = [i.split(",") for i in rendered_frames]
            rendered_frames = list(sum(rendered_frames, []))

            current_frames = self.cursor.execute('''SELECT current_ifd FROM computers''').fetchall()
            current_frames = [i[0] for i in current_frames]

            all_rendered_frames = rendered_frames + current_frames

            resolution = self.cursor.execute('''SELECT resolution FROM jobs WHERE id=?''', (current_job[0],)).fetchone()[0]
            resolutionX = int(1920.0 * (float(resolution) / 100.0))
            resolutionY = int(1080.0 * (float(resolution) / 100.0))
            sampling = self.cursor.execute('''SELECT sampling FROM jobs WHERE id=?''', (current_job[0],)).fetchone()[0]

            ifd_path = current_job[1]


            ifd_files = glob(ifd_path + "\\*")
            ifd_files = [i for i in ifd_files if ".ifd" in i]

            ifd_files = [os.path.split(i)[-1].split(".")[1] for i in ifd_files]

            frames_to_render = list(set(ifd_files) - set(all_rendered_frames))
            if len(frames_to_render) == 0:
                print("No more frames to render for IFD {0}".format(ifd_path))
                self.cursor.execute('''UPDATE jobs SET priority=100 WHERE id=?''', (current_job[0], ))
                self.db.commit()

            else:
                print("Start render for frame #" + frames_to_render[0])
                self.cursor.execute('''UPDATE computers SET current_ifd=? WHERE computer_id=?''', (frames_to_render[0], self.computer_id, ))
                self.db.commit()

                p = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.13/bin/mantra.exe", "-V", "3", "-I", "resolution={0}x{1},sampling={2}x{2}".format(resolutionX, resolutionY, sampling) ,"-f", current_job[1] + "\\" + current_seq + "." + frames_to_render[0] + ".ifd"], stdout=subprocess.PIPE)

                while self.computer_status == "rendering":
                    print("Rendering frame #" + frames_to_render[0])
                    self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()[0]
                    time.sleep(2)

                if self.computer_status == "stop":
                    p.kill()
                elif self.computer_status == "logout":
                    print("Logging out")
            self.status_check()
        else:
            print("No more job")
            self.status_check()

    def start_render_old(self):
        sequence = self.cursor.execute('''SELECT seq FROM computers WHERE computer_id=?''', (str(self.computer_id), )).fetchone()[0]
        shot = str(self.cursor.execute('''SELECT shot FROM computers WHERE computer_id=?''', (str(self.computer_id), )).fetchone()[0])
        ifd = self.cursor.execute('''SELECT ifd FROM computers WHERE computer_id=?''', (str(self.computer_id), )).fetchone()[0]
        resolution = self.cursor.execute('''SELECT resolution FROM computers WHERE computer_id=?''', (str(self.computer_id), )).fetchone()[0]
        resolutionX = int(1920.0 * (float(resolution) / 100.0))
        resolutionY = int(1080.0 * (float(resolution) / 100.0))
        sampling = self.cursor.execute('''SELECT sampling FROM computers WHERE computer_id=?''', (str(self.computer_id), )).fetchone()[0]
        first_frame = self.cursor.execute('''SELECT frame_start FROM shots WHERE sequence_name=? AND shot_number=?''', (sequence, shot,)).fetchone()[0]
        last_frame = self.cursor.execute('''SELECT frame_end FROM shots WHERE sequence_name=? AND shot_number=?''', (sequence, shot,)).fetchone()[0]

        layout_file = self.cursor.execute('''SELECT layout_scene FROM sequences WHERE sequence_name=?''', (str(sequence), )).fetchone()[0]

        render_path = self.selected_project_path + "\\assets\\rdr\\" + sequence

        all_rendered_frames = current_frames + rendered_frames
        all_rendered_frames = [int(i) for i in all_rendered_frames]
        all_rendered_frames = sorted(all_rendered_frames)

        all_frames_to_render = list(range(first_frame, last_frame))
        frames_left_to_render = sorted(list(set(all_frames_to_render) - set(all_rendered_frames)))

        if int(ifd) == 1:
            p = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.13/bin/hython.exe", self.cur_path + "\\lib\\software_scripts\\houdini_create_ifd.py", str(last_frame), str(layout_file), str(shot)], stdout=subprocess.PIPE)
            p.wait()
            for line in p.stdout:
                if "No more frames to render" in line:
                    self.cursor.execute('''UPDATE computers SET ifd=0 WHERE computer_id=?''', (str(self.computer_id), ))
                    self.db.commcit()
                print(line)
        else:

            print("Rendering frame #" + str(frames_left_to_render[0]))

            self.cursor.execute('''UPDATE computers SET current_frame=? WHERE computer_id=?''', (frames_left_to_render[0], str(self.computer_id),))
            self.db.commit()

            p = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.13/bin/mantra.exe", "-I", "resolution={0}x{1},sampling={2}x{2}".format(resolutionX, resolutionY, sampling) ,"-f", "Z:/Groupes-cours/NAND999-A15-N01/pub/assets/rdr/" + sequence + "/" + sequence + "." + str(frames_left_to_render[0]) + ".ifd"], stdout=subprocess.PIPE)
            p.wait()
            for line in p.stdout:
                print(line)

            print("Finished frame")
            rendered_frames_for_computer = self.cursor.execute('''SELECT rendered_frames FROM computers WHERE computer_id=?''', (str(self.computer_id),)).fetchone()[0]
            rendered_frames_for_computer = rendered_frames_for_computer  + "," + str(frames_left_to_render[0])

            self.cursor.execute('''UPDATE computers SET current_frame=? WHERE computer_id=?''', (frames_left_to_render[0], (self.computer_id),))
            self.cursor.execute('''UPDATE computers SET rendered_frames=? WHERE computer_id=?''', (rendered_frames_for_computer, (self.computer_id),))
            self.db.commit()

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
        elif self.computer_id.split("-")[0] == "346":
            self.classroom = "Catmull"
        else:
            self.classroom = "Unknown"