from twisted.internet import reactor, protocol

class SessionMessageClient(protocol.Protocol):
    
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
        self.message = message
        self.session = session

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        reactor.stop()

'''
# this connects the protocol to a server runing on port 8000
def main():
    f = EchoFactory()
    reactor.connectTCP("localhost", 8000, f)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
'''