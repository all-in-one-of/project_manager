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

        if key == QtCore.Qt.Key_Up:
            while True:
                try:
                    self.setCurrentRow(self.currentRow() - 1)
                    item = self.selectedItems()[0]
                    self.emit(QtCore.SIGNAL('arrow_key_pressed'))
                except:
                    break
                if not item.isHidden():
                    break
        elif key == QtCore.Qt.Key_Down:
            while True:
                try:
                    self.setCurrentRow(self.currentRow() + 1)
                    item = self.selectedItems()[0]
                    self.emit(QtCore.SIGNAL('arrow_key_pressed'))
                except:
                    break
                if not item.isHidden():
                    break


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




