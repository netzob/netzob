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
import socket

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Grammar.Transitions.Transition import Transition
from netzob.Model.Grammar.Transitions.OpenChannelTransition import OpenChannelTransition
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
    def copy(self):
        r"""Copy the current state.

        :return: A new object of the same type.
        :rtype: :class:`State <netzob.Model.Grammar.States.State.State>`

        """
        state = State(name=self.name)
        state.transitions = list(self.transitions)
        state.active = self.active
        state.cbk_modify_transition = list(self.cbk_modify_transition)
        state.cbk_filter_transitions = list(self.cbk_filter_transitions)
        return state

    def execute(self, actor):
        self._logger.debug("  [+] At state '{}'".format(self.name))
        actor.visit_log.append("  [+] At state '{}'".format(self.name))

        # If necessary, filter available transitions
        available_transitions = self.__filter_available_transitions(actor, self.transitions)

        # Check if the actor has received a message. If so, we execute the step as not an initiator
        if actor.abstractionLayer.check_received():

            # Check if we should consider reception (i.e. there exists at least one transition in inverseInitiator mode)
            should_consider_reception = False
            for transition in available_transitions:
                if isinstance(transition, Transition):
                    is_transition_initiator = (actor.initiator and not transition.inverseInitiator) or (not actor.initiator and transition.inverseInitiator)
                    if is_transition_initiator is False:
                        should_consider_reception = True
                        break

            if should_consider_reception:
                actor.visit_log.append("  [+] At state '{}', received packet on communication channel. Switching to execution as not initiator.".format(self.name))
                self._logger.debug("Data received on the communication channel. Switching to execution as not initiator to handle the received message.")
                return self.executeAsNotInitiator(actor, available_transitions)

        # Else, randomly pick a transition
        actor.visit_log.append("  [+]   Randomly choosing a transition to execute or to wait for an input symbol")
        next_transition = self.__pick_next_transition(actor, available_transitions)

        if next_transition is None:
            return None

        # If transition is in initiator mode
        if (actor.initiator and not next_transition.inverseInitiator) or (not actor.initiator and next_transition.inverseInitiator):

            # If necessary, modify the current transition
            next_transition = self.__modify_current_transition(actor, next_transition, available_transitions)

            # Execute next transition as initiator
            nextState = self.executeAsInitiator(actor, next_transition)
        else:
            # Execute next transition as not initiator
            nextState = self.executeAsNotInitiator(actor, available_transitions)

        return nextState

    def executeAsInitiator(self, actor, next_transition):
        """This method picks the next available transition and executes it.

        """

        self._logger.debug("[actor='{}'] Execute state {} as an initiator".format(str(actor), self.name))

        self.active = True

        self._logger.debug("[actor='{}'] Next transition for state '{}': {}.".format(str(actor), self.name, next_transition))

        # Execute picked transition as an initiator
        try:
            nextState = next_transition.executeAsInitiator(actor)
            self._logger.debug("[actor='{}'] Transition '{}' leads to state: {}.".format(str(actor), str(next_transition), str(nextState)))
        except Exception as e:
            self.active = False
            raise

        if nextState is None:
            self._logger.debug("[actor='{}'] The execution of transition '{}' on state '{}' did not return the next state".format(str(actor), str(next_transition), self.name))

        self.active = False

        return nextState

    def executeAsNotInitiator(self, actor, available_transitions):
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
            return None

        next_transition = None
        nextState = None

        # Execute the first special transition (inputSymbolProbability equals 100.0)
        for transition in self.transitions:
            if transition.inputSymbolProbability == 100.0:
                next_transition = transition

        # Else, execute the closing transition, if it is the last one remaining
        if next_transition is None:
            if len(self.transitions) == 1 and self.transitions[
                    0].TYPE == CloseChannelTransition.TYPE:
                next_transition = self.transitions[0]

        if next_transition is not None:

            actor.visit_log.append("  [+]   Going to execute transition '{}'".format(str(next_transition)))

            nextState = next_transition.executeAsNotInitiator(actor)
            self._logger.debug("[actor='{}'] Transition '{}' leads to state: {}.".format(
                str(actor), str(next_transition), str(nextState)))
            if nextState is None:
                self.active = False
                raise Exception(
                    "The execution of transition '{}' on state '{}' did not return the next state.".
                    format(next_transition.name, self.name))

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

            # Find the transition which accepts the received symbol as an input symbol, along with the correct input symbol preset
            next_transition = None
            for transition in self.transitions:

                is_transition_initiator = (actor.initiator and not transition.inverseInitiator) or (not actor.initiator and transition.inverseInitiator)

                if is_transition_initiator:
                    continue

                if transition.type == Transition.TYPE and id(transition.inputSymbol) == id(received_symbol):
                    if transition.inputSymbolPreset is not None:
                        self._logger.debug("Checking input symbol preset")
                        # Check preset
                        if received_symbol.check_preset(received_structure, transition.inputSymbolPreset):
                            self._logger.debug("Receive good symbol with good preset setting")
                            actor.visit_log.append("  [+]   Received one of the expected symbols ('{}'), with good preset settings ('{}')".format(received_symbol, transition.inputSymbolPreset))
                            next_transition = transition
                            break
                    else:
                        next_transition = transition
                        break

            actor.visit_log.append("  [+]   Input symbol '{}' corresponds to transition '{}'".format(str(received_symbol), str(next_transition)))

        except ActorStopException:
            raise
        except socket.timeout:
            self._logger.debug("[actor='{}'] In state '{}', timeout on abstractionLayer.readSymbol()".format(str(actor), self.name))

            # Check if there is a transition with an EmptySymbol as input symbol
            self._logger.debug("[actor='{}'] Check if a transition expects an EmptySymbol as input symbol".format(str(actor)))
            next_transition = None
            for transition in self.transitions:
                if transition.type == Transition.TYPE and isinstance(transition.inputSymbol, EmptySymbol):
                    self._logger.debug("[actor='{}'] The transition '{}' expects an EmptySymbol as input symbol ".format(str(actor), str(transition)))
                    next_transition = transition

                    actor.visit_log.append("  [+]   Receiving no symbol (EmptySymbol) corresponds to transition '{}'".format(str(next_transition)))

                    break
            else:
                self._logger.debug("[actor='{}'] No transition expects an EmptySymbol as input symbol".format(str(actor)))
                self.active = False

                if actor.automata.cbk_read_symbol_timeout is not None:
                    actor.automata.cbk_read_symbol_timeout(self, None)

                # Returning None here will stop the actor
                return

        except OSError as e:
            self._logger.debug("[actor='{}'] The underlying abstraction channel seems to be closed, so we stop the current actor".format(str(actor)))
            return
        except Exception as e:
            self._logger.debug("[actor='{}'] An exception occured when waiting for a symbol at state '{}': '{}'".format(str(actor), self.name, e))
            self.active = False
            raise

        # If a callback function is defined, we call it in order to execute an external program that may change the selected transition
        next_transition = self.__modify_current_transition(actor, next_transition, available_transitions)

        # Execute the retained transition
        if next_transition is None:
            self._logger.debug("[actor='{}'] The received symbol did not match any of the registered transition".format(str(actor)))
            #nextState = self

            # Handle case where received symbol is unknown
            if isinstance(received_symbol, UnknownSymbol):

                if actor.automata.cbk_read_unknown_symbol is not None:
                    actor.automata.cbk_read_unknown_symbol(self,
                                                           None,
                                                           received_message)
                else:
                    raise Exception("The received message is unknown")

            # Handle case where received symbol is known but unexpected
            else:

                if actor.automata.cbk_read_unexpected_symbol is not None:
                    actor.automata.cbk_read_unexpected_symbol(self,
                                                              None,
                                                              received_symbol,
                                                              received_message,
                                                              received_structure)
                else:
                    raise Exception("The received symbol did not match any of expected symbols, for actor '{}'".format(actor))

        else:

            for cbk in next_transition.cbk_action:
                self._logger.debug("[actor='{}'] A callback function is defined at the end of transition '{}'".format(str(actor), next_transition.name))
                cbk(received_symbol, received_message, received_structure, Operation.ABSTRACT, self, actor.memory)

            nextState = next_transition.executeAsNotInitiator(actor)
            self._logger.debug("[actor='{}'] Transition '{}' leads to state: {}.".format(str(actor), str(next_transition), str(nextState)))

        self.active = False

        return nextState

    def __pick_next_transition(self, actor, available_transitions):
        """Returns the next transition by considering the priority (inputSymbolProbability) of the transition and a random choice.

        It can return None.

        :return: the next transition or None if no transition available
        :rtype: :class:`AbstractTransition <netzob.Model.Grammar.Transition.AbstractTransition.AbstractTransition>`
        """

        # create a dictionary to host the available transition
        prioritizedTransitions = dict()
        for transition in available_transitions:
            # Handle transition priority (inputSymbolProbability)
            if transition.inputSymbolProbability in list(prioritizedTransitions.keys()):
                prioritizedTransitions[transition.inputSymbolProbability].append(transition.copy())
            else:
                prioritizedTransitions[transition.inputSymbolProbability] = [transition.copy()]

        if len(prioritizedTransitions) == 0:
            return None

        list_probabilities = sorted(prioritizedTransitions.keys())
        list_probabilities = list_probabilities[::-1]
        available_transitions = prioritizedTransitions[list_probabilities[0]]

        # Randomly select the next transition
        next_transition = random.choice(available_transitions)

        # Log initiator mode
        if isinstance(next_transition, Transition):
            is_transition_initiator = (actor.initiator and not next_transition.inverseInitiator) or (not actor.initiator and next_transition.inverseInitiator)
            if is_transition_initiator:
                actor.visit_log.append("  [+]   Picking transition '{}' (initiator)".format(next_transition))
            else:
                actor.visit_log.append("  [+]   Waiting for an input symbol to decide the transition (not initiator)")
        elif isinstance(next_transition, OpenChannelTransition):
            initiator_mode = "open channel"
            actor.visit_log.append("  [+]   Picking transition '{}' ({})".format(next_transition, initiator_mode))
        else:
            initiator_mode = "close channel"
            actor.visit_log.append("  [+]   Picking transition '{}' ({})".format(next_transition, initiator_mode))

        return next_transition

    def __modify_current_transition(self, actor, current_transition, available_transitions):
        r"""If a callback function is defined, we call it in order to execute
        an external program that may change the selected transition.

        """

        self._logger.debug("[actor='{}'] Test if a callback function is defined at state '{}'".format(actor, self.name))
        for cbk in self.cbk_modify_transition:
            self._logger.debug("[actor='{}'] A callback function is defined at state '{}'".format(actor, self.name))
            available_transitions = [cloned_transition.copy() for cloned_transition in available_transitions]
            current_transition = cbk(available_transitions,
                                     current_transition,
                                     self,
                                     actor.abstractionLayer.last_sent_symbol,
                                     actor.abstractionLayer.last_sent_message,
                                     actor.abstractionLayer.last_sent_structure,
                                     actor.abstractionLayer.last_received_symbol,
                                     actor.abstractionLayer.last_received_message,
                                     actor.abstractionLayer.last_received_structure,
                                     actor.memory)
            is_transition_initiator = (actor.initiator and not current_transition.inverseInitiator) or (not actor.initiator and current_transition.inverseInitiator)
            if is_transition_initiator:
                transition_mode = "initiator"
            else:
                transition_mode = "not initiator"
            actor.visit_log.append("  [+]   Changing transition to '{}' ({}), through callback".format(current_transition, transition_mode))
        else:
            self._logger.debug("[actor='{}'] No callback function is defined at state '{}'".format(actor, self.name))

        return current_transition

    def __filter_available_transitions(self, actor, available_transitions):
        r"""If a callback function is defined, we call it in order to execute
        an external program that may change the available transitions.

        """

        self._logger.debug("[actor='{}'] Test if a callback function is defined at state '{}'".format(actor, self.name))
        for cbk in self.cbk_filter_transitions:
            self._logger.debug("[actor='{}'] A callback function is defined at state '{}'".format(actor, self.name))
            available_transitions = [cloned_transition.copy() for cloned_transition in available_transitions]
            available_transitions = cbk(available_transitions,
                                        self,
                                        actor.abstractionLayer.last_sent_symbol,
                                        actor.abstractionLayer.last_sent_message,
                                        actor.abstractionLayer.last_sent_structure,
                                        actor.abstractionLayer.last_received_symbol,
                                        actor.abstractionLayer.last_received_message,
                                        actor.abstractionLayer.last_received_structure,
                                        actor.memory)
            actor.visit_log.append("  [+]   Filtering available transitions through callback")
        else:
            self._logger.debug("[actor='{}'] No callback function is defined at state '{}'".format(actor, self.name))

        return available_transitions

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


    # Test copy()

    >>> from netzob.all import *
    >>> s0 = State(name="s0")
    >>> s1 = State(name="s1")
    >>> t = CloseChannelTransition(s0, s1, name="transition")
    >>> s0.copy()
    s0

    """
