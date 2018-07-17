from PyQt5.QtGui import QStandardItem, QIcon
from PyQt5.QtWidgets import (QMenu, QMessageBox, QInputDialog, QFileDialog,
                             QMessageBox)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from pathlib import Path

class BoxItem(QStandardItem):
    def __init__(self, box, boxfile):
        super(BoxItem, self).__init__(boxfile['name'])
        self.boxData = boxfile
        self.box = box
        self.itemType = self.boxData['type']


    def showContextMenu(self, view, position):
        menu = QMenu()
        delete = menu.addAction("Delete")
        if self.itemType == 'folder':
            upload = menu.addAction("Upload Here")
            newFolder = menu.addAction("New Folder")
        elif self.itemType == 'file':
            link = menu.addAction("Get Link")

        action = menu.exec_(view.viewport().mapToGlobal(position))

        if action == delete:
            confirmBox = QMessageBox()
            if self.itemType == 'file':
                confirmBox.setText("Confirm Deletion of File?")
                confirmBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
                confirmBox.setDefaultButton(QMessageBox.Yes)

                choice = confirmBox.exec_()
                if choice == QMessageBox.Yes:
                    self.box.delete_file(self.boxData)
                    self.emitDataChanged()
            elif self.itemType == 'folder':
                confirmBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
                confirmBox.setDefaultButton(QMessageBox.Yes)
                if len(self.box.get_folder_contents(self.boxData)) == 0:
                    confirmBox.setText("Confirm Deletion of Folder?")
                    force = False
                else:
                    confirmBox.setText("Confirm Deletion of Non-Empty Folder?")
                    force = True

                choice = confirmBox.exec_()
                if choice == QMessageBox.Yes:
                    self.box.delete_folder(self.boxData, force)
                    self.emitDataChanged()
        elif self.itemType == 'folder' and action == newFolder:
            newName, choice = QInputDialog.getText(view, "New Folder", "Please input name:")
            if choice:
                self.box.create_folder(self.boxData, newName)
                self.emitDataChanged()
        elif self.itemType == 'folder' and action == upload:
            choices, type = QFileDialog.getOpenFileNames(view, "Choose Files to Upload")

            uploadMessage = QMessageBox(view)
            uploadMessage.setWindowTitle("Wait")
            uploadMessage.show()

            for choice in choices:
                self.box.upload(self.boxData, Path(choice))

            uploadMessage.close()

            self.emitDataChanged()
        elif self.itemType == 'file' and action == link:
            linkBox = QMessageBox()
            linkBox.setTextInteractionFlags(Qt.TextSelectableByMouse)
            linkBox.setText(self.box.get_direct_download(self.boxData))
            linkBox.setStandardButtons(QMessageBox.Ok)
            linkBox.exec_()


    @pyqtSlot()
    def setData(self, value, role):
        if isinstance(value, str):
            if not self.boxData['id'] == '0':
                if self.box.rename(self.boxData, data): # Only if rename successful
                    self.emitDataChanged()
                    super(BoxItem, self).setData(value, role)
        else:
            super(BoxItem, self).setData(value, role)
