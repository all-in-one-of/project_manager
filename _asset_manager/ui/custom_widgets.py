#!/usr/bin/env python
# coding=utf-8

from PyQt4 import QtGui, QtCore
import subprocess
import webbrowser

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
        self.emit(QtCore.SIGNAL('clicked'), self, self._data)

    def getData(self):
        return self._data

    def setData(self, data):
        self._data = data

