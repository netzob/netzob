# -*- coding: utf-8 -*-


#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import logging
from lxml.etree import ElementTree
from lxml import etree

#+---------------------------------------------------------------------------+
#| Local Imports
#+---------------------------------------------------------------------------+
from netzob.Common.MMSTD.States.AbstractState import AbstractState
from netzob.Common.MMSTD.Transitions.AbstractTransition import AbstractTransition

#+---------------------------------------------------------------------------+
#| Grammar :
#|     Class definition of a grammar
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class Grammar(object):
    
    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self, type):
        self.type = type
        self.states = []
        self.transitions = []
        self.states = []
        self.initialState = None
        
        
    def setInitialState(self, state):
        self.initialState = state    
    
    def addState(self, state):
        if not state in self.states :
            self.states.append(state)
        else :
            logging.warn("The state cannot be added one more time in the grammar.")
            
    def addTransition(self, transition):
        if not transition in self.transitions :
            self.transitions.append(transition)
            
    def getType(self):
        return self.type
    def getInitialState(self):
        return self.initialState
    def getStates(self):
        return self.states
    def getTransitions(self):
        return self.transitions
            
    def save(self, root, namespace):
        xmlGrammar = etree.SubElement(root, "{" + namespace + "}grammar")
        xmlGrammar.set("type", str(self.getType()))
        xmlGrammar.set("initialState", str(self.getInitialState().getID()))
        xmlStates = etree.SubElement(xmlGrammar, "{" + namespace + "}states")
        for state in self.getStates():
            state.save(xmlStates, namespace)
        
        xmlTransitions = etree.SubElement(xmlGrammar, "{" + namespace + "}transitions")
        for transition in self.getTransitions():
            transition.save(xmlTransitions, namespace)
        
        
    
    @staticmethod
    def loadGrammar(xmlRoot, vocabulary, namespace, version):
        if version == "0.1" :
            grammarType = xmlRoot.get("type")
            initialStateID = xmlRoot.get("initialState")
            grammar = Grammar(grammarType)
            states = []
            transitions = []
            if grammarType == "MMSTD" :
                # Retrieve all the states
                for xmlState in xmlRoot.findall("{" + namespace + "}states/{" + namespace + "}state") :
                    state = AbstractState.loadFromXML(xmlState, namespace, version)
                    if state != None :
                        states.append(state)
                        
                # Retrieve all the transitions
                if xmlRoot.find("{" + namespace + "}transitions") != None :
                    xmlTransitions = xmlRoot.find("{" + namespace + "}transitions")
                    for xmlTransition in xmlTransitions.findall("{" + namespace + "}transition") :
                        transition = AbstractTransition.loadFromXML(states, vocabulary, xmlTransition, namespace, version)
                        if transition != None :
                            transitions.append(transition)
            
                for state in states :
                    if state.getID() == initialStateID :
                        grammar.setInitialState(state)
                    
                    grammar.addState(state)
                    
                for transition in transitions :
                    grammar.addTransition(transition)
                
                return grammar
            
            else :
                logging.warn("Impossible to parse the grammar since its type (" + grammarType + ") is not supported.")
               
        
        
        
        
        
        
