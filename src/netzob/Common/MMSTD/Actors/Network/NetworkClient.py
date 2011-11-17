# -* - coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging.config
import asyncore
import threading
import socket
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from ..AbstractActor import AbstractActor
from ..MMSTDVisitor import MMSTDVisitor
from ...Dictionary.AbstractionLayer import AbstractionLayer


#+---------------------------------------------------------------------------+
#| NetworkClient :
#|     Definition of a network client
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class NetworkClient(AbstractActor):
    
    def __init__(self, host, protocol, port):
        AbstractActor.__init__(self, False)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkClient.py')
        self.port = port
        self.host = host
        self.protocol = protocol
        self.socket = None
        self.inputMessages = []
        self.outputMessages = []        
    
        
    def open(self):
        try :
            if (self.protocol == "UDP") :
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else :
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
            self.socket.connect((self.host, self.port))
        except :
            self.socket = None
            
        if self.socket == None :
            self.log.warn("Impossible to open the socket created in the NetworkClient")
            return False
        
#        self.inputFile = self.socket.makefile('r', -1)
        self.outputFile = self.socket.makefile('w', -1)
        return True
    
    def close(self):
        if self.socket == None:
            self.log.info("No need to close the socket since it's not even open")
            return True
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        return True
    
    def read(self):
        result = bitarray(endian='big')        
        
        receivedChars = []
        chars = self.socket.recv(4096)
        self.log.info("Read finished")
        if (len(chars) == 0) : 
            return result
        result.fromstring(chars)
        
#        self.inputMessages.append(receivedData)
        
        self.log.info("Received : " + str(result))
        return result
        
    def write(self, message):
        self.outputMessages.append(message)
        self.outputFile.flush()
        self.outputFile.write(message.tostring())
        self.outputFile.flush()
        self.log.info("Write down !")        
        
    def getInputMessages(self):
        return self.inputMessages
    def getOutputMessages(self):
        return self.outputMessages
    def getGeneratedInstances(self):
        return []
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port
    
    def setPort(self, port):
        self.port = port
    
