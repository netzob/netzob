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
import logging
import time


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Transitions.AbstractTransition import AbstractTransition


#+---------------------------------------------------------------------------+
#| CloseChannelTransition :
#|    Special transition in charge of closing the transition
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class CloseChannelTransition(AbstractTransition):
    
    def __init__(self, id, name, inputState, outputState, disconnectionTime):
        AbstractTransition.__init__(self, "CloseChannel", id, name, inputState, outputState)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Transitions.impl.CloseChannelTransition.py')
        self.disconnectionTime = disconnectionTime
    
    #+-----------------------------------------------------------------------+
    #| isValid
    #|     Computes if the received symbol is valid
    #| @return a boolean which indicates if received symbol is equivalent
    #+-----------------------------------------------------------------------+
    def isValid(self, receivedSymbol):
        return True
    
    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Open the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, abstractionLayer):
        self.activate()        
        result = self.closeConnection(abstractionLayer)
        self.deactivate()
        if result :
            return self.outputState
        else :
            return None
        
    #+-----------------------------------------------------------------------+
    #| executeAsMaster
    #|     Open the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def executeAsMaster(self, abstractionLayer):    
        self.activate()        
        result = self.closeConnection(abstractionLayer)
        self.deactivate()
        if result :
            return self.outputState
        else :
            return None
        
    #+-----------------------------------------------------------------------+
    #| closeConnection
    #|     Close the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def closeConnection(self, abstractionLayer):
        self.log.debug("CloseChannelTransition executed.")
        time.sleep(int(self.disconnectionTime) / 1000)
        abstractionLayer.disconnect()
        time.sleep(int(self.disconnectionTime) / 1000)
        return True
    
    def getDescription(self):
        return "CloseChannelTransition"
    
    #+-----------------------------------------------------------------------+
    #| toXMLString
    #|     Abstract method to retrieve the XML definition of current transition
    #| @return String representation of the XML
    #+-----------------------------------------------------------------------+
    def toXMLString(self, idStartState):
        root = ElementTree.Element("transition")
        root.set("id", int(self.getID()))
        root.set("name", self.name)
        root.set("class", "CloseChannelTransition")
        root.set("idStart", int(idStartState))
        root.set("idEnd", int(self.outputState.getID()))
        root.set("disconnectionTime", self.disconnectionTime)                                  
                 
        return ElementTree.tostring(root)

    #+-----------------------------------------------------------------------+
    #| parse
    #|     Extract from an XML declaration the definition of the transition
    #| @param states the states already parsed while analyzing the MMSTD
    #| @return the instanciated object declared in the XML
    #+-----------------------------------------------------------------------+
    @staticmethod
    def parse(xmlTransition, states):
        idTransition = int(xmlTransition.get("id", "-1"))
        nameTransition = xmlTransition.get("name", "none")
            
        idStartTransition = int(xmlTransition.get("idStart", "-1"))
        idEndTransition = int(xmlTransition.get("idEnd", "-1"))
        
        inputStateTransition = None
        outputStateTransition = None
        for state in states :
            if state.getID() == idStartTransition :
                inputStateTransition = state
            if state.getID() == idEndTransition :
                outputStateTransition = state
        
        disconnectionTime = int(xmlTransition.get("disconnectionTime", "0"))

        transition = CloseChannelTransition(idTransition, nameTransition, inputStateTransition, outputStateTransition, disconnectionTime)
        inputStateTransition.registerTransition(transition)
        return transition
