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
import logging
import os

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
import ConfigurationParser
from netzob.Capturing.GOTPoisoning import HijackedFunction

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| SharedLib :
#|     Model object of a shared lib
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class SharedLib(object):
    #+-----------------------------------------------------------------------+
    #| Constructor
    #| @param name     : name of the lib
    #|        
    #+-----------------------------------------------------------------------+
    def __init__(self, name):
        self.name = name
        self.functions = []
    
    @staticmethod
    def loadFromXML(rootElement):
        # First we verify rootElement is a message
        if rootElement.tag != "lib" :
            raise NameError("The parsed xml doesn't represent a shared lib.")
        # Then we verify its a Network Message
        if rootElement.get("name", "none") == "none" :
            raise NameError("The parsed xml doesn't represent a shared lib with a valid name.")
        
        # parse the name of the lib
        libName = rootElement.get("name", "none")
        
        functions = []
        # parse the declared functions
        for xmlFunc in rootElement.findall("functions//function") :
            function = HijackedFunction.HijackedFunction.loadFromXML(xmlFunc)
            functions.append(function)
        
        
        lib = SharedLib(libName)
        lib.setFunctions(functions)
        
        return lib
        
        
    
    
    
    
        
    def setName(self, name):
        self.name = name
    def getName(self):
        return self.name
    def setFunctions(self, functions):
        self.functions = functions
    def getFunctions(self):
        return self.functions
    
    