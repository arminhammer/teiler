"""
This module is resposible for peer discovery over UDP only.

The process is simple. 
1) Start up the client and broadcast a UDP datagram on a defined interval.
2) Listen for other packets
3) When another packet is heard, pull it into the list of the peers. 
    But, if the peer is already in the list, do nothing.
4) On disconnect, the client sends an exit message, letting the other 
    users know that they are no longer online; making it safe for the 
    client to disconnect
"""

import json
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
    UDP protocol used to find others running the same program. 
    The protocol will do several things, on program start, a connection
    message will be sent; basically announcing itself as a node to the network.
    Then the protocol will regularly send a heartbeat message at a defined interval.
    Once the peer has decided to disconnect, it will send an exit message to alert 
    the other nodes of its demise.
    """
    def __init__(self, 
                 reactor,
                 peers,
                 name, 
                 multiCastAddress, 
                 multiCastPort, 
                 tcpAddress, 
                 tcpPort):
        """Set up an instance of the PeerDiscovery protocol by creating 
        the message information needed to broadcast other instances 
        of the protocol running on the same network.
        """
        self.peers = peers # your list needs to implement append
        self.id = makeId(name, tcpAddress, tcpPort)
        self.reactor = reactor
        self.name = name
        self.multiCastAddress = multiCastAddress
        self.multiCastPort = multiCastPort
        self.tcpAddress = tcpAddress
        self.tcpPort = tcpPort

    def sendMessage(self, message):
        self.transport.write(message, 
                             (self.multiCastAddress, self.multiCastPort))

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
        self.transport.joinGroup(self.multiCastAddress)
        self.loop = task.LoopingCall(self.sendHeartBeat)
        self.loop.start(5)

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
        """Sends message alerting other peers to your presence."""
        message = Message(heartbeatMsg, 
                          self.name, 
                          self.tcpAddress, 
                          self.tcpPort, 
                          ).serialize()
        self.sendMessage(message)
        log.msg("Sent " + message)

    def stopProtocol(self):
        message = Message(exitMsg, self.teiler.sessionID)
        message.name = self.teiler.name
        message.address = self.teiler.address
        message.tcpPort = self.teiler.tcpPort
        
        self.transport.write(message.serialize() + '\r\n', (self.teiler.multiCastAddress, self.teiler.multiCastPort))
        log.msg("Sent {0} message: {1}".format(exitMsg, message))
        """Gracefully tell peers to remove you."""
        message = Message(exitMsg, 
                          self.name, 
                          self.tcpAddress, 
                          self.tcpPort, 
                          ).serialize()
        self.sendMessage(message)
        self.loop.stop()
        log.msg("Exit " + message)

    def datagramReceived(self, datagram, address):
        """Handles how datagrams are read when they are received. Here, 
        as this is a json serialised message, we are pulling out the 
        peer information and placing it in a list."""
        log.msg("Decoding: " + datagram)

        msg = json.loads(datagram)
        peerName = msg['name']
        peerAddress = msg['address']
        peerPort = msg['tcpPort']
        peerMsg = msg['message']
        peerId = makeId(peerName, peerAddress, peerPort)

        peerPort = message['tcpPort']
        peerID = message['sessionID']
        log.msg("Peer: Address: {0} Name: {1}".format(peerAddress, peerName))

        log.msg("Does the list contain? {0}".format(self.teiler.peerList.contains(peerID, peerAddress, peerPort)))    
        if not self.teiler.peerList.contains(peerID, peerAddress, peerPort):
            newPeer = TeilerPeer(peerID, peerName, peerAddress, peerPort)
            self.teiler.peerList.addItem(newPeer)
            log.msg("Added new Peer: address: {0}:{1}, name: {2}, id: {3}".format(peerAddress, peerPort, peerName, peerID))
            
        if peerMsg == exitMsg:
            if self.isPeer(peerId):
                log.msg('dropping a peer')
                self.removePeer(peerId)

        elif peerMsg == heartbeatMsg:
            if self.isPeer(peerId) == False:
                newPeer = Peer(peerName, peerAddress, peerPort)
                self.addPeer(newPeer)
                log.msg("Added new Peer: address: {0}, name: {1}".format(peerAddress, peerName))
            
    def isPeer(self, id):
        """Convenience method to make it easy to tell whether or not a peer 
        is already a peer. """
        return id in self.peers # for use with default dict

    def removePeer(self, id):
        del self.peers[id]

    def addPeer(self, peer):
        self.peers[peer.id] = peer

        
