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
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| AbstractTransition :
#|     Definition of a transition
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class AbstractTransition():
    #+-----------------------------------------------------------------------+
    #| WARNING :
    #|     it does not register the transition on the input state !!!!!!!
    #+-----------------------------------------------------------------------+
    def __init__(self, type, id, name, inputState, outputState):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Transitions.AbstractTransition.py')
        self.type = type
        self.id = id
        self.name = name
        self.outputState = outputState
        self.inputState = inputState
        self.active = False
    
    #+-----------------------------------------------------------------------+
    #| isValid
    #|     Abstract method to compute if current transition is valid with
    #|     given input symbol 
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def isValid(self, inputSymbol):
        self.log.error("The transition class doesn't support 'isValid'.")
        raise NotImplementedError("The transition class doesn't support 'isValid'.")
    
    #+-----------------------------------------------------------------------+
    #| executeAsClient
    #|     Abstract method to execute the current transition as a client given the
    #|     the input and the output method access
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def executeAsClient(self, abstractionLayer):
        self.log.error("The transition class doesn't support 'executeAsClient'.")
        raise NotImplementedError("The transition class doesn't support 'executeAsClient'.")
    
    #+-----------------------------------------------------------------------+
    #| executeAsMaster
    #|     Abstract method to execute the current transition as a server given the
    #|     the input and the output method access
    #| @param abstractionLayer the abstract layer to contact in order to reach outside world
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def executeAsMaster(self, abstractLayer):
        self.log.error("The transition class doesn't support 'executeAsMaster'.")
        raise NotImplementedError("The transition class doesn't support 'executeAsMaster'.")
    
    #+-----------------------------------------------------------------------+
    #| getDescription
    #|     computes and return a description for the current transition
    #| @return a string composed of a description
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def getDescription(self):
        self.log.error("The transition class doesn't support 'getDescription'.")
        raise NotImplementedError("The transition class doesn't support 'getDescription'.")
    
    
    #+-----------------------------------------------------------------------+
    #| toXMLString
    #|     Abstract method to retrieve the XML definition of current transition
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def toXMLString(self, idStartState):
        self.log.error("The transition class doesn't support 'toXMLString'.")
        raise NotImplementedError("The transition class doesn't support 'toXMLString'.")
    
    
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
    def getOutputState(self):
        return self.outputState
    def getInputState(self):
        return self.inputState
    def isActive(self):
        return self.active
    def getType(self):
        return self.type
        
    def setID(self, id):
        self.id = id
    def setName(self, name):
        self.name = name
    def setOutputState(self, outputState):
        self.outputState = outputState
    def setInputState(self, inputState):
        self.inputState = inputState
    
    
