from PyQt5.QtGui import QStandardItem

def BoxItem(QStandardItem):
    def __init__(box, boxfile):
        super(BoxItem, self).__init__(boxfile['name'])
        self.boxData = boxfile
        self.box = box

    def contextMenuEvent(event):
        print("context!")
