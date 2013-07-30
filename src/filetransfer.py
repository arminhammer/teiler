from binascii import crc32
import os, json
import Queue
from twisted.protocols import basic
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import FileSender, LineReceiver
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.python import log
import utils

beginMsg = "BEGIN"
acceptMsg = "ACCEPT"
rejectMsg = "REJECT"
receivedMsg = "RECEIVED"
fileMsg = "FILE"
dirMsg = "DIR"
endMsg = "EOT"

class Message(object):
    """mesage to be sent across the wire"""
    def __init__(self, command):
        self.command = command
    
    def serialize(self):
        return json.dumps(self.__dict__)
'''
class FileInfoMessage(Message):
    def __init__(self, command, fileName, fileSize):
        Message.__init__(self, command)
        self.fileName = fileName
        self.fileSize = fileSize

    def serialize(self):
        return json.dumps({
                "command" : self.command,
                "fileName" : self.fileName,
                "fileSize" : self.fileSize
        })
'''

class FileReceiverProtocol(LineReceiver):
    """ File Receiver """

    def __init__(self, teiler, teilerWindow):
        self.outfile = None
        self.remain = 0
        self.crc = 0
        self.teiler = teiler
        self.teilerWindow = teilerWindow
        
    def lineReceived(self, line):
        """ """
        d = defer.Deferred()
        message = json.loads(line)
        log.msg("Receiver received message {0}".format(message))
        if message['command'] == beginMsg:
            # ok = self.teilerWindow.displayAcceptFileDialog(fileName)
            ok = self.teilerWindow.questionMessage(message['fileName'], "peer")
            log.msg("OK is {0}".format(ok))
            if ok == "no":
                log.msg("Download rejected")
                rejectMessage = Message(rejectMsg)
                self.transport.write(rejectMessage.serialize() + '\r\n')
            elif ok == "yes":
                log.msg("The file is accepted!")
                acceptMessage = Message(acceptMsg)
                self.transport.write(acceptMessage.serialize() + '\r\n')
        elif message['command'] == dirMsg:
            dirName = message['dirName']
            d.addCallBack(self.createDirectory(dirName))
            d.addCallBack(self.sendReceivedMessage())
        elif message['command'] == fileMsg:
            fileNath = message['fileName']
            fileSize = message['fileSize']
            self.setRawMode()
        elif message['command'] == endMsg:
            pass
        else:
            log.msg("Command not recognized.")
        
        def createDirectory(dirName):
            pass
        
        def sendReceivedMessage():
            pass
        
        '''
        print ' ~ lineReceived:\n\t', line
        self.instruction = json.loads(line)
        self.instruction.update(dict(client=self.transport.getPeer().host))
        self.size = self.instruction['file_size']
        self.original_fname = self.instruction.get('original_file_path',
                                                   'not given by client')
        
        fileName = utils.getFilenameFromPath(self.original_fname)
        log.msg("Opening file accept dialog")
        # ok = self.teilerWindow.displayAcceptFileDialog(fileName)
        ok = self.teilerWindow.questionMessage(fileName, "peer")
        log.msg("OK is {0}".format(ok))
        if ok == "no":
            log.msg("Download rejected")
            return
        else:
            # Create the upload directory if not already present
            uploaddir = self.teiler.downloadPath
            print " * Using upload dir:", uploaddir
            if not os.path.isdir(uploaddir):
                os.makedirs(uploaddir)
    
            self.outfilename = os.path.join(uploaddir, fileName)
    
            print ' * Receiving into file@', self.outfilename
            try:
                self.outfile = open(self.outfilename, 'wb')
            except Exception, value:
                print ' ! Unable to open file', self.outfilename, value
                self.transport.loseConnection()
                return
    
            self.remain = int(self.size)
            print ' & Entering raw mode.', self.outfile, self.remain
            self.setRawMode()
        '''

    def rawDataReceived(self, data):
        """ """
        if self.remain % 10000 == 0:
            print '   & ', self.remain, '/', self.size
        self.remain -= len(data)

        self.crc = crc32(data, self.crc)
        self.outfile.write(data)

    def connectionMade(self):
        """ """
        basic.LineReceiver.connectionMade(self)
        print '\n + a connection was made'
        print ' * ', self.transport.getPeer()

    def connectionLost(self, reason):
        """ """
        basic.LineReceiver.connectionLost(self, reason)
        print ' - connectionLost'
        if self.outfile:
            self.outfile.close()
        # Problem uploading - tmpfile will be discarded
        if self.remain != 0:
            print str(self.remain) + ')!=0'
            remove_base = '--> removing tmpfile@'
            if self.remain < 0:
                reason = ' .. file moved too much'
            if self.remain > 0:
                reason = ' .. file moved too little'
            print remove_base + self.outfilename + reason
            os.remove(self.outfilename)

        # Success uploading - tmpfile will be saved to disk.
        else:
            print '\n--> finished saving upload@ ' + self.outfilename
            client = self.instruction.get('client', 'anonymous')

def fileinfo(fname):
    """ when "file" tool is available, return it's output on "fname" """
    return (os.system('file 2> /dev/null') != 0 and \
             os.path.exists(fname) and \
             os.popen('file "' + fname + '"').read().strip().split(':')[1])

