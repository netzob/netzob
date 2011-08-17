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
import array
import binascii
import logging.config
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .. import ConfigurationParser
from .AbstractMessage import AbstractMessage

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| NetworkMessage :
#|     Definition of a network message
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| XML Definition :
#| <message type="network" id="">
#|     <timestamp></timestamp>
#|     <ipSource></ipSource>
#|     <ipTarget></ipTarget>
#|     <protocol></protocol>
#|     <l4SourcePort></l4SourcePort>
#|     <l4TargetPort></l4TargetPort>
#|     <data></data>
#| </message>
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
class NetworkMessage(AbstractMessage):
    
    def __init__(self):
        AbstractMessage.__init__(self, "Network")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.NetworkMessage.py')
    
    
        
#+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getProtocol(self):
        return self.protocol
    def getIPSource(self):
        return self.ipSource
    def getIPTarget(self):
        return self.ipTarget
    def getL4SourcePort(self):
        return self.l4SourcePort
    def getL4TargetPort(self):
        return self.l4TargetPort
    def getTimestamp(self):
        return self.timestamp
       
    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------
    def setProtocol(self, protocol):
        self.protocol = protocol
    def setIPSource(self, ipSource):
        self.ipSource = ipSource
    def setIPTarget(self, ipTarget):
        self.ipTarget = ipTarget
    def setL4SourcePort(self, l4sourcePort):
        try :
            self.l4SourcePort = int(l4sourcePort)
        except :
            self.log.warning("Impossible to set the given L4 source port since its not an int !")
            
    def setL4TargetPort(self, l4targetPort):
        try :
            self.l4TargetPort = int(l4targetPort)
        except :
            self.log.warning("Impossible to set the given L4 target port since its not an int !")
        
    def setTimestamp(self, timestamp):
        self.timestamp = timestamp
  

