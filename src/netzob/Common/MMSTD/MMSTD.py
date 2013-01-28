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

#+----------------------------------------------
#| Standard library imports
#+----------------------------------------------
from gettext import gettext as _
from lxml import etree
from lxml.etree import ElementTree
import logging
import uuid

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Common.Automata import Automata
from netzob.Common.MMSTD.Actors.SimpleCommunicationChannel import \
    SimpleCommunicationLayer
from netzob.Common.MMSTD.Dictionary.AbstractionLayer import AbstractionLayer
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Common.MMSTD.States.AbstractState import AbstractState
from netzob.Common.MMSTD.Transitions.AbstractTransition import \
    AbstractTransition
from netzob.Common.MMSTD.Transitions.impl.SemiStochasticTransition import SemiStochasticTransition
from netzob.Common.Symbol import Symbol
from netzob.Common.MMSTD.Symbols.impl.EmptySymbol import EmptySymbol
from netzob.Common.MMSTD.Symbols.impl.UnknownSymbol import UnknownSymbol


#+----------------------------------------------
#| MMSTD:
#|    Definition of an "Machine de Mealy Stochastiques
#|    à Transitions Déterministes"
#+----------------------------------------------
class MMSTD(Automata):

    TYPE = "mmstd"

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, initialState, vocabulary):
        Automata.__init__(self, MMSTD.TYPE)

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.MMSTD.py')

        # Initial state
        self.initialState = initialState

        # The states of the automata
        self.states = []

        # The transitions
        self.transitions = []

        # The dictionary
        self.vocabulary = vocabulary

    def setInitialState(self, state):
        self.initialState = state

    def addState(self, state):
        if not state in self.states:
            self.states.append(state)
        else:
            logging.debug("The state cannot be added one more time in the grammar.")

    #+---------------------------------------------------------------------------+
    #| getTransitionsLeadingToState:
    #|     retrieve all the transitions which ends on the provide state
    #| @return a list of transition
    #+---------------------------------------------------------------------------+
    def getTransitionsLeadingToState(self, state):
        transitions = []
        for transition in self.getTransitions():
            if transition.getOutputState().getID() == state.getID():
                transitions.append(transition)

        return transitions

    def getTransitionsStartingFromState(self, state):
        """getTransitionsStartingFromState:
                Retreive all the transitions which starts from the provide state.
                @return: a list of transition
        """
        transitions = []
        for transition in self.getTransitions():
            if transition.getInputState().getID() == state.getID():
                transitions.append(transition)
        return transitions

    def removeState(self, state):
        # First we remove the transitions
        transitionsToRemove = []
        for transition in self.transitions:
            if transition.getOutputState().getID() == state.getID():
                transitionsToRemove.append(transition)
        for transition in state.getTransitions():
            transitionsToRemove.append(transition)

        for transition in transitionsToRemove:
            self.removeTransition(transition)

        self.states.remove(state)

    def removeTransition(self, transition):
        if transition in self.transitions:
            for state in self.states:
                self.log.debug("Unregister transition {0} from state {1}".format(transition.getName(), state.getName()))
                state.unregisterTransition(transition)
            self.log.debug("Remove transition {0} from the MMSTD".format(transition.getName()))
            self.transitions.remove(transition)

    def addTransition(self, transition):
        if not transition in self.transitions:
            self.transitions.append(transition)

    #+---------------------------------------------------------------------------+
    #| getOutputTrace:
    #|     Returns the generated symbols and the end state if we simulate the given symbols as inputs
    #| @return the generated traces (a list of symbols) by the MMSTD and the end state
    #+---------------------------------------------------------------------------+
    def getOutputTrace(self, state, symbols):
        communicationLayer = SimpleCommunicationLayer(uuid.uuid4(), symbols, [], self.vocabulary, Memory())
        abstractionLayer = AbstractionLayer(communicationLayer, self.vocabulary, Memory())
        # communicationLayer = SimpleCommunicationLayer(symbols, [], self.vocabulary, Memory(self.vocabulary.getVariables()))
        # abstractionLayer = AbstractionLayer(communicationLayer, self.vocabulary, Memory(self.vocabulary.getVariables()))
        for i in range(0, len(symbols)):
            if state is not None:
                state = state.executeAsClient(abstractionLayer)
        outputMessages = abstractionLayer.getOutputMessages()
        generatedSymbols = []
        for (sendingTime, strMessage, symbol) in outputMessages:
            generatedSymbols.append(symbol)

        return (generatedSymbols, state)

    #+---------------------------------------------------------------------------+
    #| getDotCode:
    #|     Generates the dot code representing the automata
    #| @return a string containing the dot code of the automata
    #+---------------------------------------------------------------------------+
    def getDotCode(self):
        dotCode = []
        dotCode.append("digraph G {")
        # first we include all the states declared in the automata
        states = self.getStates()
        for state in states:
            if state.isActive():
                color = "red"
            else:
                color = "white"

            if state == self.initialState:
                shape = "doubleoctagon"
            else:
                shape = "ellipse"

            dotCode.append('"{0}" [shape={1}, style=filled, fillcolor={2}, URL="{3}"];'.format(state.getName(), shape, color, state.getID()))

        for inputState in states:
            for transition in inputState.getTransitions():
                outputState = transition.getOutputState()
                dotCode.append('"{0}" -> "{1}" [fontsize=5, label="{2}", URL="{3}"];'.format(inputState.getName(), outputState.getName(), transition.getDescription(), transition.getID()))

        dotCode.append("}")

        return '\n'.join(dotCode)

    #+---------------------------------------------------------------------------+
    #| getAllStates:
    #|     Visits the automata to discover all the available states
    #| @return a list containing all the discovered states
    #+---------------------------------------------------------------------------+
    def getAllStates(self):
        states = []
        toAnalyze = []
        toAnalyze.append(self.initialState)
        while (len(toAnalyze) > 0):
            currentState = toAnalyze.pop()
            if currentState is not None:
                found = False
                for tmpState in states:
                        if tmpState.getID() == currentState.getID():
                            found = True
                if not found:
                    for transition in currentState.getTransitions():
                        self.log.info("currentState " + str(currentState.getName()) + " has the following transition : " + str(transition))
                        outputState = transition.getOutputState()
                        found = False
                        for tmpState in states:
                            if tmpState.getID() == outputState.getID():
                                found = True
                        for tmpState in toAnalyze:
                            if tmpState.getID() == outputState.getID():
                                found = True
                        if not found:
                            toAnalyze.append(outputState)
                    states.append(currentState)
            else:
                self.log.error("state = NONE !!")
        return states

    def update(self, vocabulary):
        """update the definition of the automata
        and searched for deprecated symbols"""
        deprecatedTransitions = []

        for transition in self.transitions:
            if transition.getType() == SemiStochasticTransition.TYPE:
                symbols = []
                symbols.append(transition.getInputSymbol())
                for (s, p, ti) in transition.getOutputSymbols():
                    if s.getType() == Symbol.TYPE:
                        symbols.append(s)

                error = False
                for symbol in symbols:
                    found = False
                    vocaSymbols = [EmptySymbol(), UnknownSymbol()]
                    vocaSymbols.extend(vocabulary.getSymbols())
                    for s in vocaSymbols:
                        if str(s.getID()) == str(symbol.getID()):
                            found = True
                            break
                    if not found:
                        self.log.warning("Symbol {0} has not been found in vocabulary".format(symbol.getName()))
                        error = True
                        break
                if error:
                    deprecatedTransitions.append(transition)
        for transiton in deprecatedTransitions:
            self.removeTransition(transition)

    #+---------------------------------------------------------------------------+
    #| Save & Load
    #+---------------------------------------------------------------------------+
    def save(self, root, namespace):
        xmlGrammar = etree.SubElement(root, "{" + namespace + "}automata")
        xmlGrammar.set("type", MMSTD.TYPE)
        xmlGrammar.set("initialState", str(self.getInitialState().getID()))
        xmlStates = etree.SubElement(xmlGrammar, "{" + namespace + "}states")
        for state in self.getStates():
            state.save(xmlStates, namespace)

        xmlTransitions = etree.SubElement(xmlGrammar, "{" + namespace + "}transitions")
        for transition in self.getTransitions():
            transition.save(xmlTransitions, namespace)

    @staticmethod
    def loadFromXML(xmlRoot, vocabulary, namespace, version):
        if version == "0.1":
            initialStateID = xmlRoot.get("initialState")
            states = []
            transitions = []

            # Retrieve all the states
            for xmlState in xmlRoot.findall("{" + namespace + "}states/{" + namespace + "}state"):
                state = AbstractState.loadFromXML(xmlState, namespace, version)
                if state is not None:
                    states.append(state)

            # Retrieve all the transitions
            if xmlRoot.find("{" + namespace + "}transitions") is not None:
                xmlTransitions = xmlRoot.find("{" + namespace + "}transitions")
                for xmlTransition in xmlTransitions.findall("{" + namespace + "}transition"):
                    transition = AbstractTransition.loadFromXML(states, vocabulary, xmlTransition, namespace, version)
                    if transition is not None:
                        transitions.append(transition)

            # First we retrieve the initial state to create the grammar
            initialState = None
            for state in states:
                if state.getID() == initialStateID:
                    initialState = state

            if initialState is None:
                logging.warn("Impossible to retrieve the initial state of the saved grammar")
                return None

            # Creation of the automata
            automata = MMSTD(initialState, vocabulary)

            # Register all the states
            for state in states:
                automata.addState(state)

            for transition in transitions:
                automata.addTransition(transition)

            return automata

    #+----------------------------------------------
    #| GETTERS
    #+----------------------------------------------
    def getType(self):
        return self.type

    def getInitialState(self):
        return self.initialState

    def getVocabulary(self):
        return self.vocabulary

    def getStates(self):
        return self.states

    def getTransitions(self):
        return self.transitions
