from twisted.python import log

# Class to maintain the state of the program
class Config():
    """ Class to hold on to all instance variables used for state. 
    """
    def __init__(self, 
                 address, 
                 tcpPort,
                 sessionID,
                 name,
                 peerList,
                 multiCastAddress,
                 multiCastPort,
                 downloadPath):
        self.address = address # this is the local IP
        # port for file receiver to listen on 
        self.tcpPort = tcpPort
        self.sessionID = sessionID
        self.name = name
        self.peerList = peerList
        self.multiCastAddress = multiCastAddress
        self.multiCastPort = multiCastPort
        self.downloadPath = downloadPath
        self.sessions = {}
        ''' Sessions currently downloading, only the Session IDs '''
        self.dlSessions = set()
        
    def notifySession(self, sessionID, message):
        log.msg("Printing sessions:")
        for k,v in self.sessions.iteritems():
            log.msg("Key: {0}, Value: {1}".format(k, v))
        if not self.sessions.has_key(sessionID):
            log.msg("Session key cannot be found!")
            return False
        else:
            self.sessions[sessionID].processResponse(message)
            return True
            
    def closeSession(self, session):
        del self.sessions[session.id]
        