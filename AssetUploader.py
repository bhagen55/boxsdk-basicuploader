import sys
from backend import BoxInterface
from treeitems import BoxTreeModel, BoxTreeItem
from PyQt5.QtCore import (QDate, QDateTime, QRegExp, QSortFilterProxyModel, Qt,
        QTime)
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
        QGroupBox, QHBoxLayout, QLabel, QLineEdit, QTreeView, QVBoxLayout,
        QWidget)



class AssetUploader(QWidget):

    def __init__(self):
        super().__init__()

        # Setup Box interface
        self.box = BoxInterface.BoxInterface("./keys/appauth.json")

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

        # Tree view
        self.dataGroupBox = QGroupBox("Asset Store")
        self.dataView = QTreeView()
        #self.dataView.setRootIsDecorated(False)
        #self.dataView.setAlternatingRowColors(True)

        dataLayout = QHBoxLayout()
        dataLayout.addWidget(self.dataView)
        self.dataGroupBox.setLayout(dataLayout)

        model = BoxTreeModel.BoxTreeModel(self.box)
        self.dataView.setModel(model)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.dataGroupBox)
        self.setLayout(mainLayout)

        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = AssetUploader()
    sys.exit(app.exec_())
