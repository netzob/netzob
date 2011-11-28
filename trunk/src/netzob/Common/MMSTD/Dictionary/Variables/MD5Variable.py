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
import hashlib

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable import Variable
from netzob.Common.TypeConvertor import TypeConvertor

#+---------------------------------------------------------------------------+
#| MD5Variable :
#|     Definition of an md5 variable defined in a dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class MD5Variable(Variable):
    
    def __init__(self, id, name, init, id_var):
        Variable.__init__(self, id, name, "MD5")
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.HexVariable.py')
        self.init = init
        self.id_var = id_var
        self.binVal = None
        self.strVal = None
        
    def getValue(self, negative, dictionary):
        return (self.binVal, self.strVal)
        
   
    def generateValue(self, negative, dictionary):
        # Retrieve the value of the data to hash
        var = dictionary.getVariableByID(self.id_var)
        (binToHash, strToHash) = var.getValue(negative, dictionary)
        
        toHash = TypeConvertor.bin2ascii(binToHash)
        self.log.debug("Will hash the followings : " + toHash)
        
        md5core = hashlib.md5(self.init)
        md5core.update(toHash)
        
        md5Hex = md5core.digest()
        self.binVal = TypeConvertor.hex2bin(md5Hex)
        self.strVal = TypeConvertor.bin2strhex(self.binVal)
        self.log.debug("Generated MD5 = " + self.strVal)
    
    def learn(self, val, indice, isForced, dictionary):
        
        if self.strVal == None or isForced :
            tmp = val[indice:]
            self.log.debug("Taille MD5 " + str(len(tmp)))
            # MD5 size = 16 bytes = 16*8 = 128
            if (len(tmp) >= 128) :
                binVal = tmp[0:128]
                # We verify its realy the MD5
                var = dictionary.getVariableByID(self.id_var)
                (binToHash, strToHash) = var.getValue(False, dictionary)
                
                toHash = TypeConvertor.bin2ascii(binToHash)
                self.log.debug("Will hash the followings : " + toHash)
                
                md5core = hashlib.md5(self.init)
                md5core.update(toHash)
                
                md5Hex = md5core.digest()
                
                self.log.debug("We should received an MD5 = " + str(TypeConvertor.hex2bin(md5Hex)))
                self.log.debug("We have received " + str(binVal))
                
                if (TypeConvertor.hex2bin(md5Hex) == binVal) :
                    self.binVal = TypeConvertor.hex2bin(md5Hex)
                    self.strVal = TypeConvertor.bin2strhex(self.binVal)
                    self.log.debug("Perfect, there are equals we return  " + str(len(binVal)))
                    return indice + len(binVal)
                else :
                    return -1
                
            else :
                return -1
            
        
        self.log.debug("value = " + str(self.strVal) + ", isForced = " + str(isForced))
        return -1
   
   
