from PyQt4.QtCore import SIGNAL, QMargins, Qt
from PyQt4.QtGui import QWidget, QVBoxLayout
from ipeerlist import IPeerList
from twisted.python import log
import zope.interface

# Class that keeps track of the peers and displays them to the user
class PeerList(QWidget):
    zope.interface.implements(IPeerList)
    
    def __init__(self, parent=None):
        super(PeerList, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setMinimumSize(320, 480)
        self.layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.layout.setAlignment(Qt.AlignTop)
        did = IPeerList.implementedBy(PeerList)
        log.msg("did is " + str(did))
        if not IPeerList.implementedBy(PeerList):
            log.msg("The PeerList class does not correctly implement IPeerList!")
        
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
    
    def askPeer(self, fileName, peerID, peerName, peerAddress, peerPort):
        peer = self.getPeer(peerID, peerAddress, peerPort)
        peer.addAcceptTransferPrompt(fileName, peerName)
        