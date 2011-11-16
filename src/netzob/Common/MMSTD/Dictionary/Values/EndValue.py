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
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from .AbstractValue import AbstractValue

#+---------------------------------------------------------------------------+
#| EndValue :
#|     Represents the end of a symbol
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class EndValue(AbstractValue):
    
    def __init__(self):
        AbstractValue.__init__(self, "EndValue")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Values.EndValue.py')
        
    
    def send(self, negative, dictionary):
        return (bitarray(endian='big'), "")
    
    def compare(self, val, indice, negative, dictionary):
        self.log.info("Endvalue ? indice = " + str(indice))
        if len(val[indice:]) == 0 :
            self.log.info("Compare successful (" + str(indice) + " != " + str(len(val)) + ")")
            return indice
        else :
            cr = bitarray('00001010', endian='big')
            
            if val[indice:] == cr :
                self.log.info("Compare successfull we consider \\n as the end")
                return indice + len(cr)
                
            self.log.info("Compare Fail, received '" + str(val[indice:]) + "'")
            return -1
        
    def restore(self):
        return
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
  
    
    
