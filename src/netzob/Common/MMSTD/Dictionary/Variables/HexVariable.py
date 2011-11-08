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
import binascii
import random

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
#| HexVariable :
#|     Definition of an hex variable defined in a dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class HexVariable(Variable):
    
    def __init__(self, id, name, value):
        Variable.__init__(self, id, name, "HEX")
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.HexVariable.py')
        self.value = value
        self.size = -1
        self.min = -1
        self.max = -1   
        self.reset = "normal"     
        
    def getValue(self, negative, dictionary):
        if self.value == None :
            return (None, None)
                    
        return (binascii.unhexlify(self.value), self.value)
    
    def generateValue(self, negative, dictionary) :
        if self.min != -1 and self.max != 1 :
            r = random.randint(self.min, self.max)
            v = str(hex(r)).replace("0x", "")
            if (len(v) % 2 == 1) :
                v = "0" + v
            self.value = v
       
    def learn(self, val, indice, isForced, dictionary):
        
        if self.value != None and not isForced :
            self.log.info("Won't learn the hex value (" + self.name + ") since it already has one is not forced to (return " + str(len(self.value)) + ")")
            return indice + len(self.value)
        
        tmp = val[indice:]
        self.log.info("Learn hex given its size : " + str(self.size) + " from " + tmp) 
        if len(tmp) >= self.size :
            self.value = val[indice:indice + self.size]
            self.log.info("learning value : " + self.value)
            return indice + self.size
        else :
            return -1

    def setReset(self, reset) :
        self.reset = reset
    def setSize(self, size):
        self.size = size
    def setMin(self, min):
        self.min = int(min)
    def setMax(self, max):
        self.max = int(max) 
