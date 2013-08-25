from twisted.trial import unittest
from peerlist import PeerList

class PeerListTestCase(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_contains(self):
        self.fail()
        '''
        for i in range(self.count()):
            item = self.item(i)
            if peerID == item.id:
                if(peerAddress == item.address):
                    if(int(peerPort) == item.port):
                        return True
        return False
        '''
        
    def test_iterAllItems(self):
        self.fail()
        '''
        for i in range(self.count()):
            yield self.item(i)
       '''
       
    def test_dragEnterEvent(self):
        self.fail()
        '''
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()
        '''
        
    def test_dragMoveEvent(self):
        self.fail()
        '''
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
        '''
        
    def test_dropEvent(self, event):
        self.fail()
        '''
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
        '''
        