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
import binascii
import random
import string

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.Dictionary.Variable import Variable



#+---------------------------------------------------------------------------+
#| WordVariable :
#|     Definition of a word variable defined in a dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class WordVariable(Variable):
    
    def __init__(self, id, name, defaultVar):
        Variable.__init__(self, id, name, "WORD")
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.WordVariable.py')
        if defaultVar == "" or defaultVar == None :
            self.binVal = None
            self.strVal = None
        else :
            self.strVal = defaultVar
            self.binVal = self.ascii2bin(self.strVal)
            
    def getValue(self, negative, dictionary):
        return (self.binVal, self.strVal)
        
    
    def ascii2bin(self, ascii):
        chars = []
        for c in ascii :
            v = str(hex(ord(c))).replace("0x", "")
            if len(str(v)) != 2 : 
                v = "0" + str(v)
            chars.append(v)
        return ''.join(chars)
   
    def generateValue(self, negative, dictionary):
        # Generate a WORD value 
        nb_letter = random.randint(0, 10)
        self.strVal = ''.join(random.choice(string.ascii_letters) for x in range(nb_letter))
        self.binVal = self.ascii2bin(self.strVal)
        self.log.debug("Generated : " + self.strVal)
        self.log.debug("Generated -bin )= " + str(self.binVal))
    
    def learn(self, val, indice, isForced, dictionary):
        self.log.debug("Received : " + str(val))
        
        if self.binVal == None or isForced :
            tmp = val[indice:]
            
            res = ""
            i = 0
            finish = False
            while not finish :
                v = int(tmp[i: i + 2], 16)
                if v > 0x21 and v <= 0x7e:
                    res += chr(v)
                    i = i + 2
                else:
                    finish = True
                
            if i > 0 :
                self.strVal = res
                self.binVal = binascii.unhexlify(self.strVal)
#                
#                
#                
#                self.log.debug("value = " + str(self.strVal) + ", isForced = " + str(isForced))
#                
#                tmp = ""
#                for c in self.strVal :
#                    h = str(hex(ord(c))).replace("0x", "")
#                    if len(h) != 2 :
#                        h = "0" + h
#                    tmp = tmp + h
#                
#                self.binVal = binascii.unhexlify(tmp)
#                
                return indice + i
            
        
                
        return -1
   
   
