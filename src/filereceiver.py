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
        self.crc = 0
        self.teiler = teiler
        self.teilerWindow = teilerWindow
        
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
            log.msg("Vals are {0} and {1}".format(self.fileName, self.fileSize))
            self.outFile = open(self.teiler.downloadPath + self.fileName, 'wb+')
            log.msg("Saving file to {0}".format(self.outFile)) 
            self.setRawMode()
        elif message['command'] == session.endMsg:
            pass
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
        self.outFile.write(data)

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
                #print remove_base + self.outfilename + reason
                #os.remove(self.outfilename)
            receivedMessage = Message(session.receivedMsg)
            f = SessionMessageFactory(self, receivedMessage)
            reactor.connectTCP(self.teiler.address, self.teiler.tcpPort, f)
        
    def fileFinished(self, reason):
        """ """
        basic.LineReceiver.connectionLost(self, reason)
        print ' - connectionLost'
        if self.outfile:
            self.outfile.close()
        # Problem uploading - tmpfile will be discarded
        if self.remain != 0:
            print str(self.remain) + ')!=0'
            remove_base = '--> removing tmpfile@'
            if self.remain < 0:
                reason = ' .. file moved too much'
            if self.remain > 0:
                reason = ' .. file moved too little'
            print remove_base + self.outfilename + reason
            os.remove(self.outfilename)

        # Success uploading - tmpfile will be saved to disk.
        else:
            print '\n--> finished saving upload@ ' + self.outfilename
            client = self.instruction.get('client', 'anonymous')

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
