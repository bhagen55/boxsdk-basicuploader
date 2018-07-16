import sys
from backend import BoxInterface
from objects import BoxItem
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QTreeView,
        QVBoxLayout, QWidget, QMenu, QMessageBox, QAction, QMainWindow)


class AssetUploader(QMainWindow):

    def __init__(self):
        super().__init__()

        # Setup Box interface
        self.box = BoxInterface.BoxInterface("./keys/appauth.json")

        # Icon location
        self.iconPath = Path("./icons")

        self.title = ("Asset Uploader")

        self.left = 50
        self.top = 50
        self.width = 640
        self.height = 240

        self.initUI()


    def initUI(self):
        # Title/icon
        self.setWindowTitle(self.title)

        # Location/size
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Menu bar
        refreshAction = QAction("&Refresh")
        menu = self.menuBar()
        utMenu = menu.addMenu('&Utilities')

        # Icons
        print(str(self.iconPath / "folder.png"))
        self.folderIcon = QIcon(str(self.iconPath / "folder.png"))
        self.windowIcon = QIcon(str(self.iconPath / "upload.png"))
        self.setWindowIcon(self.windowIcon)

        # Tree view
        self.treeView = QTreeView()
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.setHeaderHidden(True)

        self.model = QStandardItemModel()
        self.model.dataChanged.connect(self.updateIndex)
        self.buildModel(self.model)

        self.treeView.setModel(self.model)

        # Add all to main layout
        # mainLayout = QVBoxLayout()
        # mainLayout.addWidget(self.treeView)
        # self.setLayout(mainLayout)

        # Communication/action
        self.treeView.customContextMenuRequested.connect(self.contextMenu)
        refreshAction.triggered.connect(self.buildModel)

        self.show()


    def buildFileTree(self, root):
        for item in self.box.get_folder_contents(root.boxData):
            new = BoxItem.BoxItem(self.box, item)
            root.appendRow(new)
            #print("Adding " + new.boxData['name'] + " to " + root.boxData['name'])
            if item['type'] == "folder":
                    new.setIcon(self.folderIcon)
                    print(new.icon())
                    self.buildFileTree(new)

    def buildModel(self, model):
        model.clear()
        root = BoxItem.BoxItem(self.box, self.box.get_folder('0'))
        root.setIcon(self.folderIcon)
        root.setIcon(self.folderIcon)
        model.appendRow(root)
        self.buildFileTree(root)


    def updateIndex(self, index):
        modified = index.model().itemFromIndex(index)
        print(index.column())
        print(index.row())
        print(modified)
        parent = modified.parent()
        parent.removeRows(0, parent.columnCount())
        self.buildFileTree(parent)


    def contextMenu(self, position):
        index = self.treeView.selectedIndexes()[0]
        selected = index.model().itemFromIndex(index)
        selected.showContextMenu(self.treeView, position)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = AssetUploader()
    sys.exit(app.exec_())
