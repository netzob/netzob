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
import datetime

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
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

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
        self.connected = False
        
    def connect(self):
        if self.connected :
            self.log.warn("Impossible to connect : already connected")
        else :
            self.log.info("Connecting ...")
    
    def disconnect(self):
        if self.connected :
            self.log.info("Disconnecting ...")
        else :
            self.log.warn("Impossible to disconnect : not connected")
            

    #+-----------------------------------------------------------------------+
    #| receiveSymbol
    #|     Manage the reception of a message and its transformation in a symbol
    #| @return a tupple containing the symbol and the associated received message
    #+-----------------------------------------------------------------------+
    def receiveSymbol(self):
        self.log.info("Waiting for the reception of a message")
        # First we read from the input the message 
        finish = False
        receivedChars = []
#        while not finish :
#            char = self.input.read(1)
#            self.log.info("Received : " + char)
#            receivedChars.append(hex(ord(char)))
#            if char == '\n' or char == '\r' or char == '\0' :
#                finish = True

        chars = ""
        
        chars = self.input.read(4096)
        if (len(chars) == 0) : 
            return (EmptySymbol(), "") 
        
        for c in chars :
            v = str(hex(ord(c))).replace("0x", "")
            if len(str(v)) != 2 : 
                v = "0" + str(v)
            receivedChars.append(v)
#        receivedData = "".join(receivedChars)
            
        
        receivedData = ''.join(receivedChars)
        
        self.log.info("Received : " + receivedData)
        
        now = datetime.datetime.now()
        receptionTime = now.strftime("%H:%M:%S")
        self.log.info("Received following message : " + receivedData)
                
        self.inputMessages.append([receptionTime, receivedData])
        
        # Now we abstract the message
        symbol = self.abstract(receivedData)
        
        return (symbol, receivedData)
    
    def writeSymbol(self, symbol):
        # First we specialize the symbol in a message
        (binMessage, strMessage) = self.specialize(symbol)
        self.log.info("Sending message : bin('" + strMessage + "')")
        self.log.info(str(binMessage))
        # now we send it
        self.output.flush()
        now = datetime.datetime.now()
        self.output.write(binMessage)
        self.log.info("Write down !")
        self.output.flush()
        sendingTime = now.strftime("%H:%M:%S")
        self.outputMessages.append([sendingTime, strMessage])
    
    
    #+-----------------------------------------------------------------------+
    #| abstract
    #|     Searches in the dictionary the symbol which abstract the received message
    #| @return a possible symbol or None if none exist in the dictionary
    #+-----------------------------------------------------------------------+    
    def abstract(self, message):        
        # we search in the dictionary an entry which match the message
        for entry in self.dictionary.getEntries() :            
            if entry.compare(message, 0, False, self.dictionary) != -1:
                self.log.info("Entry in the dictionary found")
                return entry
            else :
                self.log.info("Entry " + str(entry.getID()) + " doesn't match")
            
        
        return EmptySymbol()
        
    def specialize(self, symbol):
        (value, strvalue) = symbol.getValueToSend(self.dictionary)
        return (value, strvalue)     
        
    def getMemory(self):
        memory = []
        for variable in self.dictionary.getVariables() :
            (binVal, strVal) = variable.getValue(False, self.dictionary)
            memory.append([variable.getName(), variable.getType(), strVal])
        return memory
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getInputMessages(self):
        return self.inputMessages
    def getOutputMessages(self):
        return self.outputMessages
    
    
