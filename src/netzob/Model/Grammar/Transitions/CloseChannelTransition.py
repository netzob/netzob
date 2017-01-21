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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Grammar.Transitions.AbstractTransition import AbstractTransition
from netzob.Simulator.AbstractionLayer import AbstractionLayer


@NetzobLogger
class CloseChannelTransition(AbstractTransition):
    """Represents a transition which when executed request to close
   the current channel

    >>> from netzob.all import *
    >>> s0 = State()
    >>> s1 = State()
    >>> t = CloseChannelTransition(s0, s1)
    >>> print(t.name)
    None
    >>> print(s0 == t.startState)
    True
    >>> print(s1 == t.endState)
    True

    """

    TYPE = "CloseChannelTransition"

    def __init__(self, startState, endState, _id=uuid.uuid4(), name=None):
        """Constructor of a CloseChannelTransition.

        :param startState: initial state of the transition
        :type startState: :class:`netzob.Model.Grammar.States.AbstractState.AbstractState`
        :param endState: end state of the transition
        :type endState: :class:`netzob.Model.Grammar.States.AbstractState.AbstractState`
        :keyword _id: the unique identifier of the transition
        :param _id: :class:`uuid.UUID`
        :keyword name: the name of the transition
        :param name: :class:`str`

        """
        super(CloseChannelTransition, self).__init__(CloseChannelTransition.TYPE, startState, endState, _id, name, priority=20)

    @typeCheck(AbstractionLayer)
    def executeAsInitiator(self, abstractionLayer):
        """Execute the current transition and close the communication channel. Being an initiator or not
        changes nothing from the close channel transition point of view.

        :param abstractionLayer: the abstraction layer which allows to access to the channel
        :type abstractionLayer: :class:`netzob.Simulator.AbstractionLayer.AbstractionLayer`
        :return: the end state of the transition if not exception is raised
        :rtype: :class:`netzob.Model.Grammar.States.AbstractState.AbstractState`
        """
        return self.__execute(abstractionLayer)

    @typeCheck(AbstractionLayer)
    def executeAsNotInitiator(self, abstractionLayer):
        """Execute the current transition and close the communication channel. Being an initiator or not
        changes nothing from the open close channel transition point of view.

        :param abstractionLayer: the abstraction layer which allows to access to the channel
        :type abstractionLayer: :class:`netzob.Simulator.AbstractionLayer.AbstractionLayer`
        :return: the end state of the transition if not exception is raised
        :rtype: :class:`netzob.Model.Grammar.States.AbstractState.AbstractState`
        """
        return self.__execute(abstractionLayer)

    @typeCheck(AbstractionLayer)
    def __execute(self, abstractionLayer):
        """Execute the current transition and close the communication channel. Being an initiator or not
        changes nothing from the close channel transition point of view.

        :param abstractionLayer: the abstraction layer which allows to access to the channel
        :type abstractionLayer: :class:`netzob.Simulator.AbstractionLayer.AbstractionLayer`
        :return: the end state of the transition if not exception is raised
        :rtype: :class:`netzob.Model.Grammar.States.AbstractState.AbstractState`
        """

        if abstractionLayer is None:
            raise TypeError("The abstraction layer cannot be None")

        self.active = True

        # close the channel throught the abstraction layer
        try:
            abstractionLayer.closeChannel()
        except Exception as e:
            self._logger.warning("An error occured which prevented the good execution of the close channel transition")
            self.active = False
            raise e

        self.active = False
        return self.endState

    @property
    def description(self):
        if self._description is not None:
            return self._description
        else:
            return "CloseChannelTransition"

