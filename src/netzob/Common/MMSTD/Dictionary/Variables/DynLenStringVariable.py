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
import hashlib
import binascii
import random
import string

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from ..Variable import Variable
from ....TypeConvertor import TypeConvertor


#+---------------------------------------------------------------------------+
#| DynLenStringVariable :
#|     Definition of a dynamic sized string variable defined in a dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class DynLenStringVariable(Variable):
    
    def __init__(self, id, name, idVar):
        Variable.__init__(self, id, name, "DynLenString")
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.WordVariable.py')
        self.idVar = idVar
        self.binVal = None
        self.strVal = None
            
    def getValue(self, negative, dictionary):
        return (self.binVal, self.strVal)
        
   
    def generateValue(self, negative, dictionary):
        
        variable = dictionary.getVariableByID(self.idVar)
        (binValue, strValue) = variable.getValue(negative, dictionary)
        
        self.log.info("GENERATE VALUE of size : " + str(binValue))
        nb_letter = int(binValue.tostring(), 16)
        self.strVal = ''.join(random.choice(string.ascii_letters) for x in range(nb_letter))
        self.binVal = TypeConvertor.ascii2bin(self.strVal, 'big')
        self.log.info("Generated value = " + self.strVal)
        self.log.info("Generated value = " + str(self.binVal))
        
        
        
    
    def learn(self, val, indice, isForced, dictionary):
        self.log.info("LEARN")
        return -1
   
   
