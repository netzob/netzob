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
import random
# import traceback
import socket

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Simulator.AbstractionLayer import AbstractionLayer
from netzob.Model.Grammar.Transitions.Transition import Transition
from netzob.Model.Grammar.States.AbstractState import AbstractState
from netzob.Model.Grammar.Transitions.AbstractTransition import AbstractTransition
from netzob.Model.Grammar.Transitions.CloseChannelTransition import CloseChannelTransition
from netzob.Model.Vocabulary.EmptySymbol import EmptySymbol


@NetzobLogger
class State(AbstractState):
    """This class represents a state in an automaton.

    The State constructor expects some parameters:

    :param name: The name of the state. If `None`, it is set to 'State'.
    :type name: :class:`str`, optional


    The State class provides the following public variables:

    :var name: The name of the state. The default value is 'State'.
    :var active: Indicates that the current position of the actor in the automaton is this state.
                 If a state is active, it also means none of its transitions has yet
                 been fully initiated.
    :var transitions: The list of outgoing transitions
    :vartype name: :class:`str`
    :vartype active: :class:`bool`
    :vartype transitions: ~typing.List[~netzob.Model.Grammar.Transitions.Transition.Transition]


    The following example shows the definition of an `s0` state and an `s1` state:

    >>> from netzob.all import *
    >>> s0 = State()
    >>> s0.name
    'State'
    >>> s1 = State(name="S1")
    >>> s1.name
    'S1'

    """

    def __init__(self, name=None):
        super(State, self).__init__(name=name)
        self.__transitions = []

    @typeCheck(AbstractionLayer)
    def executeAsInitiator(self, abstractionLayer):
        """This method picks the next available transition and executes it.

        :parameter abstractionLayer: The abstraction layer that will be used to access to the channel.
        :type abstractionLayer: :class:`AbstractionLayer <netzob.Simulator.AbstractionLayer.AbstractionLayer>`
        """
        if abstractionLayer is None:
            raise TypeError("AbstractionLayer cannot be None")

        self._logger.debug(
            "Execute state {0} as an initiator".format(self.name))

        self.active = True

        # Pick the next transition
        nextTransition = self.__pickNextTransition(abstractionLayer)
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
            raise

        if nextState is None:
            self.active = False
            raise Exception(
                "The execution of transition {0} on state {1} did not return the next state.".
                format(str(nextTransition), self.name))

        self.active = False
        return nextState

    @typeCheck(AbstractionLayer)
    def executeAsNotInitiator(self, abstractionLayer):
        """This method executes the current state as not an initiator.

        :param abstractionLayer: The abstraction layer from which it receives messages.
        :type abstractionLayer: :class:`AbstractionLayer <netzob.Simulator.AbstractionLayer.AbstractionLayer>`

        This method will wait for a maximum amount of time the
        reception of a symbol and will try to select the appropriate
        transition which would be triggered by received symbol. At
        the end, if no exception occurs, it returns the next state.

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
            if len(self.transitions) == 1 and self.transitions[
                    0].TYPE == CloseChannelTransition.TYPE:
                nextTransition = self.transitions[0]

        if nextTransition is not None:
            nextState = nextTransition.executeAsNotInitiator(abstractionLayer)
            self._logger.debug("Transition '{0}' leads to state: {1}.".format(
                str(nextTransition), str(nextState)))
            if nextState is None:
                self.active = False
                raise Exception(
                    "The execution of transition {0} on state {1} did not return the next state.".
                    format(nextTransition.name, self.name))
            return nextState

        # Else, we wait to receive a symbol
        received_symbol = None
        received_message = None
        try:
            (received_symbol, received_message) = abstractionLayer.readSymbol()
            if received_symbol is None:
                raise Exception("The abstraction layer returned a None received symbol")
            self._logger.debug("Input symbol: " + str(received_symbol.name))

            # Find the transition which accepts the received symbol as an input symbol
            nextTransition = None
            for transition in self.transitions:
                if transition.type == Transition.TYPE and transition.inputSymbol.id == received_symbol.id:
                    nextTransition = transition
                    break

        except socket.timeout:
            self._logger.debug("Timeout on abstractionLayer.readSymbol()")

            # Check if there is a transition with an EmptySymbol as input symbol
            self._logger.debug("Check if a transition expects an EmptySymbol as input symbol")
            nextTransition = None
            for transition in self.transitions:
                if isinstance(transition.inputSymbol, EmptySymbol):
                    self._logger.debug("The transition '{}' expects an EmptySymbol as input symbol ".format(transition.name))
                    nextTransition = transition
                    break
            else:
                self._logger.debug("No transition expects an EmptySymbol as input symbol")
                self.active = False
                raise ReadSymbolTimeoutException(current_state=self, current_transition=None)

        except Exception as e:
            self._logger.warning("An exception occured when receiving a symbol from the abstraction layer.")
            self.active = False
            #self._logger.warning(traceback.format_exc())
            raise

        # If a callback function is defined, we call it in order to
        # execute an external program that may change the selected
        # transition
        self._logger.debug("Test if a callback function is defined at state '{}'".format(self.name))
        for cbk in self.cbk_modify_transition:
            self._logger.debug("A callback function is defined at state '{}'".format(self.name))
            availableTransitions = self.transitions
            nextTransition = cbk(availableTransitions,
                                 nextTransition,
                                 self,
                                 abstractionLayer.last_sent_symbol,
                                 abstractionLayer.last_sent_message,
                                 abstractionLayer.last_received_symbol,
                                 abstractionLayer.last_received_message)
        else:
            self._logger.debug("No callback function is defined at state '{}'".format(self.name))

        # Execute the retained transition
        if nextTransition is None:
            self._logger.debug("The received symbol did not match any of the registered transition")
            #nextState = self
            if isinstance(received_symbol, UnknownSymbol):
                raise ReadUnknownSymbolException(current_state=self,
                                                 current_transition=None,
                                                 received_symbol=received_symbol,
                                                 received_message=received_message)
            else:
                raise ReadUnexpectedSymbolException(current_state=self,
                                                    current_transition=None,
                                                    received_symbol=received_symbol,
                                                    received_message=received_message)
        else:
            nextState = nextTransition.executeAsNotInitiator(abstractionLayer)
            self._logger.debug("Transition '{0}' leads to state: {1}.".format(str(nextTransition), str(nextState)))

        self.active = False
        return nextState

    def __pickNextTransition(self, abstractionLayer):
        """Returns the next transition by considering the priority
        and a random choice.

        It can return None.

        :return: the next transition or None if no transition available
        :rtype: :class:`AbstractTransition <netzob.Model.Grammar.Transition.AbstractTransition.AbstractTransition>`
        """
        if len(self.transitions) == 0:
            return None

        # create a dictionnary to host the available transition
        prioritizedTransitions = dict()
        for transition in self.transitions:
            if transition.priority in list(prioritizedTransitions.keys()):
                prioritizedTransitions[transition.priority].append(transition)
            else:
                prioritizedTransitions[transition.priority] = [transition]

        availableTransitions = prioritizedTransitions[sorted(prioritizedTransitions.keys())[0]]

        # Randomly select the next transition
        nextTransition = random.choice(availableTransitions)

        # If a callback function is defined, we call it in order to
        # execute an external program that may change the selected
        # transition
        self._logger.debug("Test if a callback function is defined at state '{}'".format(self.name))
        for cbk in self.cbk_modify_transition:
            self._logger.debug("A callback function is defined at state '{}'".format(self.name))
            nextTransition = cbk(availableTransitions,
                                 nextTransition,
                                 self,
                                 abstractionLayer.last_sent_symbol,
                                 abstractionLayer.last_sent_message,
                                 abstractionLayer.last_received_symbol,
                                 abstractionLayer.last_received_message)
        else:
            self._logger.debug("No callback function is defined at state '{}'".format(self.name))

        return nextTransition

    @typeCheck(AbstractTransition)
    def removeTransition(self, transition):
        """remove the specified transition from the list
        of transition which starts on the current state.

        :param transition: the transition to remove
        :type transition: :class:`Transition <netzob.Model.Grammar.Transitions.Transition.Transition>`
        :raise: TypeError if param is not a Transition and a ValueError if the transition
                is not registered

        """
        if transition not in self.__transitions:
            raise ValueError("The transition is not associated to the current state so cannot be removed.")
        self.__transitions.remove(transition)

    @public_api
    @property
    def transitions(self):
        return self.__transitions


def _test():
    """
    >>> from netzob.all import *
    >>> s0 = State()
    >>> s0.name
    'State'
    >>> s1 = State(name="S1")
    >>> s1.name
    'S1'
    >>> t = Transition(s0, s1, None, None)
    >>> t.startState.name
    'State'
    >>> t.endState.name
    'S1'
    >>> len(s0.transitions)
    1
    >>> s0.transitions[0].startState.name
    'State'
    >>> s0.transitions[0].endState.name
    'S1'
    """
