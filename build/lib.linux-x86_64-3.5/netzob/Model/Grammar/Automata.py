# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2016 Georges Bossert and Frédéric Guihéry              |
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

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Grammar.States.State import State
from netzob.Inference.Grammar.AutomataFactories.OneStateAutomataFactory import OneStateAutomataFactory
from netzob.Inference.Grammar.AutomataFactories.ChainedStatesAutomataFactory import ChainedStatesAutomataFactory
from netzob.Inference.Grammar.AutomataFactories.PTAAutomataFactory import PTAAutomataFactory


@NetzobLogger
class Automata(object):
    """Class which describes an automata (of a grammar) in the form of
    an SMMDT (i.e. Stochastic Mealy Machine with Deterministic
    Transitions).

    >>> # Create some states and transitions
    >>> from netzob.all import *
    >>> s0 = State(name="S0")
    >>> s1 = State(name="S1")
    >>> s2 = State(name="S2")
    >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="Open")
    >>> inputSymbol = Symbol()
    >>> outputSymbol = Symbol()
    >>> mainTransition = Transition(startState=s1, endState=s1, inputSymbol=inputSymbol, outputSymbols=[outputSymbol], name="hello")
    >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2, name="Close")

    >>> # Create the automata
    >>> automata = Automata(s0, [inputSymbol, outputSymbol])

    """

    @typeCheck(State, list)
    def __init__(self, initialState, vocabulary):
        self.initialState = initialState
        self.vocabulary = vocabulary  # A list of symbols

    def generateDotCode(self):
        """Generates the dot code representing the automata.

        >>> # Create some states and transitions
        >>> from netzob.all import *
        >>> s0 = State(name="S0")
        >>> s1 = State(name="S1")
        >>> s2 = State(name="S2")
        >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="Open")
        >>> inputSymbol = Symbol()
        >>> outputSymbol = Symbol()
        >>> mainTransition = Transition(startState=s1, endState=s1, inputSymbol=inputSymbol, outputSymbols=[outputSymbol], name="hello")
        >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2, name="Close")

        >>> # Create the automata
        >>> automata = Automata(s0, [inputSymbol, outputSymbol])
        >>> print(automata.generateDotCode()) #doctest: +ELLIPSIS
        digraph G {
        "S0" [shape=doubleoctagon, style=filled, fillcolor=white, URL="..."];
        "S1" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "S2" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "S0" ... "S1" [fontsize=5, label="OpenChannelTransition", URL="..."];
        "S1" ... "S1" [fontsize=5, label="hello (Symbol;{Symbol})", URL="..."];
        "S1" ... "S2" [fontsize=5, label="CloseChannelTransition", URL="..."];
        }

        :return: a string containing the dot code of the automata.
        :rtype: a :class:`list`
        """
        dotCode = []
        dotCode.append("digraph G {")

        # First we include all the states declared in the automata
        states = self.getAllStates()
        for state in states:
            if state.active:
                color = "red"
            else:
                color = "white"

            if state == self.initialState:
                shape = "doubleoctagon"
            else:
                shape = "ellipse"

            dotCode.append('"{0}" [shape={1}, style=filled, fillcolor={2}, URL="{3}"];'.format(state.name, shape, color, state.id))

        for inputState in states:
            for transition in inputState.transitions:
                outputState = transition.endState
                dotCode.append('"{0}" -> "{1}" [fontsize=5, label="{2}", URL="{3}"];'.format(inputState.name, outputState.name, transition.description, transition.id))

        dotCode.append("}")

        return '\n'.join(dotCode)

    def getAllStates(self):
        """Visits the automata to discover all the available states.

        >>> from netzob.all import *
        >>> # Create some states and transitions
        >>> s0 = State(name="State 0")
        >>> s1 = State(name="State 1")
        >>> s2 = State(name="State 2")
        >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="Open")
        >>> inputSymbol = Symbol()
        >>> outputSymbol = Symbol()
        >>> mainTransition = Transition(startState=s1, endState=s1, inputSymbol=inputSymbol, outputSymbols=[outputSymbol], name="hello")
        >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2, name="Close")

        >>> # Create the automata
        >>> automata = Automata(s0, [inputSymbol, outputSymbol])
        >>> for state in automata.getAllStates():
        ...    print(state)
        State 0
        State 1
        State 2

        :return: a list containing all the discovered states.
        :rtype: a :class:`list`
        """

        states = []
        toAnalyze = []
        toAnalyze.append(self.initialState)
        while (len(toAnalyze) > 0):
            currentState = toAnalyze.pop()
            if currentState is not None:
                found = False
                for tmpState in states:
                        if tmpState.id == currentState.id:
                            found = True
                if not found:
                    for transition in currentState.transitions:
                        outputState = transition.endState
                        found = False
                        for tmpState in states:
                            if tmpState.id == outputState.id:
                                found = True
                        for tmpState in toAnalyze:
                            if tmpState.id == outputState.id:
                                found = True
                        if not found:
                            toAnalyze.append(outputState)
                    states.append(currentState)
        return states

    @staticmethod
    @typeCheck(list, list)
    def generateChainedStatesAutomata(abstractSession, symbolList):
        """Generate an automata that contains as many states and
        transitions as the number of request-response couples in the
        abstract session. This automata has thus the shape of a uniq
        chain.

        >>> from netzob.all import *
        >>> symbolSYN = Symbol([Field(ASCII("SYN"))], name="Symbol_SYN")
        >>> symbolSYNACK = Symbol([Field(ASCII("SYN/ACK"))], name="Symbol_SYNACK")
        >>> symbolACK = Symbol([Field(ASCII("ACK"))], name="Symbol_ACK")
        >>> symbolPUSH = Symbol([Field(ASCII("PUSH"))], name="Symbol_PUSH")
        >>> symbolList = [symbolSYN, symbolSYNACK, symbolACK, symbolPUSH]

        >>> msg1 = RawMessage("SYN", source="A", destination="B")
        >>> msg2 = RawMessage("SYN/ACK", source="B", destination="A")
        >>> msg3 = RawMessage("ACK", source="A", destination="B")
        >>> msg4 = RawMessage("PUSH", source="B", destination="A")
        >>> session = Session([msg1, msg2, msg3, msg4])
        >>> abstractSession = session.abstract(symbolList)

        >>> automata = Automata.generateChainedStatesAutomata(abstractSession, symbolList)
        >>> dotcode = automata.generateDotCode()
        >>> print(len(dotcode))
        1024
        >>> print(dotcode) #doctest: +ELLIPSIS
        digraph G {
        "Start state" [shape=doubleoctagon, style=filled, fillcolor=white, URL="..."];
        "State 1" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "State 2" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "State 3" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "End state" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "Start state" ... "State 1" [fontsize=5, label="OpenChannelTransition", URL="..."];
        "State 1" ... "State 2" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_SYNACK})", URL="..."];
        "State 2" ... "State 3" [fontsize=5, label="Transition (Symbol_ACK;{Symbol_PUSH})", URL="..."];
        "State 3" ... "End state" [fontsize=5, label="CloseChannelTransition", URL="..."];
        }

        :return: an automata with one sequence of chained states.
        :rtype: a :class:`netzob.Model.Grammar.Automata.Automata`

        """
        return ChainedStatesAutomataFactory.generate(abstractSession, symbolList)

    @staticmethod
    @typeCheck(list, list)
    def generateOneStateAutomata(abstractSession, symbolList):
        """Generate an automata that, according to an abstract
        session, contains a main state where each request-response
        couples are permitted.

        >>> from netzob.all import *
        >>> symbolSYN = Symbol([Field(ASCII("SYN"))], name="Symbol_SYN")
        >>> symbolSYNACK = Symbol([Field(ASCII("SYN/ACK"))], name="Symbol_SYNACK")
        >>> symbolACK = Symbol([Field(ASCII("ACK"))], name="Symbol_ACK")
        >>> symbolPUSH = Symbol([Field(ASCII("PUSH"))], name="Symbol_PUSH")
        >>> symbolList = [symbolSYN, symbolSYNACK, symbolACK, symbolPUSH]

        >>> msg1 = RawMessage("SYN", source="A", destination="B")
        >>> msg2 = RawMessage("SYN/ACK", source="B", destination="A")
        >>> msg3 = RawMessage("ACK", source="A", destination="B")
        >>> msg4 = RawMessage("PUSH", source="B", destination="A")
        >>> session = Session([msg1, msg2, msg3, msg4])
        >>> abstractSession = session.abstract(symbolList)

        >>> automata = Automata.generateOneStateAutomata(abstractSession, symbolList)
        >>> dotcode = automata.generateDotCode()
        >>> print(len(dotcode))
        841
        >>> print(dotcode) #doctest: +ELLIPSIS
        digraph G {
        "Start state" [shape=doubleoctagon, style=filled, fillcolor=white, URL="..."];
        "Main state" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "End state" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "Start state" ... "Main state" [fontsize=5, label="OpenChannelTransition", URL="..."];
        "Main state" ... "Main state" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_SYNACK})", URL="..."];
        "Main state" ... "End state" [fontsize=5, label="CloseChannelTransition", URL="..."];
        }

        :return: an automata with one main state.
        :rtype: a :class:`netzob.Model.Grammar.Automata.Automata`

        """
        return OneStateAutomataFactory.generate(abstractSession, symbolList)

    @staticmethod
    @typeCheck(list, list)
    def generatePTAAutomata(abstractSessions, symbolList):
        """Generate 

        >>> from netzob.all import *
        >>> symbolSYN = Symbol([Field(ASCII("SYN"))], name="Symbol_SYN")
        >>> symbolSYNACK = Symbol([Field(ASCII("SYN/ACK"))], name="Symbol_SYNACK")
        >>> symbolACK = Symbol([Field(ASCII("ACK"))], name="Symbol_ACK")
        >>> symbolPUSH = Symbol([Field(ASCII("PUSH"))], name="Symbol_PUSH")
        >>> symbolList = [symbolSYN, symbolSYNACK, symbolACK, symbolPUSH]

        >>> msg1 = RawMessage("SYN", source="A", destination="B")
        >>> msg2 = RawMessage("SYN/ACK", source="B", destination="A")
        >>> msg3 = RawMessage("ACK", source="A", destination="B")
        >>> msg4 = RawMessage("PUSH", source="B", destination="A")
        >>> session = Session([msg1, msg2, msg3, msg4])
        >>> abstractSession1 = session.abstract(symbolList)

        >>> msg1 = RawMessage("SYN", source="A", destination="B")
        >>> msg2 = RawMessage("SYN/ACK", source="B", destination="A")
        >>> msg3 = RawMessage("SYN", source="A", destination="B")
        >>> msg4 = RawMessage("PUSH", source="B", destination="A")
        >>> msg5 = RawMessage("SYN", source="A", destination="B")
        >>> msg6 = RawMessage("PUSH", source="B", destination="A")
        >>> session = Session([msg1, msg2, msg3, msg4, msg5, msg6])
        >>> abstractSession2 = session.abstract(symbolList)

        >>> msg1 = RawMessage("SYN", source="A", destination="B")
        >>> msg2 = RawMessage("SYN/ACK", source="B", destination="A")
        >>> msg3 = RawMessage("ACK", source="A", destination="B")
        >>> msg4 = RawMessage("PUSH", source="B", destination="A")
        >>> msg5 = RawMessage("SYN", source="A", destination="B")
        >>> msg6 = RawMessage("PUSH", source="B", destination="A")
        >>> msg7 = RawMessage("SYN", source="A", destination="B")
        >>> msg8 = RawMessage("PUSH", source="B", destination="A")
        >>> session = Session([msg1, msg2, msg3, msg4, msg5, msg6, msg7, msg8])
        >>> abstractSession3 = session.abstract(symbolList)

        >>> abstractSessions = [abstractSession1, abstractSession2, abstractSession3]

        >>> automata = Automata.generatePTAAutomata(abstractSessions, symbolList)
        >>> dotcode = automata.generateDotCode()
        >>> print(dotcode) #doctest: +ELLIPSIS
        digraph G {
        "Start state" [shape=doubleoctagon, style=filled, fillcolor=white, URL="..."];
        "State 0" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "State 1" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "State 4" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "State 5" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "End state 6" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "State 2" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "State 7" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "State 8" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "End state 9" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "End state 3" [shape=ellipse, style=filled, fillcolor=white, URL="..."];
        "Start state" ... "State 0" [fontsize=5, label="OpenChannelTransition", URL="..."];
        "State 0" ... "State 1" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_SYNACK})", URL="..."];
        "State 1" ... "State 2" [fontsize=5, label="Transition (Symbol_ACK;{Symbol_PUSH})", URL="..."];
        "State 1" ... "State 4" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_PUSH})", URL="..."];
        "State 4" ... "State 5" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_PUSH})", URL="..."];
        "State 5" ... "End state 6" [fontsize=5, label="CloseChannelTransition", URL="..."];
        "State 2" ... "End state 3" [fontsize=5, label="CloseChannelTransition", URL="..."];
        "State 2" ... "State 7" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_PUSH})", URL="..."];
        "State 7" ... "State 8" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_PUSH})", URL="..."];
        "State 8" ... "End state 9" [fontsize=5, label="CloseChannelTransition", URL="..."];
        }

        :return: an automata based on a PTA (Prefix Tree Acceptator).
        :rtype: a :class:`netzob.Model.Grammar.Automata.Automata`

        """
        return PTAAutomataFactory.generate(abstractSessions, symbolList)

    @property
    def initialState(self):
        return self.__initialState

    @initialState.setter
    @typeCheck(State)
    def initialState(self, initialState):
        if initialState is None:
            raise TypeError("AbstractionLayer cannot be None")
        self.__initialState = initialState

    @property
    def vocabulary(self):
        return self.__vocabulary

    @vocabulary.setter
    @typeCheck(list)
    def vocabulary(self, vocabulary):
        self.__vocabulary = vocabulary

