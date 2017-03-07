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
import abc

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Grammar.States.AbstractState import AbstractState


class AbstractTransition(object, metaclass=abc.ABCMeta):

    def __init__(self, _type, startState, endState, _id=uuid.uuid4(), name=None, priority=10, description=None):
        """Constructor of a Transition.

        :param _type: the type of the transition
        :type _type: :class:`str`
        :param startState: initial state of the transition
        :type startState: :class:`netzob.Model.Grammar.States.AbstractState.AbstractState`
        :param endState: end state of the transition
        :type endState: :class:`netzob.Model.Grammar.States.AbstractState.AbstractState`
        :keyword _id: the unique identifier of the transition
        :type _id: :class:`uuid.UUID`
        :keyword name: the name of the transition
        :type name: :class:`str`
        :keyword priority: the priority of the transition
        :type priority: :class:`int`

        """
        self.__startState = None
        self.__endState = None

        self.__startState = None
        self.__endState = None

        self.type = _type
        self.startState = startState
        self.endState = endState
        self.id = _id
        self.name = name
        self.priority = priority
        self._description = description
        self.active = False

    def __str__(self):
        return str(self.name)

    # Execution abstract methods

    @abc.abstractmethod
    def executeAsInitiator(self, abstractionLayer):
        pass

    @abc.abstractmethod
    def executeAsNotInitiator(self, abstractionLayer):
        pass

    # Priorities

    @property
    def type(self):
        """The type of the transition

        :type: :class:`str`
        """
        return self.__type

    @type.setter
    @typeCheck(str)
    def type(self, _type):
        if _type is None:
            raise TypeError("Type cannot be None")
        if len(_type) == 0:
            raise ValueError("Type cannot be an empty string")
        self.__type = _type

    @property
    def startState(self):
        """
        The start state from which the transition allows to go to the end state.

        When modifying the startState, it removes itself from previous start state

        >>> from netzob.all import *
        >>> s0 = State(name="S0")
        >>> s1 = State(name="S1")
        >>> s2 = State(name="S2")
        >>> t = Transition(s0, s1, name="T0")
        >>> print(t.startState.name)
        S0
        >>> print(len(s0.transitions))
        1
        >>> t.startState = s2
        >>> print(len(s0.transitions))
        0

        :type: :class:`netzob.Model.Grammar.State.AbstractState.AbstractState`
        :raise: TypeError if type of param is not valid
        """
        return self.__startState

    @startState.setter
    @typeCheck(AbstractState)
    def startState(self, startState):
        if self.__startState is not None:
            self.__startState.removeTransition(self)
        if startState is not None:
            startState.transitions.append(self)

        self.__startState = startState

    @property
    def endState(self):
        """
        The end state from which the transition allows to go from the start state

        >>> from netzob.all import *
        >>> s0 = State(name="S0")
        >>> s1 = State(name="S1")
        >>> t = Transition(s0, s1, name="T0")
        >>> print(t.endState.name)
        S1

        :type: :class:`netzob.Model.Grammar.State.AbstractState.AbstractState`
        :raise: TypeError if type of param is not valid
        """
        return self.__endState

    @endState.setter
    @typeCheck(AbstractState)
    def endState(self, endState):
        self.__endState = endState

    @property
    def priority(self):
        """The priority of the transition. The lower its its
        the highest priority it gets.
        For instance, an open and close channel transition are both declared
        with a priority of 0 whereas per default a transition has a priority of 10.

        >>> from netzob.all import *
        >>> s0 = State(name="Start")
        >>> s1 = State(name="End")
        >>> openTransition = OpenChannelTransition(s0, s1)
        >>> openTransition.priority
        0
        >>> transition = Transition(s1, s1, priority=1)
        >>> transition.priority
        1
        >>> transition.priority = 50
        >>> transition.priority
        50

        :type: :class:`int`
        """
        return self.__priority

    @priority.setter
    @typeCheck(int)
    def priority(self, priority):
        if priority is None:
            raise TypeError("Priority cannot be None")
        if priority < 0 or priority > 100:
            raise TypeError("The priority must respect range : 0<=priority<100")

        self.__priority = priority

    @property
    def active(self):
        """Represents the current execution status of the transition.
        If a transition is active, it means it did not yet finish to execute it

        :type: :class:`bool`
        """
        return self.__active

    @active.setter
    @typeCheck(bool)
    def active(self, active):
        if active is None:
            raise TypeError("The active info cannot be None")
        self.__active = active

    @property
    def description(self):
        return self._description

    @description.setter
    @typeCheck(str)
    def description(self, description):
        self._description = description

