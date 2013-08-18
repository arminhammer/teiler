from twisted.internet import reactor, protocol

class SessionMessageClient(protocol.Protocol):
    
    def __init__(self, session, message):
        self.session = session
        self.message = message
    
    def connectionMade(self):
        self.transport.write(self.message.serialize() + '\r\n')
    
    def dataReceived(self, message):
        "As soon as any data is received, write it back."
        self.session.processResponse(message)
        self.transport.loseConnection()
    
    def connectionLost(self, reason):
        print "connection lost"

class SessionMessageFactory(protocol.ClientFactory):
    protocol = SessionMessageClient
    
    def __init__(self, session, message):
        """ """
        print "message init is {0}".format(message)
        self.message = message
        print "session init is {0}".format(session)
        self.session = session
        
    def buildProtocol(self, addr):
        print ' + building session protocol'
        print "message is {0}".format(self.message)
        p = self.protocol(self.session, self.message)
        p.factory = self
        return p

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"

    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        