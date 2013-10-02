from PyQt4.QtGui import QWidget, QVBoxLayout, QLabel
from PyQt4.QtCore import Qt, SIGNAL, QMargins

# Class to represent a peer on the network and the gui
class Peer(QWidget):
    def __init__(self, id, name, address, port):
        # super(Peer, self).__init__(parent)
        QWidget.__init__(self)
        self.id = id
        self.address = address
        self.name = name
        self.port = int(port)
        self.setAcceptDrops(True)
        self.setMinimumSize(320, 80)
        self.setMaximumSize(320, 80)
        #self.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)
        vbox = QVBoxLayout()
        nameLabel = QLabel(self.name)
        vbox.addWidget(nameLabel)
        self.setLayout(vbox)
        
    def __str__(self):
        return self.id

    def __eq__(self, other):
        """needed to be able to remove items from peers form the list"""
        if self.id == other.id:
            if self.address == other.address:
                if self.port == other.port:
                    return True
        return False
    
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
            self.emit(SIGNAL("dropped"), fileName, self.id, self.address, self.port)
        else:
            event.ignore()
