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

#+---------------------------------------------- 
#| Standard library imports
#+----------------------------------------------
import logging

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------
from xml.etree import ElementTree

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from ..... import ConfigurationParser
from ....States.impl import NormalState
from ....Dictionary import Variable
from ....Dictionary import DictionaryEntry
from ....Dictionary import MMSTDDictionary

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| DictionaryXmlParser :
#|    Parser for an XML Dictionary
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class DictionaryXmlParser(object):
    
    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of a dictionary
    #| @param rootElement: XML root of the dictionary definition 
    #| @return an instance of a dictionary
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement):     
        if rootElement.tag != "dictionary" :
            raise NameError("The parsed XML doesn't represent a dictionary.")
        
        # First we identify all the variables
        variables = []
        for xmlVariable in rootElement.findall("var") :
            idVar = int(xmlVariable.get("id", "-1"))
            nameVar = xmlVariable.get("name", "none")
            typeVar = xmlVariable.get("type", "none")
            defaultValue = xmlVariable.text
            variable = Variable.Variable(idVar, nameVar, typeVar, defaultValue)
            variables.append(variable)
            
        # Parse the entries declared in dictionary
        entries = []        
        for xmlEntry in rootElement.findall("entry") :
            idEntry = int(xmlEntry.get("id", "-1"))
            nameEntry = xmlEntry.get("name", "none")
            entry = DictionaryEntry.DictionaryEntry(idEntry, nameEntry)
            
            entries.append(entry)
        
        # Create a dictionary based on the variables and the entries
        dictionary = MMSTDDictionary.MMSTDDictionary(variables, entries)
        return dictionary
           
    
    
