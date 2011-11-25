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
from .... import ConfigurationParser
from ...Symbols.impl.DictionarySymbol import DictionarySymbol
from ...Symbols.impl.EmptySymbol import EmptySymbol
from ..AbstractTransition import AbstractTransition
from xml.etree import ElementTree
import logging.config
import random
import time


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| SimpleTransition :
#|     Definition of a simple transition (only sends something after X ms)
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class SimpleTransition(AbstractTransition):
    
    def __init__(self, id, name, inputState, outputState, timeBeforeSending, outputSymbol):
        AbstractTransition.__init__(self, "SimpleTransition", id, name, inputState, outputState)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Transitions.impl.SimpleTransition.py')
        self.outputSymbol = outputSymbol
        self.timeBeforeSending = timeBeforeSending
        
    #+-----------------------------------------------------------------------+
    #| getOutputSymbol
    #|     Return the associated output symbol
    #| @return the outputSymbol
    #+-----------------------------------------------------------------------+
    def getOutputSymbol(self):
        return self.outputSymbol
    
    #+-----------------------------------------------------------------------+
    #| getTimeBeforeSending
    #|     Return the time which will be paused before sending something
    #| @return the time time before sending
    #+-----------------------------------------------------------------------+
    def getTimeBeforeSending(self):
        return self.timeBeforeSending
   
    
    #+-----------------------------------------------------------------------+
    #| isValid
    #|     Computes if the received symbol is valid
    #| @return a boolean which indicates if received symbol is equivalent
    #+-----------------------------------------------------------------------+
    def isValid(self, receivedSymbol):
        return True
    
 
    
    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Wait for the reception of a messag
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, abstractionLayer):
        self.activate()
        self.log.debug("Execute as a client")
        self.deactivate()
        return self.outputState
    
    #+-----------------------------------------------------------------------+
    #| executeAsMaster
    #|     Send input symbol and waits to received one of the output symbol
    #| @param input method access to the input flow
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsMaster(self, abstractionLayer):
        self.activate()
        self.log.debug("Execute as a master")
        # write a message
        abstractionLayer.writeSymbol(self.outputSymbol)
        
        # listen for input symbol for fex secondes
        abstractionLayer.receiveSymbolWithTimeout(3)
        
        self.deactivate()
        return self.outputState
     
    
    def getDescription(self):
        outputSymbolId = self.getOutputSymbol().getID()
         
        return "(" + str(outputSymbolId) + ";{after " + str(self.timeBeforeSending) + "})"
    
    #+-----------------------------------------------------------------------+
    #| toXMLString
    #|     Abstract method to retrieve the XML definition of current transition
    #| @return String representation of the XML
    #+-----------------------------------------------------------------------+
    def toXMLString(self, idStartState):
        return None
    
    #+-----------------------------------------------------------------------+
    #| parse
    #|     Extract from an XML declaration the definition of the transition
    #| @param dictionary the dictionary which is used in the current MMSTD 
    #| @param states the states already parsed while analyzing the MMSTD
    #| @return the instanciated object declared in the XML
    #+-----------------------------------------------------------------------+
    @staticmethod
    def parse(xmlTransition, dictionary, states):
        return None
