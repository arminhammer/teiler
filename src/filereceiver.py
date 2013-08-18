import os, json
from binascii import crc32
from twisted.protocols import basic
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory
import session
from session import Message, Session
from twisted.internet.defer import Deferred
from twisted.python import log
from twisted.internet import reactor
from sessionmessageprotocol import SessionMessageFactory

class FileReceiverProtocol(LineReceiver):
    """ File Receiver """

    def __init__(self, teiler, teilerWindow):
        self.outFile = None
        self.remain = 0
        self.buffer = 0
        self.crc = 0
        self.teiler = teiler
        self.teilerWindow = teilerWindow
        self.sessionID = 0
        self.success = False
        
    def lineReceived(self, line):
        """ """
        d = Deferred()
        message = json.loads(line)
        log.msg("Receiver received message {0}".format(message))
        if message['command'] == session.beginMsg:
            # ok = self.teilerWindow.displayAcceptFileDialog(fileName)
            ok = self.teilerWindow.questionMessage(message['fileName'], "peer")
            log.msg("OK is {0}".format(ok))
            if ok == "no":
                log.msg("Download rejected")
                rejectMessage = Message(session.rejectMsg)
                self.transport.write(rejectMessage.serialize() + '\r\n')
            elif ok == "yes":
                log.msg("The file is accepted!")
                acceptMessage = Message(session.acceptMsg)
                self.transport.write(acceptMessage.serialize() + '\r\n')
        elif message['command'] == session.dirMsg:
            dirName = message['dirName']
            reactor.callLater(0, self.createDirectory, self.teiler.downloadPath + dirName)
            receivedMessage = Message(session.receivedMsg)
            self.transport.write(receivedMessage.serialize() + '\r\n')
        elif message['command'] == session.fileMsg:
            self.fileName = message['fileName']
            self.fileSize = message['fileSize']
            self.sessionID = message['sessionID']
            log.msg("Vals are {0} and {1}".format(self.fileName, self.fileSize))
            self.outFile = open(self.teiler.downloadPath + self.fileName, 'wb+')
            log.msg("Saving file to {0}".format(self.outFile)) 
            self.setRawMode()
        elif message['command'] == session.endFileMsg:
            sessionID = message['sessionID']
            ''' Should check to see that sessions match '''
            if sessionID != self.sessionID:
                log.msg("Sessions do not match!")
            else:
                receivedMessage = Message(session.receivedMsg)
                self.teiler.notifySession(sessionID, receivedMessage.serialize())
            #reactor.connectTCP(self.teiler.address, self.teiler.tcpPort, f)
        elif message['command'] == session.endMsg:
            log.msg("EOT message received!")
            self.transport.loseConnection()
        else:
            log.msg("Command not recognized.")
        
    def createDirectory(self, dirName):
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        log.msg("Creating dir {0}".format(dirName))
        
    def sendReceivedMessage(self):
        pass
        
    def rawDataReceived(self, data):
        """ """
        if self.remain % 10000 == 0:
            print '   & ', self.remain, '/', self.fileSize
        self.remain -= len(data)
        self.crc = crc32(data, self.crc)
        self.buffer += len(data)
        #log.msg("Buffer is: {0}, File Size is: {1}".format(self.buffer, self.fileSize))
        if self.buffer < self.fileSize:
            self.outFile.write(data)
        elif self.buffer == self.fileSize:
            self.outFile.write(data)
            self.success = True
            #self.setLineMode()
        else:
            left = self.buffer - self.fileSize
            log.msg("{0} bytes left, {1} type".format(left, data))
            #self.setLineMode()

    def connectionMade(self):
        """ """
        basic.LineReceiver.connectionMade(self)
        print 'a connection was made'
        print ' * ', self.transport.getPeer()

    def connectionLost(self, reason):
        log.msg("Connection on receiver side finished.")
        if self.outFile != None:
            self.outFile.close()
            if self.remain != 0:
                print str(self.remain) + ')!=0'
                remove_base = '--> removing tmpfile@'
                if self.remain < 0:
                    reason = ' .. file moved too much'
                if self.remain > 0:
                    reason = ' .. file moved too little'
                #print remove_base + self.outFile + reason
                #os.remove(self.outfilename)
            if self.success:
                receivedMessage = Message(session.receivedMsg)
                self.teiler.notifySession(self.sessionID, receivedMessage.serialize())
            else:
                resendMessage = Message(session.resendMsg)
                self.teiler.notifySession(self.sessionID, resendMessage.serialize())
            
                
                
def fileinfo(self, fname):
    """ when "file" tool is available, return it's output on "fname" """
    return (os.system('file 2> /dev/null') != 0 and \
             os.path.exists(fname) and \
             os.popen('file "' + fname + '"').read().strip().split(':')[1])

class FileReceiverFactory(ServerFactory):
    """ file receiver factory """
    protocol = FileReceiverProtocol

    def __init__(self, teiler, teilerWindow):
        self.teiler = teiler
        self.teilerWindow = teilerWindow
        
    def buildProtocol(self, addr):
        print ' + building protocol'
        p = self.protocol(self.teiler, self.teilerWindow)
        p.factory = self
        return p
