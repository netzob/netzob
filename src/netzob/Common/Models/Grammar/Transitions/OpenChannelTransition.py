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
from netzob.Common.Models.Grammar.Transitions.AbstractTransition import AbstractTransition


class OpenChannelTransition(AbstractTransition):
    """Represents a transition which when executed request to open
   the current channel

    >>> from netzob import *
    >>> s0 = State()
    >>> s1 = State()
    >>> t = OpenChannelTransition(s0, s1)
    >>> print t.name
    None
    >>> print s0 == t.startState
    True
    >>> print s1 == t.endState
    True

    """

    def __init__(self, startState, endState, _id=uuid.uuid4(), name=None):
        """Constructor of an OpenChannelTransition.

        :param startState: initial state of the transition
        :type startState: :class:`netzob.Common.Models.Grammar.States.AbstractState.AbstractState`
        :param endState: end state of the transition
        :type endState: :class:`netzob.Common.Models.Grammar.States.AbstractState.AbstractState`
        :keyword _id: the unique identifier of the transition
        :param _id: :class:`uuid.UUID`
        :keyword name: the name of the transition
        :param name: :class:`str`

        """
        super(OpenChannelTransition, self).__init__(startState, endState, _id, name)
        self.__logger = logging.getLogger(__name__)
