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
