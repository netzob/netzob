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
from netzob.Inference.Grammar.AutomataFactories.OneStateAutomataFactory import OneStateAutomataFactory
from netzob.Inference.Grammar.AutomataFactories.ChainedStatesAutomataFactory import ChainedStatesAutomataFactory
from netzob.Inference.Grammar.AutomataFactories.PTAAutomataFactory import PTAAutomataFactory


@NetzobLogger
class Automata(object):
    """Class which describes an automaton (of a grammar) of a protocol.

    The Automata constructor expects some parameters:

    :param initialState: The initial state of the automaton.
    :param vocabulary: The list of permitted symbols for every transition of the automaton.
    :type initialState: :class:`State <netzob.Model.Grammar.States.State.State>`, required
    :type vocabulary: a :class:`list` of :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`, required

    The underlying structure of the automaton in the form of an SMMDT
    (i.e. Stochastic Mealy Machine with Deterministic Transitions),
    which is a Mealy machine (cf. https://en.wikipedia.org/wiki/Mealy_machine).


    The Automata class provides the following public variables:

    :var initialState: The initial state of the automaton.
    :var vocabulary: The list of permitted symbols for every transition of the automaton.
    :vartype initialState: :class:`State <netzob.Model.Grammar.States.State.State>`
    :vartype vocabulary: a :class:`list` of :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`


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

    @typeCheck(State, list)
    def __init__(self, initialState, vocabulary):
        self.initialState = initialState
        self.vocabulary = vocabulary  # A list of symbols

    def generateASCII(self):
        """Render the ASCII representation of the automaton.
        """

        f = tempfile.NamedTemporaryFile(delete=False)
        f.write(str.encode(self.generateDotCode()))
        f.close()

        cmd = ['/usr/bin/graph-easy', '--input', f.name, '--as_ascii']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.wait()
        result = p.stdout.read().decode("utf-8")

        os.unlink(f.name)

        return result

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

            descr = state.name

            for cbk in state.cbk_modify_transition:
                descr += " [CBK modify transition] "

            dotCode.append(
                '"{}" [shape={}, label="{}", style=filled, fillcolor={}, URL="{}"];'.
                format(state.name, shape, descr, color, state.id))

        for inputState in states:
            for transition in inputState.transitions:
                outputState = transition.endState

                descr = transition.description

                for cbk in transition.cbk_modify_symbol:
                    descr += " [CBK modify symbol] "
                
                dotCode.append(
                    '"{}" -> "{}" [fontsize=5, label="{}", URL="{}"];'.

                    format(inputState.name, outputState.name,
                           descr, transition.id))

        dotCode.append("}")

        return '\n'.join(dotCode)

    @public_api
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

        :return: A list containing all the discovered states.
        :rtype: a :class:`list` of :class:`State <netzob.Model.Grammar.States.State.State>`
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

    @public_api
    def getState(self, stateName):
        """Returns the State object of the given name.

        :param stateName: The name of the State object
        :type stateName: :class:`str`, required
        :return: The State object with stateName as name.
        :rtype: :class:`State <netzob.Model.Grammar.States.State.State>`
        :raise: :class:`KeyError` if the name is not found.
        """
        raise NotImplementedError

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
        :rtype: a :class:`Automata <netzob.Model.Grammar.Automata.Automata>`

        """
        return PTAAutomataFactory.generate(abstractSessions, symbolList)

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
    def vocabulary(self):
        return self.__vocabulary

    @vocabulary.setter  # type: ignore
    @typeCheck(list)
    def vocabulary(self, vocabulary):
        self.__vocabulary = vocabulary


    @public_api
    @typeCheck(callable)
    def set_cbk_read_symbol_timeout(self, cbk_method, states=None):
        """Function called to handle cases where a timeout appears when
        waiting for a symbol. For a server, this symbol would
        correspond to the input symbol that should trigger a
        transition. For a client, this symbol would correspond to an
        output symbol that is expected according to the current
        transition.

        :param cbk_method: A function used to handle the selection of the next
                           state when no symbol is received after the timeout
                           has expired.
        :type cbk_method: ~typing.Callable, required

        :param states: A list of states on which the callback function should apply.
                       If no states are specified, the callback function is
                       applied on all states of the automaton.
        :type states: ~typing.List[~netzob.Model.Grammar.States.State.State], optional

        :raise: :class:`TypeError` if :attr:`cbk_method` is not a callable function

        :attr:`cbk_method` should have the following prototype:

        .. function:: cbk_method(current_state, current_transition)
           :noindex:

           :param current_state:
             Corresponds to the current state in the automaton.
             It is expected that the current state may not be ``None``.
           :type current_state: ~netzob.Model.Grammar.States.State.State

           :param current_transition:
             Corresponds to the current transition in the automaton.
             It is expected that the current transition may be ``None``, especially
             in a server context, where no transition has been initiated.
           :type current_transition: ~netzob.Model.Grammar.Transitions.Transition.Transition

           :return:
             The callback function should return the next :class:`~netzob.Model.Grammar.States.State.State`.
             For example, to stay at the same state, the callback function
             would have to return the :attr:`current_state` value.

        """
        if not callable(cbk_method):
            raise TypeError("'cbk_method' should be a callable function")

        raise NotImplementedError("Not yet implemented")

    @public_api
    @typeCheck(callable, list)
    def set_cbk_read_unexpected_symbol(self, cbk_method, states=None):
        """Function called to handle cases where a symbol is received but not
        expected. In a server context, this symbol would not match the input
        symbol of the available transitions. In a client context, this
        symbol would not match the expected output symbols of the current
        transition.

        The method expects some parameters:

        :param cbk_method: A function used to handle the selection of the next
                           state when a unexpected symbol is received.
        :type cbk_method: ~typing.Callable, required

        :param states: A list of states on which the callback function should apply.
                       If no states are specified, the callback function is
                       applied on all states of the automaton.
        :type states: ~typing.List[~netzob.Model.Grammar.States.State.State], optional

        :raise: :class:`TypeError` if :attr:`cbk_method` is not a callable function

        :attr:`cbk_method` should have the following prototype:

        .. function:: cbk_method(current_state, current_transition=None,\
                                 received_symbol=None, received_message=None)
           :noindex:

           :param current_state:
             Corresponds to the current state in the automaton.
             It is expected that the current state may not be ``None``.
           :type current_state: ~netzob.Model.Grammar.States.State.State

           :param current_transition:
             Corresponds to the current transition in the automaton.
             It is expected that the current transition may be ``None``, especially
             in a server context, where no transition has been initiated.
           :type current_transition: ~netzob.Model.Grammar.Transitions.Transition.Transition

           :param received_symbol:
             Corresponds to the received symbol.
           :type received_symbol: ~netzob.Model.Vocabulary.Symbol.Symbol

           :param current_message:
             Corresponds to the received raw message.
           :type current_message: ~netzob.Model.Vocabulary.Messages.RawMessage.RawMessage

           :return:
             The callback function should return the next state.
             For example, to stay at the same state, the callback function
             would have to return the :attr:`current_state` value.
           :rtype: ~netzob.Model.Grammar.States.State.State

        """
        if not callable(cbk_method):
            raise TypeError("'cbk_method' should be a callable function")

        raise NotImplementedError("Not yet implemented")

    @public_api
    @typeCheck(callable, list)
    def set_cbk_read_unknown_symbol(self, cbk_method, states=None):
        """Function called to handle cases where a message is received but
        does not correspond to a known symbol. In a server context,
        this message would not match the input symbol of the available
        transitions. In a client context, this message would not match
        the expected output symbols of the current transition.

        The method expects some parameters:

        :param cbk_method: A callable function used to handle the selection of
                           the next state when an unknown symbol is received.
        :type cbk_method: ~typing.Callback, required

        :param states: A list of states on which the callback function should apply.
                       If no states are specified, the callback function is
                       applied on all states of the automaton.
        :type states: ~typing.List[~netzob.Model.Grammar.States.State.State], optional

        :raise: :class:`TypeError` if :attr:`cbk_method` is not a callable function

        :attr:`cbk_method` function should have the following prototype:

        .. function:: cbk_method(current_state, current_transition=None,\
                                 received_symbol=None, received_message=None)
           :noindex:

           :param current_state:
             Corresponds to the current state in the automaton.
             It is expected that the current state may not be ``None``.
           :type current_state: ~netzob.Model.Grammar.States.State.State

           :param current_transition:
             Corresponds to the current transition in the automaton.
             It is expected that the current transition may be ``None``,
             especially in a server context, where no transition has been initiated.
           :type current_transition: ~netzob.Model.Grammar.Transitions.Transition.Transition

           :param received_symbol:
             Corresponds to the received symbol.
           :type received_symbol: ~netzob.Model.Vocabulary.Symbol.Symbol

           :param current_message:
             Corresponds to the received raw message.
           :type received_message: ~netzob.Model.Vocabulary.Messages.RawMessage.RawMessage

        The callback function should return the next state
        (:class:`~netzob.Model.Grammar.States.State.State`). For
        example, to stay at the same state, the callback function
        would have to return the ``current_state`` value.

        """
        if not callable(cbk_method):
            raise TypeError("'cbk_method' should be a callable function")

        raise NotImplementedError("Not yet implemented")