class FileReceiverFactory(ServerFactory):
    """ file receiver factory """
    protocol = FileReceiverProtocol

    def __init__(self, teiler, teilerWindow):
        self.teiler = teiler
        self.teilerWindow = teilerWindow
        
    def buildProtocol(self, addr):
        print ' + building protocol'
        p = self.protocol(self.teiler, self.teilerWindow)
        p.factory = self
        return p

class FileSenderClient(LineReceiver):
    """ file sender """

    def __init__(self, path, controller):
        """ """
        self.path = path
        self.fileName = str(utils.getFilenameFromPath(path))
        self.controller = controller
        self.transferQueue = Queue.Queue()

        if os.path.isfile(self.path):
            self.infile = open(self.path, 'rb')
        self.insize = os.stat(self.path).st_size

        self.result = None
        self.completed = False

        self.controller.file_sent = 0
        self.controller.file_size = self.insize

    def _monitor(self, data):
        """ """
        self.controller.file_sent += len(data)
        self.controller.total_sent += len(data)

        # Check with controller to see if we've been cancelled and abort
        # if so.
        if self.controller.cancel:
            print 'FileSenderClient._monitor Cancelling'

            # Need to unregister the producer with the transport or it will
            # wait for it to finish before breaking the connection
            self.transport.unregisterProducer()
            self.transport.loseConnection()

            # Indicate a user cancelled result
            self.result = TransferCancelled('User cancelled transfer')

        return data

    def cbTransferCompleted(self, lastsent):
        """ """
        self.completed = True
        self.transport.loseConnection()

    def connectionMade(self):
        """ """
        beginMessage = Message(beginMsg)
        beginMessage.fileName = self.fileName
        log.msg("Sending BEGIN")
        self.transport.write(beginMessage.serialize() + '\r\n')
        
    def lineReceived(self, line):
        message = json.loads(line)
        log.msg("Sender received message {0}".format(message))
        if message['command'] == rejectMsg:
            log.msg("Received rejection.  Closing...")
            self.loseConnection()
        elif message['command'] == acceptMsg:
            self.initTransfer()
        elif message['command'] == receivedMsg:
            pass
        else:
            log.msg("Command not recognized.")

    def initTransfer(self):
        log.msg("Begin transfer")
        if os.path.isdir(self.path):
            for root, dirs, files in os.walk(self.path, topdown=True):
                for name in dirs:
                    self.transferQueue.put(os.path.join(root, name))
                for name in files:
                    self.transferQueue.put(os.path.join(root, name))
            # log.msg("Printing queue")
            # while not self.transferQueue.empty():
            #    log.msg(self.transferQueue.get())
        else:
            log.msg("Just sending a file")
            relfilePath = os.path.join(os.path.relpath(root, self.path), name)
            fileMessage = Message(fileMsg)
            fileMessage.fileName = "{0}/{1}".format(self.fileName, relfilePath)
            fileMessage.fileSize = os.path.getsize(relFilePath)
            self.transport.write(fileMessage)
            
    def processTransferQueue(self):
        d = defer.Deferred()
        path = self.transferQueue.get()
        if os.path.isdir():
            relDirPath = os.path.join(os.path.relpath(root, self.path), path) 
            dirMessage = Message(dirMessage)
            dirMessage.dirName = "{0}/{1}".format(self.fileName, relDirPath)
            self.transport.write(dirMessage)
        else:
            relfilePath = os.path.join(os.path.relpath(root, self.path), path)
            fileMessage = Message(fileMsg)
            fileMessage.fileName = "{0}/{1}".format(self.fileName, relfilePath)
            fileMessage.fileSize = os.path.getsize(relFilePath)
            self.transport.write(fileMessage)
        sender = FileSender()
        sender.CHUNK_SIZE = 4096
        d = sender.beginFileTransfer(open(path, 'rb'), self.transport,
                                     self._monitor)
        d.addCallback(self.cbTransferCompleted)
        d.addCallback(self.processTransferQueue())
    
    def connectionLost(self, reason):
        """
            NOTE: reason is a twisted.python.failure.Failure instance
        """
        from twisted.internet.error import ConnectionDone
        basic.LineReceiver.connectionLost(self, reason)
        print ' - connectionLost\n  * ', reason.getErrorMessage()
        print ' * finished with', self.path
        self.infile.close()
        if self.completed:
            self.controller.completed.callback(self.result)
        else:
            self.controller.completed.errback(reason)

class FileSenderClientFactory(ClientFactory):
    """ file sender factory """
    protocol = FileSenderClient

    def __init__(self, path, controller):
        """ """
        self.path = path
        self.controller = controller

    def clientConnectionFailed(self, connector, reason):
        """ """
        ClientFactory.clientConnectionFailed(self, connector, reason)
        self.controller.completed.errback(reason)

    def buildProtocol(self, addr):
        """ """
        print ' + building protocol'
        p = self.protocol(self.path, self.controller)
        p.factory = self
        return p
    
def sendFile(path, address='localhost', port=1234,):
    controller = type('test', (object,), {'cancel':False, 'total_sent':0, 'completed':Deferred()})
    f = FileSenderClientFactory(path, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed
