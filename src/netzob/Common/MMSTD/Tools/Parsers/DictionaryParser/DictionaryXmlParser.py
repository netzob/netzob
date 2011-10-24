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

from ....Dictionary.Values import Aggregate
from ....Dictionary.Values import TextValue
from ....Dictionary.Values import EndValue
from ....Dictionary.Values import VarValue
from ....Dictionary.Variables.HexVariable import HexVariable
from ....Dictionary.Variables.MD5Variable import MD5Variable
from ....Dictionary.Variables.AggregateVariable import AggregateVariable



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
        log = logging.getLogger('netzob.Common.MMSTD.Tools.Parser.DictionaryXmlParser.py')
          
        if rootElement.tag != "dictionary" :
            raise NameError("The parsed XML doesn't represent a dictionary.")
        
        # First we identify all the variables
        variables = []
        for xmlVariable in rootElement.findall("var") :
            idVar = int(xmlVariable.get("id", "-1"))
            nameVar = xmlVariable.get("name", "none")
            typeVar = xmlVariable.get("type", "none")
            
            variable = None
            if typeVar == "HEX" :
                size = int(xmlVariable.get("size", "-1"))
                min = int(xmlVariable.get("min", "-1"))
                max = int(xmlVariable.get("max", "-1"))
                variable = HexVariable(idVar, nameVar, xmlVariable.text)
                if size != -1 :
                    variable.setSize(size)
                if min != -1 :
                    variable.setMin(min)
                if max != -1 :
                    variable.setMax(max)
                    
                
            elif typeVar == "MD5" :
                initVar = xmlVariable.get("init", "")
                valVar = int(xmlVariable.get("idVariable", "0"))
                variable = MD5Variable(idVar, nameVar, initVar, valVar)
            elif typeVar == "AGGREGATE" :
                variable = AggregateVariable(idVar, nameVar, xmlVariable.text.split(';'))
           
            if variable != None :
                variables.append(variable)
            
            
        # Parse the entries declared in dictionary
        entries = []        
        for xmlEntry in rootElement.findall("entry") :
            idEntry = int(xmlEntry.get("id", "-1"))
            nameEntry = xmlEntry.get("name", "none")
            
            initialValue = Aggregate.Aggregate()
            
            currentValue = initialValue
            
            # Let's rock baby !
            # We start the parsing process of the dictionary
            for xmlValue in list(xmlEntry) :
                if xmlValue.tag == "text" :
                    currentValue.registerValue(DictionaryXmlParser.getTextValue(xmlValue))
                elif xmlValue.tag == "end" :
                    currentValue.registerValue(DictionaryXmlParser.getEndValue(xmlValue))
                elif xmlValue.tag == "var" :
                    currentValue.registerValue(DictionaryXmlParser.getVarValue(xmlValue, variables))
                else :
                    log.warn("The tag " + xmlValue.tag + " has not been parsed !")
            
            
            
            
            
            entry = DictionaryEntry.DictionaryEntry(idEntry, nameEntry, initialValue)
            
            entries.append(entry)
        
        # Create a dictionary based on the variables and the entries
        dictionary = MMSTDDictionary.MMSTDDictionary(variables, entries)
        return dictionary
    
    
    @staticmethod       
    def getTextValue(xmlElement):
        value = None
        if xmlElement.tag == "text" and len(xmlElement.text) > 0 :
            value = TextValue.TextValue(xmlElement.text)
        else :
            # create logger with the given configuration
            log = logging.getLogger('netzob.Common.MMSTD.Tools.Parser.DictionaryXmlParser.py')
            log.warn("Error in the XML Dictionary, the xmlElement is not a text value")
        return value
    
    @staticmethod       
    def getEndValue(xmlElement):
        value = None
        if xmlElement.tag == "end" :
            value = EndValue.EndValue()
        else :
            # create logger with the given configuration
            log = logging.getLogger('netzob.Common.MMSTD.Tools.Parser.DictionaryXmlParser.py')
            log.warn("Error in the XML Dictionary, the xmlElement is not an end value")
        return value
    
    @staticmethod       
    def getVarValue(xmlElement, variables):
        value = None
        if xmlElement.tag == "var" and xmlElement.get("id", "none") != "none" :
            idVariable = int(xmlElement.get("id", "-1"))
            resetCondition = xmlElement.get("reset", "normal")
            variable = None
            for tmp_var in variables :
                if tmp_var.getID() == idVariable :
                    variable = tmp_var
            
            value = VarValue.VarValue(variable, resetCondition)
        else :
            # create logger with the given configuration
            log = logging.getLogger('netzob.Common.MMSTD.Tools.Parser.DictionaryXmlParser.py')
            log.warn("Error in the XML Dictionary, the xmlElement is not a var value")
        return value
