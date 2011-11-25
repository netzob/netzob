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
from .... import ConfigurationParser
from .AbstractValue import AbstractValue
from ....TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| TextValue :
#|     Represents a text value
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class TextValue(AbstractValue):
    
    def __init__(self, text):
        AbstractValue.__init__(self, "TextValue")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Values.TextValue.py')
        
        self.strtext = text
        self.bintext = TypeConvertor.ascii2bin(self.strtext, 'big')
        
    def send(self, negative, dictionary):
        return (self.bintext, self.strtext)
        
    def compare(self, val, indice, negative, dictionary):
        self.log.debug("Compare received : '" + str(val[indice:]) + "' with '" + str(self.bintext) + "' ")
        
        tmp = val[indice:]
        if len(tmp) >= len(self.bintext) :
            if tmp[:len(self.bintext)] == self.bintext :
                self.log.debug("Compare successful")
                return indice + len(self.bintext)                                
        else :
            self.log.debug("Compare fail")
            return -1
     
    
    def restore(self):
        return
    
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
  
    
    
