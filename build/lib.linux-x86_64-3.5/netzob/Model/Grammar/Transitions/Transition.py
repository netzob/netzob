#-*- coding: utf-8 -*-

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

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import uuid
import time
import random
    
#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Model.Grammar.Transitions.AbstractTransition import AbstractTransition
from netzob.Simulator.AbstractionLayer import AbstractionLayer


@NetzobLogger
class Transition(AbstractTransition):
    """Represents a transition between two states.

    >>> from netzob.all import *
    >>> s0 = State()
    >>> s1 = State()
    >>> t = Transition(s0, s1)
    >>> print(t.name)
    None
    >>> print(s0 == t.startState)
    True
    >>> print(s1 == t.endState)
    True

    Additionnal informations can be attached to a transition

    >>> t = Transition(State(), State(), name="testTransition")
    >>> t.inputSymbol = Symbol()
    >>> t.outputSymbols = [Symbol()]

    """

    TYPE = "Transition"

    def __init__(self, startState, endState, inputSymbol=None, outputSymbols=None, _id=uuid.uuid4(), name=None):
        """Constructor of a Transition.

        :param startState: initial state of the transition
        :type startState: :class:`netzob.Model.Grammar.States.AbstractState.AbstractState`
        :param endState: end state of the transition
        :type endState: :class:`netzob.Model.Grammar.States.AbstractState.AbstractState`
        :keyword inputSymbol: the symbol which triggers the execution of the transition
        :type inputSymbol: :class:`netzob.Model.Vocabulary.Symbol.Symbol`
        :keyword outputSymbols: a list of output Symbols
        :type outputSymbols: list of :class:`netzob.Model.Vocabulary.Symbol.Symbol`
        :keyword _id: the unique identifier of the transition
        :param _id: :class:`uuid.UUID`
        :keyword name: the name of the transition
        :param name: :class:`str`

        """
        super(Transition, self).__init__(Transition.TYPE, startState, endState, _id, name, priority=10)

        if outputSymbols is None:
            outputSymbols = []

        self.inputSymbol = inputSymbol
        self.outputSymbols = outputSymbols
        self.outputSymbolProbabilities = {}  # TODO: not yet implemented
        self.outputSymbolReactionTimes = {}  # TODO: not yet implemented

    @typeCheck(AbstractionLayer)
    def executeAsInitiator(self, abstractionLayer):
        """Execute the current transition as an initiator.
        Being an initiator means it will send the input symbol attached to the transition
        and wait for the reception of the output symbols.

        If the received symbol is part of the expected symbols (included in the list of output symbols)
        it returns the endState of the transition. On the contrary if the received symbol is not expected
        it raises an exception.

        :param abstractionLayer: the abstraction layer which allows to access to the channel
        :type abstractionLayer: :class:`netzob.Simulator.AbstractionLayer.AbstractionLayer`
        :return: the end state of the transition if not exception is raised
        :rtype: :class:`netzob.Model.Grammar.States.AbstractState.AbstractState`
        :raise: TypeError if parameter are not valid and Exception if an error occurs whil executing the transition.
        """
        if abstractionLayer is None:
            raise TypeError("Abstraction layer cannot be None")

        self.active = True

        try:
            # Write the input symbol on the channel
            abstractionLayer.writeSymbol(self.inputSymbol)

            # Waits for the reception of a symbol
            (receivedSymbol, receivedMessage) = abstractionLayer.readSymbol()

        except Exception as e:
            self.active = False
            self._logger.warning("An error occured while executing the transition {} as an initiator: {}".format(self.name, e))
            raise e

        # Computes the next state following the received symbol
        # if its an expected one, it returns the endState of the transition
        # if not it raises an exception
        for outputSymbol in self.outputSymbols:
            self._logger.debug("Possible output symbol: '{0}' (id={1}).".format(outputSymbol.name, outputSymbol.id))

        if receivedSymbol in self.outputSymbols:
            self.active = False
            return self.endState
        else:
            self.active = False
            errorMessage = "Received symbol '{}' was unexpected.".format(receivedSymbol.name)
            self._logger.warning(errorMessage)
            raise Exception(errorMessage)

    @typeCheck(AbstractionLayer)
    def executeAsNotInitiator(self, abstractionLayer):
        """Execute the current transition as a not initiator.
        Being not an initiator means the startState has already received the input symbol which made it
        choose this transition. We only have to pick an output symbol and emit it.

        :param abstractionLayer: the abstraction layer which allows to access to the channel
        :type abstractionLayer: :class:`netzob.Simulator.AbstractionLayer.AbstractionLayer`
        :return: the end state of the transition if not exception is raised
        :rtype: :class:`netzob.Model.Grammar.States.AbstractState.AbstractState`
        """
        if abstractionLayer is None:
            raise TypeError("Abstraction layer cannot be None")

        self.active = True

        # Pick the output symbol to emit
        pickedSymbol = self.__pickOutputSymbol()
        if pickedSymbol is None:
            self._logger.debug("No output symbol to send, we pick an EmptySymbol as output symbol.")
            pickedSymbol = EmptySymbol()

        # Sleep before emiting the symbol (if equired)
        if pickedSymbol in list(self.outputSymbolReactionTimes.keys()):
            time.sleep(self.outputSymbolReactionTimes[pickedSymbol])

        # Emit the symbol
        abstractionLayer.writeSymbol(pickedSymbol)

        # Return the endState
        self.active = False
        return self.endState

    def __pickOutputSymbol(self):
        """Picks the output symbol to emit following their probability.

        It computes the probability of symbols which don't explicitly have one by
        spliting the remaining available probability given by others.

        :return: the output symbol following their probability.
        :rtype: :class:`netzob.Model.Vocabulary.Symbol.Symbol`
        """
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
            raise ValueError("The sum of output symbol's probability if above 100%")

        remainProbability = 100.0 - totalProbability

        # Share the remaining probability
        probabilityPerSymbolWithNoExplicitProbability = remainProbability / nbSymbolWithNoExplicitProbability

        # Update the probability
        for outputSymbol in self.outputSymbols:
            if outputSymbolsWithProbability[outputSymbol] is None:
                outputSymbolsWithProbability[outputSymbol] = probabilityPerSymbolWithNoExplicitProbability

        # pick the good output symbol following the probability
        distribution = [outputSymbol for inner in [[k] * int(v) for k, v in list(outputSymbolsWithProbability.items())] for outputSymbolsWithNoProbability in inner]

        return random.choice(distribution)

    # Properties

    @property
    def inputSymbol(self):
        """The input symbol is the symbol which triggers the execution
        of the transition.

        :type: :class:`netzob.Model.Vocabulary.Symbol.Symbol`
        :raise: TypeError if not valid
        """
        return self.__inputSymbol

    @inputSymbol.setter
    @typeCheck(Symbol)
    def inputSymbol(self, inputSymbol):
        if inputSymbol is None:
            inputSymbol = EmptySymbol()

        self.__inputSymbol = inputSymbol

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
        >>> print(len(transition.outputSymbols))
        3
        >>> transition.outputSymbols = []
        >>> print(len(transition.outputSymbols))
        0

        :type: list of :class:`netzob.Model.Vocabulary.Symbol.Symbol`
        :raise: TypeError if not valid.
        """
        return self.__outputSymbols

    @outputSymbols.setter
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

    @property
    def description(self):
        if self._description is not None:
            return self._description
        else:
            desc = []
            for outputSymbol in self.outputSymbols:
                desc.append(str(outputSymbol.name))
            return self.name + " (" + str(self.inputSymbol.name) + ";{" + ",".join(desc) + "})"

