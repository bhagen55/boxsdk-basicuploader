"""
Using QAbstractItemModel, creates a model useable in PyQT's tree view
containing needed data to act as a file tree for Box.
"""

from PyQt5.QtCore import QAbstractItemModel, QFile, QIODevice, QModelIndex, Qt
from PyQt5.QtWidgets import QApplication, QTreeView
# TODO: Check imports for unused

class BoxTreeItem(object):

    def __init__(self, boxitem, parentfolder=None, contents=[]):
        self.parentFolder = parentfolder
        self.boxItem = boxitem
        self.data = [self.boxItem['id'], self.boxItem['name']]
        self.contents = contents

    def appendChild(self, item):
        self.contents.append(item)

    def child(self, row):
        return self.contents[row]

    def childCount(self):
        return len(self.contents)

    # Show 2 columns: Name and Size
    def columnCount(self):
        return(len(self.data))

    def data(self, column):
        try:
            return self.data[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentFolder

    def row(self):
        if self.parentFolder:
            return self.parentFolder.contents.index(self)
