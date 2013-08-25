#!/usr/bin/env python
import codecs 

try: 
    codecs.lookup('mbcs') 
except LookupError: 
    ascii = codecs.lookup('ascii') 
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs') 
    codecs.register(func)
    
from distutils.core import setup

setup(name = "teiler",
      packages = ["teiler"],
      version = "0.1.0",
      description = "Peer2peer ad-hoc file sharing for LANs",
      author = "Armin Graf & Chris Wolfe",
      author_email = "arminhammer@gmail.com",
      url="github.com/arminhammer/teiler",
)
