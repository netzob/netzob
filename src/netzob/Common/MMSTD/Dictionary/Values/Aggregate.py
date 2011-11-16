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
#| Configuration of the logger
#+---------------------------------------------------------------------------+
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| Aggregate :
#|     Definition of an aggregation
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class Aggregate(AbstractValue):
    
    def __init__(self):
        AbstractValue.__init__(self, "Aggregate")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Values.Aggregate.py')
        
        self.values = []
        
    def registerValue(self, value):
        self.values.append(value)
    
    def send(self, negative, dictionary):
        binResult = bitarray(endian='big')
        strResult = []
        for value in self.values :
            (binVal, strVal) = value.send(negative, dictionary)
            self.log.info("Aggregate : " + str(binVal))
            self.log.info("Aggregate : " + str(strVal))
            binResult.extend(binVal)
            strResult.append(strVal)
            
        return (binResult, "".join(strResult))         
    
    def compare(self, val, indice, negative, dictionary):
        result = indice
        self.log.info("Will compare with :")        
        for value in self.values :
            self.log.info(str(value.getType()))
        
        for value in self.values :
            self.log.info("Indice = " + str(result) + " : " + value.getType())
            result = value.compare(val, result, negative, dictionary)
            if result == -1 or result == None :
                self.log.info("Compare fail")
                return -1
            else :
                self.log.info("Compare successfull")
        
        return result
    
    def restore(self):
        for value in self.values :
            value.restore()
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id
    def getName(self):
        return self.name
    def getType(self):
        return self.type

        
    def setID(self, id):
        self.id = id
    def setName(self, name):
        self.name = name
    def setType(self, type):
        self.type = type
    
    
