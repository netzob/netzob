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
import logging
import socket
import select

from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Actors.AbstractActor import AbstractActor


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
        self.log.debug("Closing the socket")
        if self.socket == None:
            self.log.debug("No need to close the socket since it's not even open")
            return True
        self.log.debug("SHUTDOWN THE SOCKET")
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        return True
    
    def read(self, timeout):
        self.log.debug("Reading from the socket some data")
        result = bitarray(endian='big')       
        
        
        chars = []    
        try :
            if timeout > 0 :
                ready = select.select([self.socket], [], [], timeout)
                if ready[0]:
                    chars = self.socket.recv(4096)
            else :
                ready = select.select([self.socket], [], [])
                self.log.debug("ready = " + str(ready[0]))
                if ready[0]:
                    chars = self.socket.recv(4096)
        except :
            self.log.debug("Impossible to read from the network socket")
            return None
        
        
                
        if (len(chars) == 0) : 
            return result
        result.fromstring(chars)
        
#        self.inputMessages.append(receivedData)
        
        self.log.debug("Received : " + str(result))
        return result
        
    def write(self, message):
        self.log.debug("Writing to the socket")
        self.outputMessages.append(message)
        self.socket.send(message.tostring())
        
        self.log.debug("Write down !")        
        
    def getInputMessages(self):
        return self.inputMessages
    def getOutputMessages(self):
        return self.outputMessages
    
    def isOpen(self):
        return self.open
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port
    
    def setPort(self, port):
        self.port = port
    
