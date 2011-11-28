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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Models.AbstractMessage import AbstractMessage
from netzob.Common.Models.Factories.IPCMessageFactory import IPCMessageFactory

#+---------------------------------------------------------------------------+
#| IPCMessage :
#|     Definition of an IPC message
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class IPCMessage(AbstractMessage):
    def __init__(self):
        AbstractMessage.__init__(self, "IPC")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.IPCMessage.py')
    
    #+-----------------------------------------------------------------------+
    #| getFactory
    #| @return the associated factory
    #+-----------------------------------------------------------------------+
    def getFactory(self):
        return IPCMessageFactory
    
    #+-----------------------------------------------------------------------+
    #| getProperties
    #|     Computes and returns the properties of the current message
    #| @return an array with all the properties [[key,val],...]
    #+-----------------------------------------------------------------------+
    def getProperties(self):
        properties = []        
        properties.append(['ID', str(self.getID())])
        properties.append(['Type', self.getType()])
        properties.append(['Timestamp', self.getTimestamp()])
        properties.append(['Category', self.getCategory()])
        properties.append(['Key', self.getKey()])
        properties.append(['Direction', self.getDirection()])
        properties.append(['Data', self.getStringData()])
        
        return properties   
        
    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getCategory(self):
        return self.category
    def getKey(self):
        return self.key
    def getName(self):
        return self.name
    def getType(self):
        return self.type
    def getDirection(self):
        return self.direction
    def getTimestamp(self):
        return self.timestamp
       
    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------
    def setCategory(self, category):
        self.category = category
    def setKey(self, key):
        self.key = key
    def setName(self, name):
        self.name = name
    def setType(self, type):
        self.type = type
    def setDirection(self, direction):
        self.direction = direction
    def setTimestamp(self, timestamp):
        self.timestamp = timestamp

