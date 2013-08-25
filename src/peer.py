from PyQt4.QtCore import *
from PyQt4.QtGui import *
import utils
from abstractpeer import AbstractPeer

# Class to represent a peer on the network and the gui
class Peer(QListWidgetItem, AbstractPeer):
    def __init__(self, id, name, address, port):
        QListWidgetItem.__init__(self)
        self.id = id
        self.address = address
        self.name = name
        self.port = int(port)
        self.setText("\n  {0}\n  {1}:{2}\n".format(self.name, self.address, self.port))
        self.setSelected(False)
        
    def __str__(self):
        return self.id

    def __eq__(self, other):
        """needed to be able to remove items from peers form the list"""
        if self.id == other.id:
            if self.address == other.address:
                if self.port == other.port:
                    return True
        return False
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
            self.setSelected(False)
        else:
            event.ignore()