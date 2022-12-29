# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
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
import os
import subprocess
import tempfile

#+----------------------------------------------
#| Related third party imports
#+----------------------------------------------

#+----------------------------------------------
#| Local application imports
#+----------------------------------------------
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Grammar.States.State import State
from netzob.Model.Grammar.Transitions.OpenChannelTransition import OpenChannelTransition
from netzob.Model.Grammar.Transitions.CloseChannelTransition import CloseChannelTransition
from netzob.Inference.Grammar.AutomataFactories.OneStateAutomataFactory import OneStateAutomataFactory
from netzob.Inference.Grammar.AutomataFactories.ChainedStatesAutomataFactory import ChainedStatesAutomataFactory
from netzob.Inference.Grammar.AutomataFactories.PTAAutomataFactory import PTAAutomataFactory


@NetzobLogger
class Automata(object):
    """Class which describes an automaton (i.e. state machine) of a
    protocol. The underlying structure of the automaton is a Mealy
    machine (cf. https://en.wikipedia.org/wiki/Mealy_machine).

    The Automata constructor expects some parameters:

    :param initialState: The initial state of the automaton.
    :param symbols: The list of permitted symbols for every transition of the automaton.
    :type initialState: :class:`State <netzob.Model.Grammar.States.State.State>`, required
    :type symbols: a :class:`list` of :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`, required


    The Automata class provides the following public variables:

    :var initialState: This parameter is the initial state of the automaton.
    :var symbols: This parameter is the list of permitted symbols for every transition of the automaton.
    :vartype initialState: :class:`State <netzob.Model.Grammar.States.State.State>`
    :vartype symbols: a :class:`list` of :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`


    The following example shows the definition of an automaton with
    three states `s0`, `s1`, `s2`, an opening transition between
    states `s0` and `s1`, a standard transition within the same state
    `s1` which accepts the input symbol `inputSymbol` and generate the
    output symbol `outputSymbol`, and a closing transition between
    states `s1` and `s2`.

    >>> # Creation of some states and transitions
    >>> from netzob.all import *
    >>> s0 = State(name="S0")
    >>> s1 = State(name="S1")
    >>> s2 = State(name="S2")
    >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="Open")
    >>> inputSymbol = Symbol()
    >>> outputSymbol = Symbol()
    >>> mainTransition = Transition(startState=s1, endState=s1, inputSymbol=inputSymbol, outputSymbols=[outputSymbol], name="hello")
    >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2, name="Close")
    >>> # Creation of the automata
    >>> automata = Automata(s0, [inputSymbol, outputSymbol])

    """

    @public_api
    @typeCheck(State, list)
    def __init__(self, initialState, symbols):

        # Initialize public variables from parameters
        self.initialState = initialState
        self.symbols = symbols  # A list of symbols accepted by the automaton

        # Initialize local variables
        self.cbk_read_symbol_timeout = None     # list of callbacks
        self.cbk_read_unexpected_symbol = None  # list of callbacks
        self.cbk_read_unknown_symbol = None     # list of callbacks

    @public_api
    def copy(self):
        r"""Copy the current automaton.

        This method copies the states and transitions of the
        automaton, but keeps references to the original callbacks and
        symbols.

        :return: A new object of the same type.
        :rtype: :class:`Automata <netzob.Model.Grammar.Automata.Automata>`

        >>> # Creation of some states and transitions
        >>> from netzob.all import *
        >>> s0 = State(name="S0")
        >>> s1 = State(name="S1")
        >>> s2 = State(name="S2")
        >>> openTransition = OpenChannelTransition(startState=s0, endState=s1, name="open transition")
        >>> inputSymbol = Symbol()
        >>> outputSymbol = Symbol()
        >>> mainTransition = Transition(startState=s1, endState=s1, inputSymbol=inputSymbol, outputSymbols=[outputSymbol], name="main transition")
        >>> closeTransition = CloseChannelTransition(startState=s1, endState=s2, name="close transition")
        >>> # Creation of the automata
        >>> automata = Automata(s0, [inputSymbol, outputSymbol])
        >>> automata_bis = automata.copy()

        """

        map_new_states = {}  # Store mapping [original state -> cloned state]

        for state in self.getStates():
            new_transitions = []
            for transition in state.transitions:

                new_transition = transition.copy()
                new_transitions.append(new_transition)

                # Handle startState
                if transition.startState in map_new_states.keys():
                    new_transition._startState = map_new_states[transition.startState]
                else:
                    new_transition._startState = transition.startState.copy()
                    map_new_states[transition.startState] = new_transition.startState

                # Handle endState
                if transition.endState in map_new_states.keys():
                    new_transition.endState = map_new_states[transition.endState]
                else:
                    new_transition.endState = transition.endState.copy()
                    map_new_states[transition.endState] = new_transition.endState

            if state in map_new_states.keys():
                map_new_states[state].transitions = new_transitions
            else:
                map_new_states[state] = state.copy()
                map_new_states[state].transitions = new_transitions

        automata = Automata(map_new_states[self.initialState], self.symbols)
        automata.cbk_read_symbol_timeout = self.cbk_read_symbol_timeout
        automata.cbk_read_unexpected_symbol = self.cbk_read_unexpected_symbol
        automata.cbk_read_unknown_symbol = self.cbk_read_unknown_symbol

        return automata

    @public_api
    def generateASCII(self):
        """Render the ASCII representation of the automaton.

        :return: A string containing an ASCII representation of the automaton.
        :rtype: :class:`str`

        """

        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(str.encode(self.generateDotCode()))
        f.close()

        binary_path = '/usr/bin/graph-easy'
        if not os.path.isfile(binary_path):
            error_message = "Cannot generate ASCII graph as a dependency is missing: 'graph-easy' (see libgraph-easy-perl package)"
            self._logger.warning(error_message)
            return error_message

        cmd = [binary_path, '--input', f.name, '--as_ascii']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.wait()
        result = p.stdout.read().decode("utf-8")

        os.unlink(f.name)

        return result

    @public_api
    def generateDotCode(self):
        """Generates the dot code representing the automaton.

        :return: A string containing a dot code representation of the automaton.
        :rtype: :class:`str`

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

        >>> # Create the automaton
        >>> automata = Automata(s0, [inputSymbol, outputSymbol])
        >>> print(automata.generateDotCode()) #doctest: +ELLIPSIS
        digraph G {
        "S0" [shape=doubleoctagon, label="S0", style=filled, fillcolor=white, URL="..."];
        "S1" [shape=ellipse, label="S1", style=filled, fillcolor=white, URL="..."];
        "S2" [shape=ellipse, label="S2", style=filled, fillcolor=white, URL="..."];
        "S0" -> "S1" [fontsize=5, label="OpenChannelTransition", URL="..."];
        "S1" -> "S1" [fontsize=5, label="hello (Symbol;{Symbol})", URL="..."];
        "S1" -> "S2" [fontsize=5, label="CloseChannelTransition", URL="..."];
        }

        :return: a string containing the dot code of the automata.
        :rtype: a :class:`list`
        """
        dotCode = []
        dotCode.append("digraph G {")

        # First we include all the states declared in the automata
        states = self.getStates()
        for state in states:
            if state.active:
                color = "red"
            else:
                color = "white"

            if state == self.initialState:
                shape = "doubleoctagon"
            else:
                shape = "ellipse"

            descr = state.name

            for cbk in state.cbk_modify_transition:
                descr += " [CBK modify transition] "

            dotCode.append(
                '"{}" [shape={}, label="{}", style=filled, fillcolor={}, URL="{}"];'.
                format(state.name, shape, descr, color, id(state)))

        for inputState in states:
            for transition in inputState.transitions:
                outputState = transition.endState

                descr = transition.description

                for cbk in transition.cbk_modify_symbol:
                    descr += " [CBK modify symbol] "

                dotCode.append(
                    '"{}" -> "{}" [fontsize=5, label="{}", URL="{}"];'.

                    format(inputState.name, outputState.name,
                           descr, id(transition)))

        dotCode.append("}")

        return '\n'.join(dotCode)

    @public_api
    def getStates(self, main_states=False):
        """Visits the automata to discover all the available states.

        :param main_states: Specify that all states except the initial state and the closing states are returned. Default value is ``False``, meaning that all states are returned.
        :type main_states: :class:`bool`, optional
        :return: A list containing all the automaton states.
        :rtype: a :class:`list` of :class:`State <netzob.Model.Grammar.States.State.State>`

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
        >>> for state in automata.getStates():
        ...    print(state)
        State 0
        State 1
        State 2

        >>> for state in automata.getStates(main_states=True):
        ...    print(state)
        State 1


        """

        states = []
        toAnalyze = []
        toAnalyze.append(self.initialState)
        while (len(toAnalyze) > 0):
            currentState = toAnalyze.pop()
            if currentState is not None:
                found = False
                for tmpState in states:
                    if id(tmpState) == id(currentState):
                        found = True
                        break
                if not found:
                    for transition in currentState.transitions:
                        outputState = transition.endState
                        found = False
                        for tmpState in states:
                            if id(tmpState) == id(outputState):
                                found = True
                                break
                        for tmpState in toAnalyze:
                            if id(tmpState) == id(outputState):
                                found = True
                                break
                        if not found:
                            toAnalyze.append(outputState)
                    states.append(currentState)

        states_to_drop = []
        if main_states:
            for state in states:
                if len(state.transitions) == 1 and isinstance(state.transitions[0], OpenChannelTransition):
                    states_to_drop.append(state)
                else:
                    for t in state.transitions:
                        if isinstance(t, CloseChannelTransition):
                            states_to_drop.append(t.endState)
        for state in states_to_drop:
            states.remove(state)
        return states

    @public_api
    @typeCheck(str)
    def getState(self, name):
        """Returns the State object of the given name.

        :param name: The name of the State object
        :type name: :class:`str`, required
        :return: The State object with stateName as name.
        :rtype: :class:`State <netzob.Model.Grammar.States.State.State>`
        :raise: :class:`KeyError` if the name is not found.
        """

        states = self.getStates()
        for state in states:
            if state.name == name:
                return state
        else:
            raise KeyError("State with name '{}' does not exist".format(name))

    @public_api
    def getTransitions(self):
        """Return all the transitions of the automaton.

        :return: A list containing all the automaton transitions.
        :rtype: a :class:`list` of :class:`Transition <netzob.Model.Grammar.States.AbstractTransition.AbstractTransition>`

        """
        states = self.getStates()
        transitions = set()
        for state in states:
            for transition in state.transitions:
                transitions.add(transition)
        return list(transitions)

    @public_api
    @typeCheck(str)
    def getTransition(self, name):
        """Returns the Transition object of the given name.

        :param name: The name of the Transition object
        :type name: :class:`str`, required
        :return: The Transition object.
        :rtype: :class:`Transition <netzob.Model.Grammar.Transitions.Transition.Transition>`
        :raise: :class:`KeyError` if the name is not found.
        """

        transitions = self.getTransitions()
        for transition in transitions:
            if transition.name == name:
                return transition
        else:
            raise KeyError("Transition with name '{}' does not exist".format(name))

    @staticmethod
    @typeCheck(list, list)
    def generateChainedStatesAutomata(abstractSession, symbolList):
        """Generate an automata that contains as many states and
        transitions as the number of request-response couples in the
        abstract session. This automata has thus the shape of a uniq
        chain.

        >>> from netzob.all import *
        >>> symbolSYN = Symbol([Field(String("SYN"))], name="Symbol_SYN")
        >>> symbolSYNACK = Symbol([Field(String("SYN/ACK"))], name="Symbol_SYNACK")
        >>> symbolACK = Symbol([Field(String("ACK"))], name="Symbol_ACK")
        >>> symbolPUSH = Symbol([Field(String("PUSH"))], name="Symbol_PUSH")
        >>> symbolList = [symbolSYN, symbolSYNACK, symbolACK, symbolPUSH]

        >>> msg1 = RawMessage("SYN", source="A", destination="B")
        >>> msg2 = RawMessage("SYN/ACK", source="B", destination="A")
        >>> msg3 = RawMessage("ACK", source="A", destination="B")
        >>> msg4 = RawMessage("PUSH", source="B", destination="A")
        >>> session = Session([msg1, msg2, msg3, msg4])
        >>> abstractSession = session.abstract(symbolList)

        >>> automata = Automata.generateChainedStatesAutomata(abstractSession, symbolList)
        >>> dotcode = automata.generateDotCode()
        >>> len(dotcode)
        926
        >>> print(dotcode) #doctest: +ELLIPSIS
        digraph G {
        "Start state" [shape=doubleoctagon, label="Start state", style=filled, fillcolor=white, URL="..."];
        "State 1" [shape=ellipse, label="State 1", style=filled, fillcolor=white, URL="..."];
        "State 2" [shape=ellipse, label="State 2", style=filled, fillcolor=white, URL="..."];
        "State 3" [shape=ellipse, label="State 3", style=filled, fillcolor=white, URL="..."];
        "End state" [shape=ellipse, label="End state", style=filled, fillcolor=white, URL="..."];
        "Start state" -> "State 1" [fontsize=5, label="OpenChannelTransition", URL="..."];
        "State 1" -> "State 2" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_SYNACK})", URL="..."];
        "State 2" -> "State 3" [fontsize=5, label="Transition (Symbol_ACK;{Symbol_PUSH})", URL="..."];
        "State 3" -> "End state" [fontsize=5, label="CloseChannelTransition", URL="..."];
        }

        :return: an automata with one sequence of chained states.
        :rtype: a :class:`Automata <netzob.Model.Grammar.Automata.Automata>`

        """
        return ChainedStatesAutomataFactory.generate(abstractSession,
                                                     symbolList)

    @staticmethod
    @typeCheck(list, list)
    def generateOneStateAutomata(abstractSession, symbolList):
        """Generate an automata that, according to an abstract
        session, contains a main state where each request-response
        couples are permitted.

        >>> from netzob.all import *
        >>> symbolSYN = Symbol([Field(String("SYN"))], name="Symbol_SYN")
        >>> symbolSYNACK = Symbol([Field(String("SYN/ACK"))], name="Symbol_SYNACK")
        >>> symbolACK = Symbol([Field(String("ACK"))], name="Symbol_ACK")
        >>> symbolPUSH = Symbol([Field(String("PUSH"))], name="Symbol_PUSH")
        >>> symbolList = [symbolSYN, symbolSYNACK, symbolACK, symbolPUSH]

        >>> msg1 = RawMessage("SYN", source="A", destination="B")
        >>> msg2 = RawMessage("SYN/ACK", source="B", destination="A")
        >>> msg3 = RawMessage("ACK", source="A", destination="B")
        >>> msg4 = RawMessage("PUSH", source="B", destination="A")
        >>> session = Session([msg1, msg2, msg3, msg4])
        >>> abstractSession = session.abstract(symbolList)

        >>> automata = Automata.generateOneStateAutomata(abstractSession, symbolList)
        >>> dotcode = automata.generateDotCode()
        >>> len(dotcode)
        754
        >>> print(dotcode) #doctest: +ELLIPSIS
        digraph G {
        "Start state" [shape=doubleoctagon, label="Start state", style=filled, fillcolor=white, URL="..."];
        "Main state" [shape=ellipse, label="Main state", style=filled, fillcolor=white, URL="..."];
        "End state" [shape=ellipse, label="End state", style=filled, fillcolor=white, URL="..."];
        "Start state" -> "Main state" [fontsize=5, label="OpenChannelTransition", URL="..."];
        "Main state" -> "Main state" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_SYNACK})", URL="..."];
        "Main state" -> "Main state" [fontsize=5, label="Transition (Symbol_ACK;{Symbol_PUSH})", URL="..."];
        "Main state" -> "End state" [fontsize=5, label="CloseChannelTransition", URL="..."];
        }

        :return: an automata with one main state.
        :rtype: a :class:`Automata <netzob.Model.Grammar.Automata.Automata>`

        """
        return OneStateAutomataFactory.generate(abstractSession, symbolList)

    @staticmethod
    @typeCheck(list, list)
    def generatePTAAutomata(abstractSessions, symbolList):
        """Generate an automata according to the observed sequence of messages/symbols

        >>> from netzob.all import *
        >>> symbolSYN = Symbol([Field(String("SYN"))], name="Symbol_SYN")
        >>> symbolSYNACK = Symbol([Field(String("SYN/ACK"))], name="Symbol_SYNACK")
        >>> symbolACK = Symbol([Field(String("ACK"))], name="Symbol_ACK")
        >>> symbolPUSH = Symbol([Field(String("PUSH"))], name="Symbol_PUSH")
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
        "Start state" [shape=doubleoctagon, label="Start state", style=filled, fillcolor=white, URL="..."];
        "State 0" [shape=ellipse, label="State 0", style=filled, fillcolor=white, URL="..."];
        "State 1" [shape=ellipse, label="State 1", style=filled, fillcolor=white, URL="..."];
        "State 4" [shape=ellipse, label="State 4", style=filled, fillcolor=white, URL="..."];
        "State 5" [shape=ellipse, label="State 5", style=filled, fillcolor=white, URL="..."];
        "End state 6" [shape=ellipse, label="End state 6", style=filled, fillcolor=white, URL="..."];
        "State 2" [shape=ellipse, label="State 2", style=filled, fillcolor=white, URL="..."];
        "State 7" [shape=ellipse, label="State 7", style=filled, fillcolor=white, URL="..."];
        "State 8" [shape=ellipse, label="State 8", style=filled, fillcolor=white, URL="..."];
        "End state 9" [shape=ellipse, label="End state 9", style=filled, fillcolor=white, URL="..."];
        "End state 3" [shape=ellipse, label="End state 3", style=filled, fillcolor=white, URL="..."];
        "Start state" -> "State 0" [fontsize=5, label="OpenChannelTransition", URL="..."];
        "State 0" -> "State 1" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_SYNACK})", URL="..."];
        "State 1" -> "State 2" [fontsize=5, label="Transition (Symbol_ACK;{Symbol_PUSH})", URL="..."];
        "State 1" -> "State 4" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_PUSH})", URL="..."];
        "State 4" -> "State 5" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_PUSH})", URL="..."];
        "State 5" -> "End state 6" [fontsize=5, label="CloseChannelTransition", URL="..."];
        "State 2" -> "End state 3" [fontsize=5, label="CloseChannelTransition", URL="..."];
        "State 2" -> "State 7" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_PUSH})", URL="..."];
        "State 7" -> "State 8" [fontsize=5, label="Transition (Symbol_SYN;{Symbol_PUSH})", URL="..."];
        "State 8" -> "End state 9" [fontsize=5, label="CloseChannelTransition", URL="..."];
        }

        :return: an automata based on a PTA (Prefix Tree Acceptator).
        :rtype: a :class:`Automata <netzob.Model.Grammar.Automata.Automata>`

        """
        return PTAAutomataFactory.generate(abstractSessions, symbolList)

    @public_api
    def set_cbk_read_symbol_timeout(self, cbk_method, states=None):
        """Function called to handle cases where a timeout appears when
        waiting for a symbol. In a non initiator context, this symbol would
        correspond to the input symbol that should trigger a
        transition. In an initiator context, this symbol would correspond to an
        output symbol that is expected according to the current
        transition.

        :param cbk_method: A function used to handle the selection of the next
                           state when no symbol is received after the timeout
                           has expired.
        :type cbk_method: :class:`Callable <collections.abc.Callable>`, required

        :param states: A list of states on which the callback function should apply.
                       If no states are specified, the callback function is
                       applied on all states of the automaton.
        :type states: ~typing.List[~netzob.Model.Grammar.States.State.State], optional

        :raise: :class:`TypeError` if :attr:`cbk_method` is not a callable function

        The callback function that can be used in the
        :attr:`cbk_method` parameter has the following prototype:

        .. function:: cbk_method(current_state, current_transition)
           :noindex:

           :param current_state:
             Corresponds to the current state in the automaton.
             It is expected that the current state cannot be ``None``, because when an actor visits an automaton, it is always positioned at a state even if it is executing a transition (in such case, the current state is the initial state of the transition).
           :type current_state: ~netzob.Model.Grammar.States.State.State

           :param current_transition:
             Corresponds to the current transition in the automaton.
             It is expected that the current transition may be ``None``, especially
             in a non initiator context, where no transition has been initiated.
           :type current_transition: ~netzob.Model.Grammar.Transitions.Transition.Transition

           :return: The callback function should return the next
                    state.  For example, to stay at the same state,
                    the callback function would have to return the
                    :attr:`current_state` value.
           :rtype: :class:`~netzob.Model.Grammar.States.State.State`

        """
        if not callable(cbk_method):
            raise TypeError("'cbk_method' should be a callable function")

        self.cbk_read_symbol_timeout = cbk_method

    @public_api
    def set_cbk_read_unexpected_symbol(self, cbk_method, states=None):
        """Function called to handle cases where a symbol is received but not
        expected. In a non initiator context, this symbol would not match the input
        symbol of the available transitions. In an initiator context, this
        symbol would not match the expected output symbols of the current
        transition.

        The method expects some parameters:

        :param cbk_method: A function used to handle the selection of the next
                           state when a unexpected symbol is received.
        :type cbk_method: :class:`Callable <collections.abc.Callable>`, required

        :param states: A list of states on which the callback function should apply.
                       If no states are specified, the callback function is
                       applied on all states of the automaton.
        :type states: ~typing.List[~netzob.Model.Grammar.States.State.State], optional

        :raise: :class:`TypeError` if :attr:`cbk_method` is not a callable function

        The callback function that can be used in the
        :attr:`cbk_method` parameter has the following prototype:

        .. function:: cbk_method(current_state, current_transition,\
                                 received_symbol, received_message, received_structure)
           :noindex:

           :param current_state:
             Corresponds to the current state in the automaton.
             It is expected that the current state cannot be ``None``, because when an actor visits an automaton, it is always positioned at a state even if it is executing a transition (in such case, the current state is the initial state of the transition).
           :type current_state: ~netzob.Model.Grammar.States.State.State

           :param current_transition:
             Corresponds to the current transition in the automaton.
             It is expected that the current transition may be ``None``, especially
             in a non initiator context, where no transition has been initiated.
           :type current_transition: ~netzob.Model.Grammar.Transitions.Transition.Transition

           :param received_symbol:
             Corresponds to the received symbol.
           :type received_symbol: ~netzob.Model.Vocabulary.Symbol.Symbol

           :param received_message:
             Corresponds to the received raw message.
           :type received_message: :class:`bytes`

           :param received_structure:
             Corresponds to the received message structure.
           :type received_structure: :class:`OrderedDict` where keys are :class:`~netzob.Model.Vocabulary.Field.Field` and values are :class:`bytes`

           :return: The callback function should return the next
                    state.  For example, to stay at the same state,
                    the callback function would have to return the
                    :attr:`current_state` value.
           :rtype: :class:`~netzob.Model.Grammar.States.State.State`

        """
        if not callable(cbk_method):
            raise TypeError("'cbk_method' should be a callable function")

        self.cbk_read_unexpected_symbol = cbk_method

    @public_api
    def set_cbk_read_unknown_symbol(self, cbk_method, states=None):
        """Function called to handle cases where a message is received but
        does not correspond to a known symbol. In a non initiator context,
        this message would not match the input symbol of the available
        transitions. In an initiator context, this message would not match
        the expected output symbols of the current transition.

        The method expects some parameters:

        :param cbk_method: A callable function used to handle the selection of
                           the next state when an unknown symbol is received.
        :type cbk_method: :class:`Callable <collections.abc.Callable>`, required

        :param states: A list of states on which the callback function should apply.
                       If no states are specified, the callback function is
                       applied on all states of the automaton.
        :type states: ~typing.List[~netzob.Model.Grammar.States.State.State], optional

        :raise: :class:`TypeError` if :attr:`cbk_method` is not a callable function

        The callback function that can be used in the
        :attr:`cbk_method` parameter has the following prototype:

        .. function:: cbk_method(current_state, current_transition,\
                                 received_message)
           :noindex:

           :param current_state:
             Corresponds to the current state in the automaton.
             It is expected that the current state cannot be ``None``, because when an actor visits an automaton, it is always positioned at a state even if it is executing a transition (in such case, the current state is the initial state of the transition).
           :type current_state: ~netzob.Model.Grammar.States.State.State

           :param current_transition:
             Corresponds to the current transition in the automaton.
             It is expected that the current transition may be ``None``,
             especially in a non initiator context, where no transition has been initiated.
           :type current_transition: ~netzob.Model.Grammar.Transitions.Transition.Transition

           :param received_message:
             Corresponds to the received raw message.
           :type received_message: :class:`bytes`

           :return: The callback function should return the next
                    state.  For example, to stay at the same state,
                    the callback function would have to return the
                    :attr:`current_state` value.
           :rtype: :class:`~netzob.Model.Grammar.States.State.State`

        """
        if not callable(cbk_method):
            raise TypeError("'cbk_method' should be a callable function")

        self.cbk_read_unknown_symbol = cbk_method

    ## Automata Fuzzing ##

    @public_api
    def mutate(self, strategy=None, target=None, generator=None, seed=None):
        r"""This is the mutation method of the automaton. This method returns
        a new automaton that may be used for fuzzing purpose.

        The mutate method expects some parameters:

        :param strategy: The strategy used to build the new automaton.

                         The following strategies are available:

                         * :attr:`AutomataMutatorStrategy.RANDOM`: Randomly insert and remove transitions between states of the original automaton,
                         * :attr:`AutomataMutatorStrategy.FULL`: At each state of the automaton, it is possible to reach any states,
                         * :attr:`AutomataMutatorStrategy.ONESTATE`: Build an automaton with one main state that accepts every symbols.
                         * :attr:`AutomataMutatorStrategy.TARGETED`: Build an automaton similar to the original one, where a targeted state, given in parameters, will accept every symbols.

                         If set to None, the default strategy is :attr:`AutomataMutatorStrategy.RANDOM`.
        :param target: The name of the state considered for targeted fuzzing (should be used with :attr:`AutomataMutatorStrategy.TARGETED`).
        :param generator: The underlying generator used to produce
                          pseudo-random or deterministic
                          values.

                          Default generator is ``'xorshift'``, which is
                          efficient to produce unique pseudo-random
                          numbers.

        :param seed: An integer used to initialize the underlying
                     generator.

                     If None, the default value will be set to :attr:`Mutator.SEED_DEFAULT`. The :attr:`Mutator.SEED_DEFAULT` constant is initialized from the configuration variable :attr:`Conf.seed` from the Netzob API :class:`Conf` class.

        :type strategy: :class:`AutomataMutatorStrategy`, optional
        :type target: :class:`str`, optional
        :type generator: :class:`iter`, optional
        :type seed: :class:`int`, optional
        :return: The mutated automata.
        :rtype: :class:`Automata <netzob.Model.Grammar.Automata.Automata>`


        **Catching abnormal responses from the remote target**

        By default, the state machine is configured so that the
        reception of abnormal messages from the remote peer will
        terminate the visit loop of the automaton from the current
        actor. When applying fuzzing, this behavior could be annoying
        as it will quickly stop the fuzzing session as soon as a
        non-legitimate response is received. In order to catch this
        kind of responses and adapt the current actor behavior, it is
        recommended to set the following callbacks on the automaton:

        * :attr:`set_cbk_read_symbol_timeout <netzob.Model.Grammar.Automata.Automata.set_cbk_read_symbol_timeout>`
        * :attr:`set_cbk_read_unexpected_symbol <netzob.Model.Grammar.Automata.Automata.set_cbk_read_unexpected_symbol>`
        * :attr:`set_cbk_read_unknown_symbol <netzob.Model.Grammar.Automata.Automata.set_cbk_read_unknown_symbol>`


        The following example shows how to specify a global behavior,
        on all states and transitions, in order to catch reception of
        unexpected symbols (i.e. symbols that are known but not
        expected at this state/transition) and unknown messages
        (i.e. messages that cannot be abstracted to a symbol).

        >>> from netzob.all import *
        >>> import time
        >>>
        >>> # First we create the symbols
        >>> symbol1 = Symbol(name="Hello1", fields=[Field("hello1")])
        >>> symbol2 = Symbol(name="Hello2", fields=[Field("hello2")])
        >>> symbolList = [symbol1, symbol2]
        >>>
        >>> # Create Bob's automaton
        >>> bob_s0 = State(name="S0")
        >>> bob_s1 = State(name="S1")
        >>> bob_s2 = State(name="S2")
        >>> bob_s3 = State(name="S3")
        >>> bob_error_state = State(name="Error state")
        >>> bob_openTransition = OpenChannelTransition(startState=bob_s0, endState=bob_s1, name="Open")
        >>> bob_mainTransition = Transition(startState=bob_s1, endState=bob_s2,
        ...                                 inputSymbol=symbol1, outputSymbols=[symbol2],
        ...                                 name="T1")
        >>> bob_closeTransition1 = CloseChannelTransition(startState=bob_error_state, endState=bob_s3, name="Close")
        >>> bob_closeTransition2 = CloseChannelTransition(startState=bob_s2, endState=bob_s3, name="Close")
        >>> bob_automata = Automata(bob_s0, symbolList)
        >>>
        >>> def cbk_method(current_state, current_transition, received_symbol, received_message, received_structure):
        ...     return bob_error_state
        >>> bob_automata.set_cbk_read_unexpected_symbol(cbk_method)
        >>> bob_automata.set_cbk_read_unknown_symbol(cbk_method)
        >>>
        >>> automata_ascii = bob_automata.generateASCII()
        >>> print(automata_ascii)
        #=========================#
        H           S0            H
        #=========================#
          |
          | OpenChannelTransition
          v
        +-------------------------+
        |           S1            |
        +-------------------------+
          |
          | T1 (Hello1;{Hello2})
          v
        +-------------------------+
        |           S2            |
        +-------------------------+
          |
          | CloseChannelTransition
          v
        +-------------------------+
        |           S3            |
        +-------------------------+
        <BLANKLINE>
        >>>
        >>> # Create Alice's automaton
        >>> alice_s0 = State(name="S0")
        >>> alice_s1 = State(name="S1")
        >>> alice_s2 = State(name="S2")
        >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
        >>> alice_mainTransition = Transition(startState=alice_s1, endState=alice_s1,
        ...                                   inputSymbol=symbol1, outputSymbols=[symbol1],
        ...                                   name="T1")
        >>> alice_closeTransition = CloseChannelTransition(startState=alice_s1, endState=alice_s2, name="Close")
        >>> alice_automata = Automata(alice_s0, symbolList)
        >>>
        >>> automata_ascii = alice_automata.generateASCII()
        >>> print(automata_ascii)
        #=========================#
        H           S0            H
        #=========================#
          |
          | OpenChannelTransition
          v
        +-------------------------+   T1 (Hello1;{Hello1})
        |                         | -----------------------+
        |           S1            |                        |
        |                         | <----------------------+
        +-------------------------+
          |
          | CloseChannelTransition
          v
        +-------------------------+
        |           S2            |
        +-------------------------+
        <BLANKLINE>
        >>>
        >>> # Create Bob actor (a client)
        >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
        >>> bob = Actor(automata=bob_automata, channel=channel, name="Bob")
        >>> bob.nbMaxTransitions = 10
        >>>
        >>> # Create Alice actor (a server)
        >>> channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
        >>> alice = Actor(automata=alice_automata, channel=channel, initiator=False, name="Alice")
        >>>
        >>> alice.start()
        >>> time.sleep(0.5)
        >>> bob.start()
        >>>
        >>> time.sleep(1)
        >>>
        >>> bob.stop()
        >>> alice.stop()
        >>>
        >>> print(bob.generateLog())
        Activity log for actor 'Bob' (initiator):
          [+] At state 'S0'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 'Open' (open channel)
          [+]   Transition 'Open' lead to state 'S1'
          [+] At state 'S1'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 'T1' (initiator)
          [+]   During transition 'T1', sending input symbol ('Hello1')
          [+]   During transition 'T1', receiving unexpected symbol triggered a callback that lead to state 'Error state'
          [+] At state 'Error state'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 'Close' (close channel)
          [+]   Transition 'Close' lead to state 'S3'
          [+] At state 'S3'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
        >>> print(alice.generateLog())
        Activity log for actor 'Alice' (not initiator):
          [+] At state 'S0'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 'Open' (open channel)
          [+]   Going to execute transition 'Open'
          [+]   Transition 'Open' lead to state 'S1'
          [+] At state 'S1'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Waiting for an input symbol to decide the transition (not initiator)
          [+]   Input symbol 'Hello1' corresponds to transition 'T1'
          [+]   During transition 'T1', choosing an output symbol ('Hello1')
          [+]   Transition 'T1' lead to state 'S1'
          [+] At state 'S1'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Waiting for an input symbol to decide the transition (not initiator)


        **Basic example of automata fuzzing**

        Mutators may be used in order to create fuzzed/mutated automaton.

        The following code shows the creation of the new automaton with
        random transitions between the existing states:

        >>> from netzob.all import *
        >>> import time
        >>> sym1 = Symbol([Field(String(nbChars=3))], name='Sym1')
        >>> sym2 = Symbol([Field(String(nbChars=5))], name='Sym2')
        >>> symbols = [sym1, sym2]
        >>> s0 = State(name="s0")
        >>> s1 = State(name="s1")
        >>> s2 = State(name="s2")
        >>> s3 = State(name="s3")
        >>> s4 = State(name="s4")
        >>> t0 = OpenChannelTransition(startState=s0, endState=s1,
        ...                            name="t0")
        >>> t1 = Transition(startState=s1, endState=s1,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t1")
        >>> t2 = Transition(startState=s1, endState=s2,
        ...                 inputSymbol=sym2, outputSymbols=[sym2],
        ...                 name="t2")
        >>> t3 = Transition(startState=s2, endState=s3,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t3")
        >>> t4 = CloseChannelTransition(startState=s2, endState=s4,
        ...                             name="t4")
        >>>
        >>> automata = Automata(s0, symbols=symbols)
        >>> automata_ascii = automata.generateASCII()
        >>> print(automata_ascii)
                                         #========================#
                                         H           s0           H
                                         #========================#
                                           |
                                           | OpenChannelTransition
                                           v
                                         +------------------------+   t1 (Sym1;{Sym1})
                                         |                        | -------------------+
                                         |           s1           |                    |
                                         |                        | <------------------+
                                         +------------------------+
                                           |
                                           | t2 (Sym2;{Sym2})
                                           v
        +----+  CloseChannelTransition   +------------------------+
        | s4 | <------------------------ |           s2           |
        +----+                           +------------------------+
                                           |
                                           | t3 (Sym1;{Sym1})
                                           v
                                         +------------------------+
                                         |           s3           |
                                         +------------------------+
        <BLANKLINE>
        >>>
        >>> # Generate a random automaton
        >>>
        >>> mutatedAutomata = automata.mutate()
        >>> automata_ascii_2 = mutatedAutomata.generateASCII()
        >>> print(automata_ascii_2)
        #========================#
        H           s0           H
        #========================#
          |
          | OpenChannelTransition
          v
        +----------------------------------------------------------------------------------------+   t1 (Sym1;{Sym1})
        |                                                                                        | -------------------+
        |                                           s1                                           |                    |
        |                                                                                        | <------------------+
        +----------------------------------------------------------------------------------------+
          |                         ^                               ^
          | t2 (Sym2;{Sym2})        | t_random (Sym1;{Sym1,Sym2})   | t_random (Sym2;{Sym1,Sym2})
          v                         |                               |
        +----------------------------------------------------------------------------------------+
        |                                           s2                                           |
        +----------------------------------------------------------------------------------------+
          |                                                         |
          | t3 (Sym1;{Sym1})                                        | CloseChannelTransition
          v                                                         v
        +------------------------+                                +------------------------------+
        |           s3           |                                |              s4              |
        +------------------------+                                +------------------------------+
        <BLANKLINE>
        >>>
        >>> # Generate a full automaton
        >>>
        >>> mutatedAutomata = automata.mutate(strategy=AutomataMutatorStrategy.FULL)
        >>>
        >>> # The ASCII representation is not displayed as it is too big
        >>>
        >>> # Generate an automaton with one main state
        >>>
        >>> mutatedAutomata = automata.mutate(strategy=AutomataMutatorStrategy.ONESTATE)
        >>> automata_ascii_2 = mutatedAutomata.generateASCII()
        >>> print(automata_ascii_2)
                                          #========================#
                                          H     Initial state      H
                                          #========================#
                                            |
                                            | OpenChannelTransition
                                            v
            t_random (Sym2;{Sym1,Sym2})   +------------------------+   t_random (Sym1;{Sym1,Sym2})
          +------------------------------ |                        | ------------------------------+
          |                               |       Main state       |                               |
          +-----------------------------> |                        | <-----------------------------+
                                          +------------------------+
        <BLANKLINE>
        >>>
        >>> # Generate an automaton with targeted fuzzing on one specific state
        >>>
        >>> mutatedAutomata = automata.mutate(strategy=AutomataMutatorStrategy.TARGETED, target=s2.name)
        >>> automata_ascii_2 = mutatedAutomata.generateASCII()
        >>> print(automata_ascii_2)
                                          #========================#
                                          H           s0           H
                                          #========================#
                                            |
                                            | OpenChannelTransition
                                            v
                                          +------------------------+
                                          |           s1           |
                                          +------------------------+
                                            |
                                            | t2 (Sym2;{Sym2})
                                            v
            t_random (Sym2;{Sym1,Sym2})   +------------------------+   t_random (Sym1;{Sym1,Sym2})
          +------------------------------ |                        | ------------------------------+
          |                               |           s2           |                               |
          +-----------------------------> |                        | <-----------------------------+
                                          +------------------------+
        <BLANKLINE>


        **Combining message formats and automata fuzzing**

        By combining message formats and automata fuzzing, it is possible
        to fuzz specific message formats at specific states in the
        automaton.

        The following code shows the creation of a mutated automaton
        with targeted automaton mutations at state 's6', and with a
        precision concerning the state at which fuzzing of message
        formats will be performed. Here, the message format fuzzing
        only applies at state 's6'. An actor is also created to
        simulate a target.

        >>> from netzob.all import *
        >>> import time
        >>> sym1 = Symbol([Field(uint16())], name='Sym1')
        >>> symbols = [sym1]
        >>> s0 = State(name="s0")
        >>> s1 = State(name="s1")
        >>> s2 = State(name="s2")
        >>> s3 = State(name="s3")
        >>> s4 = State(name="s4")
        >>> s5 = State(name="s5")
        >>> s6 = State(name="s6")
        >>> s7 = State(name="s7")
        >>> t0 = OpenChannelTransition(startState=s0, endState=s1,
        ...                            name="t0")
        >>> t1 = Transition(startState=s1, endState=s1,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t1")
        >>> t2 = Transition(startState=s1, endState=s2,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t2")
        >>> t3 = Transition(startState=s2, endState=s3,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t3")
        >>> t4 = Transition(startState=s2, endState=s4,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t4")
        >>> t5 = Transition(startState=s4, endState=s6,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t5")
        >>> t6 = Transition(startState=s3, endState=s5,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t6")
        >>> t7 = Transition(startState=s5, endState=s6,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t7")
        >>> t8 = Transition(startState=s6, endState=s6,
        ...                 inputSymbol=sym1, outputSymbols=[sym1],
        ...                 name="t8")
        >>> t9 = CloseChannelTransition(startState=s6, endState=s7,
        ...                             name="t9")
        >>>
        >>> automata = Automata(s0, symbols=symbols)
        >>> automata_ascii = automata.generateASCII()
        >>> print(automata_ascii)
                                   #=========================#
                                   H           s0            H
                                   #=========================#
                                     |
                                     | OpenChannelTransition
                                     v
                                   +-------------------------+   t1 (Sym1;{Sym1})
                                   |                         | -------------------+
                                   |           s1            |                    |
                                   |                         | <------------------+
                                   +-------------------------+
                                     |
                                     | t2 (Sym1;{Sym1})
                                     v
        +----+  t4 (Sym1;{Sym1})   +-------------------------+
        | s4 | <------------------ |           s2            |
        +----+                     +-------------------------+
          |                          |
          |                          | t3 (Sym1;{Sym1})
          |                          v
          |                        +-------------------------+
          |                        |           s3            |
          |                        +-------------------------+
          |                          |
          |                          | t6 (Sym1;{Sym1})
          |                          v
          |                        +-------------------------+
          |                        |           s5            |
          |                        +-------------------------+
          |                          |
          |                          | t7 (Sym1;{Sym1})
          |                          v
          |                        +-------------------------+   t8 (Sym1;{Sym1})
          |                        |                         | -------------------+
          |    t5 (Sym1;{Sym1})    |           s6            |                    |
          +----------------------> |                         | <------------------+
                                   +-------------------------+
                                     |
                                     | CloseChannelTransition
                                     v
                                   +-------------------------+
                                   |           s7            |
                                   +-------------------------+
        <BLANKLINE>
        >>> # Creation of a mutated automaton
        >>> mutatedAutomata = automata.mutate(strategy=AutomataMutatorStrategy.TARGETED, target=s6.name, seed=42)
        >>> automata_ascii = mutatedAutomata.generateASCII()
        >>> print(automata_ascii)
        #========================#
        H           s0           H
        #========================#
          |
          | OpenChannelTransition
          v
        +------------------------+
        |           s1           |
        +------------------------+
          |
          | t2 (Sym1;{Sym1})
          v
        +------------------------+
        |           s2           |
        +------------------------+
          |
          | t4 (Sym1;{Sym1})
          v
        +------------------------+
        |           s4           |
        +------------------------+
          |
          | t5 (Sym1;{Sym1})
          v
        +------------------------+   t_random (Sym1;{Sym1})
        |                        | -------------------------+
        |           s6           |                          |
        |                        | <------------------------+
        +------------------------+
        <BLANKLINE>
        >>>
        >>> # Define fuzzing configuration
        >>> preset_symbol1 = Preset(sym1)
        >>> preset_symbol1.fuzz(sym1)
        >>>
        >>> # Creation of an automaton visitor/actor and a channel on which to emit the fuzzed symbol
        >>> bob_channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
        >>> bob_actor = Actor(automata=mutatedAutomata, channel=bob_channel, name='Fuzzer')
        >>> bob_actor.fuzzing_presets = [preset_symbol1]
        >>> bob_actor.fuzzing_states = [s6.name]
        >>> bob_actor.nbMaxTransitions = 7
        >>>
        >>> # Create Alice's automaton
        >>> alice_s0 = State(name="s0")
        >>> alice_s1 = State(name="s1")
        >>> alice_openTransition = OpenChannelTransition(startState=alice_s0, endState=alice_s1, name="Open")
        >>> alice_transition1 = Transition(startState=alice_s1, endState=alice_s1,
        ...                                inputSymbol=sym1, outputSymbols=[sym1],
        ...                                name="T1")
        >>> alice_transition2 = Transition(startState=alice_s1, endState=alice_s1,
        ...                                inputSymbol=sym2, outputSymbols=[sym2],
        ...                                name="T2")
        >>> alice_automata = Automata(alice_s0, symbols)
        >>> automata_ascii = alice_automata.generateASCII()
        >>> print(automata_ascii)
                               #========================#
                               H           s0           H
                               #========================#
                                 |
                                 | OpenChannelTransition
                                 v
            T2 (Sym2;{Sym2})   +------------------------+   T1 (Sym1;{Sym1})
          +------------------- |                        | -------------------+
          |                    |           s1           |                    |
          +------------------> |                        | <------------------+
                               +------------------------+
        <BLANKLINE>
        >>>
        >>> # Creation of an automaton visitor/actor and a channel on which to receive the fuzzing traffic
        >>> alice_channel = UDPServer(localIP="127.0.0.1", localPort=8887, timeout=1.)
        >>>
        >>> # Creation of a callback function that returns a new transition
        >>> def cbk_modifyTransition(availableTransitions, nextTransition, current_state,
        ...                          last_sent_symbol, last_sent_message, last_sent_structure,
        ...                          last_received_symbol, last_received_message, last_received_structure, memory):
        ...     if nextTransition is None:
        ...         return alice_transition2
        ...     else:
        ...         return nextTransition
        >>>
        >>> alice_automata.getState('s1').add_cbk_modify_transition(cbk_modifyTransition)
        >>>
        >>> alice_actor = Actor(automata=alice_automata, channel=alice_channel, initiator=False, name='Target')
        >>>
        >>> # We start the targeted actor
        >>> alice_actor.start()
        >>> time.sleep(0.5)
        >>>
        >>> # We start the visitor, thus the fuzzing of message formats will be applied when specific states are reached
        >>> bob_actor.start()
        >>> time.sleep(1)
        >>>
        >>> bob_actor.stop()
        >>> alice_actor.stop()
        >>>
        >>> print(bob_actor.generateLog())
        Activity log for actor 'Fuzzer' (initiator):
          [+] At state 's0'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 't0' (open channel)
          [+]   Transition 't0' lead to state 's1'
          [+] At state 's1'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 't2' (initiator)
          [+]   During transition 't2', sending input symbol ('Sym1')
          [+]   During transition 't2', receiving expected output symbol ('Sym1')
          [+]   Transition 't2' lead to state 's2'
          [+] At state 's2'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 't4' (initiator)
          [+]   During transition 't4', sending input symbol ('Sym1')
          [+]   During transition 't4', receiving expected output symbol ('Sym1')
          [+]   Transition 't4' lead to state 's4'
          [+] At state 's4'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 't5' (initiator)
          [+]   During transition 't5', sending input symbol ('Sym1')
          [+]   During transition 't5', receiving expected output symbol ('Sym1')
          [+]   Transition 't5' lead to state 's6'
          [+] At state 's6'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 't_random' (initiator)
          [+]   During transition 't_random', sending input symbol ('Sym1')
          [+]   During transition 't_random', fuzzing activated
          [+]   During transition 't_random', receiving expected output symbol ('Sym1')
          [+]   Transition 't_random' lead to state 's6'
          [+] At state 's6'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 't_random' (initiator)
          [+]   During transition 't_random', sending input symbol ('Sym1')
          [+]   During transition 't_random', fuzzing activated
          [+]   During transition 't_random', receiving expected output symbol ('Sym1')
          [+]   Transition 't_random' lead to state 's6'
          [+] At state 's6'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 't_random' (initiator)
          [+]   During transition 't_random', sending input symbol ('Sym1')
          [+]   During transition 't_random', fuzzing activated
          [+]   During transition 't_random', receiving expected output symbol ('Sym1')
          [+]   Transition 't_random' lead to state 's6'
          [+] At state 's6', we reached the max number of transitions (7), so we stop
        >>> print(alice_actor.generateLog())
        Activity log for actor 'Target' (not initiator):
          [+] At state 's0'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Picking transition 'Open' (open channel)
          [+]   Going to execute transition 'Open'
          [+]   Transition 'Open' lead to state 's1'
          [+] At state 's1'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Waiting for an input symbol to decide the transition (not initiator)
          [+]   Input symbol 'Sym1' corresponds to transition 'T1'
          [+]   Changing transition to 'T1' (not initiator), through callback
          [+]   During transition 'T1', choosing an output symbol ('Sym1')
          [+]   Transition 'T1' lead to state 's1'
          [+] At state 's1'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Waiting for an input symbol to decide the transition (not initiator)
          [+]   Input symbol 'Sym1' corresponds to transition 'T1'
          [+]   Changing transition to 'T1' (not initiator), through callback
          [+]   During transition 'T1', choosing an output symbol ('Sym1')
          [+]   Transition 'T1' lead to state 's1'
          [+] At state 's1'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Waiting for an input symbol to decide the transition (not initiator)
          [+]   Input symbol 'Sym1' corresponds to transition 'T1'
          [+]   Changing transition to 'T1' (not initiator), through callback
          [+]   During transition 'T1', choosing an output symbol ('Sym1')
          [+]   Transition 'T1' lead to state 's1'
          [+] At state 's1'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Waiting for an input symbol to decide the transition (not initiator)
          [+]   Input symbol 'Sym1' corresponds to transition 'T1'
          [+]   Changing transition to 'T1' (not initiator), through callback
          [+]   During transition 'T1', choosing an output symbol ('Sym1')
          [+]   Transition 'T1' lead to state 's1'
          [+] At state 's1'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Waiting for an input symbol to decide the transition (not initiator)
          [+]   Input symbol 'Sym1' corresponds to transition 'T1'
          [+]   Changing transition to 'T1' (not initiator), through callback
          [+]   During transition 'T1', choosing an output symbol ('Sym1')
          [+]   Transition 'T1' lead to state 's1'
          [+] At state 's1'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Waiting for an input symbol to decide the transition (not initiator)
          [+]   Input symbol 'Sym1' corresponds to transition 'T1'
          [+]   Changing transition to 'T1' (not initiator), through callback
          [+]   During transition 'T1', choosing an output symbol ('Sym1')
          [+]   Transition 'T1' lead to state 's1'
          [+] At state 's1'
          [+]   Randomly choosing a transition to execute or to wait for an input symbol
          [+]   Waiting for an input symbol to decide the transition (not initiator)


        """

        from netzob.Fuzzing.Mutators.AutomataMutator import AutomataMutator, AutomataMutatorStrategy
        from netzob.Fuzzing.Mutator import Mutator

        if generator is None:
            generator = 'xorshift'
        if seed is None:
            seed = Mutator.SEED_DEFAULT
        if strategy is None:
            strategy = AutomataMutatorStrategy.RANDOM

        # Create mutator
        mutator = AutomataMutator(self, generator=generator, seed=seed)

        # Mutat automata
        mutatedAutomata = mutator.mutate(strategy=strategy, target=target)

        return mutatedAutomata

    ## Public properties ##

    @public_api
    @property
    def initialState(self):
        return self.__initialState

    @initialState.setter  # type: ignore
    @typeCheck(State)
    def initialState(self, initialState):
        if initialState is None:
            raise TypeError("AbstractionLayer cannot be None")
        self.__initialState = initialState

    @public_api
    @property
    def symbols(self):
        return self.__symbols

    @symbols.setter  # type: ignore
    @typeCheck(list)
    def symbols(self, symbols):
        self.__symbols = symbols
