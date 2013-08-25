from twisted.trial import unittest
from config import Config
from peerlist import PeerList
import utils

''' Needs help mocking the PeerList qt object '''

class ConfigTestCase(unittest.TestCase):
    
    def setUp(self):
        peerList = PeerList()
        self.config = Config('192.168.1.100', 8899, utils.generateSessionID(), 'Test', peerList, '192.168.1.100', 8891, '/home/dir')
        self.goodSession = Session('/home/test', self.config, '192.168.1.100', 8912)
        self.config.sessions[goodSession.id] = self.goodSession
        
    ''' Test to make sure that notifySession works. goodSession should return true, while badSession is not in self.config and should return false '''
    def test_notifySession(self, sessionID, message):
        self.assertEqual(True, self.config.notifySession(self.goodSession.id, Message('TEST')))
        badSession = Session('/home/test', self.config, '192.168.1.100', 8912)
        self.assertEqual(False, self.config.notifySession(badSession.id, Message('TEST')))
            
    ''' Tests closeSession.  Should close goodSession and make sure that it is no longer in self.config.sessions '''
    def test_closeSession(self, session):
        self.config.closeSession(self.goodSession)
        self.assertEqual(None, self.sessions[session.id])        
    