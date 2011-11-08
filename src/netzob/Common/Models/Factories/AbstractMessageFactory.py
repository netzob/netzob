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
from ... import ConfigurationParser
from netzob.Common.Models.Factories.FileMessageFactory import FileMessageFactory
from netzob.Common.Models.Factories.NetworkMessageFactory import NetworkMessageFactory
from netzob.Common.Models.Factories.IPCMessageFactory import IPCMessageFactory

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| AbstractMessageFactory :
#|     Factory dedicated to the manipulation of file messages
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class AbstractMessageFactory():
    
    @staticmethod
    #+-----------------------------------------------------------------------+
    #| saveInXML
    #|     Generate an XML representation of a message
    #| @return a string which include the xml definition of the msg
    #+-----------------------------------------------------------------------+
    def saveInXML(message):
        if message.getType() == "File" :
            return FileMessageFactory.saveInXML(message)
        elif message.getType() == "Network" :
            return NetworkMessageFactory.saveInXML(message)
        elif message.getType() == "IPC" :
            return IPCMessageFactory.saveInXML(message)
        else :
            raise NameError('''There is no factory which would support 
            the generation of an xml representation of the message : ''' + str(message))
    
    
    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of a file message
    #| @param rootElement: XML root of the file message 
    #| @return an instance of a FipSource (default 0.0.0.0)ileMessage
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement):        
        # First we verify rootElement is a message
        if rootElement.tag != "message" :
            raise NameError("The parsed xml doesn't represent a message.")
        # Computes which type is it
        if rootElement.get("type", "abstract") == "abstract" :
            raise NameError("The parsed xml doesn't represent a valid type message.")
        
        if rootElement.get("type", "abstract") == "file" :
            return FileMessageFactory.loadFromXML(rootElement)
        if rootElement.get("type", "abstract") == "network" :
            return NetworkMessageFactory.loadFromXML(rootElement)
        if rootElement.get("type", "abstract") == "IPC" :
            return IPCMessageFactory.loadFromXML(rootElement)
        else :
            raise NameError("The parsed xml doesn't represent a valid type message.")
            return None
        
