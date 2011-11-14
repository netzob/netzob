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
import random
import time


#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from ..AbstractTransition import AbstractTransition
from ...Symbols.impl.EmptySymbol import EmptySymbol


#+---------------------------------------------------------------------------+
#| OpenChannelTransition :
#|    Special transition in charge of opening the transition
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class OpenChannelTransition(AbstractTransition):
    
    def __init__(self, id, name, inputState, outputState, connectionTime, maxNumberOfAttempt):
        AbstractTransition.__init__(self, id, name, inputState, outputState)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Transitions.impl.OpenChannelTransition.py')
        self.connectionTime = connectionTime
        self.maxNumberOfAttempt = maxNumberOfAttempt
    
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
        result = self.openConnection(abstractionLayer)
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
        result = self.openConnection(abstractionLayer)
        self.deactivate()
        if result :
            return self.outputState
        else :
            return None
        
    #+-----------------------------------------------------------------------+
    #| openConnection
    #|     Open the connection
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #| @return the new state
    #+-----------------------------------------------------------------------+
    def openConnection(self, abstractionLayer):
        self.log.debug("OpenChannelTransition executed.")
        
        i = self.maxNumberOfAttempt
        while (not abstractionLayer.isConnected()  and i > 0) :
            time.sleep(int(self.connectionTime) / 1000)
            abstractionLayer.connect()
            if abstractionLayer.isConnected() :
                self.log.info("Connected !")
            else :
                self.log.warn("Error, the connection attempt failed")
            i = i - 1
        
        if (abstractionLayer.isConnected()) :
            return True
        else :
            self.log.warn("Max connection attempt reached !")
            return False
    
    def getDescription(self):
        return "OpenChannelTransition"
    
    #+-----------------------------------------------------------------------+
    #| toXMLString
    #|     Abstract method to retrieve the XML definition of current transition
    #| @return String representation of the XML
    #+-----------------------------------------------------------------------+
    def toXMLString(self, idStartState):
        root = ElementTree.Element("transition")
        root.set("id", int(self.getID()))
        root.set("name", self.name)
        root.set("class", "OpenChannelTransition")
        root.set("idStart", int(idStartState))
        root.set("idEnd", int(self.outputState.getID()))
        root.set("connectionTime", self.connectionTime)
        root.set("maxNumberOfAttempt", self.maxNumberOfAttempt)                                  
                 
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
        
        connectionTime = int(xmlTransition.get("connectionTime", "0"))
        maxNumberOfAttempt = int(xmlTransition.get("maxNumberOfAttempt", "1"))
        
        
        

        transition = OpenChannelTransition(idTransition, nameTransition, inputStateTransition, outputStateTransition, connectionTime, maxNumberOfAttempt)
        inputStateTransition.registerTransition(transition)
        return transition
