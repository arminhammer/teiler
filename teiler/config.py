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
        self.address = address  # this is the local IP
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
    
    def closeSession(self, session):
        del self.sessions[session.id]
        
