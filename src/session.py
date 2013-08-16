from binascii import crc32
import os, json
import Queue
from twisted.protocols import basic
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import FileSender, LineReceiver
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.python import log
from filesender import FileSenderClientFactory
import utils
from sessionmessageprotocol import SessionMessageFactory

beginMsg = "BEGIN"
acceptMsg = "ACCEPT"
rejectMsg = "REJECT"
receivedMsg = "RECEIVED"
fileMsg = "FILE"
dirMsg = "DIR"
endMsg = "EOT"

class Message(object):
    """mesage to be sent across the wire"""
    def __init__(self, command):
        self.command = command
        
    def __str__(self):
        return self.serialize()
    
    def serialize(self):
        return json.dumps(self.__dict__)

class Session(object):
    
    def __init__(self, fileName, teiler):
        self.id = utils.generateSessionID()
        self.transferQueue = Queue.Queue()
        self.address = teiler.address
        self.port = teiler.tcpPort
        self.fileName = fileName
        self.status = 0
       
    def __str__(self):
        return str(self.id)
    
    def startTransfer(self):
        self.sendBeginning()
         
    def processResponse(self, msg):
        log.msg("Response received: {0}".format(msg))
        message = json.loads(msg)
        if message['command'] == acceptMsg and self.status == 1:
            self.status = 2
            reactor.callLater(0, self.startFileSend)
        elif message['command'] == rejectMsg and self.status == 1:
            log.msg("File transfer was rejected.  Closing.")
        elif message['command'] == receivedMsg and self.status == 2:
            log.msg("Receipt from receiver")
            reactor.callLater(0, self.processTransferQueue)
        else:
            log.msg("NOT RECOGNIZED!")  
    
    def sendBeginning(self):
        beginMessage = Message(beginMsg)
        beginMessage.fileName = self.fileName
        log.msg("Sending BEGIN")
        log.msg("Message is {0}".format(beginMsg))
        f = SessionMessageFactory(self, beginMessage)
        self.status = 1
        reactor.connectTCP(self.address, self.port, f)
        
    def sendEnd(self):
        endMessage = Message(endMsg)
        log.msg("Sending EOT")
        f = SessionMessageFactory(endMessage)
        self.status = "finished"
        reactor.connectTCP(self.address, self.port, f)
    
    def sendFile(self, path, address='localhost', port=1234,):
        controller = type('test', (object,), {'cancel':False, 'total_sent':0, 'completed':Deferred()})
        f = FileSenderClientFactory(path, controller)
        reactor.connectTCP(address, port, f)
        return controller.completed
    
    def startFileSend(self):
            log.msg("Calculating files...")
            if os.path.isdir(self.fileName):
                for root, dirs, files in os.walk(self.fileName, topdown=True):
                    for name in dirs:
                        self.transferQueue.put(os.path.join(root, name))
                    for name in files:
                        self.transferQueue.put(os.path.join(root, name))
                reactor.callLater(0, self.processTransferQueue)
            else:
                log.msg("Just sending a file...")
                relfilePath = os.path.join(os.path.relpath(root, self.fileName), name)
                fileMessage = Message(filetransfer.fileMsg)
                fileMessage.fileName = "{0}/{1}".format(self.fileName, relfilePath)
                fileMessage.fileSize = os.path.getsize(relFilePath)
                self.transport.write(fileMessage)
                
    def processTransferQueue(self):
        log.msg("Processing queue")
        path = self.transferQueue.get()
        log.msg("Sending {0}".format(path))
        if path == None:
            endMessage = Message(filetransfer.endMsg)
            self.transport.write(endMessage)
            reactor.callLater(self.cbTransferCompleted)
        else:
            if os.path.isdir(path):
                dirMessage = Message(dirMsg)
                dirMessage.dirName = "{0}".format(self.fileName)
                f = SessionMessageFactory(self, dirMessage)
                reactor.connectTCP(self.address, self.port, f)
            else:
                reactor.callLater(0, self.sendFile, self.fileName, self.address, self.port)
