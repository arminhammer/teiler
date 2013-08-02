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
