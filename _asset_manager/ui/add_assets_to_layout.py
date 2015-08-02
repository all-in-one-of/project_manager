# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'H:\01-NAD\_pipeline\_utilities\_asset_manager\ui\add_assets_to_layout.ui'
#
# Created: Sat Aug 01 14:10:05 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_addAssetsToLayoutWidget(object):
    def setupUi(self, addAssetsToLayoutWidget):
        addAssetsToLayoutWidget.setObjectName(_fromUtf8("addAssetsToLayoutWidget"))
        addAssetsToLayoutWidget.resize(1100, 750)
        addAssetsToLayoutWidget.setMinimumSize(QtCore.QSize(1100, 750))
        addAssetsToLayoutWidget.setMaximumSize(QtCore.QSize(1100, 750))
        self.verticalLayout_3 = QtGui.QVBoxLayout(addAssetsToLayoutWidget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.listsFrame = QtGui.QFrame(addAssetsToLayoutWidget)
        self.listsFrame.setFrameShape(QtGui.QFrame.NoFrame)
        self.listsFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.listsFrame.setObjectName(_fromUtf8("listsFrame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.listsFrame)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.addAssetsListFrame = QtGui.QFrame(self.listsFrame)
        self.addAssetsListFrame.setFrameShape(QtGui.QFrame.NoFrame)
        self.addAssetsListFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.addAssetsListFrame.setObjectName(_fromUtf8("addAssetsListFrame"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.addAssetsListFrame)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.availableAssetsLbl = QtGui.QLabel(self.addAssetsListFrame)
        self.availableAssetsLbl.setObjectName(_fromUtf8("availableAssetsLbl"))
        self.verticalLayout_2.addWidget(self.availableAssetsLbl)
        self.availableAssetsListWidget = QtGui.QListWidget(self.addAssetsListFrame)
        self.availableAssetsListWidget.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.availableAssetsListWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.availableAssetsListWidget.setIconSize(QtCore.QSize(256, 256))
        self.availableAssetsListWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.availableAssetsListWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.availableAssetsListWidget.setViewMode(QtGui.QListView.IconMode)
        self.availableAssetsListWidget.setObjectName(_fromUtf8("availableAssetsListWidget"))
        self.verticalLayout_2.addWidget(self.availableAssetsListWidget)
        self.horizontalLayout.addWidget(self.addAssetsListFrame)
        self.addRemoveAssetFrame = QtGui.QFrame(self.listsFrame)
        self.addRemoveAssetFrame.setFrameShape(QtGui.QFrame.NoFrame)
        self.addRemoveAssetFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.addRemoveAssetFrame.setObjectName(_fromUtf8("addRemoveAssetFrame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.addRemoveAssetFrame)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.addAssetBtn = QtGui.QPushButton(self.addRemoveAssetFrame)
        self.addAssetBtn.setMaximumSize(QtCore.QSize(32, 32))
        self.addAssetBtn.setObjectName(_fromUtf8("addAssetBtn"))
        self.verticalLayout.addWidget(self.addAssetBtn)
        self.removeAssetBtn = QtGui.QPushButton(self.addRemoveAssetFrame)
        self.removeAssetBtn.setMaximumSize(QtCore.QSize(32, 32))
        self.removeAssetBtn.setObjectName(_fromUtf8("removeAssetBtn"))
        self.verticalLayout.addWidget(self.removeAssetBtn)
        self.horizontalLayout.addWidget(self.addRemoveAssetFrame)
        self.assetsToAddFrame = QtGui.QFrame(self.listsFrame)
        self.assetsToAddFrame.setFrameShape(QtGui.QFrame.NoFrame)
        self.assetsToAddFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.assetsToAddFrame.setObjectName(_fromUtf8("assetsToAddFrame"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.assetsToAddFrame)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.assetsToAddLbl = QtGui.QLabel(self.assetsToAddFrame)
        self.assetsToAddLbl.setObjectName(_fromUtf8("assetsToAddLbl"))
        self.verticalLayout_4.addWidget(self.assetsToAddLbl)
        self.assetsToAddListWidget = QtGui.QListWidget(self.assetsToAddFrame)
        self.assetsToAddListWidget.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.assetsToAddListWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.assetsToAddListWidget.setIconSize(QtCore.QSize(256, 256))
        self.assetsToAddListWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.assetsToAddListWidget.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.assetsToAddListWidget.setViewMode(QtGui.QListView.IconMode)
        self.assetsToAddListWidget.setObjectName(_fromUtf8("assetsToAddListWidget"))
        self.verticalLayout_4.addWidget(self.assetsToAddListWidget)
        self.horizontalLayout.addWidget(self.assetsToAddFrame)
        self.verticalLayout_3.addWidget(self.listsFrame)
        self.addAssetsToLayoutBtn = QtGui.QPushButton(addAssetsToLayoutWidget)
        self.addAssetsToLayoutBtn.setObjectName(_fromUtf8("addAssetsToLayoutBtn"))
        self.verticalLayout_3.addWidget(self.addAssetsToLayoutBtn)

        self.retranslateUi(addAssetsToLayoutWidget)
        QtCore.QMetaObject.connectSlotsByName(addAssetsToLayoutWidget)
        
        return self

    def retranslateUi(self, addAssetsToLayoutWidget):
        addAssetsToLayoutWidget.setWindowTitle(_translate("addAssetsToLayoutWidget", "Layout Asset Manager", None))
        self.availableAssetsLbl.setText(_translate("addAssetsToLayoutWidget", "Available assets", None))
        self.addAssetBtn.setText(_translate("addAssetsToLayoutWidget", ">>", None))
        self.removeAssetBtn.setText(_translate("addAssetsToLayoutWidget", "<<", None))
        self.assetsToAddLbl.setText(_translate("addAssetsToLayoutWidget", "Assets to add", None))
        self.addAssetsToLayoutBtn.setText(_translate("addAssetsToLayoutWidget", "Add Assets to Layout", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    addAssetsToLayoutWidget = QtGui.QWidget()
    ui = Ui_addAssetsToLayoutWidget()
    ui.setupUi(addAssetsToLayoutWidget)
    addAssetsToLayoutWidget.show()
    sys.exit(app.exec_())

