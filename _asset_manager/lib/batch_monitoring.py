#!/usr/bin/env python
# coding=utf-8

import sys
import os
import subprocess
import socket
from glob import glob
import atexit

from datetime import date
from datetime import datetime
from dateutil import relativedelta

import sqlite3
import time
import threading
from PyQt4 import QtGui, QtCore

class Monitoring(object):
    def __init__(self):
        os.system("C:/Windows/System32/hserver.exe -S licenseserver")

        self.db_path = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering.sqlite"  # Database projet pub
        self.db = sqlite3.connect(self.db_path, timeout=30.0)
        self.cursor = self.db.cursor()

    def initialize_slave(self):
        self.computer_id = socket.gethostname()

        print("Successfully started slave on computer #" + self.computer_id)

        self.get_classroom_from_id()

        self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()

        if self.computer_status == None:
            last_active = datetime.now().strftime("%d/%m/%Y %H:%M")
            self.cursor.execute('''INSERT INTO computers(computer_id, classroom, status, rendered_ifd, current_ifd, last_active) VALUES(?,?,?,?,?,?)''',
                                (self.computer_id, self.classroom, "idle", "", "", last_active))
            self.db.commit()
        elif type(self.computer_status) == type(()):
            if self.computer_status[0] == "rendering":
                self.cursor.execute('''UPDATE computers SET status="idle" WHERE computer_id=?''', (self.computer_id,))
                self.db.commit()
            last_active = datetime.now().strftime("%d/%m/%Y %H:%M")
            self.cursor.execute('''UPDATE computers SET last_active=? WHERE computer_id=?''', (last_active, self.computer_id,))
            self.db.commit()
        self.check_status()

    def check_status(self):
        print("Checking Status")
        self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()[0]
        subprocess.Popen(["Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/MPC/mpc-hc.exe", "/fullscreen", "Z:/Groupes-cours/NAND999-A15-N01/pub/_info/waiting_for_render.jpg"])

        if self.computer_status != "rendering":
            i = 0
            while True:
                print("Computer is idle...")

                if i == 10:
                    last_active = datetime.now().strftime("%d/%m/%Y %H:%M")
                    self.cursor.execute('''UPDATE computers SET last_active=? WHERE computer_id=?''', (last_active, self.computer_id,))
                    self.db.commit()

                self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()[0]
                if self.computer_status == "logout":
                    os.system("shutdown -l")

                if self.computer_status == "start":
                    break

                i += 1
                time.sleep(6)

            # Update status to rendering
            self.cursor.execute('''UPDATE computers SET status="rendering" WHERE computer_id=?''', (self.computer_id,))
            self.db.commit()
            self.computer_status = "rendering"

        self.start_render()

    def start_render(self):
        print("Starting Render")
        subprocess.Popen(["Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/MPC/mpc-hc.exe", "/fullscreen", "Z:/Groupes-cours/NAND999-A15-N01/pub/_info/render_in_progress.jpg"])

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

            frames_to_render = sorted(list(set(ifd_files) - set(all_rendered_frames)))
            frame_to_render = frames_to_render[0]

            if len(frames_to_render) == 0:
                print("No more frames to render for IFD {0}".format(ifd_path))
                self.cursor.execute('''UPDATE jobs SET priority=100 WHERE id=?''', (current_job[0],))
                self.db.commit()
            else:
                print("Start render for frame #" + frame_to_render)
                
                self.cursor.execute('''UPDATE computers SET current_ifd=? WHERE computer_id=?''', (frame_to_render, self.computer_id,))
                self.db.commit()

                ifd_file = current_job[1] + "\\" + current_seq + "." + frame_to_render + ".ifd"

                p = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.13/bin/mantra.exe", "-V", "0", "-I", "resolution={0}x{1},sampling={2}x{2}".format(resolutionX, resolutionY, sampling), "-f", ifd_file])

                tasks = subprocess.check_output(['tasklist']).split("\r\n")
                while True:
                    print("Waiting for render to start")
                    tasks = subprocess.check_output(['tasklist']).split("\r\n")

                    if "mantra" in str(tasks):
                        break
                    else:
                        time.sleep(1)

                i = 0
                while self.computer_status == "rendering":
                    print("Rendering frame #" + frames_to_render[0])
                    self.computer_status = self.cursor.execute('''SELECT status FROM computers WHERE computer_id=?''', (self.computer_id,)).fetchone()[0]
                    
                    if self.computer_status == "stop":
                        p.kill()
                        self.cursor.execute('''UPDATE computers SET status="idle" WHERE computer_id=?''', (self.computer_id, ))
                        self.cursor.execute('''UPDATE computers SET current_ifd="" WHERE computer_id=?''', (self.computer_id, ))
                        self.db.commit()
                        time.sleep(2)
                        try:
                            os.remove(current_job[1] + "\\" + current_seq + "." + frame_to_render + ".exr")
                        except:
                            print("Failed to remove exr")
                    elif self.computer_status == "logout":
                        print("Logging out")
                        self.cursor.execute('''DELETE FROM computers WHERE computer_id=?''', (self.computer_id, ))
                        self.db.commit()
                        time.sleep(2)
                        try:
                            os.remove(current_job[1] + "\\" + current_seq + "." + frame_to_render + ".exr")
                        except:
                            print("Failed to remove exr")
                        os.system("shutdown -l")
                        

                    # Check if render is finished (finished if mantra is not running)
                    tasks = subprocess.check_output(['tasklist']).split("\r\n")
                    if not "mantra" in str(tasks):
                        rendered_frames_for_computer = self.cursor.execute('''SELECT rendered_ifd FROM computers WHERE computer_id=?''', (str(self.computer_id),)).fetchone()[0]
                        if len(rendered_frames_for_computer) == 0:
                            rendered_frames_for_computer = str(frame_to_render)
                        else:
                            rendered_frames_for_computer = rendered_frames_for_computer  + "," + str(frame_to_render)

                        self.cursor.execute('''UPDATE computers SET rendered_ifd=? WHERE computer_id=?''', (rendered_frames_for_computer, (self.computer_id),))
                        self.db.commit()
                        os.system('taskkill /f /im mpc-hc.exe')
                        break

                    if i == 10:
                        last_active = datetime.now().strftime("%d/%m/%Y %H:%M")
                        self.cursor.execute('''UPDATE computers SET last_active=? WHERE computer_id=?''', (last_active, self.computer_id,))
                        self.db.commit()

                    i += 1
                    time.sleep(6)
                
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

if __name__ == "__main__":
    test = Monitoring()
    test.initialize_slave()