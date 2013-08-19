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
endFileMsg = "EOF"
endMsg = "EOT"
resendMsg = "RESEND"

class Message(object):
    """mesage to be sent across the wire"""
    def __init__(self, command):
        self.command = command
        
    def __str__(self):
        return self.serialize()
    
    def serialize(self):
        return json.dumps(self.__dict__)

class Session(object):
    
    def __init__(self, fileName, teiler, address, port):
        self.id = utils.generateSessionID()
        self.transferQueue = Queue.Queue()
        self.address = address
        self.port = port
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
        f = FileSenderClientFactory(path, controller, self.id)
        reactor.connectTCP(address, port, f)
        return controller.completed
    
    def startFileSend(self):
            log.msg("Calculating files...")
            self.transferQueue.put(self.fileName)
            if os.path.isdir(self.fileName):
                for root, dirs, files in os.walk(self.fileName, topdown=True):
                    for name in dirs:
                        self.transferQueue.put(os.path.join(root, name))
                        log.msg("QUEUE: Adding dir {0}".format(name))
                    for name in files:
                        self.transferQueue.put(os.path.join(root, name))
                        log.msg("QUEUE: Adding file {0}".format(name))
                reactor.callLater(0, self.processTransferQueue)
       
    def processTransferQueue(self):
        remaining = self.transferQueue.qsize()
        log.msg("Processing queue.  Queue items remaining: {0}".format(remaining))
        if remaining == 0:
            endMessage = Message(endMsg)
            f = SessionMessageFactory(self, endMessage)
            reactor.connectTCP(self.address, self.port, f)
        else:
            path = self.transferQueue.get()
            log.msg("Sending {0}".format(path))
            if os.path.isdir(path):
                dirMessage = Message(dirMsg)
                dirMessage.dirName = "{0}".format(path)
                f = SessionMessageFactory(self, dirMessage)
                reactor.connectTCP(self.address, self.port, f)
            else:
                reactor.callLater(0, self.sendFile, path, self.address, self.port)
