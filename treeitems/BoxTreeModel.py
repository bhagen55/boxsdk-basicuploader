from PyQt5.QtCore import QAbstractItemModel, QFile, QIODevice, QModelIndex, Qt
from PyQt5.QtWidgets import QApplication, QTreeView
from backend import BoxInterface
from treeitems import BoxTreeItem
from pathlib import Path


class BoxTreeModel(QAbstractItemModel):

    def __init__(self, boxclient, parent=None):
        super(BoxTreeModel, self).__init__(parent)

        self.box = boxclient
        self.rootItem = BoxTreeItem.BoxTreeItem(self.box.get_folder('0'))
        self.buildFileStructure(self.box, self.rootItem)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data[index.column()]

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data[section]

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)
        for file in self.box.get_folder_contents(self.box.get_folder('0')):
            self.addFile(model, file)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()


    def buildFileStructure(self, boxinterface, boxitem, parent=None):
        for item in boxinterface.get_folder_contents(boxitem.boxItem):
            new = BoxTreeItem.BoxTreeItem(item, boxitem)
            boxitem.appendChild(new)
            print("Adding " + new.boxItem['name'] + " to " + boxitem.boxItem['name'])
            if item['type'] == "folder":
                    self.buildFileStructure(boxinterface, new, boxitem)
