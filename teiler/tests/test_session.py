from twisted.trial import unittest
from session import Session
from config import Config
from peerlist import PeerList
import os, utils

class SessionTestCase(unittest.TestCase):
    
    def setUp(self):
        self.fileName = os.path.join(os.path.expanduser("~"), "teiler/test/test.txt")
        self.address = '127.0.0.1'
        self.port = 8989
        self.multiCastAddress = '230.0.0.40'
        self.multiCastPort = 9090
        self.name = 'TestNode'
        self.downloadPath = os.path.join(os.path.expanduser("~"), "teiler/test/downloads")
        self.peerList = PeerList()
        self.config = Config(self.address, 
                             self.port, 
                             utils.generateSessionID(), 
                             self.name, 
                             self.peerList,
                             self.multiCastAddress,
                             self.multiCastPort,
                             self.downloadPath)
        
        self.session = Session(self.fileName, self.config, self.address, self.port)
    
    
    def test_startTransfer(self):
        self.session.startTransfer()
    
    '''     
    def test_processResponse(self):
        self.fail()
        
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
        '''
    
    '''    
    def test_sendBeginning(self):
        self.fail()
        
        beginMessage = Message(beginMsg, self.id)
        beginMessage.fileName = self.fileName
        log.msg("Sending BEGIN")
        log.msg("Message is {0}".format(beginMsg))
        f = SessionMessageFactory(self, beginMessage)
        self.status = 1
        reactor.connectTCP(self.address, self.port, f)
        '''
    
    '''    
    def test_sendEnd(self):
        self.fail()
        
        endMessage = Message(endMsg, self.id)
        log.msg("Sending EOT")
        f = SessionMessageFactory(endMessage)
        self.status = "finished"
        reactor.connectTCP(self.address, self.port, f)
        self.config.closeSession(self)
        '''
        
    '''
    def test_sendFile(self):
        self.fail()
        
        controller = type('test', (object,), {'cancel':False, 'total_sent':0, 'completed':Deferred()})
        f = FileSenderClientFactory(path, controller, self.id)
        reactor.connectTCP(address, port, f)
        return controller.completed
        '''
    
    '''    
    def test_startFileSend(self):
        self.fail()
       
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
       '''
    '''    
    def test_processTransferQueue(self):
        self.fail()
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
                dirMessage = Message(dirMsg, self.id)
                dirMessage.dirName = "{0}".format(path)
                f = SessionMessageFactory(self, dirMessage)
                reactor.connectTCP(self.address, self.port, f)
            else:
                reactor.callLater(0, self.sendFile, path, self.address, self.port)
        '''
        