#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import unicodedata
import PIL
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import subprocess
import os
import collections
import ctypes
import sys
from threading import Thread
import time
import distutils.core
import shutil
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from dateutil import relativedelta
from glob import glob
from functools import partial


class Lib(object):

    def create_thumbnails(self, obj_path="", thumbs_to_create="", version="", selected_version_item="", selected_asset_item=""):
        self.updateThumbBtn.setEnabled(False)
        self.full_obj_path = obj_path
        self.obj_name = obj_path[obj_path.find("_mod_")+len("_mod_"):obj_path.rfind("_out")]
        self.obj_tmp_path = "H:\\tmp\\" + obj_path.split("\\")[-1]
        self.type = type
        self.version = version
        self.i = 0

        self.thumbnailProgressBar.show()
        self.thumbnailProgressBar.setValue(0)

        self.thumbs_to_create = thumbs_to_create

        if "full" in self.thumbs_to_create:
            self.type = "full"
            self.sampling = 250
            self.resolution = 150
            self.thumbs_to_create = thumbs_to_create.replace("full", "")
        elif "turn" in self.thumbs_to_create:
            self.type = "turn"
            self.sampling = 50
            self.resolution = 100
            self.thumbs_to_create = thumbs_to_create.replace("turn", "")

        if self.type == "full":
            self.thumbnailProgressBar.setMaximum(67 + int(self.sampling))
        elif self.type == "turn":
            self.thumbnailProgressBar.setMaximum(1171 + (int(self.sampling) * 20))

        if os.path.getsize(self.full_obj_path) < 100:
            self.message_box(type="warning", text="It looks like the published modeling is nothing. Make sure you model something before trying to make a thumbnail out of it!")
            self.thumbnailProgressBar.hide()
            return

        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            self.thumbnailProgressBar.hide()
            self.updateThumbBtn.setEnabled(True)
            self.message_box(type="info", text="Successfully created thumbnails")
            return

        self.create_thumbnail_process = QtCore.QProcess(self)
        self.create_thumbnail_process.readyReadStandardOutput.connect(self.create_thumbnail_new_data)
        self.create_thumbnail_process.setProcessChannelMode(QtCore.QProcess.SeparateChannels)
        self.create_thumbnail_process.finished.connect(partial(self.create_thumbnail_finished, selected_version_item, selected_asset_item, version))
        self.create_thumbnail_process.start("C:/Program Files/Blender Foundation/Blender/blender.exe", ["-b", self.cur_path + "\\lib\\thumbnailer\\Thumbnailer.blend", "--python-text",
                                                                                                                                        "ThumbScript", self.full_obj_path, self.type, str(self.sampling),
                                                                                                                                        str(self.resolution), self.version
                                                                                                                                        ])

    def create_thumbnail_new_data(self):
        while self.create_thumbnail_process.canReadLine():
            self.i += 1
            out = self.create_thumbnail_process.readLine()
            self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.value() + 1)
            hue = self.fit_range(self.i, 0, self.thumbnailProgressBar.maximum(), 0, 76)
            self.thumbnailProgressBar.setStyleSheet("QProgressBar::chunk {background-color: hsl(" + str(hue) + ", 255, 205);}")

    def create_thumbnail_finished(self, selected_version_item, selected_asset_item, version):
        thumb_filename = os.path.split(self.full_obj_path)[0] + "\\.thumb\\" + os.path.split(self.full_obj_path)[1].replace("out.obj", self.version + "_full.jpg")

        if self.type == "full":
            filename = self.obj_tmp_path.replace("out.obj", self.version + "_full.jpg")
            self.compress_image(filename, int(1920 * float(self.resolution) / 100), 100)

            shutil.copy(self.obj_tmp_path.replace("out.obj", self.version + "_full.jpg"), thumb_filename)
            os.remove(self.obj_tmp_path.replace("out.obj", self.version + "_full.jpg"))

        elif self.type == "turn":
            file_sequence = self.obj_tmp_path.replace("out.obj", self.version + "_%02d.jpg")
            movie_path = self.obj_tmp_path.replace("out.obj", self.version + "_advanced.mp4")
            subprocess.call([self.cur_path_one_folder_up + "\\_soft\\ffmpeg\\ffmpeg.exe", "-i", file_sequence, "-vcodec", "libx264", "-b", "800k", "-crf", "0", "-y", "-r", "24", movie_path])

            turn_filename = os.path.split(self.full_obj_path)[0] + "\\.thumb\\" + os.path.split(self.full_obj_path)[1].replace("out.obj", self.version + "_advanced.mp4")
            shutil.copy(self.obj_tmp_path.replace("out.obj", self.version + "_advanced.mp4"), turn_filename)
            os.remove(self.obj_tmp_path.replace("out.obj", self.version + "_advanced.mp4"))
            for i in range(24):
                os.remove(self.obj_tmp_path.replace("out.obj", self.version + "_" + str(i).zfill(2) + ".jpg"))

        self.create_thumbnail_process.kill()
        self.thumbnailProgressBar.setValue(self.thumbnailProgressBar.maximum())

        if len(self.thumbs_to_create) > 0:
            self.create_thumbnails(self.full_obj_path, self.thumbs_to_create, self.version, selected_asset_item, selected_version_item)
        else:
            if version != "01":
                selected_asset_item.setIcon(QtGui.QIcon(thumb_filename))
            selected_version_item.setIcon(QtGui.QIcon(thumb_filename))
            self.thumbnailProgressBar.hide()
            self.updateThumbBtn.setEnabled(True)
            self.message_box(type="info", text="Successfully created thumbnails")

    def get_asset_item_from_version_asset(self, version_asset):
        """
        Get assetList QListWidgetItem from selected version asset
        (Ex: selected QListWidgetItem from versionList is modeling Flippy v03, asset_item will be assetList QListWidgetItem corresponding to modeling Flippy v01
        :param version_asset: versionList selected item as an Asset object
        :return: asset_item as a QListWidgetItem
        """

        # Get asset id from database which corresponds to selected version asset
        selected_asset_id = self.cursor.execute('''SELECT asset_id FROM assets WHERE asset_name=? AND asset_extension=? AND asset_type=? AND asset_version="01"''', (version_asset.name, version_asset.extension, version_asset.type,)).fetchone()[0]
        selected_asset = self.Asset(self, selected_asset_id, get_infos_from_id=True)
        for asset, asset_item in self.assets.items():
            if selected_asset.name == asset.name and selected_asset.extension == asset.extension and selected_asset.type == asset.type and selected_asset.version == asset.version and selected_asset.sequence == asset.sequence and selected_asset.path == asset.path:
                return asset_item

    def setup_user_session(self):
        # Set soft preferences environment variables
        os.environ["HOUDINI_USER_PREF_DIR"] = "Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_soft/_prefs/houdini/houdini__HVER__"

        if not os.path.isdir("H:/tmp"):
            os.makedirs("H:/tmp")

        if not os.path.isdir("H:/plugins"):
            distutils.dir_util.copy_tree(self.cur_path_one_folder_up + "\\_setup\\plugins", "H:/plugins")

        if not os.path.isdir("H:/DJView"):
            distutils.dir_util.copy_tree(self.cur_path_one_folder_up + "\\_setup\\DJView", "H:/DJView")

        if not os.path.isdir("H:/.mari"):
            distutils.dir_util.copy_tree(self.cur_path_one_folder_up + "\\_setup\\.mari", "H:/.mari")

        if not os.path.isdir("H:/mari_cache"):
            os.makedirs("H:/mari_cache")

        if not os.path.isdir("H:/mari_cache_tmp_synthese"):
            os.makedirs("H:/mari_cache_tmp_synthese")

        mari_cache_file = open("H:/.mari/TheFoundry/CacheLocations.ini", "r")
        for line in mari_cache_file.readlines():
            if "Path" in line:
                mari_cache_path = line.split("=")[-1].replace("\n", "")
                break

        mari_cache_file.close()

        if not os.path.isdir("H:/Documents/Mari/Scripts"):
            os.makedirs("H:/Documents/Mari/Scripts")
            distutils.dir_util.copy_tree("Z:/Groupes-cours/NAND999-A15-N01/Nature/_pipeline/_utilities/_asset_manager/lib/software_scripts/mari", "H:/Documents/Mari/Scripts")

        self.cursor.execute('''UPDATE preferences SET mari_cache_path=? WHERE username=?''', (mari_cache_path, self.username,))
        self.db.commit()

    def message_box(self, type="warning", text="warning", yes_button_text="", no_button=False, no_button_text="", exec_now=True, window_title="Manager"):

        self.msgBox = QtGui.QMessageBox()
        self.msgBox.setWindowIcon(self.app_icon)

        self.Lib.apply_style(self, self.msgBox)

        self.msgBox.setWindowTitle(window_title)
        self.msgBox.setText(text)

        self.msgBox_okBtn = self.msgBox.addButton(QtGui.QMessageBox.Ok)
        if len(yes_button_text) > 0:
            self.msgBox_okBtn.setText(yes_button_text)
        self.msgBox_okBtn.setStyleSheet("width: 64px;")
        self.msgBox.setDefaultButton(self.msgBox_okBtn)
        self.msgBox_okBtn.clicked.connect(self.msgBox.accept)

        if no_button == True:
            self.msgBox_noBtn = self.msgBox.addButton(QtGui.QMessageBox.No)
            if len(no_button_text) > 0:
                self.msgBox_noBtn.setText(no_button_text)
            self.msgBox_noBtn.setStyleSheet("width: 64px;")
            self.msgBox_noBtn.clicked.connect(self.msgBox.reject)

        if type.lower() == "warning":
            self.msgBox.setIcon(QtGui.QMessageBox.Warning)
        elif type.lower() == "error":
            self.msgBox.setIcon(QtGui.QMessageBox.Critical)
        elif type.lower() == "info":
            self.msgBox.setIcon(QtGui.QMessageBox.Information)

        if exec_now == True:
            return self.msgBox.exec_()
        else:
            return self.msgBox

    def thumbnail_creation_box(self, text=""):
        self.thumbnail_creation_box = QtGui.QMessageBox()
        self.thumbnail_creation_box.setWindowIcon(self.app_icon)
        self.Lib.apply_style(self, self.thumbnail_creation_box)

        self.thumbnail_creation_box.setWindowTitle("Manager")
        self.thumbnail_creation_box.setText(text)

        self.thumbnail_creation_box_okBtn = self.thumbnail_creation_box.addButton(QtGui.QMessageBox.Ok)
        self.thumbnail_creation_box_noBtn = self.thumbnail_creation_box.addButton(QtGui.QMessageBox.No)
        self.thumbnail_creation_box_okBtn.setStyleSheet("width: 64px;")
        self.thumbnail_creation_box_noBtn.setStyleSheet("width: 64px;")
        self.thumbnail_creation_box_okBtn.clicked.connect(self.thumbnail_creation_box.accept)
        self.thumbnail_creation_box.setDefaultButton(self.thumbnail_creation_box_okBtn)

        return self.thumbnail_creation_box.exec_()

    def center_window(self):
        """
        Move the window to the center of the screen

        """
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2), (resolution.height() / 2) - (self.frameSize().height() / 2))
        self.setFixedSize(0, 0)

    def open_in_explorer(self):
        """
        Open selected assets in explorer
        """
        subprocess.Popen(r'explorer /select,' + str(self.assetPathLbl.text()))

    def apply_style(self, form):

        form.setWindowFlags(form.windowFlags() | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)

        # Create Favicon
        app_icon = QtGui.QIcon()
        app_icon.addFile(self.cur_path + "\\media\\favicon_cube.png", QtCore.QSize(16, 16))
        form.setWindowIcon(app_icon)

        if int(self.theme) == 0:
            # Apply custom CSS to msgBox
            css = QtCore.QFile(self.cur_path + "\\media\\style.css")
            css.open(QtCore.QIODevice.ReadOnly)
            if css.isOpen():
                form.setStyleSheet(QtCore.QVariant(css.readAll()).toString().replace("checkbox|placeholder", self.cur_path.replace("\\", "/") + "/media/checkbox.png"))
            css.close()

        elif int(self.theme) == 2:
            form.setStyle(QtGui.QStyleFactory.create("plastique"))

        elif int(self.theme) == 0:
            form.setStyle(QtGui.QStyleFactory.create("cleanlooks"))

    def normalize_str(self, data):
        try:
            data = unicode(data, "utf-8")
        except:
            pass
        return unicodedata.normalize('NFKD', data).encode('ascii', 'ignore')

    def convert_to_camel_case(self, str):
        str = str.lower()
        str = str.replace("(", "")
        str = str.replace(")", "")
        str = str.replace("'", "")
        str = str.replace("_", " ")
        str = str.replace("-", " ")
        str = str.replace(":", "")
        str = str.replace(";", "")
        str = str.replace("|", "")
        str = str.replace("#", "")
        str = str.replace("!", "")
        str = str.replace("?", "")
        str = str.replace("0", "")
        str = str.replace("1", "")
        str = str.replace("2", "")
        str = str.replace("3", "")
        str = str.replace("4", "")
        str = str.replace("5", "")
        str = str.replace("6", "")
        str = str.replace("7", "")
        str = str.replace("8", "")
        str = str.replace("9", "")
        liste = str.split(" ")
        liste = filter(None, liste)
        liste_finale = []
        for i, item in enumerate(liste):
            if i != 0:
                uppercase_str = item[0].upper() + item[1:len(item)]
                liste_finale.append(uppercase_str)
            else:
                liste_finale.append(item)

        str = "".join(liste_finale)
        return str

    def compress_image(self, image_path, width, quality):
        basewidth = width
        img = Image.open(image_path)
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
        img.save(image_path, 'JPEG', quality=quality)

    def squarify_image(self, image_path):
        img = Image.open(image_path)
        w, h = img.size
        background = Image.new('RGBA', (w, w), (255, 255, 255, 0))
        background_w, background_h = background.size
        background.paste(img, ((background_w - w) / 2, (background_h - h) / 2))
        background.save(image_path.replace(".jpg", ".png"))
        os.remove(image_path)

    def take_screenshot(self, path, software="maya", user_selection=False):

        if user_selection:
            self.hide()
            # constants
            SCREEN_GRABBER = self.cur_path_one_folder_up + "\\_soft\\screenshot_grabber\\MiniCap.exe"

            # filename
            file_name = path

            # run the screen grabber
            subprocess.call([SCREEN_GRABBER, '-captureregselect', '-exit', '-save', file_name])
            # winsound.PlaySound("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_soft\\screenshot_grabber\\camera.wav", winsound.SND_FILENAME)

            self.show()
            self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.activateWindow()
        else:

            self.hide()
            time.sleep(0.5)

            # constants
            SCREEN_GRABBER = self.cur_path_one_folder_up + "\\_soft\\screenshot.exe"

            # filename
            file_name = path

            # run the screen grabber
            if software == "maya":
                subprocess.call([SCREEN_GRABBER, '-rc', '506', '87', '1450', '1031', '-o', file_name])
            elif software == "houdini":
                subprocess.call([SCREEN_GRABBER, '-rc', '506', '87', '1450', '1031', '-o', file_name])
            elif software == "mari":
                subprocess.call([SCREEN_GRABBER, '-rc', '642', '233', '1292', '883', '-o', file_name])
            #winsound.PlaySound("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_soft\\screenshot_grabber\\camera.wav", winsound.SND_FILENAME)

            self.show()
            self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.activateWindow()

    def fit_range(self, base_value=2.5, base_min=0, base_max=5, limit_min=0, limit_max=1):
        return ((limit_max - limit_min) * (base_value - base_min) / (base_max - base_min)) + limit_min

    def disk_usage(self, path):
        _ntuple_diskusage = collections.namedtuple('usage', 'total used free')
        _, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), \
                         ctypes.c_ulonglong()
        if sys.version_info >= (3,) or isinstance(path, unicode):
            fun = ctypes.windll.kernel32.GetDiskFreeSpaceExW
        else:
            fun = ctypes.windll.kernel32.GetDiskFreeSpaceExA
        ret = fun(path, ctypes.byref(_), ctypes.byref(total), ctypes.byref(free))
        if ret == 0:
            raise ctypes.WinError()
        used = total.value - free.value
        return _ntuple_diskusage(total.value, used, free.value)

    def bytes2human(self, n):
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i+1)*10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return '%.3f' % (value)
        return "%sB" % n

    def get_folder_space(self, path="Z:\\Groupes-cours\\NAND999-A15-N01\\Nature"):
        usage = self.disk_usage(path)
        return self.bytes2human(usage.total)

    def get_files_from_folder(self, path):
        files_list = []
        folder_path = path

        for (dir, _, files) in os.walk(folder_path):
            for f in files:
                path = os.path.join(dir, f)
                if os.path.exists(path):
                    files_list.append(path)

        return files_list

    def add_watermark(self, in_file, text, out_file='watermark.jpg', angle=0, opacity=0.75):
        font = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\arial.ttf"
        img = Image.open(in_file).convert('RGB')
        watermark = Image.new('RGBA', img.size, (0,0,0,0))
        size = 2
        n_font = ImageFont.truetype(font, size)
        n_width, n_height = n_font.getsize(text)
        while n_width+n_height < watermark.size[0]:
            size += 2
            n_font = ImageFont.truetype(font, size)
            n_width, n_height = n_font.getsize(text)
        draw = ImageDraw.Draw(watermark, 'RGBA')
        draw.text(((watermark.size[0] - n_width) / 2,
                   (watermark.size[1] - n_height) / 2),
                  text, font=n_font)
        watermark = watermark.rotate(angle,Image.BICUBIC)
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        watermark.putalpha(alpha)
        Image.composite(watermark, img, watermark).save(out_file, 'JPEG')

    def reference_check_if_projSeqShot_is_selected(self):


        # Check if a project is selected
        if len(self.projectList.currentText()) == 0:
            self.message_box(text="Please select a project first")
            return None, None

        # Check if a sequence is selected
        if len(self.seqReferenceList.selectedItems()) == 0:
            selected_sequence = "xxx"
        else:
            selected_sequence = str(self.seqReferenceList.selectedItems()[0].text())
            if selected_sequence == "All" or selected_sequence == "None": selected_sequence = "xxx"

        # Check if a shot is selected
        if len(self.shotReferenceList.selectedItems()) == 0:
            selected_shot = "xxxx"
        else:
            selected_shot = str(self.shotReferenceList.selectedItems()[0].text())
            if selected_shot == "All" or selected_shot == "None": selected_shot = "xxxx"


        return selected_sequence, selected_shot

    def get_diff_between_lists(self, list1, list2):
        c = set(list1).union(set(list2))
        d = set(list1).intersection(set(list2))
        return list(c - d)

    def modification_date(self, filename):
        t = os.path.getmtime(filename)
        return datetime.fromtimestamp(t)

    def add_entry_to_log(self, members_list="", members_concerned="", asset_id=0, type="", description=""):
        if members_list == "All":
            members_list = self.members.keys()

        members_list = ["|{0}|".format(member) for member in members_list]
        members_list = "".join(members_list)

        if members_concerned == "All":
            members_concerned = self.members.keys()

        members_concerned = ["|{0}|".format(member) for member in members_concerned]
        members_concerned = "".join(members_concerned)

        self.cursor.execute('''INSERT INTO log(log_dependancy, viewed_by, members_concerned, log_type, log_description) VALUES(?,?,?,?,?)''', (asset_id, members_list, members_concerned, type, description))
        self.db.commit()

    def remove_log_entry_from_asset_id(self, asset_id, type=None):
        if type != None:
            self.cursor.execute('''DELETE FROM log WHERE log_dependancy=? AND log_type=?''', (asset_id, type))
        else:
            self.cursor.execute('''DELETE FROM log WHERE log_dependancy=?''', (asset_id,))
        self.db.commit()

    def read_process_data(self, process):
        while process.canReadLine():
            out = process.readLine()
            print(out)

    def send_email(self, from_addr="nad.update@gmail.com", addr_list=[], subject="", message="", login="nad.update@gmail.com", password="python123", username=""):

        if username == "":
            username = self.members[self.username]

        subject = unicode(self.utf8_codec.fromUnicode(subject), 'utf-8').encode('utf-8')
        message = unicode(self.utf8_codec.fromUnicode(message), 'utf-8').encode('utf-8')

        smtpserver = 'smtp.gmail.com:25'
        header = 'From: {0}\n'.format(from_addr)
        header += 'To: %s\n' % ','.join(addr_list)
        header += 'Subject: {0} by {1}\n\n'.format(subject, username)
        message = "{0}{1}".format(header, message)

        server = smtplib.SMTP(smtpserver)
        server.starttls()
        server.login(login, password)
        problems = server.sendmail(from_addr, addr_list, message)
        server.quit()

        self.message_box(type="info", text="Mail successfully sent!")

    def check_last_active(self):
        for member in self.members.keys():
            last_active = self.cursor.execute('''SELECT last_active FROM preferences WHERE username=?''', (member,)).fetchone()
            self.last_active = last_active[0]
            now = datetime.now()
            date = self.last_active.split(" ")[0]
            time = self.last_active.split(" ")[-1]
            day = date.split("/")[0]
            month = date.split("/")[1]
            year = date.split("/")[2]
            hour = time.split(":")[0]
            minutes = time.split(":")[1]
            self.last_active_as_date = datetime(int(year), int(month), int(day), int(hour), int(minutes))

            last_active_period = relativedelta.relativedelta(now, self.last_active_as_date)

            if last_active_period.days > 0 or last_active_period.hours > 0 or last_active_period.minutes >= 2:
                self.cursor.execute('''UPDATE preferences SET is_online=0 WHERE username=?''', (member,))
            else:
                self.cursor.execute('''UPDATE preferences SET is_online=1 WHERE username=?''', (member,))

    def switch_mari_cache(self, cache_location):
        if cache_location == "perso":
            mari_cache_path = self.cursor.execute('''SELECT mari_cache_path FROM preferences WHERE username=?''', (self.username,)).fetchone()[0]
        elif cache_location == "server":
            mari_cache_path = "Z:/Groupes-cours/NAND999-A15-N01/Nature/tex"
        elif cache_location == "home":
            mari_cache_path = "H:/mari_cache_tmp_synthese"

        os.remove("H:/.mari/TheFoundry/CacheLocations.ini")
        mari_cachelocation_file = open("H:/.mari/TheFoundry/CacheLocations.ini", "a")
        mari_cachelocation_file.write("[CacheRoots]\n")
        mari_cachelocation_file.write("1\Path=" + mari_cache_path + "\n")
        mari_cachelocation_file.write("size=1\n")
        mari_cachelocation_file.close()

    def get_mari_project_path_from_asset_name(self, asset_name, asset_version):
        paths = glob("Z:/Groupes-cours/NAND999-A15-N01/Nature/tex/*")
        paths = [i.replace("\\", "/") for i in paths]
        paths = [i for i in paths if not "SINGLE" in i and not "Generic" in i]

        for path in paths:
            sumary_file = path + "\\Summary.txt"
            f = open(sumary_file, "r")
            lines = f.readlines()
            for line in lines:
                if "Name=" in line:
                    if asset_name.lower() + "_" + asset_version in line.lower():
                        return path.split("/")[-1] # Return path (Ex: "8e0930b8-61b1-4ade-8dbd-8bb422ef6686")
            f.close()

        return None

    def delete_unecessary_folders(self, folder_path=None, folders_to_delete=[]):
        if folder_path == None:
            return

        for folder in folders_to_delete:
            folders = [x[0] for x in os.walk(folder_path) if folder in x[0].split("\\")[-1]]
            for folder in folders:
                shutil.rmtree(folder, ignore_errors=True)

