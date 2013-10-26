from PyQt4.QtGui import QApplication
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QPushButton
from peer import Peer
from peerlist import PeerList
import sys, time

app = QApplication(sys.argv)

peer1 = Peer(101, "TestPeer1", "127.0.0.1", 8888)
peer2 = Peer(102, "TestPeer2", "127.0.0.1", 9999)

class TestPeerList(PeerList):
    
    def __init__(self, parent=None):
        super(TestPeerList, self).__init__(parent)
        
        self.sendAsk1 = QPushButton('Ask Peer1', self)
        self.sendAsk1.id = 103
        self.sendAsk1.clicked.connect(lambda: self.askPeer("File1", 1001, peer1.id, peer1.name, peer1.address, peer1.port))
        self.layout.addWidget(self.sendAsk1)
        
        self.sendAsk2 = QPushButton('Ask Peer2', self)
        self.sendAsk2.id = 104
        self.sendAsk2.clicked.connect(lambda: self.askPeer("File2", 512, peer2.id, peer2.name, peer2.address, peer2.port))
        self.layout.addWidget(self.sendAsk2)
        
        #self.add(self.sendAsk)
        print "test"

def main():    

    list = TestPeerList()
    list.add(peer1)
    list.add(peer2)
    list.show()

    #list.askPeer("File1", peer.id, peer.name, peer.address, peer.port)
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    main()