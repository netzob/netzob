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
import logging.config
import uuid

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .. import ConfigurationParser
from . import AbstractMessage

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

 self.protocol = ""
        self.ipSource = ""
        self.ipTarget = ""
        self.l4SourcePort = -1
        self.l4TargetPort = -1
        self.timestamp = -1
        self.data = ""
#+---------------------------------------------------------------------------+
class NetworkMessage(AbstractMessage):
    
    def __init__(self, type,):
        AbstractMessage.__init__(self, "Network")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.NetworkMessage.py')
        

   
        
  

