#!/usr/bin/ python
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

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
from ..Common import Message
from ..Common import ConfigurationParser
from netzob.Common.Models.Factories.AbstractMessageFactory import AbstractMessageFactory

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| TraceParser :
#|     parse the content of a trace file and retrives all the messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class TraceParser(object):
    #+---------------------------------------------- 
    #| Constructor :NeedemanWunsch
    #| @param path: path of the file to parse 
    #+----------------------------------------------   
    def __init__(self, path):
        self.path = path
        self.messages = []
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.TraceParser.py')
        
        
       
    #+---------------------------------------------- 
    #| Parse :  
    #+----------------------------------------------   
    def parse(self):
        self.log.info("Extract traces from file {0}".format(self.path))
        
        tree = ElementTree.ElementTree()
        tree.parse(self.path)
        xmlMessages = tree.findall("message")
        for xmlMessage in xmlMessages:
            message = AbstractMessageFactory.loadFromXML(xmlMessage)
            
#            
#            # create a new message for each entry
#            message = Message.Message()
#            message.setProtocol(xmlMessage.attributes["proto"].value)
#            message.setIPSource(xmlMessage.attributes["sourceIp"].value)
#            message.setIPTarget(xmlMessage.attributes["targetIp"].value)
#            message.setL4SourcePort(xmlMessage.attributes["sourcePort"].value)
#            message.setL4TargetPort(xmlMessage.attributes["targetPort"].value)
#            message.setTimestamp(xmlMessage.attributes["timestamp"].value)
#            for node in xmlMessage.childNodes:
#                message.setData(node.data.split())

            self.messages.append(message)     
        
        self.log.info("Found : {0} messages ".format(len(self.messages)))
        return self.messages  
        
