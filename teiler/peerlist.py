from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QWidget, QVBoxLayout, QScrollArea
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
        self.layout.addChildWidget(peer)
        #peer.show()
        self.connect(peer, SIGNAL("dropped"), self.notifyTeiler)
        log.msg("Peerlist: added peer " + str(peer))
    
    def notifyTeiler(self, fileName, peerID, peerAddress, peerPort):
        self.emit(SIGNAL("initTransfer"), fileName, peerID, peerAddress, peerPort)
        
    def contains(self, peerID, peerAddress, peerPort):
        for i in range(len(self.peers)):
            item = self.peers[i]
            if peerID == item.id:
                if(peerAddress == item.address):
                    if(int(peerPort) == item.port):
                        return True
        return False
    
    def iterAllItems(self):
        for i in range(self.count()):
            yield self.item(i)
 