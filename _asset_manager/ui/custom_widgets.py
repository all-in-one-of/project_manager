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

        if key == QtCore.Qt.Key_Delete:
            self.emit(QtCore.SIGNAL('delete_selected_asset_version'))
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


class ThibQLabel(QtGui.QLabel):

    def __init(self, parent, *args, **kwargs):
        QtGui.QLabel.__init__(self, parent, *args, **kwargs)
        self._data = None

    def mouseDoubleClickEvent(self, ev):
        try:
            image_path = self._data
        except:
            return
        webbrowser.open(image_path)

    def data(self):
        return self._data

    def setData(self, data):
        self._data = data

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




