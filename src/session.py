from binascii import crc32
import os, json
#import Queue
from twisted.protocols import basic
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import FileSender, LineReceiver
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.python import log
from filesender import FileSenderClientFactory
import utils
from sessionprotocol import SessionFactory

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
    
    def serialize(self):
        return json.dumps(self.__dict__)

def __init__(self, address, port, path):
    self.id = utils.generateSessionID()
    self.transferQueue = Queue.Queue()
    self.address = address
    self.port = port
    self.path = path
    self.status = "initial"
    
def processResponse(self, message):
    pass

def sendBeginning(self):
    beginMessage = Message(beginMsg)
    beginMessage.fileName = self.fileName
    log.msg("Sending BEGIN")
    f = SessionFactory(beginMessage)
    self.status = "begun"
    reactor.connectTCP(self.address, self.port, f)
    
def sendEnd(self):
    endMessage = Message(endMsg)
    log.msg("Sending EOT")
    f = SessionFactory(endMessage)
    self.status = "finished"
    reactor.connectTCP(self.address, self.port, f)

def sendFile(path, address='localhost', port=1234,):
    controller = type('test', (object,), {'cancel':False, 'total_sent':0, 'completed':Deferred()})
    f = FileSenderClientFactory(path, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed

def initTransfer(self):
        log.msg("Begin transfer")
        if os.path.isdir(self.path):
            for root, dirs, files in os.walk(self.path, topdown=True):
                for name in dirs:
                    self.transferQueue.put(os.path.join(root, name))
                for name in files:
                    self.transferQueue.put(os.path.join(root, name))
            reactor.callLater(self.processTransferQueue())
        else:
            log.msg("Just sending a file")
            relfilePath = os.path.join(os.path.relpath(root, self.path), name)
            fileMessage = Message(filetransfer.fileMsg)
            fileMessage.fileName = "{0}/{1}".format(self.fileName, relfilePath)
            fileMessage.fileSize = os.path.getsize(relFilePath)
            self.transport.write(fileMessage)
            
def processTransferQueue(self):
    log.msg("Processing queue")
    #d = Deferred()
    path = self.transferQueue.get()
    log.msg("Sending {0}".format(path))
    if path == None:
        endMessage = Message(filetransfer.endMsg)
        self.transport.write(endMessage)
        reactor.callLater(self.cbTransferCompleted())
    else:
        if os.path.isdir(path):
            relDirPath = os.path.join(os.path.relpath(root, self.path), path) 
            dirMessage = filetransfer.Message(dirMessage)
            dirMessage.dirName = "{0}/{1}".format(self.fileName, relDirPath)
            self.transport.write(dirMessage)
        else:
            relfilePath = os.path.join(os.path.relpath(root, self.path), path)
            fileMessage = filetransfer.Message(filetransfer.fileMsg)
            fileMessage.fileName = "{0}/{1}".format(self.fileName, relfilePath)
            fileMessage.fileSize = os.path.getsize(relFilePath)
            self.transport.write(fileMessage)
        #sender = FileSender()
        #sender.CHUNK_SIZE = 4096
        #d = sender.beginFileTransfer(open(path, 'rb'), self.transport, self._monitor)
        #d.addCallback(self.cbTransferCompleted)
        #d.addCallback(self.processTransferQueue())
    
