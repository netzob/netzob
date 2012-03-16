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
from netzob.Common.Automata import Automata
from netzob.Common.Sequence import Sequence


#+---------------------------------------------------------------------------+
#| Grammar:
#|     Class definition of a grammar
#+---------------------------------------------------------------------------+
class Grammar(object):

    #+-----------------------------------------------------------------------+
    #| Constructor
    #+-----------------------------------------------------------------------+
    def __init__(self):
        self.automata = None
        self.sequences = []

    def addsequence(self, sequence):
        if not sequence in self.sequences:
            self.sequences.append(sequence)
        else:
            logging.debug("Can't add the provided sequence, since its already registered")

    #+-----------------------------------------------------------------------+
    #| Save & Load
    #+-----------------------------------------------------------------------+
    def save(self, root, namespace):
        xmlGrammar = etree.SubElement(root, "{" + namespace + "}grammar")
        if self.automata != None:
            self.automata.save(xmlGrammar, namespace)

        if len(self.sequences) > 0:
            xmlSequences = etree.SubElement(xmlGrammar, "{" + namespace + "}sequences")
            for sequence in self.getSequences():
                sequence.save(xmlSequences, namespace)

    @staticmethod
    def loadGrammar(xmlRoot, vocabulary, namespace, version):
        if version == "0.1":
            automata = None
            sequences = []

            if xmlRoot.find("{" + namespace + "}automata") != None:
                xmlAutomata = xmlRoot.find("{" + namespace + "}automata")
                automata = Automata.loadFromXML(xmlAutomata, vocabulary, namespace, version)

            if xmlRoot.find("{" + namespace + "}sequences") != None:
                xmlSequences = xmlRoot.find("{" + namespace + "}sequences")
                for xmlSequence in xmlSequences.findall("{" + namespace + "}sequence"):
                    sequence = Sequence.loadFromXML(xmlSequence, vocabulary, namespace, version)
                    sequences.append(sequence)

            grammar = None
            if automata != None or len(sequences) > 0:
                grammar = Grammar()
                if automata != None:
                    grammar.setAutomata(automata)
                if len(sequences) > 0:
                    grammar.setSequences(sequences)

            return grammar

        return None

    #+-----------------------------------------------------------------------+
    #| Getters & Setters
    #+-----------------------------------------------------------------------+
    def getAutomata(self):
        return self.automata

    def getSequences(self):
        return self.sequences

    def setAutomata(self, automata):
        self.automata = automata

    def setSequences(self, sequences):
        self.sequences = sequences

