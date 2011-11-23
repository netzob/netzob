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
import select
from bitarray import bitarray
from collections import deque
#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
#from .... import ConfigurationParser
from AbstractActor import AbstractActor
#from ..MMSTDVisitor import MMSTDVisitor
#from ...Dictionary.AbstractionLayer import AbstractionLayer


#+---------------------------------------------------------------------------+
#| SimpleCommunicationLayer :
#|     Definition of a simple communicationLayer
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class SimpleCommunicationLayer(AbstractActor):
    
    def __init__(self, inputs, outputs, dictionary):
        AbstractActor.__init__(self, False)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.SimpleCommunicationLayer.py')
        self.predefinedInputs = deque(inputs)
        self.predefinedOutputs = deque(outputs)
        self.inputMessages = []
        self.outputMessages = []        
        self.dictionary = dictionary
    
        
    def open(self):
        self.log.info("We open it !")
        return True
    
    def close(self):
        self.log.info("We close it !")
        return True
    
    def read(self, timeout):
        self.log.info("We read it !")
        if (len(self.predefinedInputs) > 0) :
            symbol = self.predefinedInputs.popleft()
            self.log.info("We simulate the reception of symbol " + str(symbol))
            (value, strvalue) = symbol.getValueToSend(self.dictionary)
            self.inputMessages.append(value)
            return value
        else :
            self.log.info("No more inputs to simulate, nothing was read ")
            return None
       
        
    def write(self, message):
        self.log.info("Write down !")  
        self.outputMessages.append(message)
        
        
    def getInputMessages(self):
        return self.inputMessages
    def getOutputMessages(self):
        return self.outputMessages
    def getGeneratedInstances(self):
        return []
    
    def stop(self):
        self.log.info("Stopping the thread of the client")
        AbstractActor.stop(self)
    
   
    
