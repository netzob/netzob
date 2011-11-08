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
import socket
import random
import binascii
from random import choice
import string
#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+


#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from ... import ConfigurationParser

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
#loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
#logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| Variable :
#|     Definition of a variable defined in a dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class Variable():
    
    def __init__(self, id, name, type):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.py')
        self.id = id
        self.name = name
        self.type = type
 
 
    def getValue(self, negative, dictionary):
        self.log.error("Error, the current value (declared as " + self.type + ") do not support function getValue")
        raise NotImplementedError("The current variable doesn't support 'getValue'.")
 
        
#    def learn(self, val, indice):
#        if self.type == "Word" :
#            return self.learnAsWord(val, indice)
#        elif self.type == "IP" :
#            return self.learnAsIP(val, indice)
#        elif self.type == "HEX" :
#            return self.learnAsHex(val, indice)
#        else :
#            self.log.warn("Impossible to learn, the type " + self.type + " is not yet supported")
#        return -1
#    
#    def learnAsHex(self, val, indice):
#        if self.parameters != None  and 'size' in self.parameters :
#            size = int(self.parameters['size'])
#            
#            tmp = val[indice:]
#            self.log.info("Learn hex given its size : " + str(size) + " from " + tmp)
#            if len(tmp) >= size :
#                self.value = val[indice:indice + size]
#                self.log.info("learning value : " + self.value)
#                return indice + size
#                
#            else :
#                return -1
#            
#        
#    
#    def learnAsWord(self, val, indice):        
#        tmp = val[indice:]
#        
#        i = tmp.find(" ")
#        self.log.info("Learn word from " + tmp + " i=" + str(i))
#        if i > 0 :
#            self.value = val[indice:indice + i]
#            return indice + i
#        elif i == -1 and len(tmp) > 0:
#            self.value = tmp
#            return indice + len(tmp)
#        else :
#            return -1
#    def learnAsIP(self, val, indice):
#        self.log.info("Learn IP from " + val[indice:])
#        for i in range(len(val[indice:]), 0, -1) :
#            tmp = val[indice:indice + i]
#            self.log.info("Tries to learn " + tmp + " (i=" + str(i) + ") as an IP")
#            try: 
#                socket.inet_aton(tmp)
#            except socket.error: 
#                pass
#            else:
#                if tmp.count('.') == 3 :
#                    self.log.info("Value learnt is " + tmp)
#                    self.value = tmp
#                    return indice + len(tmp)
#                
#
#    
#    def generateValue(self):
#        if self.type == "Word" :
#            self.generateWordValue()
#        elif self.type == "IP" :
#            self.generateIPValue()
#    
#    def generateIPValue(self):        
#        elt1 = str(random.randint(0, 255))
#        elt2 = str(random.randint(0, 255))
#        elt3 = str(random.randint(0, 255))
#        elt4 = str(random.randint(0, 255))
#        self.value = elt1 + "." + elt2 + "." + elt3 + "." + elt4
#    
#    def generateWordValue(self):
#        length = random.randint(5, 8)
#        self.value = ''.join([choice(string.letters + string.digits) for i in range(length)])
#        
#    
#    def getBinaryValue(self, negative):
#        if self.type == "HEX" :
#            return self.transformHexToBinary(self.getValue(negative))
#        elif self.type == "MD5" :
#            return self.transformHexToBinary(self.getValue(negative))
#        else :
#            self.log.warn("Impossible to retrieve the binary value of the variable (no type transformator available for " + self.type + ")")
#            return self.getValue(negative)
#        
#    #+-----------------------------------------------------------------------+
#    #| TYPES TRANSFORMATORS
#    #+-----------------------------------------------------------------------+
#    #+---------------------------------------------- 
#    #| Transform the current hex message ( '1fdf' ) in binary ( '\x1f\xdf' )
#    #+---------------------------------------------
#    def transformHexToBinary(self, msg):
#        return binascii.unhexlify(msg)
#        
    
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
    
    
