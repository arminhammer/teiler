from PySide.QtCore import *
from PySide.QtGui import *

# Class to represent a peer on the network and the gui
class TeilerPeer(QListWidgetItem):
    def __init__(self, address, name):
        QListWidgetItem.__init__(self)
        self.address = address
        self.name = name
        self.setText("{0} at {1}".format(self.name, self.address))

# Class that keeps track of the peers and displays them to the user
class TeilerPeerList(QListWidget):
    def __init__(self):
        QListWidget.__init__(self)
        
    def contains(self, peer):
        for i in range(self.count()):
            item = self.item(i)
            if(peer.name == item.name):
                return True
        return False