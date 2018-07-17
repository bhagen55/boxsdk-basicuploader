import sys, os
from shutil import copy
from boxwrappers import BoxInterface, BoxItem
from pathlib import Path
import logging
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QTreeView,
        QVBoxLayout, QWidget, QMenu, QMessageBox, QAction, QMainWindow, QDialog,
        QCheckBox, QPushButton, QGridLayout, QLineEdit, QFileDialog, QLabel,
        QStyle)


class AssetUploader(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup Box interface
        self.keyPath = Path("./authfiles")
        self.keyName = "appauth.json"
        self.box = None
        if os.path.isdir(str(self.keyPath)):
            if os.path.exists(str(self.keyPath / self.keyName)):
                self.box = BoxInterface.BoxInterface(str(self.keyPath / self.keyName))
        else:
            os.makedirs(str(self.keyPath))

        if self.box is None:
            auth = AuthWindowDialog(self)
            choice = auth.exec_() # blocks while dialog open
            if choice == 0: # cancelled
                sys.exit()
            else:
                if auth.importKey:
                    copy(auth.path, (self.keyPath / self.keyName))
                    self.box = BoxInterface.BoxInterface(self.keyPath / self.keyName)
                else:
                    self.box = BoxInterface.BoxInterface(auth.path)

        # Icons
        self.folderIcon = self.style().standardIcon(getattr(QStyle, 'SP_DirClosedIcon'))
        self.fileIcon = self.style().standardIcon(getattr(QStyle, 'SP_FileIcon'))
        self.windowIcon = self.style().standardIcon(getattr(QStyle, 'SP_ArrowUp'))

        self.title = ("Asset Uploader")

        self.width = 640
        self.height = 240

        self.initUI()


    def initUI(self):
        # Title/icon
        self.setWindowTitle(self.title)

        # Menu bar
        menu = self.menuBar()
        utilMenu = menu.addMenu('File')
        refreshButton = QAction('Refresh', self)
        utilMenu.addAction(refreshButton)
        refreshButton.triggered.connect(self.rebuildModel)

        # Status bar w/ logging
        statusBarHandler = StatusBarLogger(self)
        logging.getLogger().addHandler(statusBarHandler)
        logging.getLogger().setLevel(logging.WARNING)

        # Icons
        self.setWindowIcon(self.windowIcon)

        # Tree view
        self.treeView = QTreeView()
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.setHeaderHidden(True)

        self.model = QStandardItemModel()
        self.model.dataChanged.connect(self.updateIndex)
        self.rebuildModel()

        self.treeView.setModel(self.model)

        # Add all to main layout
        mainWidget = QWidget(self)
        mainLayout = QVBoxLayout(mainWidget)
        self.setCentralWidget(mainWidget)
        mainLayout.addWidget(self.treeView)

        # Communication
        self.treeView.customContextMenuRequested.connect(self.contextMenu)

        self.show()


    def buildFileTree(self, root):
        self.model.dataChanged.disconnect(self.updateIndex)
        self.__recursBuildFileTree(root)
        self.model.dataChanged.connect(self.updateIndex)


    def __recursBuildFileTree(self, root):
        for item in self.box.get_folder_contents(root.boxData):
            new = BoxItem.BoxItem(self.box, item)
            root.appendRow(new)
            if item['type'] == "folder":
                new.setIcon(self.folderIcon)
                self.__recursBuildFileTree(new)
            else:
                new.setIcon(self.fileIcon)
        self.treeView.setSortingEnabled(True)


    def rebuildModel(self):
        self.model.clear()
        root = BoxItem.BoxItem(self.box, self.box.get_folder('0'))
        root.setIcon(self.folderIcon)
        root.setIcon(self.folderIcon)
        self.model.appendRow(root)
        self.buildFileTree(root)



    def updateIndex(self, index):
        modified = index.model().itemFromIndex(index)
        parent = modified.parent()
        if parent is None: # Must be the root that was modified
            parent = modified
        parent.removeRows(0, parent.rowCount())
        self.buildFileTree(parent)
        self.treeView


    def contextMenu(self, position):
        index = self.treeView.selectedIndexes()[0]
        selected = index.model().itemFromIndex(index)
        selected.showContextMenu(self.treeView, position)


class StatusBarLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        parent.statusBar().showMessage("Log display enabled.")


    def emit(self, record):
        msg = self.format(record)
        self.parent.statusBar().showMessage(msg)


class AuthWindowDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Authenticate")
        self.path = None
        self.importKey = False

        mainLayout = QGridLayout()
        self.setLayout(mainLayout)

        infoLabel = QLabel("Please pick authentication information file provided by Box."
                           + "\nIf Copy Key is selected, the key will be copied to"
                           "\nthe app's authfile directory and the key will not need"
                           "\nto be provided on start.")
        mainLayout.addWidget(infoLabel, 0,1)

        pathLayout = QHBoxLayout()
        mainLayout.addLayout(pathLayout, 1,1)
        self.pathBox = QLineEdit()
        self.pathBox.setPlaceholderText("Key path")
        pathLayout.addWidget(self.pathBox)
        pathBrowseButton = QPushButton('Browse', self)
        pathLayout.addWidget(pathBrowseButton)
        pathBrowseButton.clicked.connect(self.getKeyPath)

        saveLayout = QHBoxLayout()
        mainLayout.addLayout(saveLayout, 2, 1)
        self.saveCheck = QCheckBox("Copy Key")
        saveLayout.addWidget(self.saveCheck)

        buttonLayout = QHBoxLayout()
        mainLayout.addLayout(buttonLayout, 3,1)
        okButton = QPushButton('Ok', self)
        okButton.clicked.connect(self.close)
        cancelButton = QPushButton('Cancel', self)
        cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)


    def getKeyPath(self, action):
        choice, type = QFileDialog.getOpenFileName(self, "Choose key to authenticate with")
        self.pathBox.insert(choice)


    def close(self, action):
        self.path = self.pathBox.text()
        if os.path.exists(self.path):
            self.importKey = self.saveCheck.isChecked()
            self.accept()
        else:
            notFoundDialog = QMessageBox(self)
            notFoundDialog.setText("File Not Found")
            notFoundDialog.setWindowTitle("File not found.")
            notFoundDialog.setIcon(QMessageBox.Warning)
            notFoundDialog.setStandardButtons(QMessageBox.Ok)
            notFoundDialog.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = AssetUploader()
    sys.exit(app.exec_())
