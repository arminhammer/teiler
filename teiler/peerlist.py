from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QWidget, QVBoxLayout
from abstractpeerlist import AbstractPeerList
from twisted.python import log

# Class that keeps track of the peers and displays them to the user
class PeerList(QWidget, AbstractPeerList):
    
    def __init__(self, parent=None):
        super(PeerList, self).__init__(parent)
        #self.setVisible(True)
        #self.setAcceptDrops(True)
        # self.teiler.peerList.setDragEnabled(True)
        #self.setViewMode(QListView.ListMode)
        self.layout = QVBoxLayout(self)
        #self.setLayout(layout)
        self.setMinimumSize(240, 480)
        #self.scrollArea = QScrollArea(self)
        #self.scrollArea.setWidgetResizable(True)
        self.peers = []
 
    def add(self, peer):
        self.layout.addWidget(peer)
        #peer.show()
        self.connect(peer, SIGNAL("dropped"), self.notifyTeiler)
        log.msg("Peerlist: added peer " + str(peer))
        log.msg("Count is: " + str(self.layout.count()))
    
    def notifyTeiler(self, fileName, peerID, peerAddress, peerPort):
        self.emit(SIGNAL("initTransfer"), fileName, peerID, peerAddress, peerPort)
        
    def contains(self, peerID, peerAddress, peerPort):
        peers = (self.layout.itemAt(i).widget() for i in range(self.layout.count())) 
        for p in peers:
            log.msg("Type is " + str(type(p)))
            if peerID == p.id:
                if(peerAddress == p.address):
                    if(int(peerPort) == p.port):
                        return True
        return False
    
    def iterAllItems(self):
        for i in range(self.count()):
            yield self.item(i)
 