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
import logging

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Common.MMSTD.Dictionary.AbstractionLayer import AbstractionLayer
from netzob.Common.MMSTD.Actors.SimpleCommunicationChannel import SimpleCommunicationLayer
from netzob.Common.MMSTD.Dictionary.Memory import Memory
from netzob.Common.Grammar import Grammar

#+----------------------------------------------
#| MMSTD:
#|    Definition of an "Machine de Mealy Stochastiques
#|    à Transitions Déterministes"
#+----------------------------------------------
class MMSTD(object):

    #+----------------------------------------------
    #| Constructor:
    #+----------------------------------------------
    def __init__(self, initialState, dictionary):

        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.MMSTD.py')

        # Initial state
        self.initialState = initialState

        # The dictionary
        self.dictionary = dictionary

    #+---------------------------------------------------------------------------+
    #| getInitialState:
    #|     Returns the initial state of the MMSTD
    #| @return the initial state of the MMSTD
    #+---------------------------------------------------------------------------+
    def getInitialState(self):
        return self.initialState

    def getDictionary(self):
        return self.dictionary

    #+---------------------------------------------------------------------------+
    #| getOutputTrace:
    #|     Returns the generated symbols and the end state if we simulate the given symbols as inputs
    #| @return the generated traces (a list of symbols) by the MMSTD and the end state
    #+---------------------------------------------------------------------------+
    def getOutputTrace(self, state, symbols):
        communicationLayer = SimpleCommunicationLayer(symbols, [], self.dictionary, Memory(self.dictionary.getVariables()))
        abstractionLayer = AbstractionLayer(communicationLayer, self.dictionary, Memory(self.dictionary.getVariables()))
        for i in range(0, len(symbols)):
            state = state.executeAsClient(abstractionLayer)
        outputMessages = abstractionLayer.getOutputMessages()
        generatedSymbols = []
        for (sendingTime, strMessage, symbol) in outputMessages:
            generatedSymbols.append(symbol)

        return (generatedSymbols, state)

    #+---------------------------------------------------------------------------+
    #| toGrammar:
    #|     Generalize the MMSTD in a normla grammar
    #+---------------------------------------------------------------------------+
    def toGrammar(self):
        result = Grammar("MMSTD", self.initialState)
        for state in self.getAllStates():
            result.addState(state)
            # Add the transitions (only if doesn't include as only output symbol an EmptySymbol)
            for transition in state.getTransitions():
                if len(transition.getOutputSymbols()) > 0:

                    if len(transition.getOutputSymbols()) == 1:

                        outputSymbol = transition.getOutputSymbols()[0][0]
                        realSymbol = outputSymbol.getEntry()

                        if realSymbol.getName() != "EmptySymbol":
                            result.addTransition(transition)
                        else:
                            state.unregisterTransition(transition)
                    elif len(transition.getOutputSymbols()) > 1:
                        result.addTransition(transition)
                    else:
                        self.log.info("Not adding transition : " + transition.getName())

        return result


    #+---------------------------------------------------------------------------+
    #| getDotCode:
    #|     Generates the dot code representing the automata
    #| @return a string containing the dot code of the automata
    #+---------------------------------------------------------------------------+
    def getDotCode(self):
        dotCode = "digraph G {\n"
        # first we include all the states declared in the automata
        states = self.getAllStates()
        for state in states:
            if state.isActive():
                dotCode = dotCode + "\"" + state.getName() + "\" [style=filled, fillcolor = red];\n"
            else:
                dotCode = dotCode + "\"" + state.getName() + "\" [style=filled, fillcolor = white];\n"

        for inputState in states:
            for transition in inputState.getTransitions():
                outputState = transition.getOutputState()
                dotCode = dotCode + "\"" + inputState.getName() + "\" -> \"" + outputState.getName() + "\" [fontsize=5, label=\"" + transition.getDescription() + "\"]\n"

        dotCode = dotCode + "}"
        return dotCode


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
            if currentState != None:
                found = False
                for tmpState in states:
                        if tmpState.getID() == currentState.getID():
                            found = True
                if not found:
                    for transition in currentState.getTransitions():
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
        return states
