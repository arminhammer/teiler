from message import Message
import utils
from twisted.trial import unittest

class MessageTestCase(unittest.TestCase):
    
    def setUp(self):
        self.testCommand = "TEST"
        self.sessionID = utils.generateSessionID()
    
    def test_init_noSessionParam(self):
        mesg = Message(self.testCommand)
        mCommand = mesg.command
        mSession = mesg.sessionID
        self.assertEqual(mCommand, self.testCommand)
        self.assertEqual(mSession, "0000")
        
    def test_init_withSessionParam(self):
        mesg = Message(self.testCommand, self.sessionID)
        mCommand = mesg.command
        mSession = mesg.sessionID
        self.assertEqual(mCommand, self.testCommand)
        self.assertEqual(mSession, self.sessionID)
    
    def test_serialize(self):
        serialString = "{\"sessionID\": \"" + self.sessionID + "\", \"command\": \"" + self.testCommand + "\"}"
        mesg = Message(self.testCommand, self.sessionID)
        self.assertEqual(serialString, mesg.serialize())
        