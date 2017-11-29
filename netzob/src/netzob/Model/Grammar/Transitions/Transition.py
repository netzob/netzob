#-*- coding: utf-8 -*-

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

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import time
import random
import socket
from typing import Dict  # noqa: F401

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Model.Grammar.Transitions.AbstractTransition import AbstractTransition
from netzob.Simulator.AbstractionLayer import AbstractionLayer


@NetzobLogger
class Transition(AbstractTransition):
    """This class represents a transition between two states (an initial
    state and an end state) in an automaton. The initial state and the
    end state can be the same.

    The Transition constructor expects some parameters:

    :param startState: The initial state of the transition.
    :param endState: The end state of the transition.
    :param inputSymbol: The input symbol which triggers the execution of the
                        transition.
                        The default value is `None`, which means that no symbol
                        is expected in a receiving context, and no symbol is sent
                        in a sending context. Internally,
                        `None` symbol will be replaced by an
                        :class:`~netzob.Model.Vocabulary.EmptySymbol.EmptySymbol`.
    :param outputSymbols: A list of output symbols that can be expected when
                          the current transition is executed.
                          The default value is `None`, which means that no
                          symbol will be sent in a receiving context, and no
                          symbol is expected in a sending context.
                          Internally, `None` symbol will be replaced by an
                          :class:`~netzob.Model.Vocabulary.EmptySymbol.EmptySymbol`.
    :param name: The name of the transition. The default value is `None`.
    :type startState: :class:`~netzob.Model.Grammar.States.State.State`, required
    :type endState: :class:`~netzob.Model.Grammar.States.State.State`, required
    :type inputSymbol: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`, optional
    :type outputSymbols: a :class:`list` of :class:`~netzob.Model.Vocabulary.Symbol.Symbol`, optional
    :type name: :class:`str`, optional
    :param inputSymbolReactionTime: The timeout value in seconds to wait for the
                                    input value (only used in a receiving context).
    :param outputSymbolsReactionTime: A :class:`dict` containing, for each output
                                      symbol, the timeout value in seconds to
                                      wait for the output value (only used in a
                                      sending context).
    :type inputSymbolReactionTime: :class:`float`
    :type outputSymbolsReactionTime: :class:`dict` {:class:`~netzob.Model.Vocabulary.Symbol.Symbol`, :class:`float`}, optional


    The Transition class provides the following public variables:

    :var startState: The initial state of the transition.
    :var endState: The end state of the transition.
    :var active: Represents the current execution status of the transition.
                 If a transition is active, it means it has not yet finished
                 executing it.
    :var name: The name of the transition. The default value is `None`.
    :var inputSymbol: The input symbol is the symbol which triggers the
                      execution of the transition.
    :var outputSymbols: Output symbols that can be generated when
                        the current transition is executed.
    :var id: The unique identifier of the transition.
    :var description: description of the transition. If not explicitly set,
                      it is generated from the input and output symbols
    :var inputSymbolReactionTime: The timeout value in seconds to wait for the
                                  input value (only used in a receiving context).
                                  Default value is None (blocking).
    :var outputSymbolsReactionTime: A :class:`dict` containing, for each output
                                    symbol, the timeout value in seconds to
                                    wait for the output value (only used in a
                                    sending context). Default value is None (blocking).
    :vartype startState: :class:`~netzob.Model.Grammar.States.State.State`
    :vartype endState: :class:`~netzob.Model.Grammar.States.State.State`
    :vartype active: :class:`bool`
    :vartype name: :class:`str`
    :vartype inputSymbol: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`
    :vartype outputSymbols: :class:`list` of :class:`~netzob.Model.Vocabulary.Symbol.Symbol`
    :vartype id: :class:`uuid.UUID`
    :vartype description: :class:`str`
    :vartype inputSymbolReactionTime: :class:`float`
    :vartype outputSymbolsReactionTime: :class:`dict` {:class:`~netzob.Model.Vocabulary.Symbol.Symbol`, :class:`float`}

    The following example shows the definition of a transition `t` between
    two states, `s0` and `s1`:

    >>> from netzob.all import *
    >>> s0 = State()
    >>> s1 = State()
    >>> t = Transition(s0, s1)

    The following code shows access to attributes of a Transition:

    >>> print(t.name)
    None
    >>> s0 == t.startState
    True
    >>> s1 == t.endState
    True

    The following example shows the definition of a named Transition
    that accepts a specific input symbol and produces an output
    symbol from a list that contains one symbol element:

    >>> t = Transition(State(), State(), name="testTransition")
    >>> t.inputSymbol = Symbol()
    >>> t.outputSymbols = [Symbol()]

    """

    TYPE = "Transition"

    def __init__(self,
                 startState,
                 endState,
                 inputSymbol=None,
                 outputSymbols=None,
                 _id=None,
                 name=None,
                 inputSymbolReactionTime=None,   # type: float
                 outputSymbolsReactionTime=None  # type: Dict[Symbol,float]
                 ):
        # type: (...) -> None
        super(Transition, self).__init__(Transition.TYPE,
                                         startState,
                                         endState,
                                         _id,
                                         name,
                                         priority=10)

        if outputSymbols is None:
            outputSymbols = []

        self.inputSymbol = inputSymbol
        self.outputSymbols = outputSymbols
        self.outputSymbolProbabilities = {}  # TODO: not yet implemented
        self.inputSymbolReactionTime = inputSymbolReactionTime
        self.outputSymbolsReactionTime = outputSymbolsReactionTime

    @typeCheck(AbstractionLayer)
    def executeAsInitiator(self, abstractionLayer, actor):
        """Execute the current transition as an initiator.

        :param abstractionLayer: The abstraction layer which provides access
                                 to the channel.
        :type abstractionLayer: :class:`~netzob.Simulator.AbstractionLayer.AbstractionLayer`
        :return: The end state of the transition if no exception is raised.
        :rtype: :class:`~netzob.Model.Grammar.States.AbstractState.AbstractState`
        :raise: TypeError if parameter are not valid and Exception if an error
                occurs while executing the transition.

        Being an initiator means it will send the input symbol
        attached to the transition and then wait for the reception of
        one of the permitted output symbols.

        If the received symbol is part of the expected symbols
        (included in the list of output symbols) it returns the
        endState State of the transition. On the contrary, if the
        received symbol is not expected, it raises an exception.

        """
        if abstractionLayer is None:
            raise TypeError("Abstraction layer cannot be None")

        self.active = True

        # Retrieve the symbol to send
        symbol_to_send = self.inputSymbol
        symbol_presets = {}
        actor.visit_log.append("  [+]   During transition '{}', sending input symbol '{}'".format(self.name, str(symbol_to_send)))

        # If a callback is defined, we can change or modify the selected symbol
        self._logger.debug("[actor='{}'] Test if a callback function is defined at transition '{}'".format(str(actor), self.name))
        for cbk in self.cbk_modify_symbol:
            self._logger.debug("[actor='{}'] A callback function is defined at transition '{}'".format(str(actor), self.name))
            (symbol_to_send, symbol_presets) = cbk([symbol_to_send],
                                                   symbol_to_send,
                                                   self.startState,
                                                   abstractionLayer.last_sent_symbol,
                                                   abstractionLayer.last_sent_message,
                                                   abstractionLayer.last_received_symbol,
                                                   abstractionLayer.last_received_message)
            actor.visit_log.append("  [+]   During transition '{}', modifying input symbol to '{}', through callback".format(self.name, str(symbol_to_send)))
        else:
            self._logger.debug("[actor='{}'] No callback function is defined at transition '{}'".format(str(actor), self.name))

        # Write a symbol on the channel
        if isinstance(symbol_to_send, EmptySymbol):
            self._logger.debug("[actor='{}'] Nothing to write on abstraction layer (inputSymbol is an EmptySymbol)".format(str(actor)))    
        else:
            try:
                abstractionLayer.writeSymbol(symbol_to_send, presets=symbol_presets)
            except socket.timeout:
                self._logger.debug("[actor='{}'] Timeout on abstractionLayer.writeSymbol()".format(str(actor)))
                self.active = False
                raise
            except Exception as e:
                self.active = False
                errorMessage = "[actor='{}'] An error occured while executing the transition {} as an initiator: {}".format(str(actor), self.name, e)
                self._logger.debug(errorMessage)
                raise Exception(errorMessage)

        # Waits for the reception of a symbol
        try:
            (received_symbol, received_message) = abstractionLayer.readSymbol()
        except socket.timeout:
            self._logger.debug("[actor='{}'] Timeout on abstractionLayer.readSymbol()".format(str(actor)))
            self.active = False
            raise ReadSymbolTimeoutException(current_state=self.startState, current_transition=self)
        except Exception as e:
            self.active = False
            errorMessage = "[actor='{}'] An error occured while executing the transition {} as an initiator: {}".format(str(actor), self.name, e)
            self._logger.debug(errorMessage)
            raise Exception(errorMessage)

        # Computes the next state following the received symbol
        #   - if its an expected one, it returns the endState of the transition
        #   - if not it raises an exception
        for outputSymbol in self.outputSymbols:
            self._logger.debug("[actor='{}'] Possible output symbol: '{}' (id={}).".
                               format(str(actor), str(outputSymbol), outputSymbol.id))

        if received_symbol in self.outputSymbols:
            self.active = False
            actor.visit_log.append("  [+]   During transition '{}', receiving expected output symbol '{}'".format(self.name, str(received_symbol)))
            actor.visit_log.append("  [+]   Transition '{}' lead to state '{}'".format(self.name, str(self.endState)))

            return self.endState
        else:
            self.active = False
            self._logger.debug("[actor='{}'] Received symbol '{}' was unexpected.".format(str(actor), (received_symbol)))
            if isinstance(received_symbol, UnknownSymbol):
                actor.visit_log.append("  [+]   During transition '{}', receiving unknown symbol".format(self.name))
                raise ReadUnknownSymbolException(current_state=self.startState,
                                                 current_transition=self,
                                                 received_symbol=received_symbol,
                                                 received_message=received_message)
            else:
                actor.visit_log.append("  [+]   During transition '{}', receiving unexpected output symbol '{}'".format(self.name, str(received_symbol)))
                raise ReadUnexpectedSymbolException(current_state=self.startState,
                                                    current_transition=self,
                                                    received_symbol=received_symbol,
                                                    received_message=received_message)

    @typeCheck(AbstractionLayer)
    def executeAsNotInitiator(self, abstractionLayer, actor):
        """Execute the current transition as a not initiator.

        :param abstractionLayer: The abstraction layer which provides access to
                                 the channel.
        :type abstractionLayer: :class:`~netzob.Simulator.AbstractionLayer.AbstractionLayer`
        :return: The end state of the transition if not exception is raised.
        :rtype: :class:`~netzob.Model.Grammar.States.AbstractState.AbstractState`

        Being not an initiator means the startState has already received the
        input symbol which made it choose this transition.
        We only have to pick an output symbol and emit it.

        """
        if abstractionLayer is None:
            raise TypeError("Abstraction layer cannot be None")

        self.active = True

        # Pick the output symbol to emit
        (symbol_to_send, symbol_presets) = self.__pickOutputSymbol(abstractionLayer, actor)
        if symbol_to_send is None:
            self._logger.debug("[actor='{}'] No output symbol to send, we pick an EmptySymbol as output symbol".format(str(actor)))
            symbol_to_send = EmptySymbol()

        # Sleep before emiting the symbol (if equired)
        if symbol_to_send in list(self.outputSymbolsReactionTime.keys()):
            delay = self.outputSymbolsReactionTime[symbol_to_send]
            self._logger.debug("[actor='{}'] Time to wait before sending the output symbol: {}".format(str(actor), delay))
            time.sleep(delay)

        # Emit the symbol
        try:
            abstractionLayer.writeSymbol(symbol_to_send, presets=symbol_presets)
        except socket.timeout:
            self._logger.debug("[actor='{}'] Timeout on abstractionLayer.writeSymbol()".format(str(actor)))
            self.active = False
            return None
        except Exception as e:
            self._logger.debug("[actor='{}'] An exception occured when sending a symbol from the abstraction layer: '{}'".format(str(actor), e))
            self.active = False
            # self._logger.debug(traceback.format_exc())
            raise e

        # Return the endState
        self.active = False

        # Update visit log
        actor.visit_log.append("  [+]   Transition '{}' lead to state '{}'".format(self.name, str(self.endState)))

        return self.endState

    def __pickOutputSymbol(self, abstractionLayer, actor):
        """Picks the output symbol to emit following their probability.

        It computes the probability of symbols which don't explicitly have one
        by splitting the remaining available probability given by others.

        :return: the output symbol following their probability.
        :rtype: :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
        """

        # Randomly select an output symbol
        outputSymbolsWithProbability = dict()
        nbSymbolWithNoExplicitProbability = 0
        totalProbability = 0
        for outputSymbol in self.outputSymbols:
            if outputSymbol not in list(self.outputSymbolProbabilities.keys()):
                probability = None
                nbSymbolWithNoExplicitProbability += 1
            else:
                probability = self.outputSymbolProbabilities[outputSymbol]
                totalProbability += probability
            outputSymbolsWithProbability[outputSymbol] = probability

        if totalProbability > 100.0:
            raise ValueError(
                "The sum of output symbol's probability if above 100%")

        remainProbability = 100.0 - totalProbability

        # Share the remaining probability
        probabilityPerSymbolWithNoExplicitProbability = remainProbability / nbSymbolWithNoExplicitProbability

        # Update the probability
        for outputSymbol in self.outputSymbols:
            if outputSymbolsWithProbability[outputSymbol] is None:
                outputSymbolsWithProbability[
                    outputSymbol] = probabilityPerSymbolWithNoExplicitProbability

        # pick the good output symbol following the probability
        distribution = [
            outputSymbol
            for inner in [[k] * int(v) for k, v in list(
                outputSymbolsWithProbability.items())]
            for outputSymbolsWithNoProbability in inner
        ]

        # Random selection of the symbol
        symbol_to_send = random.choice(distribution)
        symbol_presets = {}

        # Update visit log
        actor.visit_log.append("  [+]   During transition '{}', choosing output symbol '{}'".format(self.name, str(symbol_to_send)))

        # Potentialy modify the selected symbol if a callback is defined
        self._logger.debug("[actor='{}'] Test if a callback function is defined at transition '{}'".format(str(actor), self.name))
        for cbk in self.cbk_modify_symbol:
            self._logger.debug("[actor='{}'] A callback function is executed at transition '{}'".format(str(actor), self.name))
            (symbol_to_send, symbol_presets) = cbk(self.outputSymbols,
                                                   symbol_to_send,
                                                   self.startState,
                                                   abstractionLayer.last_sent_symbol,
                                                   abstractionLayer.last_sent_message,
                                                   abstractionLayer.last_received_symbol,
                                                   abstractionLayer.last_received_message)
            actor.visit_log.append("  [+]   During transition '{}', modifying output symbol to '{}', through callback".format(self.name, str(symbol_to_send)))
        else:
            self._logger.debug("[actor='{}'] No callback function is defined at transition '{}'".format(str(actor), self.name))

        return (symbol_to_send, symbol_presets)

    # Properties

    @public_api
    @property
    def inputSymbol(self):
        """The input symbol is the symbol which triggers the execution
        of the transition.

        :type: :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
        """
        return self.__inputSymbol

    @inputSymbol.setter  # type: ignore
    @typeCheck(Symbol)
    def inputSymbol(self, inputSymbol):
        if inputSymbol is None:
            inputSymbol = EmptySymbol()

        self.__inputSymbol = inputSymbol

    @public_api
    @property
    def outputSymbols(self):
        """Output symbols that can be generated when
        the current transition is executed.

        >>> from netzob.all import *
        >>> transition = Transition(State(), State())
        >>> transition.outputSymbols = None
        >>> len(transition.outputSymbols)
        0
        >>> transition.outputSymbols.append(Symbol())
        >>> transition.outputSymbols.extend([Symbol(), Symbol()])
        >>> len(transition.outputSymbols)
        3
        >>> transition.outputSymbols = []
        >>> len(transition.outputSymbols)
        0

        :type: list of :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
        :raise: TypeError if not valid.
        """
        return self.__outputSymbols

    @outputSymbols.setter  # type: ignore
    def outputSymbols(self, outputSymbols):
        if outputSymbols is None:
            self.__outputSymbols = []
        else:
            for symbol in outputSymbols:
                if not isinstance(symbol, Symbol):
                    raise TypeError("One of the output symbol is not a Symbol")
            self.__outputSymbols = []
            for symbol in outputSymbols:
                if symbol is not None:
                    self.__outputSymbols.append(symbol)

    @public_api
    @property
    def description(self):
        if self._description is not None:
            return self._description
        else:
            desc = []
            for outputSymbol in self.outputSymbols:
                desc.append(str(outputSymbol.name))
            return self.name + " (" + str(
                self.inputSymbol.name) + ";{" + ",".join(desc) + "})"

    @public_api
    @property
    def outputSymbolsReactionTime(self):
        return self.__outputSymbolsReactionTime

    @outputSymbolsReactionTime.setter  # type: ignore
    def outputSymbolsReactionTime(self, outputSymbolsReactionTime):
        if outputSymbolsReactionTime is None:
            outputSymbolsReactionTime = {}
        elif not isinstance(outputSymbolsReactionTime, dict):
            raise TypeError("outputSymbolsReactionTime should be a dict of "
                            "Symbol and float, not {}"
                            .format(type(outputSymbolsReactionTime).__name__))
        self.__outputSymbolsReactionTime = outputSymbolsReactionTime
