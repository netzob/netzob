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

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

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
#| DictionaryEntry :
#|     Definition of an entry in a dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class DictionaryEntry():
    
    def __init__(self, id, name, value):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Dictionary.DictionaryEntry.py')
        self.id = id
        self.name = name
        self.value = value
        
    #+---------------------------------------------------------------------------+
    #| generate :
    #|     Generate the value of the entry
    #+---------------------------------------------------------------------------+
    def generate(self):
        self.log.debug("Generate ...")
        self.value.generate()
    
    #+---------------------------------------------------------------------------+
    #| forget :
    #|     Forgets the value of the entry
    #| @param temporary flag indicated the forget operation must be temporary
    #+---------------------------------------------------------------------------+
    def forget(self, temporary):
        self.log.debug("Forget ...")
        self.value.forget(temporary)
    
    #+---------------------------------------------------------------------------+
    #| undoForget :
    #|     Since a forget operation can be temporary, this method allows to 
    #|     reverse it
    #+---------------------------------------------------------------------------+
    def undoForget(self):
        self.log.debug("Undo forget ...")
        self.value.undoForget()
    
    #+---------------------------------------------------------------------------+
    #| send :
    #|     Prepare to send this entry
    #| @param negative a flag which indicates if we send or not the negative 
    #|        value of the entry
    #| @param current dictionnary
    #| @return the result to send (ValueResult)
    #+---------------------------------------------------------------------------+
    def send(self, negative, dictionary):
        self.log.debug("Send (negative=" + str(negative) + " ...")
        return self.value.send(negative, dictionary)
    
    #+---------------------------------------------------------------------------+
    #| compare :
    #|     Compare this entry with a specific value
    #| @param val the string value to which we must compare
    #| @param indice position in the value of the analysis
    #| @param negative a flag which indicates if we compare or not the negative 
    #|        value of the entry
    #| @return the result of the comparaison
    #+---------------------------------------------------------------------------+
    def compare(self, val, indice, negative, dictionary):
        self.log.debug("Compare (val=" + val + ", i=" + str(indice) + " neg=" + str(negative) + "...")
        return self.value.compare(val, indice, negative, dictionary)

    #+---------------------------------------------------------------------------+
    #| learn :
    #|     Learn the following value
    #| @param val the string value to learn
    #| @param indice position in the value of the analysis
    #| @return the result of the learning process
    #+---------------------------------------------------------------------------+
    def learn(self, val, indice):
        self.log.debug("Learn (val=" + val + ", i=" + str(indice) + "...")
        return self.value.learn(val, indice)

    
    
    
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id
    def getName(self):
        return self.name
    def isActive(self):
        return self.active
    def getValue(self):
        return self.value
        
    def setID(self, id):
        self.id = id
    def setName(self, name):
        self.name = name
    
    
