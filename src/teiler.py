import argparse
import os
import sys
import utils
from PyQt4.QtCore import *
from PyQt4.QtGui import *
 
import qt4reactor

qt_app = QApplication(sys.argv)
qt4reactor.install()

from twisted.python import log
from twisted.internet import reactor
from filereceiver import FileReceiverFactory

from filetransfer import FileReceiverFactory
from peerdiscovery import PeerDiscovery
from peerlist import TeilerPeer, TeilerPeerList
from session import Session
        
# Class to maintain the state of the program
class TeilerConfig():
    """ Class to hold on to all instance variables used for state. 
    """
    def __init__(self, 
                 address, 
                 tcpPort,
                 sessionID,
                 name,
                 peerList,
                 multiCastAddress,
                 multiCastPort,
                 downloadPath):
        self.address = address # this is the local IP
        # port for file receiver to listen on 
        self.tcpPort = tcpPort
        self.sessionID = sessionID
        self.name = name
        self.peerList = peerList
        self.multiCastAddress = multiCastAddress
        self.multiCastPort = multiCastPort
        self.downloadPath = downloadPath
        
    def notifySession(self, sessionID, message):
        log.msg("Printing sessions:")
        for k,v in self.sessions.iteritems():
            log.msg("Key: {0}, Value: {1}".format(k, v))
        if not self.sessions.has_key(sessionID):
            log.msg("Session key cannot be found!")
        else:
            self.sessions[sessionID].processResponse(message)
            
    def closeSession(self, session):
        del self.sessions[session.id]

# Class for the GUI
class TeilerWindow(QWidget):
    """The main front end for the application."""
    def __init__(self, peerList):
        # Initialize the object as a QWidget and
        # set its title and minimum width

        QWidget.__init__(self)

        self.peerList = peerList
        self.setWindowTitle('BlastShare')
        self.setMinimumSize(240, 480)
        

        # connects the signals!
        self.connect(self.peerList, 
                     SIGNAL("dropped"), self.sendFileToPeers)

        shareFilesAction = QAction(QIcon('exit.png'), '&Share File(s)', self)
        shareFilesAction.setShortcut('Ctrl+O')
        shareFilesAction.setStatusTip('Share File(s)')
        shareFilesAction.triggered.connect(quitApp)

        preferencesAction = QAction(QIcon('exit.png'), '&Preferences', self)
        preferencesAction.setShortcut('Ctrl+P')
        preferencesAction.setStatusTip('Preferences')
        preferencesAction.triggered.connect(quitApp)

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(quitApp)

        menubar = QMenuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(shareFilesAction)
        fileMenu.addAction(preferencesAction)
        fileMenu.addAction(exitAction)

        # Create the QVBoxLayout that lays out the whole form
        #self.teiler.peerList.setAcceptDrops(True)
        #self.teiler.peerList.setDragEnabled(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setLayout(layout)
        
        statusBar = QStatusBar()
        statusBar.showMessage('Ready')
        
        layout.addWidget(menubar)
        layout.addWidget(self.peerList)
        layout.addWidget(statusBar)
        # self.questionMessage("Borscht", "Flarb")
        
    def sendFileToPeers(self, fileName):
        log.msg("File dropped {0}".format(fileName))
        #selectedPeer = self.teiler.peerList.currentItem()
        #log.msg("Selected Peer is {0}".format(selectedPeer.name))
        for peer in self.teiler.peerList.iterAllItems():
            session = Session(str(fileName), self.teiler, peer.address, peer.port)
            self.teiler.sessions[str(session.id)] = session
            session.startTransfer()

    def questionMessage(self, fileName, peerName):    
        reply = QMessageBox.question(self, "Accept file download?",
                "Do you want to accept the {0} from {1}?".format(fileName, peerName),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            return "yes"
            # self.questionLabel.setText("Yes")
        elif reply == QMessageBox.No:
            return "no"
            # self.questionLabel.setText("No")
        else:
            return "cancel"
            # self.questionLabel.setText("Cancel")

    def displayAcceptFileDialog(self, fileName):
        log.msg("Showing filename")
        dialog = AcceptFileDialog(fileName)
        dialog.exec_()
    
    def slotFile(self):
        filename = QFileDialog.getOpenFileName("", "*.py", self, "FileDialog")
        
    def run(self):
        self.show()
        qt_app.exec_()

def quitApp():
    reactor.stop()
    qApp.quit()

def download_path_exists():
    downloadPath = os.path.join(os.path.expanduser("~"), "blaster")
    if os.path.exists(downloadPath) == False:
        os.mkdir(downloadPath)

def main():
    log.startLogging(sys.stdout)
    parser = argparse.ArgumentParser(description="Exchange files!")
    args = parser.parse_args()
    
    # Initialize peer discovery using UDP multicast
    multiCastPort = 8006
    teiler = TeilerConfig()
    teiler.multiCastPort = multiCastPort
    reactor.listenMulticast(multiCastPort,
                            PeerDiscovery(teiler),
                            listenMultiple=True)
    log.msg("Initiating Peer Discovery")
    config = TeilerConfig(utils.getLiveInterface(), #ip
                          9998, #tcp port
                          utils.generateSessionID(),
                          utils.getUsername(),
                          TeilerPeerList(),
                          #udp connection information
                          '230.0.0.30',
                          8005,
                          os.path.join(os.path.expanduser("~"), "blaster"))
    
    reactor.listenMulticast(config.multiCastPort, 
                            PeerDiscovery(
                                reactor,
                                config.peerList,
                                config.name,
                                config.multiCastAddress,
                                config.multiCastPort,
                                config.address,
                                config.tcpPort),
                            listenMultiple=True)
    
    fileReceiver = FileReceiverFactory(config)
    reactor.listenTCP(config.tcpPort, fileReceiver)
    
    app = TeilerWindow(teiler)
    # Initialize file transfer service
    fileReceiver = FileReceiverFactory(teiler, app)
    reactor.listenTCP(teiler.tcpPort, fileReceiver)
    log.msg("Starting file listener on {0}".format(teiler.tcpPort))
    log.msg("Starting file listener on ", config.tcpPort)
    
    reactor.runReturn()
    
    # Create an instance of the application window and run it
    
        
    app = TeilerWindow(config.peerList)
    app.run()

if __name__ == '__main__':
    main()
