import os, json
from binascii import crc32
from twisted.protocols import basic
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory
import session
from session import Session
from message import Message
from twisted.internet.defer import Deferred
from twisted.python import log
from twisted.internet import reactor
from sessionmessageprotocol import SessionMessageFactory
import utils

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
        self.peerAddress = ""
        self.peerPort = 0
        
    def lineReceived(self, line):
        """ """
        d = Deferred()
        message = json.loads(line)
        log.msg("Receiver received message {0}".format(message))
        if message['command'] == session.beginMsg:
            ok = self.teilerWindow.questionMessage(message['fileName'], "peer")
            log.msg("OK is {0}".format(ok))
            if ok == "no":
                log.msg("Download rejected")
                rejectMessage = Message(session.rejectMsg)
                self.transport.write(rejectMessage.serialize() + '\r\n')
            elif ok == "yes":
                log.msg("The file is accepted!")
                self.teiler.dlSessions.add(message['sessionID'])
                acceptMessage = Message(session.acceptMsg)
                self.transport.write(acceptMessage.serialize() + '\r\n')
        elif message['command'] == session.dirMsg:
            dirName = message['dirName']
            msgSession = message['sessionID']
            if message['sessionID'] in self.teiler.dlSessions:
                reactor.callLater(0, utils.createDirectory, self.teiler.downloadPath + dirName)
                receivedMessage = Message(session.receivedMsg)
                self.transport.write(receivedMessage.serialize() + '\r\n')
            else:
                log.msg("Dir Message was not in a proper session!")
                self.transport.loseConnection()
        elif message['command'] == session.fileMsg:
            self.fileName = message['fileName']
            self.fileSize = message['fileSize']
            self.sessionID = message['sessionID']
            log.msg("Vals are filename: {0}, filesize: {1}, sessionID: {2}".format(self.fileName, self.fileSize, self.sessionID))
            if message['sessionID'] in self.teiler.dlSessions:
                self.outFile = open(self.teiler.downloadPath + self.fileName, 'wb+')
                log.msg("Saving file to {0}".format(self.outFile)) 
                self.setRawMode()
            else:
                log.msg("File Message was not in a proper session!")
                self.transport.loseConnection()
        elif message['command'] == session.endMsg:
            msgSession = message['sessionID']
            if msgSession in self.teiler.dlSessions:
                log.msg("EOT message received!")
                ''' Commenting out for now '''
                self.teiler.dlSessions.remove(msgSession)
                self.transport.loseConnection()
            else:
                log.msg("EOT Message was not in a proper session!")
                self.transport.loseConnection()
        else:
            log.msg("Command not recognized.")
                
    def sendReceivedMessage(self):
        receivedMessage = Message(session.receivedMsg)
        self.transport.write(receivedMessage.serialize() + '\r\n')
        
    def rawDataReceived(self, data):
        """ """
        if self.remain % 10000 == 0:
            print '   & ', self.remain, '/', self.fileSize
        self.remain -= len(data)
        self.crc = crc32(data, self.crc)
        self.buffer += len(data)
        if self.buffer < self.fileSize:
            self.outFile.write(data)
        elif self.buffer == self.fileSize:
            self.outFile.write(data)
            self.success = True
            self.sendReceivedMessage()
        else:
            left = self.buffer - self.fileSize
            log.msg("{0} bytes left, {1} type".format(left, data))

    def connectionMade(self):
        """ """
        basic.LineReceiver.connectionMade(self)
        print 'a connection was made'
        print ' * ', self.transport.getPeer()
        self.peerAddress = self.transport.getPeer().host
        self.peerPort = self.transport.getPeer().port

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
