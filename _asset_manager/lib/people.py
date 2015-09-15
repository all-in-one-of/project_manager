#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
from functools import partial
from datetime import datetime
from dateutil import relativedelta

class PeopleTab(object):

    def __init__(self):

        if self.username not in ["thoudon", "lclavet"]:
            self.sendEmailToEveryoneBtn.hide()

        self.email = ""
        self.cell = ""

        self.sendEmailBtn.clicked.connect(self.send_email_clicked)
        self.sendEmailToEveryoneBtn.clicked.connect(self.send_email_to_everyone_clicked)

        self.profilPicLblList = [
                                 self.profilePicLbl_01,
                              self.profilePicLbl_02,
                              self.profilePicLbl_04,
                              self.profilePicLbl_05,
                              self.profilePicLbl_06,
                              self.profilePicLbl_07,
                              self.profilePicLbl_08,
                              self.profilePicLbl_09,
                              self.profilePicLbl_10,
                              self.profilePicLbl_11,
                              self.profilePicLbl_12,
                              self.profilePicLbl_13,
                              self.profilePicLbl_14,
                              self.profilePicLbl_15,
                              self.profilePicLbl]

        self.members_photos = [
                               self.cur_path + "\\media\\members_photos\\costiguy.jpg",
                               self.cur_path + "\\media\\members_photos\\cgonnord.jpg",
                               self.cur_path + "\\media\\members_photos\\erodrigue.jpg",
                               self.cur_path + "\\media\\members_photos\\jberger.jpg",
                               self.cur_path + "\\media\\members_photos\\lgregoire.jpg",
                               self.cur_path + "\\media\\members_photos\\lclavet.jpg",
                               self.cur_path + "\\media\\members_photos\\mbeaudoin.jpg",
                               self.cur_path + "\\media\\members_photos\\mroz.jpg",
                               self.cur_path + "\\media\\members_photos\\obolduc.jpg",
                               self.cur_path + "\\media\\members_photos\\slachapelle.jpg",
                               self.cur_path + "\\media\\members_photos\\thoudon.jpg",
                               self.cur_path + "\\media\\members_photos\\vdelbroucq.jpg",
                               self.cur_path + "\\media\\members_photos\\yjobin.jpg",
                               self.cur_path + "\\media\\members_photos\\yshan.jpg",
                                self.cur_path + "\\media\\members_photos\\rtremblay.jpg"]

        self.members_mail = ["ostiguy.chloe@gmail.com",
                             "christopher.gonnord@gmail.com",
                             "etienne.rodrigue89@gmail.com",
                             "jeremy.berger3d@gmail.com",
                             "lau-gregoire@hotmail.com",
                             "clavet.lp@gmail.com",
                             "beaudoinmathieu@hotmail.com",
                             "maximeroz@gmail.com",
                             "ol.bolduc@gmail.com",
                             "simonlachapelle@gmail.com",
                             "houdon.thibault@gmail.com",
                             "valentin.delbroucq@gmail.com",
                             "yannjobinphoto@gmail.com",
                             "yishan3d@gmail.com",
                             "rtremblay@nad.ca"]

        # Add image to labels
        for i, lbl in enumerate(self.profilPicLblList):
            lbl.setPixmap(QtGui.QPixmap(self.members_photos[i]))
            lbl.setData(self.members_photos[i])
            self.connect(lbl, QtCore.SIGNAL('clicked'), self.profil_pic_clicked)
            self.connect(lbl, QtCore.SIGNAL('double_clicked'), self.check_on_double_click)

        self.profilPicInfoLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\members_photos\\default.jpg"))

        self.get_online_status()

    def get_online_status(self):

        # Get online status from database
        member_online_status = self.cursor.execute('''SELECT is_online FROM preferences''').fetchall()
        member_online_status = [i[0] for i in member_online_status]

        # For each member, add online/offline icon on top of their profile picture depending on status
        for i, member_photo in enumerate(self.members_photos):
            if member_online_status[i] == 1:
                image = QtGui.QImage(member_photo)
                p1 = p2 = QtCore.QPoint()
                p2.setY(image.height())

                gradient = QtGui.QLinearGradient(p1, p2)
                gradient.setColorAt(0, QtCore.Qt.transparent)
                gradient.setColorAt(1, QtGui.QColor(255, 255, 255, 25))

                painter = QtGui.QPainter(image)
                painter.fillRect(0, 0, image.width(), image.height(), gradient)

                gradient.setColorAt(0, QtGui.QColor(255, 255, 255, 25))
                gradient.setColorAt(1, QtCore.Qt.transparent)
                painter.fillRect(0, 0, image.width(), image.height(), gradient)

                painter.end()
            else:
                image = QtGui.QImage(member_photo)
                p1 = p2 = QtCore.QPoint()
                p2.setY(image.height())

                gradient = QtGui.QLinearGradient(p1, p2)
                gradient.setColorAt(0, QtCore.Qt.transparent)
                gradient.setColorAt(1, QtGui.QColor(0, 0, 0, 225))

                painter = QtGui.QPainter(image)
                painter.fillRect(0, 0, image.width(), image.height(), gradient)

                gradient.setColorAt(0, QtGui.QColor(0, 0, 0, 225))
                gradient.setColorAt(1, QtCore.Qt.transparent)
                painter.fillRect(0, 0, image.width(), image.height(), gradient)

                painter.end()


            self.profilPicLblList[i].setPixmap(QtGui.QPixmap.fromImage(image))

    def profil_pic_clicked(self, lbl, value):

        self.profile_username = value.split("\\")[-1].replace(".jpg", "")
        infos = self.cursor.execute('''SELECT * FROM preferences WHERE username=?''', (self.profile_username,)).fetchone()

        self.email = infos[5]
        self.cell = infos[6]

        self.last_active = infos[4]
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

        self.emailInfoLbl.setText("E-mail: " + self.email)
        self.cellInfoLbl.setText("Cell: " + self.cell)
        self.lastActiveLbl.setText("Last Active: {0} ({1} days, {2} hours, {3} minutes ago)".format(self.last_active, last_active_period.days, last_active_period.hours, last_active_period.minutes))
        self.profilPicInfoLbl.setPixmap(QtGui.QPixmap(value))

        self.check_on_double_click(lbl, value)

    def send_email_clicked(self):

        subject = self.emailObjectLineEdit.text()
        subject = unicode(self.utf8_codec.fromUnicode(subject), 'utf-8')

        message = self.emailMessageTextEdit.toPlainText()
        message = unicode(self.utf8_codec.fromUnicode(message), 'utf-8')

        addr_list = []

        if self.costiguyProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[0])
        if self.cgonnordProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[1])
        if self.erodrigueProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[2])
        if self.jbergerProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[3])
        if self.lgregoireProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[4])
        if self.lclavetProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[5])
        if self.mbeaudoinProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[6])
        if self.mrozProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[7])
        if self.obolducProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[8])
        if self.slachapelleProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[9])
        if self.thoudonProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[10])
        if self.vdelbroucqProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[11])
        if self.yjobinProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[12])
        if self.yshanProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[13])
        if self.rtremblayProfilCheckBox.checkState() == 2:
            addr_list.append(self.members_mail[14])

        self.Lib.send_email(self, from_addr="nad.update@gmail.com", addr_list=addr_list, subject=subject, message=message, username=self.members[self.username])

    def send_email_to_everyone_clicked(self):

        result = self.Lib.message_box(self, type="warning", yes_button_text="Send", text="You're about to send an E-Mail to everyone, are you sure?")

        if str(result) == str(1024):
            return

        subject = self.emailObjectLineEdit.text()
        subject = unicode(self.utf8_codec.fromUnicode(subject), 'utf-8')

        message = self.emailMessageTextEdit.toPlainText()
        message = unicode(self.utf8_codec.fromUnicode(message), 'utf-8')

        addr_list = []
        addr_list.append(self.members_mail[0])
        addr_list.append(self.members_mail[1])
        addr_list.append(self.members_mail[2])
        addr_list.append(self.members_mail[3])
        addr_list.append(self.members_mail[4])
        addr_list.append(self.members_mail[5])
        addr_list.append(self.members_mail[6])
        addr_list.append(self.members_mail[7])
        addr_list.append(self.members_mail[8])
        addr_list.append(self.members_mail[9])
        addr_list.append(self.members_mail[10])
        addr_list.append(self.members_mail[11])
        addr_list.append(self.members_mail[12])
        addr_list.append(self.members_mail[13])
        addr_list.append(self.members_mail[14])

        self.Lib.send_email(self, from_addr="nad.update@gmail.com", addr_list=addr_list, subject=subject, message=message, username=self.members[self.username])

    def check_on_double_click(self, lbl, value):

        if value.split("\\")[-1].replace(".jpg", "") == "costiguy":
            if self.costiguyProfilCheckBox.checkState() == 2:
                self.costiguyProfilCheckBox.setCheckState(0)
                self.costiguyProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.costiguyProfilCheckBox.setCheckState(2)
                self.costiguyProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "cgonnord":
            if self.cgonnordProfilCheckBox.checkState() == 2:
                self.cgonnordProfilCheckBox.setCheckState(0)
                self.cgonnordProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.cgonnordProfilCheckBox.setCheckState(2)
                self.cgonnordProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "erodrigue":
            if self.erodrigueProfilCheckBox.checkState() == 2:
                self.erodrigueProfilCheckBox.setCheckState(0)
                self.erodrigueProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.erodrigueProfilCheckBox.setCheckState(2)
                self.erodrigueProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "jberger":
            if self.jbergerProfilCheckBox.checkState() == 2:
                self.jbergerProfilCheckBox.setCheckState(0)
                self.jbergerProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.jbergerProfilCheckBox.setCheckState(2)
                self.jbergerProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "lgregoire":
            if self.lgregoireProfilCheckBox.checkState() == 2:
                self.lgregoireProfilCheckBox.setCheckState(0)
                self.lgregoireProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.lgregoireProfilCheckBox.setCheckState(2)
                self.lgregoireProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "lclavet":
            if self.lclavetProfilCheckBox.checkState() == 2:
                self.lclavetProfilCheckBox.setCheckState(0)
                self.lclavetProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.lclavetProfilCheckBox.setCheckState(2)
                self.lclavetProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "mbeaudoin":
            if self.mbeaudoinProfilCheckBox.checkState() == 2:
                self.mbeaudoinProfilCheckBox.setCheckState(0)
                self.mbeaudoinProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.mbeaudoinProfilCheckBox.setCheckState(2)
                self.mbeaudoinProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "mroz":
            if self.mrozProfilCheckBox.checkState() == 2:
                self.mrozProfilCheckBox.setCheckState(0)
                self.mrozProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.mrozProfilCheckBox.setCheckState(2)
                self.mrozProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "obolduc":
            if self.obolducProfilCheckBox.checkState() == 2:
                self.obolducProfilCheckBox.setCheckState(0)
                self.obolducProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.obolducProfilCheckBox.setCheckState(2)
                self.obolducProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "slachapelle":
            if self.slachapelleProfilCheckBox.checkState() == 2:
                self.slachapelleProfilCheckBox.setCheckState(0)
                self.slachapelleProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.slachapelleProfilCheckBox.setCheckState(2)
                self.slachapelleProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "thoudon":
            if self.thoudonProfilCheckBox.checkState() == 2:
                self.thoudonProfilCheckBox.setCheckState(0)
                self.thoudonProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.thoudonProfilCheckBox.setCheckState(2)
                self.thoudonProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "vdelbroucq":
            if self.vdelbroucqProfilCheckBox.checkState() == 2:
                self.vdelbroucqProfilCheckBox.setCheckState(0)
                self.vdelbroucqProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.vdelbroucqProfilCheckBox.setCheckState(2)
                self.vdelbroucqProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "yjobin":
            if self.yjobinProfilCheckBox.checkState() == 2:
                self.yjobinProfilCheckBox.setCheckState(0)
                self.yjobinProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.yjobinProfilCheckBox.setCheckState(2)
                self.yjobinProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "yshan":
            if self.yshanProfilCheckBox.checkState() == 2:
                self.yshanProfilCheckBox.setCheckState(0)
                self.yshanProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.yshanProfilCheckBox.setCheckState(2)
                self.yshanProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")

        elif value.split("\\")[-1].replace(".jpg", "") == "rtremblay":
            if self.rtremblayProfilCheckBox.checkState() == 2:
                self.rtremblayProfilCheckBox.setCheckState(0)
                self.rtremblayProfilCheckBox.setStyleSheet("color: black; font-weight: normal;")
            else:
                self.rtremblayProfilCheckBox.setCheckState(2)
                self.rtremblayProfilCheckBox.setStyleSheet("color: #58a155; font-weight: bold;")