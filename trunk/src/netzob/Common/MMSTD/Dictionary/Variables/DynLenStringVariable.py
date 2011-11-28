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
import random
import string

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable import Variable
from netzob.Common.TypeConvertor import TypeConvertor


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
        
        self.log.debug("GENERATE VALUE of size : " + str(binValue))
        nb_letter = TypeConvertor.bin2int(binValue)
        self.strVal = ''.join(random.choice(string.ascii_letters) for x in range(nb_letter))
        self.binVal = TypeConvertor.ascii2bin(self.strVal, 'big')
        self.log.debug("Generated value = " + self.strVal)
        self.log.debug("Generated value = " + str(self.binVal))
        
        
        
    
    def learn(self, val, indice, isForced, dictionary):
        self.log.debug("LEARN")
        variable = dictionary.getVariableByID(self.idVar)
        (binValue, strValue) = variable.getValue(False, dictionary)
        nb_letter = TypeConvertor.bin2int(binValue) * 8
        self.log.debug("nb_letter = " + str(nb_letter))
        tmp = val[indice:]
        self.log.debug("tmp size : " + str(len(tmp)))
        if (len(tmp) >= nb_letter) :
            self.binVal = tmp[:nb_letter]
            self.strVal = TypeConvertor.bin2ascii(self.binVal)
            self.log.debug("Value learnt : " + self.strVal)
            return indice + nb_letter
        
        
        return -1
   
   
