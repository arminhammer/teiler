import Queue
import utils
import os, json
from twisted.protocols import basic
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ClientFactory
import filetransfer
from twisted.internet.defer import Deferred
from twisted.python import log
from twisted.internet import reactor

class FileSenderClient(LineReceiver):
    """ file sender """

    def __init__(self, path, controller):
        """ """
        self.path = path
        self.fileName = str(utils.getFilenameFromPath(path))
        self.controller = controller
        self.transferQueue = Queue.Queue()

        if os.path.isfile(self.path):
            self.infile = open(self.path, 'rb')
        self.insize = os.stat(self.path).st_size

        self.result = None
        self.completed = False

        self.controller.file_sent = 0
        self.controller.file_size = self.insize

    def _monitor(self, data):
        """ """
        self.controller.file_sent += len(data)
        self.controller.total_sent += len(data)

        # Check with controller to see if we've been cancelled and abort
        # if so.
        if self.controller.cancel:
            print 'FileSenderClient._monitor Cancelling'

            # Need to unregister the producer with the transport or it will
            # wait for it to finish before breaking the connection
            self.transport.unregisterProducer()
            self.transport.loseConnection()

            # Indicate a user cancelled result
            self.result = TransferCancelled('User cancelled transfer')

        return data

    def cbTransferCompleted(self):
        """ """
        self.completed = True
        self.transport.loseConnection()

    def connectionMade(self):
        """ """
        beginMessage = filetransfer.Message(filetransfer.beginMsg)
        beginMessage.fileName = self.fileName
        log.msg("Sending BEGIN")
        self.transport.write(beginMessage.serialize() + '\r\n')
        
    def lineReceived(self, line):
        message = json.loads(line)
        log.msg("Sender received message {0}".format(message))
        if message['command'] == filetransfer.rejectMsg:
            log.msg("Received rejection.  Closing...")
            self.loseConnection()
        elif message['command'] == filetransfer.acceptMsg:
            #d = Deferred()
            reactor.callLater(self.initTransfer())
            #d.addCallback(self.initTransfer())
        elif message['command'] == filetransfer.receivedMsg:
            pass
        else:
            log.msg("Command not recognized.")

    def initTransfer(self):
        log.msg("Begin transfer")
        if os.path.isdir(self.path):
            for root, dirs, files in os.walk(self.path, topdown=True):
                for name in dirs:
                    self.transferQueue.put(os.path.join(root, name))
                for name in files:
                    self.transferQueue.put(os.path.join(root, name))
            # log.msg("Printing queue")
            # while not self.transferQueue.empty():
            #    log.msg(self.transferQueue.get())
            reactor.callLater(self.processTransferQueue())
        else:
            log.msg("Just sending a file")
            relfilePath = os.path.join(os.path.relpath(root, self.path), name)
            fileMessage = Message(filetransfer.fileMsg)
            fileMessage.fileName = "{0}/{1}".format(self.fileName, relfilePath)
            fileMessage.fileSize = os.path.getsize(relFilePath)
            self.transport.write(fileMessage)
            
    def processTransferQueue(self):
        d = Deferred()
        path = self.transferQueue.get()
        if path == None:
            endMessage = Message(filetransfer.endMsg)
            self.transport.write(endMessage)
            reactor.callLater(self.cbTransferCompleted())
        else:
            if os.path.isdir():
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
            sender = FileSender()
            sender.CHUNK_SIZE = 4096
            d = sender.beginFileTransfer(open(path, 'rb'), self.transport,
                                         self._monitor)
            d.addCallback(self.cbTransferCompleted)
            d.addCallback(self.processTransferQueue())
    
    def connectionLost(self, reason):
        """
            NOTE: reason is a twisted.python.failure.Failure instance
        """
        from twisted.internet.error import ConnectionDone
        basic.LineReceiver.connectionLost(self, reason)
        print ' - connectionLost\n  * ', reason.getErrorMessage()
        print ' * finished with', self.path
        self.infile.close()
        if self.completed:
            self.controller.completed.callback(self.result)
        else:
            self.controller.completed.errback(reason)

class FileSenderClientFactory(ClientFactory):
    """ file sender factory """
    protocol = FileSenderClient

    def __init__(self, path, controller):
        """ """
        self.path = path
        self.controller = controller

    def clientConnectionFailed(self, connector, reason):
        """ """
        ClientFactory.clientConnectionFailed(self, connector, reason)
        self.controller.completed.errback(reason)

    def buildProtocol(self, addr):
        """ """
        print ' + building protocol'
        p = self.protocol(self.path, self.controller)
        p.factory = self
        return p