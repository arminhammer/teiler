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
from peer import Peer
from message import Message

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
                 sessionID,
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
        self.sessionID = sessionID
        self.reactor = reactor
        self.name = name
        self.multiCastAddress = multiCastAddress
        self.multiCastPort = multiCastPort
        self.tcpAddress = tcpAddress
        self.tcpPort = tcpPort

    def sendMessage(self, message):
        self.transport.write(message.serialize() + '\r\n', 
                             (self.multiCastAddress, self.multiCastPort))

    def startProtocol(self):
        self.transport.setTTL(5)   
        self.transport.joinGroup(self.multiCastAddress)
        self.loop = task.LoopingCall(self.sendHeartBeat)
        self.loop.start(10)

    def sendHeartBeat(self):
        """Sends message alerting other peers to your presence."""
        message = Message(heartbeatMsg, self.sessionID)
        message.name = self.name
        message.address = self.tcpAddress
        message.tcpPort = self.tcpPort
        self.sendMessage(message)
        log.msg("Sent " + str(message))
        
    def stopProtocol(self):
        """Gracefully tell peers to remove you."""
        message = Message(exitMsg, self.sessionID)
        message.name = self.name
        message.address = self.teiler.tcpAddress
        message.tcpPort = self.teiler.tcpPort
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
        peerCommand = msg['command']
        peerPort = msg['tcpPort']
        peerID = msg['sessionID']
        log.msg("Peer: Address: {0} Name: {1}".format(peerAddress, peerName))

        log.msg("Does the list contain? {0}".format(self.peers.contains(peerID, peerAddress, peerPort)))    
        if not self.peers.contains(peerID, peerAddress, peerPort):
            newPeer = Peer(peerID, peerName, peerAddress, peerPort)
            self.peers.addItem(newPeer)
            log.msg("Added new Peer: address: {0}:{1}, name: {2}, id: {3}".format(peerAddress, peerPort, peerName, peerID))
            
        if peerCommand == exitMsg:
            if self.isPeer(peerID, peerAddress, peerPort):
                log.msg('dropping a peer')
                self.removePeer(peerId)

        elif peerCommand == heartbeatMsg:
            if self.isPeer(peerID, peerAddress, peerPort) == False:
                newPeer = Peer(peerName, peerAddress, peerPort)
                self.addPeer(newPeer)
                log.msg("Added new Peer: address: {0}, name: {1}".format(peerAddress, peerName))
            
    def isPeer(self, id, address, port):
        """Convenience method to make it easy to tell whether or not a peer 
        is already a peer. """
        return self.peers.contains(id, address, port) # for use with default dict

    def removePeer(self, id):
        del self.peers[id]

    def addPeer(self, peer):
        self.peers[peer.id] = peer
