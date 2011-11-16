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
from bitarray import bitarray

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
#| IntVariable :
#|     Definition of an int variable defined in a dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class IntVariable(Variable):
    
    
    
    def __init__(self, id, name, size, value):
        Variable.__init__(self, id, name, "INT")
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variables.HexVariable.py')
        self.value = value
        
        self.size = size
        self.min = -1
        self.max = -1   
        self.reset = "normal"    
        if self.value != None :
            self.binValue = TypeConvertor.int2bin(self.value, self.size)
            self.strValue = TypeConvertor.int2ascii(self.value)
        else :
            self.binValue = None
            self.strValue = None
        
        self.binValueBeforeLearning = None
        self.strValueBeforeLearning = None
            
        self.log.info("Bin-value = " + str(self.binValue) + ", str-value = " + str(self.strValue))
        
    def restore(self):
        self.log.info("Restore ...")
        if self.binValueBeforeLearning != None and self.strValueBeforeLearning != None :
            self.log.info("Restore the previsouly learned value")
            self.binValue = self.binValueBeforeLearning
            self.strValue = self.strValueBeforeLearning
        
    def getValue(self, negative, dictionary):
        self.log.info("Getvalue of int")
        return (self.binValue, self.strValue)
        
    
    def generateValue(self, negative, dictionary) :
        self.log.info("Generate value of hex")
        if self.min != -1 and self.max != -1 :
            # generate a value in int
            r = random.randint(self.min, self.max)
            self.log.info("Generating hex of value : " + str(r))
            self.binValue = TypeConvertor.int2bin(r, self.size)
            self.strValue = TypeConvertor.int2ascii(r)
       
    def learn(self, val, indice, isForced, dictionary):
        self.log.info("Learn on " + str(indice) + " : " + str(val[indice:]))
        if self.binValue != None and not isForced :
            self.log.info("Won't learn the hex value (" + self.name + ") since it already has one is not forced to (return " + str(len(self.binValue)) + ")")
            return indice + len(self.binValue)
        
        tmp = val[indice:]
        self.log.info("Learn hex given its size : " + str(self.size) + " from " + str(tmp)) 
        if len(tmp) >= self.size :
            
            self.binValueBeforeLearning = self.binValue
            self.strValueBeforeLearning = self.strValue
            
            self.binValue = val[indice:indice + self.size]
            self.strValue = str(TypeConvertor.bin2int(self.binValue))
            
            self.log.info("learning value : " + str(self.binValue))
            self.log.info("learning value : " + self.strValue)
            
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
