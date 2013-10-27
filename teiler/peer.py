from PyQt4.QtGui import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt4.QtCore import Qt, SIGNAL, QMargins, QPropertyAnimation, QSize
from peerlist import PeerList

# Class to represent a peer on the network and the gui
class Peer(QWidget):
    def __init__(self, id, name, address, port, peerList = None):
        # super(Peer, self).__init__(parent)
        QWidget.__init__(self)
        self.id = id
        self.address = address
        self.name = name
        self.port = int(port)
        self.peerList = peerList
        
        self.setAcceptDrops(True)
        self.setMinimumSize(320, 80)
        #self.setMaximumSize(320, 80)
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(QMargins(0, 0, 0, 0))
        nameLabel = QLabel(self.name)
        netLabel = QLabel(str(self.address) + ":" + str(self.port))
        self.layout.addWidget(nameLabel)
        self.layout.addWidget(netLabel)
        self.setLayout(self.layout)
        
    def __str__(self):
        return str(self.id)

    def __eq__(self, other):
        """needed to be able to remove items from peers form the list"""
        if self.id == other.id:
            if self.address == other.address:
                if self.port == other.port:
                    return True
        return False
    
    '''
    def connectToList(self, peerList):
        self.peerList = peerList
        self.connect(self.peerList, SIGNAL("updateProgressBar"), self.updateProgressBar)
    '''
        
    def updateProgressBar(self, value, transferID):
        self.emit(SIGNAL("updateTransferValue"), value, transferID)
    
    def addPrompt(self, fileName, fileSize, peerName):
        prompt = Prompt(fileName, int(fileSize), peerName, self)

        self.connect(prompt, SIGNAL("accepted"), self.receiveAccept)
        self.connect(prompt, SIGNAL("rejected"), self.receiveReject)
        self.layout.addWidget(prompt)

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

    def receiveAccept(self, prompt):
        print "Peer received Accepted"
        prompt.deleteLater()
        
        transferProgress = TransferProgress(prompt.fileName, prompt.fileSize, prompt.senderPeerName, self)
        self.layout.addWidget(transferProgress)
        
        '''
        self.layout.removeWidget(prompt)
        prompt.close()
        prompt = TransferProgress(prompt.fileName, prompt.peerName)
        self.layout.addWidget(prompt)
        self.layout.update()
        '''
        
        self.emit(SIGNAL("accepted"), prompt.senderPeerName)
        
    def receiveReject(self, prompt):
        print "Peer received Rejected"
        prompt.deleteLater()
        self.emit(SIGNAL("rejected"), prompt.senderPeerName)

# Class to represent a peer on the network and the gui
class Prompt(QWidget):
    
    def __init__(self, fileName, fileSize, senderPeerName, peer):
        QWidget.__init__(self)
        self.fileName = fileName
        self.senderPeerName = senderPeerName
        self.fileSize = fileSize
        self.peer = peer
        
        #self.setMinimumSize(0, 80)
        self.resize(0,0)
        self.setContentsMargins(QMargins(0, 0, 0, 0))

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.yellow)
        self.setPalette(palette)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.acceptText = QLabel(self.senderPeerName + " wants to send you " + self.fileName + " (Size: " + str(self.fileSize) + ").  Accept?")
        self.acceptButton = QPushButton("OK", self)
        self.acceptButton.clicked.connect(self.clickAccept)

        self.rejectButton = QPushButton("Reject", self)
        self.rejectButton.clicked.connect(self.clickReject)
        
        self.layout.addWidget(self.acceptText)
        self.layout.addWidget(self.acceptButton)
        self.layout.addWidget(self.rejectButton)
        self.setLayout(self.layout)

        '''
        self.anim = QPropertyAnimation(self, "size")
        self.anim.setDuration(250)
        self.anim.setStartValue(QSize(320, 0))
        self.anim.setEndValue(QSize(320, 80))
        self.anim.start()
        self.setMinimumSize(320, 80)
        '''
        
    def clickAccept(self):
        self.emit(SIGNAL("accepted"), self)

    def clickReject(self):
        self.emit(SIGNAL("rejected"), self)

# Class to represent the file transfer graphically
class TransferProgress(QWidget):
    
    def __init__(self, fileName, fileSize, senderPeerName, peer):
        QWidget.__init__(self)
        self.fileName = fileName
        self.senderPeerName = senderPeerName
        self.connect(peer.peerList.container, SIGNAL("updateProgress"), self.updateProgressBar)
        
        #self.setMinimumSize(0, 80)
        self.resize(0,0)
        self.setContentsMargins(QMargins(0, 0, 0, 0))
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.cyan)
        self.setPalette(palette)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.acceptText = QLabel(self.senderPeerName + " transferring " + self.fileName + "...")
        self.progressBar = QProgressBar(self)
        #self.progressBar.setMinimum(0)
        #self.progressBar.setMaximum(fileSize)
        self.progressBar.setValue(50)
        
        self.layout.addWidget(self.acceptText)
        self.layout.addWidget(self.progressBar)

        self.setLayout(self.layout)
        
    def updateProgressBar(self, senderID, value):
        print "Caught emit for " + senderID + " for value " + str(value) + ", I am expecting " + self.senderPeerName
        if self.senderPeerName == senderID:
            print "Should update..."
            self.progressBar.setValue(value)
