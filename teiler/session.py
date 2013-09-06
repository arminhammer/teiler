import os, json
import Queue
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.python import log
from filesender import FileSenderClientFactory
import utils
from message import Message
from sessionmessageprotocol import SessionMessageFactory
import ntpath

beginMsg = "BEGIN"
acceptMsg = "ACCEPT"
rejectMsg = "REJECT"
receivedMsg = "RECEIVED"
fileMsg = "FILE"
dirMsg = "DIR"
endFileMsg = "EOF"
endMsg = "EOT"
resendMsg = "RESEND"

class Session(object):
    
    def __init__(self, fileName, config, address, port):
        self.id = utils.generateSessionID()
        self.transferQueue = Queue.Queue()
        self.address = address
        self.port = port
        self.fileName = fileName
        self.status = 0
        self.config = config
        self.parentPath = ""
       
    def __str__(self):
        return str(self.id)
    
    def startTransfer(self):
        beginMessage = Message(beginMsg, self.id)
        beginMessage.fileName = utils.getBaseNameFromPath(self.fileName)
        log.msg("Sending BEGIN")
        log.msg("Message is {0}".format(beginMsg))
        f = SessionMessageFactory(self, beginMessage)
        self.status = 1
        reactor.connectTCP(self.address, self.port, f)
         
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
        
    def sendEnd(self):
        endMessage = Message(endMsg, self.id)
        log.msg("Sending EOT")
        f = SessionMessageFactory(endMessage)
        self.status = "finished"
        reactor.connectTCP(self.address, self.port, f)
        self.config.closeSession(self)
    
    def sendFile(self, path, address='localhost', port=1234):
        controller = type('test', (object,), {'cancel':False, 'total_sent':0, 'completed':Deferred(), 'session': self})
        f = FileSenderClientFactory(path, controller, self.id)
        reactor.connectTCP(address, port, f)
        log.msg("Completed is " + str(controller.completed))
        return controller.completed
    
    def _sendDir(self, path):
        dirMessage = Message(dirMsg, self.id)
        dirMessage.dirName = "{0}".format(path)
        f = SessionMessageFactory(self, dirMessage)
        reactor.connectTCP(self.address, self.port, f)
        
    def sendDirectory(self, path):
        d = Deferred()
        reactor.callLater(0, self._sendDir, path)
        return d
    
    def success(self):
        print "This was success!"
        
    def failure(self):
        print "This was failure!"
        
    def startFileSend(self):
            log.msg("Calculating files...")
            if os.path.isfile(self.fileName):
                self.transferQueue.put(self.fileName)
            elif os.path.isdir(self.fileName):
                log.msg("Root is " + self.fileName)
                shortPath = utils.getBaseNameFromPath(self.fileName)
                log.msg("shortPath is " + shortPath)
                head, tail = ntpath.split(self.fileName)
                self.parentPath = head
                log.msg("self.parentPath is " + self.parentPath)
                self.transferQueue.put(self.fileName)
                for root, dirs, files in os.walk(self.fileName, topdown=True):
                    for name in dirs:
                        self.transferQueue.put(os.path.join(root, name))
                        log.msg("QUEUE: Adding dir {0}".format(os.path.join(root, name)))
                    for name in files:
                        self.transferQueue.put(os.path.join(root, name))
                        log.msg("QUEUE: Adding file {0}".format(os.path.join(root, name)))
                reactor.callLater(0, self.processTransferQueue)
            else:
                log.msg("File pathname cannot be found.")
       
    def processTransferQueue(self):
        remaining = self.transferQueue.qsize()
        log.msg("Processing queue.  Queue items remaining: {0}".format(remaining))
        if remaining == 0:
            endMessage = Message(endMsg, self.id)
            f = SessionMessageFactory(self, endMessage)
            reactor.connectTCP(self.address, self.port, f)
        else:
            path = self.transferQueue.get()
            log.msg("Sending {0}".format(path))
            if os.path.isdir(path):
                if path == self.parentPath:
                    d = self.sendDirectory(path)
                    log.msg("Sending {0}".format(path))
                else:
                    d = self.sendDirectory("/" + path.lstrip(self.parentPath))
                    log.msg("Sending {0}".format("/" + path.lstrip(self.parentPath)))
                d.addCallback(self.success)
                d.addErrback(self.failure)
            else:
                self.sendFile(path, self.address, self.port)
