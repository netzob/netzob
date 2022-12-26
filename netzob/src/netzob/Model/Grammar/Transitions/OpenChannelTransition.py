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

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import public_api, NetzobLogger
from netzob.Model.Grammar.Transitions.AbstractTransition import AbstractTransition


@NetzobLogger
class OpenChannelTransition(AbstractTransition):
    """This class represents a transition which, when executed, requests
    to open the underlying communication channel that the actor uses
    to exchange messages with the peer (i.e. a call
    to the :meth:`open` method of the channel is made). The starting
    state of this transition corresponds to the initial state of the
    automaton.

    The OpenChannelTransition expects some parameters:

    :param startState: This parameter is the initial state of the transition. This also corresponds to the initial state of the
                       automaton.
    :param endState: This parameter is the end state of the transition.
    :param name: The name of the transition. The default value is `OpenChannelTransition`.
    :type startState: :class:`State <netzob.Model.Grammar.States.State.State>`, required
    :type endState: :class:`State <netzob.Model.Grammar.States.State.State>`, required
    :type name: :class:`str`, optional


    The OpenChannelTransition class provides the following public variables:

    :var startState: The initial state of the transition.
    :var endState: The end state of the transition.
    :var name: The name of the transition.
    :var description: description of the transition. If not explicitly set,
                      its value is 'OpenChannelTransition'.
    :vartype startState: :class:`State <netzob.Model.Grammar.States.State.State>`
    :vartype endState: :class:`State <netzob.Model.Grammar.States.State.State>`
    :vartype name: :class:`str`
    :vartype description: :class:`str`


    The following example shows the creation of an
    OpenChannelTransition transition:

    >>> from netzob.all import *
    >>> s0 = State()
    >>> s1 = State()
    >>> t = OpenChannelTransition(s0, s1, name="transition")
    >>> print(t.name)
    transition
    >>> s0 == t.startState
    True
    >>> s1 == t.endState
    True

    """

    TYPE = "OpenChannelTransition"

    @public_api
    def __init__(self, startState, endState, name="OpenChannelTransition"):
        super(OpenChannelTransition, self).__init__(
            OpenChannelTransition.TYPE,
            startState,
            endState,
            name)

        self.description = "OpenChannelTransition"
        self.inputSymbolProbability = 100.0

    @public_api
    def copy(self):
        r"""Copy the current transition.

        This method copies the transition object but keeps references to the
        original callbacks.

        :return: A new object of the same type.
        :rtype: :class:`OpenChannelTransition <netzob.Model.Grammar.Transitions.OpenChannelTransition.OpenChannelTransition>`

        """
        transition = OpenChannelTransition(startState=None,
                                           endState=self.endState,
                                           name=self.name)
        transition._startState = self.startState
        transition.description = self.description
        transition.active = self.active
        transition.inputSymbolProbability = self.inputSymbolProbability
        transition.cbk_modify_symbol = list(self.cbk_modify_symbol)
        transition.inverseInitiator = self.inverseInitiator
        return transition

    def executeAsInitiator(self, actor):
        """Execute the current transition and open the communication channel. Being an initiator or not
        changes nothing from the open channel transition point of view.

        :return: the end state of the transition if not exception is raised
        :rtype: :class:`AbstractState <netzob.Model.Grammar.States.AbstractState.AbstractState>`
        """
        return self.__execute(actor)

    def executeAsNotInitiator(self, actor):
        """Execute the current transition and open the communication channel. Being an initiator or not
        changes nothing from the open channel transition point of view.

        :return: the end state of the transition if not exception is raised
        :rtype: :class:`AbstractState <netzob.Model.Grammar.States.AbstractState.AbstractState>`
        """
        return self.__execute(actor)

    def __execute(self, actor):
        """Execute the current transition and open the communication channel. Being an initiator or not
        changes nothing from the open channel transition point of view.

        :return: the end state of the transition if not exception is raised
        :rtype: :class:`AbstractState <netzob.Model.Grammar.States.AbstractState.AbstractState>`
        """

        self.active = True

        # open the channel throught the abstraction layer
        try:
            actor.abstractionLayer.openChannel()
        except Exception as e:
            self._logger.debug(
                "[actor='{}'] An error occured which prevented the good execution of the open channel transition".format(actor.name)
            )
            self.active = False
            raise e

        self.active = False

        actor.visit_log.append("  [+]   Transition '{}' lead to state '{}'".format(self.name, str(self.endState)))
        return self.endState


def _test():
    r"""

    # Test copy()

    >>> from netzob.all import *
    >>> s0 = State()
    >>> s1 = State()
    >>> t = OpenChannelTransition(s0, s1, name="transition")
    >>> t.copy()
    transition

    """
