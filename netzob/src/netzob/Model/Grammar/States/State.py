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
from netzob.Model.Grammar.Transitions.Transition import Transition
from netzob.Model.Grammar.States.AbstractState import AbstractState
from netzob.Model.Grammar.Transitions.AbstractTransition import AbstractTransition
from netzob.Model.Grammar.Transitions.CloseChannelTransition import CloseChannelTransition
from netzob.Model.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Model.Vocabulary.UnknownSymbol import UnknownSymbol
from netzob.Simulator.AbstractionLayer import Operation


@NetzobLogger
class State(AbstractState):
    """This class represents a state in an automaton.

    The State constructor expects some parameters:

    :param name: The name of the state. If `None`, it is set to 'State'.
    :type name: :class:`str`, optional


    The State class provides the following public variables:

    :var name: The name of the state. The default value is 'State'.
    :var transitions: The list of outgoing transitions
    :vartype name: :class:`str`
    :vartype transitions: ~typing.List[~netzob.Model.Grammar.Transitions.Transition.Transition]


    The following example shows the definition of an ``s0`` state and an ``s1`` state:

    >>> from netzob.all import *
    >>> s0 = State()
    >>> s0.name
    'State'
    >>> s1 = State(name="S1")
    >>> s1.name
    'S1'

    """

    @public_api
    def __init__(self, name=None):
        super(State, self).__init__(name=name)
        self.__transitions = []

    @public_api
    def clone(self):
        state = State(name=self.name)
        state.transitions = self.transitions
        state.active = self.active
        state.cbk_modify_transition = self.cbk_modify_transition
        return state

    def executeAsInitiator(self, actor):
        """This method picks the next available transition and executes it.

        """
        self._logger.debug(
            "[actor='{}'] Execute state {} as an initiator".format(str(actor), self.name))

        self.active = True

        # Pick the next transition
        nextTransition = self.__pickNextTransition(actor)
        self._logger.debug("[actor='{}'] Next transition for state '{}': {}.".format(str(actor), self.name, nextTransition))

        if nextTransition is None:
            self.active = False
            return

        # Execute picked transition as an initiator
        try:
            nextState = nextTransition.executeAsInitiator(actor)
            self._logger.debug("[actor='{}'] Transition '{}' leads to state: {}.".format(str(actor), str(nextTransition), str(nextState)))
        except Exception as e:
            self.active = False
            raise

        if nextState is None:
            self._logger.debug("[actor='{}'] The execution of transition '{}' on state '{}' did not return the next state".format(str(actor), str(nextTransition), self.name))

        self.active = False

        return nextState

    def executeAsNotInitiator(self, actor):
        """This method executes the current state as not an initiator.

        This method will wait for a maximum amount of time the
        reception of a symbol and will try to select the appropriate
        transition which would be triggered by received symbol. At
        the end, if no exception occurs, it returns the next state.

        """
        self._logger.debug("[actor='{}'] Execute state {} as a non-initiator".format(str(actor), self.name))

        self.active = True

        # if no transition exists we quit
        if len(self.transitions) == 0:
            self._logger.debug("[actor='{}'] The current state '{}' has no transitions available".format(str(actor), self.name))
            self.active = False
            return

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

            actor.visit_log.append("  [+] At state '{}'".format(self.name))
            actor.visit_log.append("  [+]   Picking transition '{}'".format(str(nextTransition)))

            nextState = nextTransition.executeAsNotInitiator(actor)
            self._logger.debug("[actor='{}'] Transition '{}' leads to state: {}.".format(
                str(actor), str(nextTransition), str(nextState)))
            if nextState is None:
                self.active = False
                raise Exception(
                    "The execution of transition '{}' on state '{}' did not return the next state.".
                    format(nextTransition.name, self.name))

            return nextState

        # Else, we wait to receive a symbol
        received_symbol = None
        received_message = None
        from netzob.Simulator.Actor import ActorStopException
        try:
            (received_symbol, received_message, received_structure) = actor.abstractionLayer.readSymbol()

            if received_symbol is None:
                raise Exception("The abstraction layer returned a None received symbol")
            self._logger.debug("[actor='{}'] Input symbol: '{}'".format(str(actor), str(received_symbol)))

            # Find the transition which accepts the received symbol as an input symbol
            nextTransition = None
            for transition in self.transitions:
                if transition.type == Transition.TYPE and id(transition.inputSymbol) == id(received_symbol):
                    nextTransition = transition
                    break

            actor.visit_log.append("  [+] At state '{}'".format(self.name))
            actor.visit_log.append("  [+]   Receiving input symbol '{}', which corresponds to transition '{}'".format(str(received_symbol), str(nextTransition)))

        except ActorStopException:
            raise
        except socket.timeout:
            self._logger.debug("[actor='{}'] In state '{}', timeout on abstractionLayer.readSymbol()".format(str(actor), self.name))

            # Check if there is a transition with an EmptySymbol as input symbol
            self._logger.debug("[actor='{}'] Check if a transition expects an EmptySymbol as input symbol".format(str(actor)))
            nextTransition = None
            for transition in self.transitions:
                if transition.type == Transition.TYPE and isinstance(transition.inputSymbol, EmptySymbol):
                    self._logger.debug("[actor='{}'] The transition '{}' expects an EmptySymbol as input symbol ".format(str(actor), str(transition)))
                    nextTransition = transition

                    actor.visit_log.append("  [+] At state '{}'".format(self.name))
                    actor.visit_log.append("  [+]   Receiving no symbol (EmptySymbol), which corresponds to transition '{}'".format(str(nextTransition)))

                    break
            else:
                self._logger.debug("[actor='{}'] No transition expects an EmptySymbol as input symbol".format(str(actor)))
                self.active = False

                if actor.automata.cbk_read_symbol_timeout is not None:
                    actor.automata.cbk_read_symbol_timeout(current_state=self, current_transition=None)

                # Returning None here will stop the actor
                return

        except OSError as e:
            self._logger.debug("[actor='{}'] The underlying abstraction channel seems to be closed, so we stop the current actor".format(str(actor)))
            return
        except Exception as e:
            self._logger.debug("[actor='{}'] An exception occured when waiting for a symbol at state '{}': '{}'".format(str(actor), self.name, e))
            self.active = False
            raise

        # If a callback function is defined, we call it in order to
        # execute an external program that may change the selected
        # transition
        self._logger.debug("[actor='{}'] Test if a callback function is defined at state '{}'".format(str(actor), self.name))
        for cbk in self.cbk_modify_transition:
            self._logger.debug("[actor='{}'] A callback function is defined at state '{}'".format(str(actor), self.name))
            availableTransitions = [cloned_transition.clone() for cloned_transition in self.transitions]
            nextTransition = cbk(availableTransitions,
                                 nextTransition,
                                 self,
                                 actor.abstractionLayer.last_sent_symbol,
                                 actor.abstractionLayer.last_sent_message,
                                 actor.abstractionLayer.last_sent_structure,
                                 actor.abstractionLayer.last_received_symbol,
                                 actor.abstractionLayer.last_received_message,
                                 actor.abstractionLayer.last_received_structure)

            actor.visit_log.append("  [+]   Changing transition to '{}', through callback".format(str(nextTransition)))
        else:
            self._logger.debug("[actor='{}'] No callback function is defined at state '{}'".format(str(actor), self.name))

        # Execute the retained transition
        if nextTransition is None:
            self._logger.debug("[actor='{}'] The received symbol did not match any of the registered transition".format(str(actor)))
            #nextState = self

            # Handle case where received symbol is unknown
            if isinstance(received_symbol, UnknownSymbol):

                if actor.automata.cbk_read_unknown_symbol is not None:
                    actor.automata.cbk_read_unknown_symbol(current_state=self,
                                                           current_transition=None,
                                                           received_symbol=received_symbol,
                                                           received_message=received_message)
                else:
                    raise Exception("The received message is unknown")

            # Handle case where received symbol is known but unexpected
            else:

                if actor.automata.cbk_read_unexpected_symbol is not None:
                    actor.automata.cbk_read_unexpected_symbol(current_state=self,
                                                              current_transition=None,
                                                              received_symbol=received_symbol,
                                                              received_message=received_message)
                else:
                    raise Exception("The received symbol did not match any of expected symbols, for actor '{}'".format(actor))

        else:

            for cbk in nextTransition.cbk_action:
                self._logger.debug("[actor='{}'] A callback function is defined at the end of transition '{}'".format(str(actor), nextTransition.name))
                cbk(received_symbol, received_message, received_structure, Operation.READ, actor)

            nextState = nextTransition.executeAsNotInitiator(actor)
            self._logger.debug("[actor='{}'] Transition '{}' leads to state: {}.".format(str(actor), str(nextTransition), str(nextState)))

        self.active = False

        return nextState

    def __pickNextTransition(self, actor):
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
                prioritizedTransitions[transition.priority].append(transition.clone())
            else:
                prioritizedTransitions[transition.priority] = [transition.clone()]

        availableTransitions = prioritizedTransitions[sorted(prioritizedTransitions.keys())[0]]

        # Randomly select the next transition
        nextTransition = random.choice(availableTransitions)

        # Update visit log
        actor.visit_log.append("  [+] At state '{}'".format(self.name))
        actor.visit_log.append("  [+]   Picking transition '{}'".format(str(nextTransition)))

        # If a callback function is defined, we call it in order to
        # execute an external program that may change the selected
        # transition
        self._logger.debug("[actor='{}'] Test if a callback function is defined at state '{}'".format(str(actor), self.name))
        for cbk in self.cbk_modify_transition:
            self._logger.debug("[actor='{}'] A callback function is defined at state '{}'".format(str(actor), self.name))
            nextTransition = cbk(availableTransitions,
                                 nextTransition,
                                 self,
                                 actor.abstractionLayer.last_sent_symbol,
                                 actor.abstractionLayer.last_sent_message,
                                 actor.abstractionLayer.last_sent_structure,
                                 actor.abstractionLayer.last_received_symbol,
                                 actor.abstractionLayer.last_received_message,
                                 actor.abstractionLayer.last_received_structure)
            actor.visit_log.append("  [+]   Changing transition to '{}', through callback".format(str(nextTransition)))
        else:
            self._logger.debug("[actor='{}'] No callback function is defined at state '{}'".format(str(actor), self.name))

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

    @transitions.setter  # type: ignore
    def transitions(self, transitions):
        self.__transitions = transitions


def _test():
    r"""
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


    # Test clone()

    >>> from netzob.all import *
    >>> s0 = State(name="s0")
    >>> s1 = State(name="s1")
    >>> t = CloseChannelTransition(s0, s1, name="transition")
    >>> s0.clone()
    s0

    """
