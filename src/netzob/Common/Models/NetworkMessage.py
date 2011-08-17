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
    
    #+-----------------------------------------------------------------------+
    #| saveInXML
    #|     Abstract method for the generation of an XML representation of
    #|     a message
    #| @return a string which include the xml definition of the network msg
    #+-----------------------------------------------------------------------+    
    def saveInXML(self):
        root = ElementTree.Element("message")
        root.set("type", "network")
        root.set("id", self.getID())
        # timestamp
        subTimestamp = ElementTree.SubElement(root, "timestamp")
        subTimestamp.text = str(self.getTimestamp())
        # ipSource
        subIpSource = ElementTree.SubElement(root, "ipSource")
        subIpSource.text = self.getIPSource()
        # ipTarget
        subIpTarget = ElementTree.SubElement(root, "ipTarget")
        subIpTarget.text = self.getIPTarget()
        # protocol
        subProtocol = ElementTree.SubElement(root, "protocol")
        subProtocol.text = self.getProtocol()
        # l4 source port
        subL4SourcePort = ElementTree.SubElement(root, "l4SourcePort")
        subL4SourcePort.text = str(self.getL4SourcePort())
        # l4 target port
        subL4TargetPort = ElementTree.SubElement(root, "l4TargetPort")
        subL4TargetPort.text = str(self.getL4TargetPort())
        # data
        subData = ElementTree.SubElement(root, "data")
        subData.text = str(self.getData())
        return ElementTree.tostring(root)
        
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
  

