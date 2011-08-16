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
    
    @staticmethod
    def loadFromXML(rootElement):
        
        # First we verify rootElement is a message
        if rootElement.tag != "message" :
            raise NameError("The parsed xml doesn't represent a message.")
        # Then we verify its a Network Message
        if rootElement.get("type", "abstract") != "network" :
            raise NameError("The parsed xml doesn't represent a network message.")
        # Verifies the data field
        if rootElement.find("data") == None or len(rootElement.find("data").text) == 0:
            raise NameError("The parsed message has no data specified")
        
        # Parse the data field and transform it into a byte array
        msg_data = bytearray(rootElement.find("data").text)
        
        # Retrieve the id (default = -1)
        msg_id = rootElement.get('id', "-1")
        
        if msg_id == "-1" :
            msg_id = str(uuid.uuid4()) 
        
        # Retrieves the timestamp (default = 0 )
        if rootElement.find("timestamp") != None :
            msg_timestamp = rootElement.find("timestamp").text
        else :
            msg_timestamp = 0
        
        # Retrieves the ipSource (default 0.0.0.0)
        if rootElement.find("ipSource") != None :
            msg_ipSource = rootElement.find("ipSource").text
        else :
            msg_ipSource = "0.0.0.0"
            
        # Retrieves the ipTarget (default 0.0.0.0)
        if rootElement.find("ipTarget") != None :
            msg_ipTarget = rootElement.find("ipTarget").text
        else :
            msg_ipTarget = "0.0.0.0"
        
        # Retrieves the protocol (default Unknown)
        if rootElement.find("protocol") != None :
            msg_protocol = rootElement.find("protocol").text
        else :
            msg_protocol = "Unknown"
            
        # Retrieves the l4 source port (default 0)
        if rootElement.find("l4SourcePort") != None :
            msg_l4SourcePort = rootElement.find("l4SourcePort").text
        else :
            msg_l4SourcePort = 0
            
        # Retrieves the l4 target port (default 0)
        if rootElement.find("l4TargetPort") != None :
            msg_l4TargetPort = rootElement.find("l4TargetPort").text
        else :
            msg_l4TargetPort = 0
        
        # Craft the Network Message
        result = NetworkMessage()
        result.setID(msg_id)
        result.setData(msg_data)
        result.setTimestamp(msg_timestamp)
        result.setIPSource(msg_ipSource)
        result.setIPTarget(msg_ipTarget)
        result.setProtocol(msg_protocol)
        result.setL4SourcePort(msg_l4SourcePort)
        result.setL4TargetPort(msg_l4TargetPort)
        
        return result
        
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
  

