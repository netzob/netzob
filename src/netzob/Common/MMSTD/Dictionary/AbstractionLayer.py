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


class TimeoutException(Exception): 
    pass 

#+---------------------------------------------------------------------------+
#| AbstractionLayer :
#|     Definition of an abstractionLayer
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class AbstractionLayer():
    
    def __init__(self, communicationChannel, dictionary):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.AbstractionLayer.py')
        self.communicationChannel = communicationChannel
        self.dictionary = dictionary
        self.inputMessages = []
        self.outputMessages = []
        self.connected = False
        
    def isConnected(self):
        return self.connected    
    
    def openServer(self, dictionary, outputState, isMaster):
        self.log.info("OpenServer ...")
        self.connected = True
        self.communicationChannel.openServer(dictionary, outputState, isMaster)
        
    def closeServer(self):
        self.log.info("CLoseServer ...")
        self.connected = False
        self.communicationChannel.close()
    
    def connect(self):
        self.log.info("Connect ...")
        if self.connected :
            self.log.warn("Impossible to connect : already connected")
        else :
            # if its a server :
            if self.communicationChannel.isServer() :
                self.log.info("Opening the server to outside connections")      
                          
            else :
            # if its a client :
                self.log.info("Connecting the client...")
                self.connected = self.communicationChannel.open()
    
    def disconnect(self):
        self.log.info("Disconnect ...")
        if self.connected :
            self.log.info("Disconnecting ...")
            self.connected = not self.communicationChannel.close()
            
            # if its a server :
            if self.communicationChannel.isServer() :
                self.log.info("Close the server")  
                self.closeServer()
                          
            else :
            # if its a client :
                self.log.info("Close the client...")
                try :
                    self.connected = self.communicationChannel.close()
                except :
                    self.log.warn("Error while trying to disconnect")
            
        else :
            self.log.info("Impossible to disconnect : not connected")
            

    #+-----------------------------------------------------------------------+
    #| receiveSymbol
    #|     Manage the reception of a message and its transformation in a symbol
    #| @return a tupple containing the symbol and the associated received message
    #+-----------------------------------------------------------------------+
    def receiveSymbol(self):
        self.log.info("Waiting for the reception of a message")
        
        # First we read from the input the message 
        receivedData = self.communicationChannel.read()
        
        if len(receivedData) > 0 :        
            now = datetime.datetime.now()
            receptionTime = now.strftime("%H:%M:%S")
            self.log.info("Received following message : " + str(receivedData))
            
            # Now we abstract the message
            symbol = self.abstract(receivedData)
            
            # We store the received messages its time and its abstract representation
            self.inputMessages.append([receptionTime, receivedData, symbol])
            return (symbol, receivedData)
        else :
            return (EmptySymbol(), None)
    
    def writeSymbol(self, symbol):
        # First we specialize the symbol in a message
        (binMessage, strMessage) = self.specialize(symbol)
        self.log.info("Sending message : str = '" + strMessage + "'")
        self.log.info("Sending message : bin = '" + str(binMessage) + "'")
        
        # transform the binMessage to a real binary message
        
        
        
        # now we send it
        now = datetime.datetime.now()
        sendingTime = now.strftime("%H:%M:%S")
        self.communicationChannel.write(binMessage)
        
        self.outputMessages.append([sendingTime, strMessage, symbol])
    
    
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
                # we first restore possibly learnt value
                self.log.info("Restore possibly learnt value")
                entry.restore()
            
        
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
    def getCommunicationLayer(self):
        return self.communicationChannel
    def getDictionary(self):
        return self.dictionary
    