#
#    def __init__(self, type, initialState):
#        self.type = type
#        self.states = []
#        self.transitions = []
#        self.states = []
#        self.initialState = initialState
#        self.states.append(initialState)
#
#    def setInitialState(self, state):
#        self.initialState = state
#
#    def addState(self, state):
#        if not state in self.states:
#            self.states.append(state)
#        else:
#            logging.debug("The state cannot be added one more time in the grammar.")
#
#    #+---------------------------------------------------------------------------+
#    #| getTransitionsLeadingToState:
#    #|     retrieve all the transitions which ends on the provide state
#    #| @return a list of transition
#    #+---------------------------------------------------------------------------+
#    def getTransitionsLeadingToState(self, state):
#        transitions = []
#        for transition in self.getTransitions() :
#            if transition.getOutputState().getID() == state.getID() :
#                transitions.append(transition)
#
#        return transitions
#
#    def removeState(self, state):
#        # First we remove the transitions
#        transitionsToRemove = []
#        for transition in self.transitions:
#            if transition.getOutputState().getID() == state.getID():
#                transitionsToRemove.append(transition)
#        for transition in state.getTransitions():
#            transitionsToRemove.append(transition)
#
#        for transition in transitionsToRemove:
#            self.removeTransition(transition)
#
#        self.states.remove(state)
#
#    def removeTransition(self, transition):
#        if transition in self.transitions:
#            for state in self.states:
#                state.unregisterTransition(transition)
#            self.transitions.remove(transition)
#
#    def addTransition(self, transition):
#        if not transition in self.transitions:
#            self.transitions.append(transition)
#
#    #+---------------------------------------------------------------------------+
#    #| getDotCode:
#    #|     Generates the dot code representing the automata
#    #| @return a string containing the dot code of the automata
#    #+---------------------------------------------------------------------------+
#    def getDotCode(self):
#        dotCode = "digraph G {\n"
#        # first we include all the states declared in the automata
#        states = self.getStates()
#        for state in states:
#            if state.isActive():
#                dotCode = dotCode + "\"" + state.getName() + "\" [style=filled, fillcolor = red];\n"
#            else:
#                dotCode = dotCode + "\"" + state.getName() + "\" [style=filled, fillcolor = white];\n"
#
#        for inputState in states:
#            for transition in inputState.getTransitions():
#                outputState = transition.getOutputState()
#                dotCode = dotCode + "\"" + inputState.getName() + "\" -> \"" + outputState.getName() + "\" [fontsize=5, label=\"" + transition.getDescription() + "\"]\n"
#
#        dotCode = dotCode + "}"
#        return dotCode
#
#    def save(self, root, namespace):
#        xmlGrammar = etree.SubElement(root, "{" + namespace + "}grammar")
#        xmlGrammar.set("type", str(self.getType()))
#        xmlGrammar.set("initialState", str(self.getInitialState().getID()))
#        xmlStates = etree.SubElement(xmlGrammar, "{" + namespace + "}states")
#        for state in self.getStates():
#            state.save(xmlStates, namespace)
#
#        xmlTransitions = etree.SubElement(xmlGrammar, "{" + namespace + "}transitions")
#        for transition in self.getTransitions():
#            transition.save(xmlTransitions, namespace)
#
#    #+----------------------------------------------
#    #| Static methods
#    #+----------------------------------------------
#    @staticmethod
#    def loadGrammar(xmlRoot, vocabulary, namespace, version):
#        if version == "0.1":
#            grammarType = xmlRoot.get("type")
#            initialStateID = xmlRoot.get("initialState")
#            states = []
#            transitions = []
#            if grammarType == "MMSTD":
#                # Retrieve all the states
#                for xmlState in xmlRoot.findall("{" + namespace + "}states/{" + namespace + "}state"):
#                    state = AbstractState.loadFromXML(xmlState, namespace, version)
#                    if state != None:
#                        states.append(state)
#
#                # Retrieve all the transitions
#                if xmlRoot.find("{" + namespace + "}transitions") != None:
#                    xmlTransitions = xmlRoot.find("{" + namespace + "}transitions")
#                    for xmlTransition in xmlTransitions.findall("{" + namespace + "}transition"):
#                        transition = AbstractTransition.loadFromXML(states, vocabulary, xmlTransition, namespace, version)
#                        if transition != None:
#                            transitions.append(transition)
#
#                # First we retrieve the initial state to create the grammar
#                initialState = None
#                for state in states:
#                    if state.getID() == initialStateID:
#                        initialState = state
#
#                if initialState == None:
#                    logging.warn("Impossible to retrieve the initial state of the saved grammar")
#                    return None
#                # Creation of the grammar
#                grammar = Grammar(grammarType, initialState)
#                # Register all the states
#                for state in states:
#                    grammar.addState(state)
#
#                for transition in transitions:
#                    grammar.addTransition(transition)
#
#                return grammar
#            else:
#                logging.warn("Impossible to parse the grammar since its type (" + grammarType + ") is not supported.")
#
#    #+----------------------------------------------
#    #| GETTERS
#    #+----------------------------------------------
#    def getType(self):
#        return self.type
#
#    def getInitialState(self):
#        return self.initialState
#
#    def getStates(self):
#        return self.states
#
#    def getTransitions(self):
#        return self.transitions
