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
import random
import traceback

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Model.Grammar.Transitions.Transition import Transition
from netzob.Model.Grammar.States.AbstractState import AbstractState
from netzob.Model.Grammar.Transitions.AbstractTransition import AbstractTransition
from netzob.Model.Grammar.Transitions.CloseChannelTransition import CloseChannelTransition


@NetzobLogger
class State(AbstractState):
    """A state in the grammar of the protocol.

    >>> from netzob.all import *
    >>> s0 = State()
    >>> print(s0.name)
    State

    >>> s1 = State(name="S1")
    >>> print(s1.name)
    S1

    >>> t = Transition(s0, s1, None, None)
    >>> print(t.startState.name)
    State
    >>> print(t.endState.name)
    S1
    >>> print(len(s0.transitions))
    1
    >>> print(s0.transitions[0].startState.name)
    State
    >>> print(s0.transitions[0].endState.name)
    S1

    """

    def __init__(self, name=None):
        """
        :keyword _id: the unique identifier of the state
        :type _id: :class:`uuid.UUID`
        :keyword name: the name of the state
        :type name: :class:`str`
        """
        super(State, self).__init__(name=name)
        self.__transitions = []

    @typeCheck(AbstractionLayer)
    def executeAsInitiator(self, abstractionLayer):
        """This method pick the next available transition and execute it.
        The abstraction layer that will be used is specified as a parameter.

        :parameter abstractionLayer: the abstraction layer that will be used to access to the channel
        :type abstractionLayer: :class:`netzob.Simulator.AbstractionLayer.AbstractionLayer`
        :raise Exceptions if an error occurs somewhere (sorry this is be vague i known @todo)
        """
        if abstractionLayer is None:
            raise TypeError("AbstractionLayer cannot be None")

        self._logger.debug("Execute state {0} as an initiator".format(self.name))

        self.active = True

        # Pick the next transition
        nextTransition = self.__pickNextTransition()
        self._logger.debug("Next transition: {0}.".format(nextTransition))

        if nextTransition is None:
            self.active = False
            raise Exception("No transition to execute, we stop here.")

        # Execute picked transition as an initiator
        try:
            nextState = nextTransition.executeAsInitiator(abstractionLayer)
            self._logger.debug("Transition '{0}' leads to state: {1}.".format(str(nextTransition), str(nextState)))
        except Exception as e:
            self.active = False
            raise e

        if nextState is None:
            self.active = False
            raise Exception("The execution of transition {0} on state {1} did not return the next state.".format(str(nextTransition), self.name))

        self.active = False
        return nextState

    @typeCheck(AbstractionLayer)
    def executeAsNotInitiator(self, abstractionLayer):
        """Execute the current state as not an initiator which means
        it will wait for a maximum amount of time the reception of a symbol and will try
        to select the appropriate transition which would be triggered by received symbol.
        At the end if no exception occur, it returns the next state.

        :param abstractionLayer: the abstraction layer from which it receives messages
        :type abstractionLayer: :class:`netzob.Simulator.AbstractionLayer.AbstractionLayer`
        :raise Exception if something goes bad (sorry for the lack of detail) @todo
        """
        if abstractionLayer is None:
            raise TypeError("AbstractionLayer cannot be None")

        self._logger.debug("Execute state {0} as a non-initiator".format(self.name))

        self.active = True

        # if no transition exists we quit
        if len(self.transitions) == 0:
            self._logger.warn("The current state has no transitions available.")
            self.active = False
            raise Exception("No transition available for this state.")

        nextTransition = None
        nextState = None

        # Execute the first special transition (priority equals 0)
        for transition in self.transitions:
            if transition.priority == 0:
                nextTransition = transition

        # Else, execute the closing transition, if it is the last one remaining
        if nextTransition is None:
            if len(self.transitions) == 1 and self.transitions[0].TYPE == CloseChannelTransition.TYPE:
                nextTransition = self.transitions[0]
            
        if nextTransition is not None:
            nextState = nextTransition.executeAsNotInitiator(abstractionLayer)
            self._logger.debug("Transition '{0}' leads to state: {1}.".format(str(nextTransition), str(nextState)))
            if nextState is None:
                self.active = False
                raise Exception("The execution of transition {0} on state {1} did not return the next state.".format(nextTransition.name, self.name))
            return nextState

        # Else, we wait to receive a symbol
        try:
            (receivedSymbol, receivedMessage) = abstractionLayer.readSymbol()
            if receivedSymbol is None:
                raise Exception("The abstraction layer returned a None received symbol")
            self._logger.debug("Input symbol: " + str(receivedSymbol.name))

            # Find the transition which accepts the received symbol as an input symbol
            nextTransition = None
            for transition in self.transitions:
                if transition.type == Transition.TYPE and transition.inputSymbol.id == receivedSymbol.id:
                    nextTransition = transition
                    break

            if nextTransition is None:
                self._logger.debug("The received symbol did not match any of the registered transition, we stay in place.")
                nextState = self
            else:
                nextState = nextTransition.executeAsNotInitiator(abstractionLayer)
                self._logger.debug("Transition '{0}' leads to state: {1}.".format(str(nextTransition), str(nextState)))

        except Exception as e:
            self._logger.warning("An exception occured when receiving a symbol from the abstraction layer.")
            self.active = False
            self._logger.warning(traceback.format_exc())
            raise e

        self.active = False
        return nextState

    def __pickNextTransition(self):
        """Returns the next transion by considering the priority
        and a random choice.

        It can return None.

        :return: the next transition or None if no transition available
        :rtype: :class:`netzob.Model.Grammar.Transition.AbstractTransition.AbstractTransition`
        """

        if len(self.transitions) == 0:
            return None

        # create a dictionnary to host the possible transition
        prioritizedTransitions = dict()
        for transition in self.transitions:
            if transition.priority in list(prioritizedTransitions.keys()):
                prioritizedTransitions[transition.priority].append(transition)
            else:
                prioritizedTransitions[transition.priority] = [transition]

        possibleTransitions = prioritizedTransitions[sorted(prioritizedTransitions.keys())[0]]

        if len(possibleTransitions) == 1:
            return possibleTransitions[0]

        idRandom = random.randint(0, len(possibleTransitions) - 1)
        return possibleTransitions[idRandom]

    @typeCheck(AbstractTransition)
    def removeTransition(self, transition):
        """remove the specified transition from the list
        of transition which starts on the current state.

        :param transition: the transition to remove
        :type transition: :class:`netzob.Model.Grammar.Transitions.AbstractTransition`
        :raise: TypeError if param is not an Abstractransition and a ValueError if the transition
        is not registered

        """
        if transition not in self.__transitions:
            raise ValueError("The transition is not associated to the current state so cannot be removed.")
        self.__transitions.remove(transition)

    @property
    def transitions(self):
        return self.__transitions

