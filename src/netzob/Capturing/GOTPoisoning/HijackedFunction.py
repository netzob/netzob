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

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from ...Common import ConfigurationParser

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| HijackedFunction :
#|     Definition of a function to hijack
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| A function to hijack has the following members :
#|     - a name
#|     - a return type
#|     - a set of parameter 
#+---------------------------------------------------------------------------+
class HijackedFunction():
    def __init__(self, name, returnType, parameters):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Capturing.GOTPoisoning.HijackedFunction.py')
        self.name = name
        self.returnType = returnType
        self.parameters = parameters
        self.source = ""
    
    
    def getSource(self):
        return self.source


    def getEndOfFunction(self):
        # add the return part of the function
        source = "\t" + self.returnType + " (*origfunc)("
        i = 0
        params = ""
        for param in self.parameters :
            params += param + " param" + str(i)
            if i != len(self.parameters) - 1 :
                params += ", "            
            i = i + 1
        source += params + ") = 0x00000000;\n\n"
        
        paramNames = ""
        i = 0
        for param in self.parameters :
            paramNames += "param" + str(i)
            if i != len(self.parameters) - 1 :
                paramNames += ", "    
            i = i + 1
        
        source += "\torigfunc(" + paramNames + ");"
        
        return source
    
    
    #+-----------------------------------------------------------------------+
    #| getPrototype
    #|    returns the official prototype of the function to hijack
    #| @return a string which contains the prototype
    #+-----------------------------------------------------------------------+ 
    def getPrototype(self):
        params = ", ".join(self.parameters)        
        prototype = self.returnType + " " + self.name + " (" + params + ")"
        return prototype
    
    #+-----------------------------------------------------------------------+
    #| getParasitePrototype
    #|    returns the prototype of the parasite of the function to hijack
    #| @return a string which contains the prototype
    #+-----------------------------------------------------------------------+ 
    def getParasitePrototype(self):
        params = ", ".join(self.parameters)        
        prototype = self.returnType + " netzobParasite_" + self.name + " (" + params + ")"
        return prototype
    
    #+-----------------------------------------------------------------------+
    #| getParasiteFunctionDeclaration
    #|    returns the function declaration of the parasite
    #| @return a string which contains the declaration of the function
    #+-----------------------------------------------------------------------+ 
    def getParasiteFunctionDeclaration(self):
        params = ""
        i = 0
        for param in self.parameters :
            params += param + " param" + str(i)
            if i != len(self.parameters) - 1 :
                params += ", "            
            i = i + 1
        
        functionDeclaration = self.returnType + " netzobParasite_" + self.name + " (" + params + ")"
        return functionDeclaration
    
    #+------------------------------------------------------------------------
    #| GETTERS AND SETTERS
    #+------------------------------------------------------------------------
    def getName(self):
        return self.name
    def getReturnType(self):
        return self.returnType
    def getParameters(self):
        return self.parameters
    
    def setName(self, name):
        self.name = name 
    def setReturnType(self, returnType):
        self.returnType = returnType
    def setParameters(self, parameters):
        self.parameters = parameters
    def setSource(self, source):
        self.source = source
        

