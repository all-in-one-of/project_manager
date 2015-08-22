#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import subprocess
import webbrowser
from PyQt4 import phonon
import os

class ThibListWidget(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(ThibListWidget, self).__init__()
        self.keylist = []

    def wheelEvent(self, event):
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + (int(-event.delta() * 3)))
        elif QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + (int(-event.delta() / 3)))
        elif QtGui.QApplication.keyboardModifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + (int(-event.delta() * 10)))
        else:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + (int(-event.delta())))

    def keyPressEvent(self, QKeyEvent):
        key = QKeyEvent.key()

        self.firstrelease = True
        self.keylist.append(key)

        if key == QtCore.Qt.Key_Delete:
            if self.objectName() == "versionList":
                self.emit(QtCore.SIGNAL('delete_selected_asset_version'))
                return
            elif self.objectName() == "referenceThumbListWidget":
                self.emit(QtCore.SIGNAL('delete_selected_reference'))
                return

        if key == QtCore.Qt.Key_Up:
            while True:
                try:
                    self.setCurrentRow(self.currentRow() - 1)
                    item = self.selectedItems()[0]
                except:
                    break
                if not item.isHidden():
                    break
        elif key == QtCore.Qt.Key_Down:
            while True:
                try:
                    self.setCurrentRow(self.currentRow() + 1)
                    item = self.selectedItems()[0]
                except:
                    break
                if not item.isHidden():
                    break

        if self.objectName() == "versionList":
            self.emit(QtCore.SIGNAL('version_arrow_key_pressed'))
        elif self.objectName() == "assetList":
            self.emit(QtCore.SIGNAL('asset_arrow_key_pressed'))
        elif self.objectName() == "departmentList":
            self.emit(QtCore.SIGNAL('department_arrow_key_pressed'))
        elif self.objectName() == "seqList":
            self.emit(QtCore.SIGNAL('seq_arrow_key_pressed'))
        elif self.objectName() == "shotList":
            self.emit(QtCore.SIGNAL('shot_arrow_key_pressed'))

        return

    def keyReleaseEvent(self, QKeyEvent):
        self.firstrelease = False
        if (QtCore.Qt.Key_Space and QtCore.Qt.Key_Control) in self.keylist:
            if self.objectName() in ["versionList", "assetList"]:
                self.emit(QtCore.SIGNAL('versionList_advanced_view'))
        elif QtCore.Qt.Key_Space in self.keylist:
            if self.objectName() in ["versionList", "assetList"]:
                self.emit(QtCore.SIGNAL('versionList_simple_view'))

        self.keylist = []



class profilPicLabel(QtGui.QLabel):
    def __init__(self, parent, *args, **kwargs):
        QtGui.QLabel.__init__(self, parent, *args, **kwargs)
        self._data = None

    def mousePressEvent(self, ev):
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            self.emit(QtCore.SIGNAL('double_clicked'), self, self._data)
        else:
            self.emit(QtCore.SIGNAL('clicked'), self, self._data)

    def getData(self):
        return self._data

    def setData(self, data):
        self._data = data




