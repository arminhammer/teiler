from PyQt4.QtGui import QApplication
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QPushButton
from peer import Peer
from peerlist import PeerList
import sys, time

app = QApplication(sys.argv)
peer1 = Peer(101, "TestPeer", "127.0.0.1", 8888)

class TestPeerList(PeerList):
    
    def __init__(self, parent=None):
        super(TestPeerList, self).__init__(parent)
        self.sendAsk = QPushButton('Ask', self)
        self.sendAsk.id = 102
        self.sendAsk.clicked.connect(lambda: self.askPeer("File1", peer1.id, peer1.name, peer1.address, peer1.port))
        self.layout.addWidget(self.sendAsk)
        #self.add(self.sendAsk)
        print "test"

def main():    

    list = TestPeerList()
    list.add(peer1)
    list.show()

    #list.askPeer("File1", peer.id, peer.name, peer.address, peer.port)
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    main()