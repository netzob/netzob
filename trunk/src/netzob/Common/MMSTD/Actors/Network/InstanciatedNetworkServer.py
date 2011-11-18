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
#| InstanciatedNetworkServer :
#|     Definition of an instanciated network server
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class InstanciatedNetworkServer(AbstractActor):
    
    def __init__(self, socket):
        AbstractActor.__init__(self, False)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.InstanciatedNetworkServer.py')
        self.socket = socket
        self.inputMessages = []
        self.outputMessages = []        
    
        
    def open(self):
        self.log.warn("Impossible to open an InstanciatedNetworkServer")
        return False
    
    def close(self):
        if self.socket == None:
            self.log.info("No need to close the socket since it's not even open")
            return True
        self.log.info("SHUTDOWN THE SOCKET")
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        return True
    
    def read(self):
        result = bitarray(endian='big')       
        
        receivedChars = []
        chars = []
        
        chars = self.socket.recv(4096)
            
        if (len(chars) == 0) : 
            return result
        result.fromstring(chars)
        
#        self.inputMessages.append(receivedData)
        
        self.log.info("Received : " + str(result))
        return result
        
    def write(self, message):
        self.outputMessages.append(message)
        self.socket.send(message.tostring())
        
        self.log.info("Write down !")        
        
    def getInputMessages(self):
        return self.inputMessages
    def getOutputMessages(self):
        return self.outputMessages
    
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port
    
    def setPort(self, port):
        self.port = port
    
