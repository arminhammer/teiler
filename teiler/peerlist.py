from PyQt4.QtCore import SIGNAL, QMargins, Qt
from PyQt4.QtGui import QWidget, QVBoxLayout, QScrollArea
from ipeerlist import IPeerList
from twisted.python import log
import zope.interface

# Class that keeps track of the peers and displays them to the user
class PeerList(QWidget):
    zope.interface.implements(IPeerList)
    
    def __init__(self, container=None, parent=None):
        super(PeerList, self).__init__(parent)
        
        self.container = container
        
        #self.setMinimumSize(320, 480)
        self.setGeometry(100, 100, 320, 480)
        self.topLayout = QVBoxLayout(self)
        self.topLayout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.scrollBox = QScrollArea()
        self.topLayout.addWidget(self.scrollBox)
        
        self.layoutWidget = QWidget(self)
        self.layoutWidget.setMinimumSize(320, 480)
        self.layout = QVBoxLayout(self.layoutWidget)
        
        self.layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.layout.setAlignment(Qt.AlignTop)
        self.scrollBox.setWidget(self.layoutWidget)

        did = IPeerList.implementedBy(PeerList)
        log.msg("did is " + str(did))
        if not IPeerList.implementedBy(PeerList):
            log.msg("The PeerList class does not correctly implement IPeerList!")
        
    def add(self, peer):
        self.layout.addWidget(peer)
        self.connect(peer, SIGNAL("dropped"), self.notifyTeiler)
        self.connect(peer, SIGNAL("accepted"), self.acceptance)
        self.connect(peer, SIGNAL("rejected"), self.rejection)
        
        log.msg("Peerlist: added peer " + str(peer))
        log.msg("Count is: " + str(self.layout.count()))
    
    def notifyTeiler(self, fileName, peerID, peerAddress, peerPort):
        self.emit(SIGNAL("initTransfer"), fileName, peerID, peerAddress, peerPort)
    
    def acceptance(self, peerID):
        self.emit(SIGNAL("accepted"), peerID)
        
    def rejection(self, peerID):
        self.emit(SIGNAL("rejected"), peerID)
        
    def contains(self, peerID, peerAddress, peerPort):
        peers = (self.layout.itemAt(i).widget() for i in range(self.layout.count())) 
        for p in peers:
            if peerID == p.id:
                if(peerAddress == p.address):
                    if(int(peerPort) == p.port):
                        return True
        return False
    
    def getPeer(self, peerID, peerAddress, peerPort):
        peers = (self.layout.itemAt(i).widget() for i in range(self.layout.count())) 
        for p in peers:
            log.msg("P: " + str(p))
            if peerID == p.id:
                if(peerAddress == p.address):
                    if(int(peerPort) == p.port):
                        return p
        log.msg("Peer not found.")
        return None
    
    def askPeer(self, fileName, fileSize, peerID, peerName, peerAddress, peerPort):
        peer = self.getPeer(peerID, peerAddress, peerPort)
        peer.addPrompt(fileName, fileSize, peerName)
        