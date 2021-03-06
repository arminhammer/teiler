"""
The module is intended to be an abstraction that helps the user find the
local ip address that will be used for broadcasting. As windows, linux/mac 
handle their interfaces differently, we want the correct IP address found and used.
"""
import os
import pwd
import netifaces
import uuid
import M2Crypto
import ntpath
from twisted.python import log
import re

def getLiveInterface():
    """will return a list of possible IPv4 addresses"""
    addresses = []
    local_network = ['127.0.0.1', '127.0.1.1', '127.1.1.1']
    lan_prefixes = ["10\.\d{1,3}\.\d{1,3}\.\d{1,3}", "192\.168\.\d{1,3}\.\d{1,3}", "172\.16\.\d{1,3}\.\d{1,3}"]
    lan_patterns = "(" + ")|(".join(lan_prefixes) + ")"
    #lan_prefixes = ['10.','192.','172.']

    # loop over the available network interfaces and try to get the LAN level IP
    for iface in netifaces.interfaces():
        test_iface = netifaces.ifaddresses(iface).get(netifaces.AF_INET) 
        if test_iface is not None:
            for i in test_iface:
                # you need to make sure it is a local
                if i['addr'] not in local_network and re.match(lan_patterns, i['addr']):
                    addresses.append(i['addr'])
    return addresses[0] 

def fileinfo(fname):
    """ when "file" tool is available, return it's output on "fname" """
    return (os.system('file 2> /dev/null') != 0 and \
             os.path.exists(fname) and \
             os.popen('file "' + fname + '"').read().strip().split(':')[1])

def createDirectory(dirName):
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        log.msg("Creating dir {0}".format(dirName))

def _list_files(home):
    file_list = []
    for root, dirs, files in os.walk(home):
        for name in files:       
            filename = os.path.join(root, name)
            file_list.append(filename)
    return file_list

def _list_dirs(home):
    """get the list of directories that need to exist for the new files"""
    dir_list = []
    for root, dirs, files in os.walk(home):
        # here the root is the directory name 
        dir_list.append(root)
    return dir_list

def make_file_list(serve_at):
    """Creates a formatted file containing the directories and the
    files that need to be created on the host system. 
    """
    os.chdir(serve_at)
    home = "./"
    files = _list_files(home)
    dirs = _list_dirs(home)
    dirs.remove("./")
    text = ""
    for foo in dirs:
        text = text + "d::" + foo + "\n"
    for thing in files:
        text = text + "f::" + thing + "\n"
    return text
    

def save_file_list(text,
                   serve_at,
                   filename):
    with open(serve_at + "/" + filename, 'w') as f:
        f.write(text)

# # NEED TESTS
def _make_file(line):
    location = line[:2].replace("\n", "")
    # at some place you will need to allow for resumption of download
    # with http/tcp this is done using the range header
    print location

def _make_dir(line):
    location = line[:2].replace("\n", "")
    print location

def make_files(filename):
    with open(filename, 'r') as f:
        for line in f.readlines():
            if "f::" in line:
                _make_file(line)
            elif "d::" in line:
                _make_dir(line)

def generateSessionID():
    return str(uuid.UUID(bytes=M2Crypto.m2.rand_bytes(16)))

def getUsername():
    """get the username by accessing env vars"""
    return pwd.getpwuid(os.getuid()).pw_name.title()

def getBaseNameFromPath(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
