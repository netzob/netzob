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
#| Local application imports
#+---------------------------------------------------------------------------+
from ... import ConfigurationParser

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| AbstractState :
#|     Definition of a state
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class AbstractState():
    
    def __init__(self, id, name):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.States.AbstractState.py')
        self.id = id
        self.name = name
        self.active = False
    
    #+-----------------------------------------------------------------------+
    #| getTransitions
    #|     Abstract method to retrieve the associated transitions
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def getTransitions(self):
        self.log.error("The state class doesn't support 'getTransitions'.")
        raise NotImplementedError("The state class doesn't support 'getTransitions'.")
    
    #+-----------------------------------------------------------------------+
    #| registerTransition
    #|     Abstract method to register a new transition to current state
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def registerTransition(self, transition):
        self.log.error("The state class doesn't support 'registerTransition'.")
        raise NotImplementedError("The state class doesn't support 'registerTransition'.")
    
    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Abstract method to execute the current state as a client given the
    #|     the input and the output method access
    #| @param input method access to the input flow
    #| @param output method access to the output flow
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, input, output):
        self.log.error("The state class doesn't support 'executeAsClient'.")
        raise NotImplementedError("The state class doesn't support 'executeAsClient'.")
    
    #+-----------------------------------------------------------------------+
    #| executeAsServer
    #|     Abstract method to execute the current state as a server given the
    #|     the input and the output method access
    #| @param input method access to the input flow
    #| @param output method access to the output flow
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def executeAsServer(self, input, output):
        self.log.error("The state class doesn't support 'executeAsServer'.")
        raise NotImplementedError("The state class doesn't support 'executeAsServer'.")
    
    #+-----------------------------------------------------------------------+
    #| toXMLString
    #|     Abstract method to retrieve the XML definition of current state
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def toXMLString(self):
        self.log.error("The state class doesn't support 'toXMLString'.")
        raise NotImplementedError("The state class doesn't support 'toXMLString'.")
    
    
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
    
    