# -*- coding: utf-8 -*-

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
    
    def __init__(self, name, model, isMaster, host, protocol, port):
        AbstractActor.__init__(self, name, model, isMaster)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.Network.NetworkClient.py')
        self.port = port
        self.host = host
        self.protocol = protocol
        self.socket = None
        self.inputFile = None
        self.outputFile = None
        
        
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
        
        self.inputFile = self.socket.makefile('r', -1)
        self.outputFile = self.socket.makefile('w', -1)
        return True
    
    def close(self):
        if self.socket == None:
            self.log.info("No need to close the socket since it's not even open")
            return True
        
        self.socket.close()
        return True
    
    def read(self):
        receivedChars = []
        self.input.flush()
        chars = self.input.read(4096)
        if (len(chars) == 0) : 
            return "" 
        
        for c in chars :
            v = str(hex(ord(c))).replace("0x", "")
            if len(str(v)) != 2 : 
                v = "0" + str(v)
            receivedChars.append(v)
        receivedData = ''.join(receivedChars)
        
        self.log.info("Received : " + receivedData)
        return receivedData
        
    def write(self, message):
        self.output.flush()
        self.output.write(message)
        self.log.info("Write down !")
        self.output.flush()
            
#        
#        # Create the input and output abstraction layer
#        self.abstractionLayer = AbstractionLayer(inputFile, outputFile, self.getModel().getDictionary())
#        
#        # Initialize a dedicated automata and creates a visitor
#        modelVisitor = MMSTDVisitor(self.getModel(), self.isMaster(), self.abstractionLayer)
#        self.log.info("An MMSTDVistor has been instantiated and assigned to the current network client.")
#        modelVisitor.run()
#        
        
        
    def getInputMessages(self):
        if self.abstractionLayer == None :
            return []
        
        return self.abstractionLayer.getInputMessages()
    def getOutputMessages(self):
        if self.abstractionLayer == None :
            return []
        return self.abstractionLayer.getOutputMessages()
    def getMemory(self):
        if self.abstractionLayer == None :
            return []
        return self.abstractionLayer.getMemory()
    
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getPort(self):
        return self.port
    
    def setPort(self, port):
        self.port = port
    
