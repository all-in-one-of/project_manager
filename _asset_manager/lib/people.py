#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
from functools import partial

class PeopleTab(object):
    def __init__(self):


        self.email = ""
        self.cell = ""

        self.sendEmailBtn.clicked.connect(self.send_email_clicked)


        self.profilPicLblList = [self.profilePicLbl_01,
                              self.profilePicLbl_02,
                              self.profilePicLbl_03,
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
                              self.profilePicLbl_16,
                              self.profilePicLbl_17,
                              self.profilePicLbl_18]

        self.members_photos = [self.cur_path + "\\media\\members_photos\\achaput.jpg",
                               self.cur_path + "\\media\\members_photos\\costiguy.jpg",
                               self.cur_path + "\\media\\members_photos\\cgonnord.jpg",
                               self.cur_path + "\\media\\members_photos\\dcayerdesforges.jpg",
                               self.cur_path + "\\media\\members_photos\\earismendez.jpg",
                               self.cur_path + "\\media\\members_photos\\erodrigue.jpg",
                               self.cur_path + "\\media\\members_photos\\jberger.jpg",
                               self.cur_path + "\\media\\members_photos\\lgregoire.jpg",
                               self.cur_path + "\\media\\members_photos\\lclavet.jpg",
                               self.cur_path + "\\media\\members_photos\\mchretien.jpg",
                               self.cur_path + "\\media\\members_photos\\mbeaudoin.jpg",
                               self.cur_path + "\\media\\members_photos\\mroz.jpg",
                               self.cur_path + "\\media\\members_photos\\obolduc.jpg",
                               self.cur_path + "\\media\\members_photos\\slachapelle.jpg",
                               self.cur_path + "\\media\\members_photos\\thoudon.jpg",
                               self.cur_path + "\\media\\members_photos\\vdelbroucq.jpg",
                               self.cur_path + "\\media\\members_photos\\yjobin.jpg",
                               self.cur_path + "\\media\\members_photos\\yshan.jpg"]

        # Add image to labels
        for i, lbl in enumerate(self.profilPicLblList):
            lbl.setPixmap(QtGui.QPixmap(self.members_photos[i]))
            lbl.setData(self.members_photos[i])
            self.connect(lbl, QtCore.SIGNAL('clicked'), self.profil_pic_clicked)

        self.profilPicInfoLbl.setPixmap(QtGui.QPixmap(self.cur_path + "\\media\\members_photos\\default.jpg"))

        self.get_online_status()

    def get_online_status(self):

        # Get online status from database
        member_online_status = self.cursor.execute('''SELECT is_online FROM preferences''').fetchall()
        member_online_status = [i[0] for i in member_online_status]

        # For each member, add online/offline icon on top of their profile picture depending on status
        for i, member_photo in enumerate(self.members_photos):
            if member_online_status[i] == 1:
                overlay = QtGui.QImage(self.cur_path + "\\media\\online.png")
            else:
                overlay = QtGui.QImage(self.cur_path + "\\media\\offline.png")

            image = QtGui.QImage(member_photo)
            painter = QtGui.QPainter()
            painter.begin(image)
            painter.drawImage(51, 4, overlay)
            painter.end()
            self.profilPicLblList[i].setPixmap(QtGui.QPixmap.fromImage(image))

    def profil_pic_clicked(self, lbl, value):

        username = value.split("\\")[-1].replace(".jpg", "")
        infos = self.cursor.execute('''SELECT * FROM preferences WHERE username=?''', (username,)).fetchone()

        self.email = infos[5]
        self.cell = infos[6]

        self.emailInfoLbl.setText("E-mail: " + self.email)
        self.cellInfoLbl.setText("Cell: " + self.cell)
        self.profilPicInfoLbl.setPixmap(QtGui.QPixmap(value))


    def send_email_clicked(self):
        subject = unicode("Projet Nature:" + self.emailObjectLineEdit.text())
        message = unicode(self.emailMessageTextEdit.toPlainText())
        self.Lib.send_email(self, from_addr="nad.update@gmail.com", addr_list=[str(self.email)], subject=subject, message=message)