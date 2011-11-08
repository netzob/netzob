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
import hashlib
import binascii

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .... import ConfigurationParser
from ..Variable import Variable

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

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
        var = dictionary.getVariableByID(self.id_var)
        (binToHash, strToHash) = var.getValue(negative, dictionary)
        
        md5core = hashlib.md5(self.init)
        md5core.update(binToHash)
        md5 = md5core.hexdigest()
        self.binVal = binascii.unhexlify(md5)
        self.strVal = md5
    
    def learn(self, val, indice, isForced, dictionary):
        
        if self.strVal == None or isForced :
                tmp = val[indice:]
                if (len(tmp) >= 32) :
                    self.strVal = tmp[0:32]
                    self.binVal = binascii.unhexlify(self.strVal)
                    return indice + 32
                else :
                    return -1
            
        
        self.log.info("value = " + str(self.strVal) + ", isForced = " + str(isForced))
        return -1
   
   
