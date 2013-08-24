from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Class that keeps track of the peers and displays them to the user
class PeerList(QListWidget):
    
    def __init__(self, parent=None):
        super(TeilerPeerList, self).__init__(parent)
        self.setVisible(True)
        self.setAcceptDrops(True)
        #self.teiler.peerList.setDragEnabled(True)
        self.setViewMode(QListView.ListMode)
        
        ''' For testing '''
        id = utils.generateSessionID()
        newPeer = TeilerPeer(id, "testHostName", "testHost", 9989)
        self.addItem(newPeer)
    
    def contains(self, peerID, peerAddress, peerPort):
        for i in range(self.count()):
            item = self.item(i)
            if peerID == item.id:
                if(peerAddress == item.address):
                    if(int(peerPort) == item.port):
                        return True
        return False
    
    def iterAllItems(self):
        for i in range(self.count()):
            yield self.item(i)
   
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mD = event.mimeData()
        if mD.hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            fileName = mD.urls()[0].toLocalFile()
            print "fileName is {0}".format(fileName)
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
                print "Added {0}".format(str(url.toLocalFile()))
            self.emit(SIGNAL("dropped"), fileName)
        else:
            event.ignore()
