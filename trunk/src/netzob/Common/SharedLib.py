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
import string

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Import.GOTPoisoning import HijackedFunction


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
    #| @param version  : version of the lib
    #| @param path     : full path of the lib
    #+-----------------------------------------------------------------------+
    def __init__(self, name, version, path):
        self.name = name
        self.version = version
        self.path = path
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
        libVersion = rootElement.get("version", "0.0")
        
        
        functions = []
        # parse the declared functions
        for xmlFunc in rootElement.findall("functions//function") :
            function = HijackedFunction.HijackedFunction.loadFromXML(xmlFunc)
            functions.append(function)
        
        
        lib = SharedLib(libName, libVersion, "")
        lib.setFunctions(functions)
        
        return lib
        
        
    
    @staticmethod
    def findNameAndVersion(path):
        
        nameWithoutPath = path.split("/")[len(path.split("/")) - 1]
        
        # Remove the extension
        if (len(nameWithoutPath) > 3 and nameWithoutPath[len(nameWithoutPath) - 3:] == ".so") :
            nameWithoutPath = nameWithoutPath[:len(nameWithoutPath) - 3]
        
        libName = nameWithoutPath
        libVersion = "0.0"   
        
        # find version number
        try :
            if (string.index(nameWithoutPath, "-") > 1) :
                libName = nameWithoutPath[:nameWithoutPath.index("-")]    
                libVersion = nameWithoutPath[nameWithoutPath.index("-") + 1:]   
        except :
            pass
            
        
        return (libName, libVersion)
    
    
        
    def setName(self, name):
        self.name = name
    def getName(self):
        return self.name
    def getVersion(self):
        return self.version
    def setVersion(self, version):
        self.version = version
    def getPath(self):
        return self.path
    def setPath(self, path):    
        self.path = path
    def setFunctions(self, functions):
        self.functions = functions
    def getFunctions(self):
        return self.functions
    
    
