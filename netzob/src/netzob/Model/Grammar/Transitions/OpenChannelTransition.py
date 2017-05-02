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
class OpenChannelTransition(AbstractTransition):
    """This class represents a transition which, when executed, requests
    to open the current underlying communication channel.

    The OpenChannelTransition expects some parameters:

    :param startState: The initial state of the transition.
    :param endState: The end state of the transition
    :param _id: The unique identifier of the transition. The default value is a randomly generated UUID.
    :param name: The name of the transition. The default value is `None`
    :type startState: :class:`AbstractState <netzob.Model.Grammar.States.AbstractState.AbstractState>`, required
    :type endState: :class:`AbstractState <netzob.Model.Grammar.States.AbstractState.AbstractState>`, required
    :type _id: :class:`uuid.UUID`, optional
    :type name: :class:`str`, optional


    The following example shows the creation of an
    OpenChannelTransition transition:

    >>> from netzob.all import *
    >>> s0 = State()
    >>> s1 = State()
    >>> t = OpenChannelTransition(s0, s1)
    >>> print(t.name)
    None
    >>> print(s0 == t.startState)
    True
    >>> print(s1 == t.endState)
    True

    """

    TYPE = "OpenChannelTransition"

    def __init__(self, startState, endState, _id=None, name=None):
        super(OpenChannelTransition, self).__init__(
            OpenChannelTransition.TYPE,
            startState,
            endState,
            _id,
            name,
            priority=0)

    @typeCheck(AbstractionLayer)
    def executeAsInitiator(self, abstractionLayer):
        """Execute the current transition and open the communication channel. Being an initiator or not
        changes nothing from the open channel transition point of view.

        :param abstractionLayer: the abstraction layer which allows to access to the channel
        :type abstractionLayer: :class:`AbstractionLayer <netzob.Simulator.AbstractionLayer.AbstractionLayer>`
        :return: the end state of the transition if not exception is raised
        :rtype: :class:`AbstractState <netzob.Model.Grammar.States.AbstractState.AbstractState>`
        """
        return self.__execute(abstractionLayer)

    @typeCheck(AbstractionLayer)
    def executeAsNotInitiator(self, abstractionLayer):
        """Execute the current transition and open the communication channel. Being an initiator or not
        changes nothing from the open channel transition point of view.

        :param abstractionLayer: the abstraction layer which allows to access to the channel
        :type abstractionLayer: :class:`AbstractionLayer <netzob.Simulator.AbstractionLayer.AbstractionLayer>`
        :return: the end state of the transition if not exception is raised
        :rtype: :class:`AbstractState <netzob.Model.Grammar.States.AbstractState.AbstractState>`
        """
        return self.__execute(abstractionLayer)

    @typeCheck(AbstractionLayer)
    def __execute(self, abstractionLayer):
        """Execute the current transition and open the communication channel. Being an initiator or not
        changes nothing from the open channel transition point of view.

        :param abstractionLayer: the abstraction layer which allows to access to the channel
        :type abstractionLayer: :class:`AbstractionLayer <netzob.Simulator.AbstractionLayer.AbstractionLayer>`
        :return: the end state of the transition if not exception is raised
        :rtype: :class:`AbstractState <netzob.Model.Grammar.States.AbstractState.AbstractState>`
        """

        if abstractionLayer is None:
            raise TypeError("The abstraction layer cannot be None")

        self.active = True

        # open the channel throught the abstraction layer
        try:
            abstractionLayer.openChannel()
        except Exception as e:
            self._logger.warning(
                "An error occured which prevented the good execution of the open channel transition"
            )
            self.active = False
            raise e

        self.active = False
        return self.endState

    @property
    def description(self):
        if self._description is not None:
            return self._description
        else:
            return "OpenChannelTransition"
