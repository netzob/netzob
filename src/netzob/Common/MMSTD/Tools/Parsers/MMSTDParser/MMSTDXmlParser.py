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
from ..DictionaryParser import DictionaryXmlParser
from .... import MMSTD

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| MMSTDXmlParser :
#|    Parser for an MMSTD
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------- 
class MMSTDXmlParser(object):
    
    @staticmethod
    #+---------------------------------------------------------------------------+
    #| loadFromXML :
    #|     Function which parses an XML and extract from it
    #[     the definition of an MMSTD
    #| @param rootElement: XML root of the MMSTD definition 
    #| @return an instance of an MMSTD
    #| @throw NameError if XML invalid
    #+---------------------------------------------------------------------------+
    def loadFromXML(rootElement):     
        if rootElement.tag != "automata" :
            raise NameError("The parsed XML doesn't represent an automata.")
        
        if rootElement.get("type", "none") != "mmstd" :
            raise NameError("The parsed XML doesn't represent an MMSTD")
        
        if rootElement.get("dictionary", "none") == "none" :
            raise NameError("The MMSTD doesn't have any dictionary declared")
        
        dictionaryFile = rootElement.get("dictionary", "none")
        # Parsing dictionary file
        dicoTree = ElementTree.ElementTree()
        dicoTree.parse(dictionaryFile)           
        dictionary = DictionaryXmlParser.DictionaryXmlParser.loadFromXML(dicoTree.getroot())
        
        # parse for all the states
        states = [] 
        for xmlState in rootElement.findall("state") :
            idState = int(xmlState.get("id", "-1"))
            classState = xmlState.get("class", "NormalState")
            nameState = xmlState.get("name", "none")
            states.append(NormalState.NormalState(idState, nameState))
            
        # parse for all the transitions
        for xmlTransition in rootElement.findall("transition") :
            idTransition = int(xmlTransition.get("id", "-1"))
            nameTransition = xmlTransition.get("name", "none")
            classTransition = xmlTransition.get("class", "none")
            idStartTransition = int(xmlTransition.get("idStart", "-1"))
            idEndTransition = int(xmlTransition.get("idEnd", "-1"))
            
            xmlInput = xmlTransition.find("input")
            inputClass = xmlInput.get("class", "none")
            inputId = xmlInput.text
            #inputSymbol = DictionarySymbol.DictionarySymbol(inputId, dictionary) 
            

           
        # create an MMSTD
        automata = MMSTD.MMSTD(None)
        return automata
    
