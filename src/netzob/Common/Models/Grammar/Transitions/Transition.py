#-*- coding: utf-8 -*-

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
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import uuid
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Common.Models.Vocabulary.Symbol import Symbol
from netzob.Common.Models.Grammar.Transitions.AbstractTransition import AbstractTransition
from netzob.Common.Models.Grammar.States.AbstractState import AbstractState


class Transition(AbstractTransition):
    """Represents a transition between two states.

    >>> from netzob import *
    >>> s0 = State()
    >>> s1 = State()
    >>> t = Transition(s0, s1)
    >>> print t.name
    None
    >>> print s0 == t.startState
    True
    >>> print s1 == t.endState
    True

    Additionnal informations can be attached to a transition

    >>> t = Transition(State(), State(), name="testTransition")
    >>> t.inputSymbol = Symbol()
    >>> t.outputSymbols = [Symbol()]

    """

    def __init__(self, startState, endState, inputSymbol=None, outputSymbols=[], _id=uuid.uuid4(), name=None):
        """Constructor of a Transition.

        :param startState: initial state of the transition
        :type startState: :class:`netzob.Common.Models.Grammar.States.AbstractState.AbstractState`
        :param endState: end state of the transition
        :type endState: :class:`netzob.Common.Models.Grammar.States.AbstractState.AbstractState`
        :keyword inputSymbol: the symbol which triggers the execution of the transition
        :type inputSymbol: :class:`netzob.Common.Models.Vocabulary.Symbol.Symbol`
        :keyword outputSymbols: a list of output Symbols
        :type outputSymbols: list of :class:`netzob.Common.Models.Vocabulary.Symbol.Symbol`
        :keyword _id: the unique identifier of the transition
        :param _id: :class:`uuid.UUID`
        :keyword name: the name of the transition
        :param name: :class:`str`

        """
        super(Transition, self).__init__(startState, endState, _id, name)
        self.__logger = logging.getLogger(__name__)

        self.inputSymbol = inputSymbol
        self.outputSymbols = outputSymbols

    @property
    def inputSymbol(self):
        """The input symbol is the symbol which triggers the execution
        of the transition.

        :type: :class:`netzob.Common.Models.Vocabulary.Symbol.Symbol`
        :raise: TypeError if not valid
        """
        return self.__inputSymbol

    @inputSymbol.setter
    @typeCheck(Symbol)
    def inputSymbol(self, inputSymbol):
        self.__inputSymbol = inputSymbol

    @property
    def outputSymbols(self):
        """Output symbols that can be generated when
        the current transition is executed.

        >>> from netzob import *
        >>> transition = Transition(State(), State())
        >>> transition.outputSymbols = None
        >>> len(transition.outputSymbols)
        0
        >>> transition.outputSymbols.append(Symbol())
        >>> transition.outputSymbols.extend([Symbol(), Symbol()])
        >>> print len(transition.outputSymbols)
        3
        >>> transition.outputSymbols = []
        >>> print len(transition.outputSymbols)
        0

        :type: list of :class:`netzob.Common.Models.Vocabulary.Symbol.Symbol`
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
