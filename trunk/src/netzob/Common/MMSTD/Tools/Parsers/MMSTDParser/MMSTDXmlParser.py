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
import os

#+---------------------------------------------- 
#| Related third party imports
#+----------------------------------------------
from xml.etree import ElementTree

#+---------------------------------------------- 
#| Local application imports
#+----------------------------------------------
from netzob.Common.ConfigurationParser import ConfigurationParser
from netzob.Common.MMSTD.States.impl import NormalState
from netzob.Common.MMSTD.Transitions.impl import SemiStochasticTransition
from netzob.Common.MMSTD.Transitions.impl import OpenChannelTransition
from netzob.Common.MMSTD.Transitions.impl import CloseChannelTransition
from netzob.Common.MMSTD.Tools.Parsers.DictionaryParser import DictionaryXmlParser
from netzob.Common.MMSTD import MMSTD

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
        
        
        automatonDir = ConfigurationParser().get("automata", "path")
        dictionaryFile = os.path.join(automatonDir, rootElement.get("dictionary", "none"))
        # Parsing dictionary file
        dicoTree = ElementTree.ElementTree()
        dicoTree.parse(dictionaryFile)           
        dictionary = DictionaryXmlParser.DictionaryXmlParser.loadFromXML(dicoTree.getroot(), dictionaryFile)
        
        # parse for all the states
        states = []
        initialState = None 
        for xmlState in rootElement.findall("state") :
            idState = int(xmlState.get("id", "-1"))
            classState = xmlState.get("class", "NormalState")
            nameState = xmlState.get("name", "none")
            state = NormalState.NormalState(idState, nameState)
            states.append(state)
            if idState == 0 :
                initialState = state
            
        # parse for all the transitions
        for xmlTransition in rootElement.findall("transition") :
            
            classTransition = xmlTransition.get("class", "none")
            
            transition = None
            if classTransition == "SemiStochasticTransition" :
                transition = SemiStochasticTransition.SemiStochasticTransition.parse(xmlTransition, dictionary, states)
            elif classTransition == "OpenChannelTransition" :
                transition = OpenChannelTransition.OpenChannelTransition.parse(xmlTransition, states)
            elif classTransition == "CloseChannelTransition" :
                transition = CloseChannelTransition.CloseChannelTransition.parse(xmlTransition, states)
        
        
        # create an MMSTD
        automata = MMSTD.MMSTD(initialState, dictionary)
        return automata
    
