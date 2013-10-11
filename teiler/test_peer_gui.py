from PyQt4.QtGui import QApplication
from peer import Peer
import sys

def main():    
    app = QApplication(sys.argv)

    peer = Peer(1, "TestPeer", "127.0.0.1", 8888)
    peer.show()


    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()