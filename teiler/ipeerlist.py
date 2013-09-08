import zope.interface

class IPeerList(zope.interface.Interface):
    
    def add(self, peer):
        ''' Add a peer to the list '''
        
    def contains(self, peerID, peerAddress, peerPort):    
        ''' Tests to see if the peer is already in the list '''

    def remove(self, peerID):
        ''' Remove a peer from the list '''
