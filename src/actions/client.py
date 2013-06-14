import os
import errno

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer

import requests

# should be limited to this module only
_fileserver = ''

def get_file_urls(url):
    r = requests.get("http://" + url + '/teiler-list.txt')
    if r.status_code == 200:
        save(r.content)
    else:
        print "Fileserver not at specified address"

def _get_file():
    """Download all fo the files specified in the file provided by teiler-list.txt"""
    check_path(handle)
    r = requests.get('http://' + filserver + '/' + handle)
    if r.status_code == 200:
        with open(handle, 'rb') as f:
            for chuck in r.iter_content(1024):
                f.write(chunk)
                    
def get_files(files):
    with open('teiler-list.txt', 'r') as f:
        for line in f:
            _get_file(line)

def check_path(path):
    try:
        os.makdirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def save(stuff, name):
    with open(name, 'w') as f:
        f.write(stuff)

class MulticastClientUDP(DatagramProtocol):
    
    def __init__(self):
        self.host = '224.0.0.5'

    def startProtocol(self):
        # this could be placed in a config
        self.transport.joinGroup(self.host)

    def datagramReceived(self, datagram, address):
        # should be a log statement
        print "Received: " + repr(datagram)
        global _fileserver
        _fileserver = repr(datagram).replace("'", "")

        # this will need more checking - it is killing the conn 
        # once it receives the address
        self.transport.loseConnection()
        reactor.stop()    

def main():
    print "Listening"
    reactor.listenMulticast(8005, 
                            MulticastClientUDP(),
                            listenMultiple = True)
    
    reactor.run()
    # async **should** be over
    # reactor is closed at this point.
    get_file_urls(_fileserver)
    get_files()
if __name__ == '__main__':
    main()
