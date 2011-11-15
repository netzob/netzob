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
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| DictionarySymbol :
#|     Definition of a symbol based on a dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class DictionarySymbol():
    
    def __init__(self, dictionaryEntry):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Symbols.impl.DictionarySymbol.py')
        self.entry = dictionaryEntry
        
    
    def isEquivalent(self, symbol):
        if self.entry.getID() == symbol.getID() :
            self.log.info("The symbols are equivalents")
            return True
        else :
            self.log.info("The symbols are not equivalents")
            return False
    
    def getValueToSend(self, dictionary):
        result = self.entry.send(False, dictionary)
        return result
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.entry.getID()
    def getEntry(self):
        return self.entry
  
        
    def setID(self, id):
        self.id = id
    def setEntry(self, entry):
        self.entry = entry
    
    def __str__(self):
        return str(self.entry)
