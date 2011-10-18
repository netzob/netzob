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
import time

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from ... import ConfigurationParser
from ..Symbols.impl.EmptySymbol import EmptySymbol

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

class TimeoutException(Exception): 
    pass 

#+---------------------------------------------------------------------------+
#| AbstractionLayer :
#|     Definition of an abstractionLayer
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class AbstractionLayer():
    
    def __init__(self, input, output, dictionary):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.AbstractionLayer.py')
        self.input = input
        self.output = output
        self.dictionary = dictionary
        self.inputMessages = []
        self.outputMessages = []

    #+-----------------------------------------------------------------------+
    #| receiveSymbol
    #|     Manage the reception of a message and its transformation in a symbol
    #| @return a tupple containing the symbol and the associated received message
    #+-----------------------------------------------------------------------+
    def receiveSymbol(self):
        self.log.info("Waiting for the reception of a message")
        # First we read from the input the message        
        receivedData = self.input.readline().strip()
        self.log.info("Received following message : " + receivedData)
        self.inputMessages.append(["00:00:00", receivedData])
        
        # Now we abstract the message
        symbol = self.abstract(receivedData)
        
        return (symbol, receivedData)
    
    def writeSymbol(self, symbol):
        # First we specialize the symbol in a message
        message = self.specialize(symbol)
        self.log.info("Sending message : '" + message + "'")
        self.outputMessages.append(["00:00:00", message])
        # now we send it
        self.output.write(message)
        self.output.flush()
        
    
    
    #+-----------------------------------------------------------------------+
    #| abstract
    #|     Searches in the dictionary the symbol which abstract the received message
    #| @return a possible symbol or None if none exist in the dictionary
    #+-----------------------------------------------------------------------+    
    def abstract(self, message):        
        # we search in the dictionary an entry which match the message
        for entry in self.dictionary.getEntries() :            
            if entry.compare(message, 0, False) != -1:
                self.log.info("Entry in the dictionary found")
                return entry
            else :
                self.log.info("Entry " + str(entry.getID()) + " doesn't match")
            
        
        return EmptySymbol()
        
    def specialize(self, symbol):
        value = symbol.getValueToSend()
        return value     
        
    def getMemory(self):
        memory = []
        for variable in self.dictionary.getVariables() :
            memory.append([variable.getName(), variable.getType(), variable.getValue(False)])
        return memory
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getInputMessages(self):
        return self.inputMessages
    def getOutputMessages(self):
        return self.outputMessages
    
    
