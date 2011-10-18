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
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| Variable :
#|     Definition of a variable defined in a dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class Variable():
    
    def __init__(self, id, name, type, defaultValue):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.Variable.py')
        self.id = id
        self.name = name
        self.value = defaultValue
        self.type = type
        
        
    def learn(self, val, indice):
        if self.type == "Word" :
            return self.learnAsWord(val, indice)
        elif self.type == "IP" :
            return self.learnAsIP(val, indice)
        return -1
    
    def learnAsWord(self, val, indice):        
        tmp = val[indice:]
        
        i = tmp.find(" ")
        self.log.info("Learn word from " + tmp + " i=" + str(i))
        if i > 0 :
            self.value = val[indice:indice + i]
            return indice + i
        elif i == -1 and len(tmp) > 0:
            self.value = tmp
            return indice + len(tmp)
        else :
            return -1
    def learnAsIP(self, val, indice):
        self.log.info("Learn IP from " + val[indice:])
        for i in range(len(val[indice:]), 0, -1) :
            tmp = val[indice:indice + i]
            self.log.info("Tries to learn " + tmp + " (i=" + str(i) + ") as an IP")
            try: 
                socket.inet_aton(tmp)
            except socket.error: 
                pass
            else:
                if tmp.count('.') == 3 :
                    self.log.info("Value learnt is " + tmp)
                    self.value = tmp
                    return indice + len(tmp)
                

    
    def generateValue(self):
        if self.type == "Word" :
            self.generateWordValue()
        elif self.type == "IP" :
            self.generateIPValue()
    
    def generateIPValue(self):        
        elt1 = str(random.randint(0, 255))
        elt2 = str(random.randint(0, 255))
        elt3 = str(random.randint(0, 255))
        elt4 = str(random.randint(0, 255))
        self.value = elt1 + "." + elt2 + "." + elt3 + "." + elt4
    
    def generateWordValue(self):
        length = random.randint(5, 8)
        self.value = ''.join([choice(string.letters + string.digits) for i in range(length)])
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id
    def getName(self):
        return self.name
    def getType(self):
        return self.type
    def getValue(self, negative):
        return self.value
        
    def setID(self, id):
        self.id = id
    def setName(self, name):
        self.name = name
    def setType(self, type):
        self.type = type
    def setValue(self, value):
        self.value = value
    
    
