#!/usr/bin/python
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
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| NetworkClient :
#|     Definition of aclient which follows the definition of the provided 
#|     automata.
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
        self.abstractionLayer = None
        
    def run (self):
        
        if (self.protocol == "UDP") :
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else :
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        
        self.socket.connect((self.host, self.port))
        
        inputFile = self.socket.makefile('r', -1)
        outputFile = self.socket.makefile('w', -1)
        
        # Create the input and output abstraction layer
        self.abstractionLayer = AbstractionLayer(inputFile, outputFile, self.getModel().getDictionary())
        
        # Initialize a dedicated automata and creates a visitor
        modelVisitor = MMSTDVisitor(self.getModel(), self.isMaster(), self.abstractionLayer)
        self.log.info("An MMSTDVistor has been instantiated and assigned to the current network client.")
        modelVisitor.run()
        
        
        
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
    
