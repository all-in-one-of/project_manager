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





class Lib(object):

    def save_prefs(self):
        """
        Save preferences

        """
        photoshop_path = str(self.photoshopPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Photoshop"''',
                            (photoshop_path,))

        maya_path = str(self.mayaPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Maya"''', (maya_path,))

        softimage_path = str(self.softimagePathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Softimage"''',
                            (softimage_path,))

        houdini_path = str(self.houdiniPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Houdini"''',
                            (houdini_path,))

        cinema4d_path = str(self.cinema4dPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Cinema 4D"''',
                            (cinema4d_path,))

        nuke_path = str(self.nukePathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Nuke"''', (nuke_path,))

        zbrush_path = str(self.zbrushPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="ZBrush"''',
                            (zbrush_path,))

        mari_path = str(self.mariPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Mari"''', (mari_path,))

        blender_path = str(self.blenderPathLineEdit.text())
        self.cursor.execute('''UPDATE software_paths SET software_path=? WHERE software_name="Blender"''',
                            (blender_path,))

        self.db.commit()

    def message_box(self, type="Warning", text="Warning"):

        self.msgBox = QtGui.QMessageBox()
        self.msgBox.setWindowIcon(self.app_icon)

        self.Lib.apply_style(self, self.msgBox)

        self.msgBox.setWindowTitle("Warning!")
        self.msgBox.setText(text)

        self.msgBox_okBtn = self.msgBox.addButton(QtGui.QMessageBox.Ok)
        self.msgBox_okBtn.setStyleSheet("width: 64px;")
        self.msgBox.setDefaultButton(self.msgBox_okBtn)

        if type == "Warning":
            self.msgBox.setIcon(QtGui.QMessageBox.Warning)
        elif type == "Error":
            self.msgBox.setIcon(QtGui.QMessageBox.Critical)

        return self.msgBox.exec_()

    def center_window(self):
        """
        Move the window to the center of the screen

        """
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def open_in_explorer(self):
        """
        Open selected assets in explorer
        """
        subprocess.Popen(r'explorer /select,' + str(self.assetPathLbl.text()))

    def apply_style(self, form):

        form.setWindowFlags(form.windowFlags() | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)

        # Create Favicon
        app_icon = QtGui.QIcon()
        app_icon.addFile(self.cur_path + "\\media\\favicon.png", QtCore.QSize(16, 16))
        form.setWindowIcon(app_icon)

        if int(self.theme) == 0:
            # Apply custom CSS to msgBox
            css = QtCore.QFile(self.cur_path + "\\media\\style.css")
            css.open(QtCore.QIODevice.ReadOnly)
            if css.isOpen():
                form.setStyleSheet(QtCore.QVariant(css.readAll()).toString())
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
        str = str
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

    def take_screenshot(self, path):

        self.hide()

        # constants
        SCREEN_GRABBER = "Z:\\Groupes-cours\\NAND999-A15-N01\\Nature\\_pipeline\\_utilities\\_soft\\screenshot_grabber\\MiniCap.exe"

        # filename
        file_name = path

        # run the screen grabber
        subprocess.call([SCREEN_GRABBER, '-captureregselect', '-exit', '-save', file_name])
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
        if len(self.projectList.selectedItems()) == 0:
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

class CheckNews(Thread):
    def __init__(self, main):
        Thread.__init__(self)
        self.last_news = ""
        self.main = main
        self.check_news_cursor = self.main.db.cursor()
        self.last_news_id = self.check_news_cursor.execute('''SELECT max(log_id) FROM log''').fetchone()[0]

    def run(self):
        while True:
            self.check_news()
            time.sleep(10)

    def check_news(self):
        last_news_id = self.check_news_cursor.execute('''SELECT max(log_id) FROM log''').fetchone()
        last_news_id = last_news_id[0]

        if last_news_id > self.last_news_id: # There are new entries on the log
            log_entry = self.check_news_cursor.execute('''SELECT log_entry FROM log WHERE log_id=?''', (last_news_id,)).fetchone()[0]
            username = log_entry.split(" ")[0]

            if "reference" in log_entry:
                title = "{0} added a new reference!".format(username)
                self.main.tray_message = "Click here to see it"
            elif "comment" in log_entry:
                title = "{0} added a new comment!".format(username)
                self.main.tray_message = "Click here to see it"
            elif "task" in log_entry:
                title = "{0} added a new task!".format(username)
                self.main.tray_message = "Click here to see it"
            else:
                title = "New event"
                self.main.tray_message = "Unknown"

            self.main.tray_icon_log_id = last_news_id
            self.main.tray_icon.showMessage(title, self.main.tray_message, QtGui.QSystemTrayIcon.Information, 10000)
            self.last_news_id = last_news_id
        elif last_news_id < self.last_news_id:
            self.last_news_id = last_news_id

        if not self.main.Tabs.currentIndex() == self.main.Tabs.count() - 1:
            self.main.WhatsNew.load_whats_new(self.main)
            self.add_to_check_news = 0


