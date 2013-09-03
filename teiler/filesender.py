import os, json

from twisted.python import log
from twisted.protocols import basic
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import FileSender
import session

class FileSenderClient(basic.LineReceiver):
    """ file sender """

    def __init__(self, path, controller, sessionID):
        """ """
        self.path = path
        self.controller = controller

        self.infile = open(self.path, 'rb')
        self.insize = os.stat(self.path).st_size

        self.result = None
        self.completed = False

        self.controller.file_sent = 0
        self.controller.file_size = self.insize
        
        self.sessionID = str(sessionID)

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
            # self.result = TransferCancelled('User cancelled transfer')

        return data

    def lineReceived(self, line):
        message = json.loads(line)
        log.msg("Sender received message {0}".format(message))
        if message['command'] == session.receivedMsg:
            if self.completed:
                log.msg("Looks like the file went through.  Closing...")
            else:
                log.msg("Message from receiver was sent before the file \
                transfer was completed")
            self.transport.loseConnection()

    def cbTransferCompleted(self, lastsent):
        """ """
        self.completed = True
        self.setLineMode()
        # eofMsg = session.Message(session.endFileMsg)
        # eofMsg.sessionID = self.sessionID
        self.transport.loseConnection()

    def connectionMade(self):
        """ """
        fileHeader = session.Message(session.fileMsg)
        fileHeader.fileSize = self.insize
        fileHeader.fileName = self.path
        fileHeader.sessionID = self.sessionID
        self.transport.write(fileHeader.serialize() + '\r\n')
        sender = FileSender()
        sender.CHUNK_SIZE = 2 ** 16
        d = sender.beginFileTransfer(self.infile, self.transport,
                                     self._monitor)
        d.addCallback(self.cbTransferCompleted)

    def connectionLost(self, reason):
        """
            NOTE: reason is a twisted.python.failure.Failure inst
            
            ance
        """
        basic.LineReceiver.connectionLost(self, reason)
        print ' - connectionLost\n  * ', reason.getErrorMessage()
        print ' * finished with', self.path
        self.infile.close()
        if self.completed:
            log.msg("Yada Yada success!")
            self.controller.session.processTransferQueue()
            # self.controller.completed.callback(self.result)
        else:
            log.msg("Yada Yada failure!")
            self.controller.completed.errback(reason)

class FileSenderClientFactory(ClientFactory):
    """ file sender factory """
    protocol = FileSenderClient

    def __init__(self, path, controller, sessionID):
        """ """
        self.path = path
        self.controller = controller
        self.sessionID = sessionID

    def clientConnectionFailed(self, connector, reason):
        """ """
        ClientFactory.clientConnectionFailed(self, connector, reason)
        self.controller.completed.errback(reason)

    def buildProtocol(self, addr):
        """ """
        print ' + building protocol'
        p = self.protocol(self.path, self.controller, self.sessionID)
        p.factory = self
        return p