class DesktopWidget(QtGui.QWidget):

    def __init__(self, task_name, task_department, task_status, task_start, task_end, task_bid):
        super(DesktopWidget, self).__init__()

        self.DesktopWidget_status = {"Ready to Start": 0, "In Progress": 1, "On Hold": 2, "Waiting for Approval": 3, "Retake": 4,
                       "Done": 5}

        # Create Favicon
        app_icon = QtGui.QIcon()
        app_icon.addFile("Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\media\\favicon.png", QtCore.QSize(16, 16))
        self.setWindowIcon(app_icon)

        self.top = False
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle("My Tasks - Desktop Widget")

        self.setStyleSheet("background: rgb(222, 222, 222);")

        self.layout = QtGui.QHBoxLayout(self)

        self.taskNameLbl = QtGui.QLabel(task_name)
        self.taskNameLbl.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(self.taskNameLbl)

        self.add_separator()

        self.taskDepartmentLbl = QtGui.QLabel(task_department)
        self.taskDepartmentLbl.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(self.taskDepartmentLbl)

        self.add_separator()

        self.statusComboBox = QtGui.QComboBox()
        self.statusComboBox.addItems(["Ready to Start", "In Progress", "On Hold", "Waiting for Approval", "Retake", "Done"])
        self.statusComboBox.setCurrentIndex(self.DesktopWidget_status[task_status])
        self.change_cell_status_color(self.statusComboBox, task_status)
        self.layout.addWidget(self.statusComboBox)

        self.add_separator()

        self.taskStartLbl = QtGui.QLabel("Start: " + task_start)
        self.taskStartLbl.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(self.taskStartLbl)

        self.add_separator()

        self.taskEndLbl = QtGui.QLabel("End: " + task_end)
        self.taskEndLbl.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(self.taskEndLbl)

        self.add_separator()

        self.taskBidtLbl = QtGui.QLabel(task_bid + " days left")
        self.taskBidtLbl.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(self.taskBidtLbl)

        self.layout.setContentsMargins(12, 12, 12, 12)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)

    def showMenu(self, pos):

        self.widget_menu=QtGui.QMenu(self)
        self.action_top = QtGui.QAction("Always on top", self.widget_menu)
        self.action_close = QtGui.QAction("Close", self.widget_menu)
        self.action_top.triggered.connect(self.always_on_top)
        self.action_close.triggered.connect(self.close_widget)
        self.widget_menu.addAction(self.action_top)
        self.widget_menu.addAction(self.action_close)
        self.widget_menu.popup(self.mapToGlobal(pos))
        self.widget_menu.setStyleSheet("QMenu::item {color: black;}")
        self.widget_menu.setStyleSheet("QMenu {color: white;}")

    def close_widget(self):
        self.close()

    def always_on_top(self):
        if self.top == False:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            self.show()
            self.top = True
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
            self.show()
            self.top = False

    def add_separator(self):
        line_01 = QtGui.QFrame()
        line_01.setFrameShape(QtGui.QFrame.VLine)
        line_01.setLineWidth(1)
        line_01.setStyleSheet("color: rgb(30, 30, 30);")
        self.layout.addWidget(line_01)

    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        try:
            x=event.globalX()
            y=event.globalY()
            x_w = self.offset.x()
            y_w = self.offset.y()
            self.move(x-x_w, y-y_w)
        except:
            pass

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

class CheckNews(QtCore.QThread):
    def __init__(self, main):
        QtCore.QThread.__init__(self)
        self.main = main

    def run(self):
        while True:
            if self.main.isHidden():
                self.emit(QtCore.SIGNAL("refresh_all"))
                # Delete unecessary folders
                self.main.Lib.delete_unecessary_folders(self.main, folder_path=self.main.selected_project_path + "\\assets", folders_to_delete=["backup", "Cache"])
                time.sleep(15)
            else:
                time.sleep(15)

if __name__ == "__main__":
    test = Lib()
    test.switch_mari_cache("server")


    # app = QtGui.QApplication(sys.argv)
    # test = Lib()
    # test.create_thumbnails(obj_path="Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_asset_manager\\lib\\thumbnailer\\statue.obj", type="quad", sampling="100", resolution="10")
    # app.exit()
