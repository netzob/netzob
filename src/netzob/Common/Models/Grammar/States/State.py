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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Common.Models.Grammar.States.AbstractState import AbstractState
from netzob.Common.Models.Grammar.Transitions.AbstractTransition import AbstractTransition


@NetzobLogger
class State(AbstractState):
    """A state in the grammar of the protocol.

    >>> from netzob import *
    >>> s0 = State()
    >>> print s0.name
    None

    >>> s1 = State(name="S1")
    >>> print s1.name
    S1

    >>> t = Transition(s0, s1, None, None)
    >>> print t.startState.name
    None
    >>> print t.endState.name
    S1
    >>> print len(s0.transitions)
    1
    >>> print s0.transitions[0].startState.name
    None
    >>> print s0.transitions[0].endState.name
    S1

    """

    def __init__(self, _id=uuid.uuid4(), name=None):
        """
        :keyword _id: the unique identifier of the state
        :type _id: :class:`uuid.UUID`
        :keyword name: the name of the state
        :type name: :class:`str`
        """
        self.id = _id
        self.name = name
        self.__transitions = []

    @typeCheck(AbstractTransition)
    def removeTransition(self, transition):
        """remove the specified transition from the list
        of transition which starts on the current state.

        :param transition: the transition to remove
        :type transition: :class:`netzob.Common.Models.Grammar.Transitions.AbstractTransition`
        :raise: TypeError if param is not an Abstractransition and a ValueError if the transition
        is not registered

        """
        if transition not in self.__transitions:
            raise ValueError("The transition is not associated to the current state so cannot be removed.")
        self.__transitions.remove(transition)

    @property
    def id(self):
        """Unique identifier of the state

        :type: :class:`uuid.UUID`
        :raise: TypeError if not valid
        """
        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, _id):
        if _id is None:
            raise TypeError("id cannot be None")
        self.__id = _id

    @property
    def name(self):
        """Optional Name of the state

        :type: str
        :raise: TypeError is not an str
        """
        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, name):
        self.__name = name

    @property
    def transitions(self):
        return self.__transitions
