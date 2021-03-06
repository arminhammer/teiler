import os
import sys

from PyQt4.QtCore import SIGNAL, QMargins
from PyQt4.QtGui import QApplication, QWidget, QAction, QIcon, QMenuBar 
from PyQt4.QtGui import QVBoxLayout, QStatusBar, QMessageBox

import qt4reactor
QT_APP = QApplication(sys.argv)
qt4reactor.install()

from twisted.python import log
from twisted.internet import reactor

import utils
from filereceiver import FileReceiverFactory
from peerdiscovery import PeerDiscovery
from peerlist import PeerList
from session import Session
from config import Config
from preferences import Preferences

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
        self.setMinimumSize(320, 480)
        self.setMaximumWidth(320)
        self.prefw = None
        
        # connects the signals!
        self.connect(self.peerList,
                     SIGNAL("initTransfer"), self.sendFileToPeer)

        ''' Will add feature in future version '''
        '''
        shareFilesAction = QAction(QIcon('exit.png'), '&Share File(s)', self)
        shareFilesAction.setShortcut('Ctrl+O')
        shareFilesAction.setStatusTip('Share File(s)')
        shareFilesAction.triggered.connect(quitApp)
        '''
        
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
        
        ''' Will enable in future versions '''
        # fileMenu.addAction(shareFilesAction)
        
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
        
    def sendFileToPeer(self, fileName, peerID, peerAddress, peerPort):
        log.msg("File dropped {0}".format(fileName))
        session = Session(str(fileName), self.config, peerAddress, peerPort)
        self.config.sessions[str(session.id)] = session
        session.startTransfer()
            
    def questionMessage(self, fileName, peerName):    
        reply = QMessageBox.question(self, "Accept file download?",
                "Do you want to accept the {0} from {1}?".format(fileName,
                                                                 peerName),
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            return "yes"
        elif reply == QMessageBox.No:
            return "no"
        else:
            return "cancel"
        
    def editPreferences(self):
        """ Launches the edit preferences dialog for this window. """
        self.prefw = Preferences(self)
        self.prefw.show()
           
    def run(self):
        self.show()
        QT_APP.exec_()
  
def quitApp():
    reactor.stop()
    QT_APP.quit()

def download_path_exists():
    downloadPath = os.path.join(os.path.expanduser("~"), "blaster")
    if os.path.exists(downloadPath) == False:
        os.mkdir(downloadPath)

def main():
    log.startLogging(sys.stdout)
    
    config = Config(utils.getLiveInterface(),  # ip
                          9998,  # tcp port
                          utils.generateSessionID(),
                          utils.getUsername(),
                          PeerList(),
                          # udp connection information
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
