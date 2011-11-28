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
from collections import deque
#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from AbstractActor import AbstractActor

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
        self.log.debug("We open it !")
        return True
    
    def close(self):
        self.log.debug("We close it !")
        return True
    
    def read(self, timeout):
        self.log.debug("We read it !")
        if (len(self.predefinedInputs) > 0) :
            symbol = self.predefinedInputs.popleft()
            self.log.debug("We simulate the reception of symbol " + str(symbol))
            (value, strvalue) = symbol.getValueToSend(self.dictionary)
            self.inputMessages.append(value)
            return value
        else :
            self.log.debug("No more inputs to simulate, nothing was read ")
            return None
       
        
    def write(self, message):
        self.log.debug("Write down !")  
        self.outputMessages.append(message)
        
        
    def getInputMessages(self):
        return self.inputMessages
    def getOutputMessages(self):
        return self.outputMessages
    def getGeneratedInstances(self):
        return []
    
    def stop(self):
        self.log.debug("Stopping the thread of the client")
        AbstractActor.stop(self)
    
   
    
