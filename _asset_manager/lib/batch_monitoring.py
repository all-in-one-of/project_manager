#!/usr/bin/env python
# coding=utf-8

import sys
import os
import subprocess
import socket
from glob import glob
import ctypes

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
        self.computer_id = socket.gethostname()
        self.get_classroom_from_id()
        print("Successfully started slave on computer #" + self.computer_id)
        #self.db_path = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering.sqlite"  # Database projet pub
        #self.db = sqlite3.connect(self.db_path, timeout=60.0)
        #self.cursor = self.db.cursor()
        ctypes.windll.user32.SetCursorPos(960, 540)

    def check_status(self):
        self.get_computers_list()
        os.system("COLOR 47")
        #os.system('taskkill /f /im mpc-hc.exe')
        #subprocess.Popen(["Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/MPC/mpc-hc.exe", "/fullscreen", "Z:/Groupes-cours/NAND999-A15-N01/pub/_info/waiting_for_render.jpg"])

        i = 0
        if self.status == "idle":
            while True:
                print("Rendering...")
                self.get_computer_status()
                self.mouse_click()
                if self.status == "start":
                    self.start_render()
                elif self.status == "logout":
                    self.change_computer_status(status="idle")
                    self.change_computer_frame(frame="0")
                    os.system("shutdown -l")
                i += 1
                if i > 100:
                    self.update_computer_last_active()
                    i = 0
                time.sleep(5)
        elif self.status == "start":
            self.change_computer_status(status="idle")
            self.check_status()
        elif self.status == "rendering":
            self.start_render()
        elif self.status == "logout":
            self.change_computer_status(status="idle")
            self.change_computer_frame(frame="0")
            os.system("shutdown -l")

    def start_render(self):
        print("Starting Render")
        os.system("COLOR 47")
        #os.system('taskkill /f /im mpc-hc.exe')
        #subprocess.Popen(["Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/MPC/mpc-hc.exe", "/fullscreen", "Z:/Groupes-cours/NAND999-A15-N01/pub/_info/render_in_progress.jpg"])

        #all_jobs = self.cursor.execute('''SELECT * FROM jobs''').fetchall()
        all_jobs = glob("Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_database/jobs/*")
        all_jobs = [i.split("\\")[-1] for i in all_jobs]
        all_jobs = [i for i in all_jobs if int(i.split("_")[0]) != 100]
        all_jobs = sorted(all_jobs)

        if len(all_jobs) > 0:

            current_job = current_job_path = all_jobs[0]
            current_job = current_job.split("_")
            current_seq = current_job[1].split("-")[1]

            if int(current_job[0]) < 100:

                self.change_computer_status(status="rendering")

                rendering_frames = glob("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_frames\\*")
                rendered_frames = glob("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendered_frames\\*")
                rendering_frames = [os.path.split(i)[1] for i in rendering_frames]
                rendered_frames = [os.path.split(i)[1] for i in rendered_frames]

                all_frames = rendered_frames + rendering_frames
                all_frames = [(i.split("_")[0], i.split("_")[1]) for i in all_frames]
                all_rendered_frames_for_current_sequence = [i[1] for i in all_frames if i[0] == current_seq]

                resolution = current_job[2]
                resolutionX = int(1920.0 * (float(resolution) / 100.0))
                resolutionY = int(800.0 * (float(resolution) / 100.0))
                sampling = current_job[3]

                ifd_path = "Z:/Groupes-cours/NAND999-A15-N01/Nature/assets/rdr/{0}/{1}".format(current_job[1].split("-")[0], current_job[1].split("-")[1])

                ifd_files = glob(ifd_path + "\\*")
                ifd_files = [i for i in ifd_files if ".ifd" in i]
                ifd_files = [os.path.split(i)[-1].split(".")[1] for i in ifd_files]

                frames_to_render = sorted(list(set(ifd_files) - set(all_rendered_frames_for_current_sequence)))

                if len(frames_to_render) == 0:
                    print("No more frames to render for IFD {0}".format(ifd_path))
                    new_file_path = "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_database/jobs/{0}_{1}_{2}_{3}".format("100", current_job[1], current_job[2], current_job[3])
                    os.rename("Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_database/jobs/" + current_job_path, new_file_path)

                else:
                    frame_to_render = frames_to_render[0]
                    print("Start render for frame #" + current_seq + "-" + frame_to_render)
                    a = datetime.now().replace(microsecond=0)

                    open("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_frames\\{0}_{1}".format(current_seq, frame_to_render), "a+")
                    self.change_computer_frame(frame=current_seq + "-" + frame_to_render)

                    ifd_file = ifd_path + "/" + current_seq + "." + frame_to_render + ".ifd"

                    p = subprocess.Popen(["Z:/RFRENC~1/Outils/SPCIFI~1/Houdini/HOUDIN~1.16/bin/mantra.exe", "-V", "0", "-I", "resolution={0}x{1},sampling={2}x{2}".format(resolutionX, resolutionY, sampling), "-f", ifd_file])

                    try:
                        tasks = subprocess.check_output(['tasklist']).split("\r\n")
                    except:
                        tasks = ""
                    while True:
                        print("Waiting for render to start")
                        try:
                            tasks = subprocess.check_output(['tasklist']).split("\r\n")
                        except:
                            tasks = ""

                        if "mantra" in str(tasks):
                            break
                        else:
                            time.sleep(1)

                    i = 0
                    while self.status == "rendering":
                        print("Rendering frame #" + current_seq + "-" + frame_to_render)
                        self.mouse_click()
                        self.get_computer_status()

                        if self.status == "stop":
                            p.kill()
                            self.change_computer_frame(frame="0")

                            time.sleep(2)
                            try:
                                os.remove("Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_database/rendering_frames/" + current_seq + "_" + frame_to_render)
                            except:
                                print("Failed to remove tmp")

                            self.change_computer_status(status="idle")
                            self.check_status()

                        elif self.status == "logout":
                            print("Logging out")
                            self.change_computer_status(status="idle")
                            self.change_computer_frame(frame="0")
                            time.sleep(2)
                            try:
                                os.remove("Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_database/rendering_frames/" + current_seq + "_" + frame_to_render)
                            except:
                                print("Failed to remove tmp")
                            os.system("shutdown -l")

                        # Check if render is finished (finished if mantra is not running)
                        try:
                            tasks = subprocess.check_output(['tasklist']).split("\r\n")
                        except:
                            tasks = "mantra"
                        if not "mantra" in str(tasks):
                            b = datetime.now().replace(microsecond=0)
                            render_time = b - a
                            render_time = str(render_time).replace(":", "-")
                            open("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendered_frames\\{0}_{1}_{2}_{3}".format(current_seq, frame_to_render, str(render_time), str(self.computer_id).lower()), "a+")
                            try:
                                os.remove("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_frames\\{0}_{1}".format(current_seq, frame_to_render))
                            except:
                                pass
                            os.system('taskkill /f /im mpc-hc.exe')
                            break

                        if i == 100:
                            self.update_computer_last_active()
                            i = 0

                        i += 1
                        time.sleep(6)
        else:
            self.get_computer_status()
            if self.status == "rendering":
                self.change_computer_status(status="idle")

        self.update_computer_last_active()
        self.check_status()

    def get_computers_list(self):
        self.all_computers = glob("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_computers\\*")
        self.all_computers = [os.path.split(i)[-1] for i in self.all_computers]
        self.all_computers_id = [i.split("_")[0] for i in self.all_computers]
        self.computers = []
        self.current_rendering_frames = []
        for computer in self.all_computers:
            id = computer.split("_")[0]
            classroom = computer.split("_")[1]
            frame = computer.split("_")[2]
            status = computer.split("_")[3]
            last_active = computer.split("_")[4]
            self.current_rendering_frames.append(frame)
            self.computers.append((id, classroom, frame, status, last_active))

        if not self.computer_id in self.all_computers_id:
            last_active = datetime.now().strftime("%d-%m-%Y-%Hh%M")
            open("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_computers\\{0}_{1}_{2}_{3}_{4}".format(self.computer_id, self.classroom, "0", "idle", last_active), "a+")
            self.current_frame = "0"
            self.status = "idle"
            self.last_active = last_active
        else:
            cur_computer = [i for i in self.computers if self.computer_id == i[0]]
            self.current_frame = cur_computer[0][2]
            self.status = cur_computer[0][3]
            self.last_active = cur_computer[0][4]

    def get_computer_status(self):
        self.all_computers = glob("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_computers\\*")
        for computer in self.all_computers:
            folder_path = os.path.split(computer)[0]
            file_path = os.path.split(computer)[1]
            if file_path.split("_")[0] == self.computer_id:
                self.status = file_path.split("_")[3]

    def change_computer_status(self, status):
        self.all_computers = glob("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_computers\\*")
        for computer in self.all_computers:
            folder_path = os.path.split(computer)[0]
            file_path =  os.path.split(computer)[1]
            if file_path.split("_")[0] == self.computer_id:
                id = file_path.split("_")[0]
                classroom = file_path.split("_")[1]
                frame = file_path.split("_")[2]
                last_active = file_path.split("_")[4]
                os.rename(computer, folder_path + "\\{0}_{1}_{2}_{3}_{4}".format(id, classroom, frame, status, last_active))
        self.status = status

    def change_computer_frame(self, frame):
        self.all_computers = glob("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_computers\\*")
        for computer in self.all_computers:
            folder_path = os.path.split(computer)[0]
            file_path = os.path.split(computer)[1]
            if file_path.split("_")[0] == self.computer_id:
                id = file_path.split("_")[0]
                classroom = file_path.split("_")[1]
                status = file_path.split("_")[3]
                last_active = file_path.split("_")[4]
                os.rename(computer, folder_path + "\\{0}_{1}_{2}_{3}_{4}".format(id, classroom, frame, status, last_active))
        self.current_frame = frame

    def update_computer_last_active(self):
        self.all_computers = glob("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_database\\rendering_computers\\*")
        for computer in self.all_computers:
            folder_path = os.path.split(computer)[0]
            file_path = os.path.split(computer)[1]
            if file_path.split("_")[0] == self.computer_id:
                id = file_path.split("_")[0]
                classroom = file_path.split("_")[1]
                frame = file_path.split("_")[2]
                status = file_path.split("_")[3]
                last_active = datetime.now().strftime("%d-%m-%Y-%Hh%M")
                os.rename(computer, folder_path + "\\{0}_{1}_{2}_{3}_{4}".format(id, classroom, frame, status, last_active))
        self.last_active = last_active

    def mouse_click(self, seconds_between_clicks=2):
        ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
        time.sleep(2)
        ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)


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
    test.check_status()