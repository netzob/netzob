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
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from ..AbstractSymbol import AbstractSymbol


#+---------------------------------------------------------------------------+
#| EmptySymbol :
#|     Definition of an empty symbol
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class EmptySymbol(AbstractSymbol):
    
    def __init__(self):
        AbstractSymbol.__init__(self, "EmptySymbol")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Symbols.impl.EmptySymbol.py')
        
    
    def isEquivalent(self, symbol):
        
        if symbol.__class__.__name__ == EmptySymbol.__name__:
            self.log.debug("The symbols are equivalents")
            return True
        else :
            self.log.debug("The symbols are not equivalents")
            return False
    
    def getValueToSend(self, dictionary):
        return (bitarray(endian='big'), "")
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return 0
    def getEntry(self):
        return None
  
  
    def __str__(self):
        return "EmptySymbol"
        
#    def setID(self, id):
#        self.id = id
#    def setEntry(self, entry):
#        self.entry = entry
    
