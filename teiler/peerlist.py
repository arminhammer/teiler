from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QWidget, QVBoxLayout, QScrollArea
from abstractpeerlist import AbstractPeerList
from twisted.python import log

# Class that keeps track of the peers and displays them to the user
class PeerList(QWidget, AbstractPeerList):
    
    def __init__(self, parent=None):
        super(PeerList, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setMinimumSize(240, 480)
 
    def add(self, peer):
        self.layout.addWidget(peer)
        self.connect(peer, SIGNAL("dropped"), self.notifyTeiler)
        log.msg("Peerlist: added peer " + str(peer))
        log.msg("Count is: " + str(self.layout.count()))
    
    def notifyTeiler(self, fileName, peerID, peerAddress, peerPort):
        self.emit(SIGNAL("initTransfer"), fileName, peerID, peerAddress, peerPort)
        
    def contains(self, peerID, peerAddress, peerPort):
        peers = (self.layout.itemAt(i).widget() for i in range(self.layout.count())) 
        for p in peers:
            if peerID == p.id:
                if(peerAddress == p.address):
                    if(int(peerPort) == p.port):
                        return True
        return False
    