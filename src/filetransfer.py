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

<<<<<<< HEAD
beginMsg = "BEGIN"
acceptMsg = "ACCEPT"
rejectMsg = "REJECT"
receivedMsg = "RECEIVED"
fileMsg = "FILE"
dirMsg = "DIR"
endMsg = "EOT"
=======
class FileReceiverProtocol(LineReceiver):
    """protocol that will be used to transfer files/raw data."""
>>>>>>> refs/remotes/christeiler/bossman

class Message(object):
    """mesage to be sent across the wire"""
    def __init__(self, command):
        self.command = command
    
    def serialize(self):
        return json.dumps(self.__dict__)
'''
class FileInfoMessage(Message):
    def __init__(self, command, fileName, fileSize):
        Message.__init__(self, command)
        self.fileName = fileName
        self.fileSize = fileSize

    def serialize(self):
        return json.dumps({
                "command" : self.command,
                "fileName" : self.fileName,
                "fileSize" : self.fileSize
        })
'''
    
def sendFile(path, address='localhost', port=1234,):
    controller = type('test', (object,), {'cancel':False, 'total_sent':0, 'completed':Deferred()})
    f = FileSenderClientFactory(path, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed
