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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from ..AbstractState import AbstractState
#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| NormalState :
#|     Definition of a normal state
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class NormalState(AbstractState):
    
    def __init__(self, id, name):
        AbstractState.__init__(self, id, name)
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.States.impl.NormalState.py')
        self.transitions = []
    
    #+-----------------------------------------------------------------------+
    #| getTransitions
    #|     Return the associated transitions
    #| @return the transitions
    #+-----------------------------------------------------------------------+
    def getTransitions(self):
        return self.transitions
    
    #+-----------------------------------------------------------------------+
    #| registerTransition
    #|     Associate a new transition ot the current state
    #| @param transition the transition to associate
    #+-----------------------------------------------------------------------+
    def registerTransition(self, transition):
        self.transitions.append(transition)
    
    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Execute the state as a client
    #| @param abstractionLayer the layer between the MMSTD and the world
    #| @return the next state after execution of current one
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, abstractionLayer):
        self.log.info("Execute state " + self.name + " as a client")
        
        # Wait for a message
        receivedSymbol = abstractionLayer.receiveSymbol()
        if not receivedSymbol == None :
            self.log.info("The following symbol has been received : " + receivedSymbol.getName())
#        
#        # Abstraction of the message into symbols
#        
#        
#        
#        
#        for transition in self.getTransitions() :
#            if transition.isValid(receivedData) :
#                self.log.info("Received data " + receivedData + " is valid for transition " + transition.getID())
#                newState = transition.executeAsClient(input, output)
#                return newState
#        self.log.info("Error, the received data is not valid")
        
        
        
        
        
        
        
        return self
    
    #+-----------------------------------------------------------------------+
    #| executeAsServer
    #|     Execute the state as a server
    #| @param abstractionLayer the layer between the MMSTD and the world
    #| @return the next state after execution of current one
    #+-----------------------------------------------------------------------+
    def executeAsServer(self, abstractionLayer):
        self.log.info("Execute state " + self.name + " as a server")
        return self
    
    #+-----------------------------------------------------------------------+
    #| toXMLString
    #|     Return the xml definition of a normal state
    #| @return the XML definition of the state
    #+-----------------------------------------------------------------------+
    def toXMLString(self):
        root = ElementTree.Element("state")
        root.set("id", int(self.id))
        root.set("name", self.name)
        root.set("class", "NormalState")
        return ElementTree.tostring(root)
    
    
    #+-----------------------------------------------------------------------+
    #| active
    #|    active the current state
    #+-----------------------------------------------------------------------+
    def activate(self):
        self.active = True
    #+-----------------------------------------------------------------------+
    #| deactivate
    #|    deactivate the current state
    #+-----------------------------------------------------------------------+
    def deactivate(self):
        self.active = False
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id
    def getName(self):
        return self.name
    def isActive(self):
        return self.active
        
    def setID(self, id):
        self.id = id
    def setName(self, name):
        self.name = name
    
    
