import sys
from backend import BoxInterface
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QTreeView,
        QVBoxLayout, QWidget, QMenu, QMessageBox)


class AssetUploader(QWidget):

    def __init__(self):
        super().__init__()

        # Setup Box interface
        self.box = BoxInterface.BoxInterface("./keys/appauth.json")

        # Icon location
        self.iconPath = Path("./icons")

        self.title = ("Asset Uploader")

        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 240

        self.initUI()


    def initUI(self):
        # Title
        self.setWindowTitle(self.title)

        # Location/size
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Icons
        self.folderIcon = QIcon(str(self.iconPath) + "/folder.png")

        # Tree view
        self.treeGroupBox = QGroupBox("Asset Store")
        self.treeView = QTreeView()
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.contextMenu)
        dataLayout = QHBoxLayout()
        dataLayout.addWidget(self.treeView)
        self.treeGroupBox.setLayout(dataLayout)

        # Box root
        self.root = QStandardItem()
        self.root.setData(self.box.get_folder('0'))
        self.root.setText("Root")
        self.root.setIcon(self.folderIcon)

        # Setup file tree
        model = QStandardItemModel()
        model.appendRow(self.root)
        self.treeView.setModel(model)
        self.buildFileTree(self.root)

        # Add all to main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.treeGroupBox)
        self.setLayout(mainLayout)

        self.show()


    def buildFileTree(self, root):
        for item in self.box.get_folder_contents(root.data()):
            new = QStandardItem(item['name'])
            new.setData(item)
            root.appendRow(new)
            print("Adding " + new.data()['name'] + " to " + root.data()['name'])
            if item['type'] == "folder":
                    new.setIcon(self.folderIcon)
                    self.buildFileTree(new)


    def contextMenu(self, position):
        index = self.treeView.selectedIndexes()[0]
        selected = index.model().itemFromIndex(index)
        boxData = selected.data()
        itemType = boxData['type']

        menu = QMenu()
        rename = menu.addAction("Rename")
        delete = menu.addAction("Delete")
        if itemType == 'folder':
            upload = menu.addAction("Upload Here")
        elif itemType == 'file':
            link = menu.addAction("Get Link")

        action = menu.exec_(self.treeView.viewport().mapToGlobal(position))

        if itemType == 'file' and action == link:
            linkWindow = QMessageBox()
            linkWindow.setWindowTitle("Permalink")
            linkWindow.setText(self.box.get_direct_download(boxData))
            linkWindow.setTextInteractionFlags(Qt.TextSelectableByMouse)
            linkWindow.exec()
        elif action == rename:

            print("rename")
        elif action == delete:
            print("delete")
        elif action == upload:
            print("upload")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = AssetUploader()
    sys.exit(app.exec_())
