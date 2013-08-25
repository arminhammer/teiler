from twisted.trial import unittest
from peer import Peer
import utils

class PeerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.id = utils.generateSessionID()
        self.peer = Peer(self.id, "Test", '192.168.1.100', 8992)
    
    def test_str(self):
        self.assertEquals(self.id, "%s" % self.peer)
    
    def test_eq(self):
        ''' Test to assert that the peers are equal '''
        newPeer1 = Peer(self.id, "newPeer1", '192.168.1.100', 8992)
        self.assertEquals(self.peer, newPeer1)
        ''' Make sure that the test fails if the sessions are different but coming from the same host '''
        newPeer2 = Peer(utils.generateSessionID(), "newPeer2", '192.168.1.100', 8992)
        self.assertNotEquals(self.peer, newPeer2)
        ''' Test to make sure that if the sessions are the same and the address/port is different, that it still fails '''
        newPeer3 = Peer(self.id, "newPeer3", '192.168.1.101', 5992)
        self.assertNotEquals(self.peer, newPeer3)
    
    def test_dragEnterEvent(self):
        self.fail()
    