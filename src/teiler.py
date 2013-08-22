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
from peerdiscovery import PeerDiscovery
from peerlist import TeilerPeer, TeilerPeerList
from session import Session
from config import Config

# Class for the GUI
class Window(QWidget):
    """The main front end for the application."""
    def __init__(self, config):
        # Initialize the object as a QWidget and
        # set its title and minimum width

        QWidget.__init__(self)

        self.config = config
        self.peerList = config.peerList
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
        preferencesAction.triggered.connect(self.editPreferences)

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(quitApp)

        menubar = QMenuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(shareFilesAction)
        fileMenu.addAction(preferencesAction)
        fileMenu.addAction(exitAction)

        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setLayout(layout)
        
        statusBar = QStatusBar()
        statusBar.showMessage('Ready')
        
        layout.addWidget(menubar)
        layout.addWidget(self.peerList)
        layout.addWidget(statusBar)
        
    def sendFileToPeers(self, fileName):
        log.msg("File dropped {0}".format(fileName))
        for peer in self.peerList.iterAllItems():
            session = Session(str(fileName), self.config, peer.address, peer.port)
            self.config.sessions[str(session.id)] = session
            session.startTransfer()

    def questionMessage(self, fileName, peerName):    
        reply = QMessageBox.question(self, "Accept file download?",
                "Do you want to accept the {0} from {1}?".format(fileName, peerName),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            return "yes"
        elif reply == QMessageBox.No:
            return "no"
        else:
            return "cancel"

    def displayAcceptFileDialog(self, fileName):
        log.msg("Showing filename")
        dialog = AcceptFileDialog(fileName)
        dialog.exec_()
        
    def editPreferences( self ):
        """ Launches the edit preferences dialog for this window. """
        prefs = PreferencesDialog(self)
        prefs.exec_()
    
    def slotFile(self):
        filename = QFileDialog.getOpenFileName("", "*.py", self, "FileDialog")
        
    def run(self):
        self.show()
        qt_app.exec_()

class PreferencesDialog(QDialog):
    def __init__( self, parent ):
        super(PreferencesDialog, self).__init__(parent)
        self.setWindowTitle('Preferences')

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
    
    config = Config(utils.getLiveInterface(), #ip
                          9998, #tcp port
                          utils.generateSessionID(),
                          utils.getUsername(),
                          TeilerPeerList(),
                          #udp connection information
                          '230.0.0.30',
                          8005,
                          os.path.join(os.path.expanduser("~"), "teiler"))
    
    reactor.listenMulticast(config.multiCastPort, 
                            PeerDiscovery(
                                reactor,
                                config.sessionID,
                                config.peerList,
                                config.name,
                                config.multiCastAddress,
                                config.multiCastPort,
                                config.address,
                                config.tcpPort),
                            listenMultiple=True)

    app = Window(config)
    
    fileReceiver = FileReceiverFactory(config, app)
    reactor.listenTCP(config.tcpPort, fileReceiver)

    # Initialize file transfer service
    log.msg("Starting file listener on {0}".format(config.tcpPort))
    
    reactor.runReturn()
    
    # Create an instance of the application window and run it
    
    app.run()

if __name__ == '__main__':
    main()
