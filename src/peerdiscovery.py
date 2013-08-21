import sys, json
from twisted.python import log
from twisted.internet import task, reactor
from twisted.internet.protocol import DatagramProtocol 
from peerlist import TeilerPeer
from message import Message

connectMsg = "CONNECT"
heartbeatMsg = "HEARTBEAT"
exitMsg = "EXIT"

class PeerDiscovery(DatagramProtocol):
    """
    Broadcast the ip to all of the listeners on the channel
    """
    def __init__(self, teiler):
        self.teiler = teiler

    def startProtocol(self):
        self.transport.setTTL(5)
        self.transport.joinGroup(self.teiler.multiCastAddress)
        message = Message(connectMsg, self.teiler.sessionID)
        message.name = self.teiler.name
        message.address = self.teiler.address
        message.tcpPort = self.teiler.tcpPort
        
        self.transport.write(message.serialize() + '\r\n', (self.teiler.multiCastAddress, 
                                       self.teiler.multiCastPort))
        log.msg("Sent {0} message: {1}".format(connectMsg, message))      
        reactor.callLater(10.0, self.sendHeartBeat)

    def sendHeartBeat(self):
        message = Message(heartbeatMsg, self.teiler.sessionID)
        message.name = self.teiler.name
        message.address = self.teiler.address
        message.tcpPort = self.teiler.tcpPort

        self.transport.write(message.serialize() + '\r\n', 
                             (self.teiler.multiCastAddress, 
                              self.teiler.multiCastPort))
        log.msg("Sent {0} message: {1}".format(heartbeatMsg, message))
        reactor.callLater(5.0, self.sendHeartBeat)

    def stopProtocol(self):
        message = Message(exitMsg, self.teiler.sessionID)
        message.name = self.teiler.name
        message.address = self.teiler.address
        message.tcpPort = self.teiler.tcpPort
        
        self.transport.write(message.serialize() + '\r\n', (self.teiler.multiCastAddress, self.teiler.multiCastPort))
        log.msg("Sent {0} message: {1}".format(exitMsg, message))

    def datagramReceived(self, datagram, address):
        log.msg("Decoding: {0}".format(datagram))
        message = json.loads(datagram)
        peerName = message['name']
        peerAddress = message['address']
        peerPort = message['tcpPort']
        peerID = message['sessionID']
        log.msg("Peer: Address: {0} Name: {1}".format(peerAddress, peerName))

        log.msg("Does the list contain? {0}".format(self.teiler.peerList.contains(peerID, peerAddress, peerPort)))    
        if not self.teiler.peerList.contains(peerID, peerAddress, peerPort):
            newPeer = TeilerPeer(peerID, peerName, peerAddress, peerPort)
            self.teiler.peerList.addItem(newPeer)
            log.msg("Added new Peer: address: {0}:{1}, name: {2}, id: {3}".format(peerAddress, peerPort, peerName, peerID))
            
