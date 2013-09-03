from PyQt4.QtCore import *
from PyQt4.QtGui import *
from twisted.python import log

class Preferences(QWidget):
    def __init__(self, parent):
       QWidget.__init__(self)
       self.config = parent.config 
       # --Layout Stuff---------------------------#
       grid = QGridLayout()
       grid.setSpacing(10)

       self.hostname = QLabel('Hostname')
       self.hostnameText = QLineEdit(parent.config.name)
       grid.addWidget(self.hostname, 1, 0)
       grid.addWidget(self.hostnameText, 1, 1)
       
       self.tcpPort = QLabel('Port')
       self.tcpPortText = QLineEdit(str(parent.config.tcpPort))
       grid.addWidget(self.tcpPort, 2, 0)
       grid.addWidget(self.tcpPortText, 2, 1)
       
       
       # layout.addWidget(self.hostname)

       # layout.addWidget(self.hostnameText)

       '''
       layout1 = QHBoxLayout()
       layout1.addWidget(self.tcpPort)

       layout1.addWidget(self.tcpPortText)
    

       mainLayout.addLayout(layout)
       mainLayout.addLayout(layout1)
        '''
       # --The Button------------------------------#
       layout = QHBoxLayout()
       button = QPushButton("OK")  # string or icon
       self.connect(button, SIGNAL("clicked()"), self.saveAndClose)
       grid.addWidget(button, 3, 0)

       # mainLayout.addLayout(layout)
       self.setLayout(grid)

       self.resize(200, 200)
       self.setWindowTitle('Preferences')

    def saveAndClose(self):
        err = False
        if self.hostnameText.isModified():
            log.msg("Changing " + self.config.name + " to " + self.hostnameText.text())
            self.config.name = self.hostnameText.text()
        if self.tcpPortText.isModified():
            try:
                self.config.tcpPort = int(self.tcpPortText.text())
            except Exception:
                QMessageBox.about(self, 'Error', 'Input can only be a number')
                err = True
        if err == False:
            self.close()
