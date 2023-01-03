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
import time
import random
import socket

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api, NetzobLogger
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Preset import Preset
from netzob.Model.Vocabulary.EmptySymbol import EmptySymbol
from netzob.Model.Vocabulary.UnknownSymbol import UnknownSymbol
from netzob.Model.Grammar.Transitions.AbstractTransition import AbstractTransition
from netzob.Simulator.AbstractionLayer import Operation


@NetzobLogger
class Transition(AbstractTransition):
    """This class represents a transition between two states (an initial
    state and an end state) in an automaton. The initial state and the
    end state can be the same.

    A transition is either in an initiator or non initiator
    context. In an initiator context, the input symbol of the
    transition is emitted and one of the output symbols of the
    transition is expected. In non initiator context, the input symbol
    of the transition is expected and one of the output symbols of the
    transition is emitted.

    The context of the transition (either initiator or non initiator)
    is defined from the actor type that visits the automaton and from the
    value of the ``inverseInitiator`` attribute of the transition
    (which is by default set to ``False``). The context is defined as
    follows:

    * if the actor has its ``initiator`` attribute set to ``True``, and if the ``inverseInitiator`` attribute is set to ``True``, the transition context is ``initiator``;
    * if the actor has its ``initiator`` attribute set to ``True``, and if the ``inverseInitiator`` attribute is set to ``False``, the transition context is ``non initiator``;
    * if the actor has its ``initiator`` attribute set to ``False``, and if the ``inverseInitiator`` attribute is set to ``True``, the transition context is ``initiator``;
    * if the actor has its ``initiator`` attribute set to ``False``, and if the ``inverseInitiator`` attribute is set to ``False``, the transition context is ``non initiator``.

    When an actor encounters a state where multiple transitions are
    defined, a random choice is made amongst all these transitions by
    considering their probabilities. Two scenarios are possible:

    * if the picked transition is in an ``initiator`` context, this transition is executed;
    * otherwise, the executed transition depends on the received symbol.

    It is possible to define probability on transition selection during
    state processing, through the
    :attr:`~netzob.Model.Grammar.Transitions.Transition.Transition.inputSymbolProbability`
    attribute. This functionality makes it possible to implement a
    variety of state machines.

    .. note::
       In a state, if several transitions are available, where some of them expect to receive the input symbol (non initiator context) and the others expect to send the input symbol (initiator context), it is recommended in the last case to not set any output symbols to be received. In such a situation, it is better to handle the receiving of the potential peer symbols in a second state.

    Two transitions in the same context, initiator or non initiator,
    that start at the same state cannot have the same input symbol, as
    this symbol is used to determine the corresponding transition when
    receiving a new message. The only exception is when the
    transitions that have the same input symbol leverage the
    ``inputSymbolPreset`` attribute. In such case, the
    ``inputSymbolPreset`` attribute makes it possible to determine the
    corresponding transition based on field content from the same
    input symbol.

    The Transition constructor expects some parameters:

    :param startState: This parameter is the initial state of the transition.
    :param endState: This parameter is the end state of the transition.
    :param inputSymbol: The input symbol which triggers the execution of the
                        transition.
                        The default value is ``None``, which means that no symbol
                        is expected in a non initiator context, and no symbol is sent
                        in an initiator context. Internally,
                        `None` symbol will be replaced by an
                        :class:`~netzob.Model.Vocabulary.EmptySymbol.EmptySymbol`.
    :param outputSymbols: A list of expected output symbols when
                          the current transition is executed.
                          The default value is ``None``, which means that no
                          symbol will be sent in a non initiator context, and no
                          symbol is expected in an initiator context.
                          Internally, ``None`` symbol will be replaced by an
                          :class:`~netzob.Model.Vocabulary.EmptySymbol.EmptySymbol`.
    :param name: The name of the transition. The default value is `None`.
    :type startState: :class:`~netzob.Model.Grammar.States.State.State`, required
    :type endState: :class:`~netzob.Model.Grammar.States.State.State`, required
    :type inputSymbol: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`, optional
    :type outputSymbols: a :class:`list` of :class:`~netzob.Model.Vocabulary.Symbol.Symbol`, optional
    :type name: :class:`str`, optional


    The Transition class provides the following public variables:

    :var startState: The initial state of the transition.
    :var endState: The end state of the transition.
    :var inputSymbolProbability: This value holds the probability of the current transition of being chosen when processing the state where it is attached. The value between ``0.0`` and ``100.0`` corresponds to the weight of the transition in terms of selection probability. The default value is set to 10.0.
    :var inputSymbol: The input symbol is the symbol which triggers the
                      execution of the transition.
    :var outputSymbols: Output symbols that can be generated or expected when
                        the current transition is executed.
    :var inputSymbolPreset: A preset configuration
                            used during specialization and abstraction
                            of symbols emitted and received. During
                            specialization, values in this
                            configuration will override any field
                            definition, constraints or relationship
                            dependencies. During abstraction, this
                            structure is used to validate the data of
                            the received symbol. If the data does
                            not match, we leave the automaton or execute the function set by the :meth:`set_cbk_read_unexepected_symbol` method. See :class:`Preset
                            <netzob.Model.Vocabulary.Preset.Preset>`
                            for a complete explanation of Preset
                            usage.
    :var outputSymbolsPreset: A :class:`dict` of preset configurations
                              used during specialization and abstraction
                              of symbols emitted and received. During
                              specialization, values in this
                              configuration will override any field
                              definition, constraints or relationship
                              dependencies. During abstraction, this
                              structure is used to validate the data of
                              the received symbol. If the data does
                              not match, we leave the automaton or execute the function set by the :meth:`~netzob.Grammar.Automata.Automata.Automata.set_cbk_read_unexepected_symbol` method. See :class:`Preset
                              <netzob.Model.Vocabulary.Preset.Preset>`
                              for a complete explanation of Preset
                              usage.
    :var name: The name of the transition.
    :var inputSymbolReactionTime: The timeout value in seconds to wait for the
                                  input value (only used in a non initiator context).
    :var outputSymbolsReactionTime: A :class:`dict` containing, for
                                    each output symbol, the timeout
                                    value in seconds to wait for the
                                    output value (only used in an initiator context).
    :var outputSymbolsProbabilities: A structure that holds the selection probability of each symbol as an output symbol. The value between ``0.0`` and ``100.0`` corresponds to the weight of the symbol in terms of selection probability. The default value of each symbol as an output symbol is set to 10.0.
    :var inverseInitiator: Indicates to inverse the behavior of the actor ``initiator`` attribute.
    :var description: The description of the transition. If not explicitly set,
                      it is generated from the input and output symbol strings.
    :vartype startState: :class:`~netzob.Model.Grammar.States.State.State`
    :vartype endState: :class:`~netzob.Model.Grammar.States.State.State`
    :vartype inputSymbolProbability: :class:`float`
    :vartype inputSymbol: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`
    :vartype outputSymbols: :class:`list` of :class:`~netzob.Model.Vocabulary.Symbol.Symbol`
    :vartype inputSymbolPreset: :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`
    :vartype outputSymbolsPreset: :class:`dict` of :class:`Preset <netzob.Model.Vocabulary.Preset.Preset>`
    :vartype name: :class:`str`
    :vartype inputSymbolReactionTime: :class:`float`
    :vartype outputSymbolsReactionTime: :class:`dict` {:class:`~netzob.Model.Vocabulary.Symbol.Symbol`, :class:`float`}
    :vartype outputSymbolsProbabilities: :class:`dict` {:class:`~netzob.Model.Vocabulary.Symbol.Symbol`, :class:`float`}
    :vartype inverseInitiator: :class:`bool`
    :vartype description: :class:`str`


    The following example shows the definition of a transition `t` between
    two states, `s0` and `s1`:

    >>> from netzob.all import *
    >>> s0 = State()
    >>> s1 = State()
    >>> t = Transition(s0, s1, name="transition")

    The following code shows access to attributes of a Transition:

    >>> print(t.name)
    transition
    >>> s0 == t.startState
    True
    >>> s1 == t.endState
    True

    The following example shows the definition of a named Transition
    that accepts a specific input symbol and produces an output
    symbol from a list that contains one symbol element:

    >>> from netzob.all import *
    >>> t = Transition(State(), State(), name="testTransition")
    >>> t.inputSymbol = Symbol()
    >>> t.outputSymbols = [Symbol()]

    The following example shows the definition of a state with two
    transitions that have a different probability. Here, the transition T2 is twice as likely to be chosen as T1.

    >>> from netzob.all import *
    >>> s0 = State()
    >>> s1 = State()
    >>> s2 = State()
    >>> t1 = Transition(s0, s1, name="T1")
    >>> t1.inputSymbolProbability = 20.0
    >>> t2 = Transition(s0, s2, name="T2")
    >>> t2.inputSymbolProbability = 40.0

    """

    TYPE = "Transition"

    @public_api
    def __init__(self,
                 startState,
                 endState,
                 inputSymbol=None,
                 outputSymbols=None,
                 name=None
                 ):
        # type: (...) -> None
        super(Transition, self).__init__(Transition.TYPE,
                                         startState,
                                         endState,
                                         name)

        # Initialize public variables from parameters
        self.inputSymbol = inputSymbol
        self.outputSymbols = outputSymbols

        # Initialize other public variables
        self.inputSymbolPreset = None
        self.outputSymbolsPreset = None
        self.inputSymbolProbability = 10.0
        self.outputSymbolsProbabilities = {}
        self.inputSymbolReactionTime = None
        self.outputSymbolsReactionTime = None
        self.description = None

        # Initialize internal variables
        self.cbk_action = []

    @public_api
    def copy(self):
        r"""Copy the current transition.

        This method copies the transition object but keeps references to the
        original callbacks and symbols.

        :return: A new object of the same type.
        :rtype: :class:`Transition <netzob.Model.Grammar.Transitions.Transition.Transition>`

        """
        transition = Transition(startState=None,
                                endState=self.endState,
                                inputSymbol=self.inputSymbol,
                                outputSymbols=self.outputSymbols,
                                name=self.name)
        transition._startState = self.startState
        transition.description = self.description
        transition.active = self.active
        transition.inputSymbolProbability = self.inputSymbolProbability
        transition.cbk_modify_symbol = list(self.cbk_modify_symbol)
        transition.cbk_action = list(self.cbk_action)
        if self.inputSymbolPreset is not None:
            transition.inputSymbolPreset = self.inputSymbolPreset.copy()
        transition.inputSymbolReactionTime = self.inputSymbolReactionTime
        if self.outputSymbolsPreset is not None:
            transition.outputSymbolsPreset = self.outputSymbolsPreset.copy()
        if self.outputSymbolsReactionTime is not None:
            transition.outputSymbolsReactionTime = self.outputSymbolsReactionTime.copy()
        transition.inverseInitiator = self.inverseInitiator

        return transition

    def executeAsInitiator(self, actor):
        """Execute the current transition as an initiator.

        :return: The end state of the transition if no exception is raised.
        :rtype: :class:`~netzob.Model.Grammar.States.AbstractState.AbstractState`
        :raise: TypeError if parameter are not valid and Exception if an error
                occurs while executing the transition.

        Being an initiator means it will send the input symbol
        attached to the transition and then wait for the reception of
        one of the permitted output symbols.

        If the received symbol is part of the expected symbols
        (included in the list of output symbols) it returns the
        endState State of the transition. On the contrary, if the
        received symbol is not expected, it raises an exception.

        """

        self.active = True

        # Retrieve the symbol to send
        symbol_to_send = self.inputSymbol
        symbol_preset = self.inputSymbolPreset
        if self.inputSymbolPreset is not None:
            actor.visit_log.append("  [+]   During transition '{}', sending input symbol ('{}') with preset ('{}')".format(self.name, str(symbol_to_send), self.inputSymbolPreset))
        else:
            actor.visit_log.append("  [+]   During transition '{}', sending input symbol ('{}')".format(self.name, str(symbol_to_send)))

        # If a callback is defined, we can change or modify the selected symbol
        self._logger.debug("[actor='{}'] Test if a callback function is defined at transition '{}'".format(str(actor), self.name))
        for cbk in self.cbk_modify_symbol:
            self._logger.debug("[actor='{}'] A callback function is defined at transition '{}'".format(str(actor), self.name))
            (symbol_to_send, symbol_preset) = cbk([symbol_to_send],
                                                   symbol_to_send,
                                                   symbol_preset,
                                                   self.startState,
                                                   actor.abstractionLayer.last_sent_symbol,
                                                   actor.abstractionLayer.last_sent_message,
                                                   actor.abstractionLayer.last_sent_structure,
                                                   actor.abstractionLayer.last_received_symbol,
                                                   actor.abstractionLayer.last_received_message,
                                                   actor.abstractionLayer.last_received_structure,
                                                   actor.memory)
            actor.visit_log.append("  [+]   During transition '{}', modifying input symbol to '{}', through callback".format(self.name, str(symbol_to_send)))
        else:
            self._logger.debug("[actor='{}'] No callback function is defined at transition '{}'".format(str(actor), self.name))

        # Write a symbol on the channel
        if isinstance(symbol_to_send, EmptySymbol):
            self._logger.debug("[actor='{}'] Nothing to write on abstraction layer (inputSymbol is an EmptySymbol)".format(str(actor)))
        else:
            # Configure symbol preset
            tmp_preset = Preset(symbol_to_send)

            # Handle actor preset
            if actor is not None and actor.presets is not None:
                for tmp_actor_preset in actor.presets:
                    if tmp_actor_preset.symbol == symbol_to_send:
                        tmp_preset.update(tmp_actor_preset)
                        break

            # Handly symbol preset specified at current transition
            if isinstance(symbol_preset, Preset):
                tmp_preset.update(symbol_preset)

            # Handle fuzzing preset specified at actor level
            if actor.fuzzing_presets is not None and (len(actor.fuzzing_states) == 0 or self.startState.name in actor.fuzzing_states):
                for tmp_fuzzing_preset in actor.fuzzing_presets:
                    if tmp_fuzzing_preset.symbol == symbol_to_send:
                        self._logger.debug("[actor='{}'] Fuzzing activated at transition".format(str(actor)))
                        actor.visit_log.append("  [+]   During transition '{}', fuzzing activated".format(self.name))
                        tmp_preset.update(tmp_fuzzing_preset)
                        break

            try:
                (data, data_len, data_structure) = actor.abstractionLayer.writeSymbol(symbol_to_send, preset=tmp_preset, cbk_action=self.cbk_action)
            except socket.timeout:
                self._logger.debug("[actor='{}'] In transition '{}', timeout on abstractionLayer.writeSymbol()".format(str(actor), self.name))
                self.active = False
                raise
            except OSError as e:
                self._logger.debug("[actor='{}'] The underlying abstraction channel seems to be closed, so we stop the current actor".format(str(actor)))
                return
            except Exception as e:
                self.active = False
                errorMessage = "[actor='{}'] An error occured while executing the transition {} as an initiator: {}".format(str(actor), self.name, e)
                self._logger.debug(errorMessage)
                raise Exception(errorMessage)

        if len(self.outputSymbols) == 0 or (len(self.outputSymbols) == 1 and isinstance(self.outputSymbols[0], EmptySymbol)):
            self.active = False
            actor.visit_log.append("  [+]   During transition '{}', receiving no symbol which was expected".format(self.name))
            actor.visit_log.append("  [+]   Transition '{}' lead to state '{}'".format(self.name, str(self.endState)))

            return self.endState

        # Waits for the reception of a symbol
        from netzob.Simulator.Actor import ActorStopException
        try:
            (received_symbol, received_message, received_structure) = actor.abstractionLayer.readSymbol(self.outputSymbolsPreset)
        except ActorStopException:
            raise
        except socket.timeout:
            self._logger.debug("[actor='{}'] In transition '{}', timeout on abstractionLayer.readSymbol()".format(str(actor), self.name))
            self.active = False

            if actor.automata.cbk_read_symbol_timeout is not None:
                nextState = actor.automata.cbk_read_symbol_timeout(self.startState, self)

                actor.visit_log.append("  [+]   During transition '{}', timeout in reception triggered a callback that lead to state '{}'".format(self.name, str(nextState)))

                return nextState
            else:
                actor.visit_log.append("  [+]   During transition '{}', timeout in reception of a symbol, leading to state '{}'".format(self.name, str(self.startState)))
                # Return the start state so that we accept a new message
                return self.startState

        except OSError as e:
            self._logger.debug("[actor='{}'] The underlying abstraction channel seems to be closed, so we stop the current actor".format(str(actor)))
            return
        except Exception as e:
            self.active = False
            errorMessage = "[actor='{}'] An error occured while executing the transition {} as an initiator: {}".format(str(actor), self.name, e)
            self._logger.debug(errorMessage)
            raise Exception(errorMessage)

        # Computes the next state following the received symbol
        if received_symbol in self.outputSymbols:
            self.active = False
            if received_symbol in self.outputSymbolsPreset:
                output_preset = self.outputSymbolsPreset[received_symbol]
            else:
                output_preset = None

            # Check symbol regarding its expected preset
            if output_preset is not None:
                actor.visit_log.append("  [+]   PAN")
                if received_symbol.check_preset(received_structure, output_preset):
                    self._logger.debug("Receive good symbol with good preset setting")
                    actor.visit_log.append("  [+]   During transition '{}', receiving expected output symbol ('{}'), with good preset settings ('{}')".format(self.name, str(received_symbol), output_preset))
                else:
                    self._logger.debug("Receive good symbol but with wrong preset setting")
                    actor.visit_log.append("  [+]   During transition '{}', received expected symbol with wrong settings".format(self.name))

                    # We leave the automaton
                    return None

            else:
                actor.visit_log.append("  [+]   During transition '{}', receiving expected output symbol ('{}')".format(self.name, str(received_symbol)))

            # Set next state
            actor.visit_log.append("  [+]   Transition '{}' lead to state '{}'".format(self.name, str(self.endState)))

            for cbk in self.cbk_action:
                self._logger.debug("[actor='{}'] A callback function is defined at the end of transition '{}'".format(str(actor), self.name))
                cbk(received_symbol, received_message, received_structure, Operation.ABSTRACT, self.startState, actor.memory)

            return self.endState
        else:
            self.active = False
            self._logger.debug("[actor='{}'] Received symbol '{}' was unexpected.".format(str(actor), str(received_symbol)))

            # Handle case where received symbol is unknown
            if isinstance(received_symbol, UnknownSymbol):

                if actor.automata.cbk_read_unknown_symbol is not None:
                    nextState = actor.automata.cbk_read_unknown_symbol(self.startState,
                                                                       self,
                                                                       received_message)
                    actor.visit_log.append("  [+]   During transition '{}', receiving unknown symbol triggered a callback that lead to state '{}'".format(self.name, str(nextState)))
                    return nextState
                else:
                    actor.visit_log.append("  [+]   During transition '{}', receiving unknown symbol, so we stay at state '{}'".format(self.name, str(self.startState)))

                    # We leave the automaton
                    return None

            # Handle case where received symbol is known but unexpected
            else:

                if actor.automata.cbk_read_unexpected_symbol is not None:
                    nextState = actor.automata.cbk_read_unexpected_symbol(self,
                                                                          self,
                                                                          received_symbol,
                                                                          received_message,
                                                                          received_structure)
                    actor.visit_log.append("  [+]   During transition '{}', receiving unexpected symbol triggered a callback that lead to state '{}'".format(self.name, str(nextState)))
                    return nextState
                else:
                    actor.visit_log.append("  [+]   During transition '{}', receiving unexpected symbol '{}', so we stay at state '{}'".format(self.name, received_symbol, str(self.startState)))

                    # We leave the automaton
                    return None

    def executeAsNotInitiator(self, actor):
        """Execute the current transition as a not initiator.

        :return: The end state of the transition if not exception is raised.
        :rtype: :class:`~netzob.Model.Grammar.States.AbstractState.AbstractState`

        Being not an initiator means the startState has already received the
        input symbol which made it choose this transition.
        We only have to pick an output symbol and emit it.

        """

        self.active = True

        # Pick the output symbol to emit
        (symbol_to_send, symbol_preset) = self.__pickOutputSymbol(actor)
        if symbol_to_send is None:
            self._logger.debug("[actor='{}'] No output symbol to send, we pick an EmptySymbol as output symbol".format(str(actor)))
            symbol_to_send = EmptySymbol()

        # Sleep before emiting the symbol (if equired)
        if symbol_to_send in list(self.outputSymbolsReactionTime.keys()):
            delay = self.outputSymbolsReactionTime[symbol_to_send]
            self._logger.debug("[actor='{}'] Time to wait before sending the output symbol: {}".format(str(actor), delay))
            time.sleep(delay)

        # Configure symbol preset
        tmp_preset = Preset(symbol_to_send)

        # Handle actor preset
        if actor is not None and actor.presets is not None:
            for tmp_actor_preset in actor.presets:
                if tmp_actor_preset.symbol == symbol_to_send:
                    tmp_preset.update(tmp_actor_preset)
                    break

        # Handle symbol preset specified at current transition
        if isinstance(symbol_preset, Preset):
            tmp_preset.update(symbol_preset)

        # Handle fuzzing preset specified at actor level
        if actor.fuzzing_presets is not None and (len(actor.fuzzing_states) == 0 or self.startState.name in actor.fuzzing_states):
            for tmp_fuzzing_preset in actor.fuzzing_presets:
                if tmp_fuzzing_preset.symbol == symbol_to_send:
                    self._logger.debug("[actor='{}'] Fuzzing activated at transition".format(str(actor)))
                    actor.visit_log.append("  [+]   During transition '{}', fuzzing activated".format(self.name))
                    tmp_preset.update(tmp_fuzzing_preset)
                    break

        # Emit the symbol
        try:
            (data, data_len, data_structure) = actor.abstractionLayer.writeSymbol(symbol_to_send, preset=tmp_preset, cbk_action=self.cbk_action)
        except socket.timeout:
            self._logger.debug("[actor='{}'] In transition '{}', timeout on abstractionLayer.writeSymbol()".format(str(actor), self.name))
            self.active = False
            raise
        except OSError as e:
            self._logger.debug("[actor='{}'] The underlying abstraction channel seems to be closed, so we stop the current actor".format(str(actor)))
            return
        except Exception as e:
            self._logger.debug("[actor='{}'] An exception occured when sending a symbol from the abstraction layer: '{}'".format(str(actor), e))
            self.active = False
            # self._logger.debug(traceback.format_exc())
            raise e

        # Return the endState
        self.active = False

        # Update visit log
        actor.visit_log.append("  [+]   Transition '{}' lead to state '{}'".format(self.name, str(self.endState)))

        return self.endState

    def __pickOutputSymbol(self, actor):
        """Picks the output symbol to emit following their probability.

        It computes the probability of symbols which don't explicitly have one
        by splitting the remaining available probability given by others.

        :return: the output symbol following their probability.
        :rtype: :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
        """

        # Randomly select an output symbol
        outputSymbolsWithProbability = dict()
        for outputSymbol in self.outputSymbols:
            if outputSymbol not in list(self.outputSymbolsProbabilities.keys()):
                probability = 10.0
            else:
                probability = self.outputSymbolsProbabilities[outputSymbol]
            outputSymbolsWithProbability[outputSymbol] = probability

        # pick the good output symbol following the probability
        distribution = [
            outputSymbol
            for inner in [[k] * int(v) for k, v in list(
                outputSymbolsWithProbability.items())]
            for outputSymbolsWithNoProbability in inner
        ]

        # Random selection of the symbol and its associated preset
        symbol_to_send = random.choice(distribution)

        if self.outputSymbolsPreset is not None and isinstance(self.outputSymbolsPreset, dict):
            if symbol_to_send in self.outputSymbolsPreset:
                symbol_preset = self.outputSymbolsPreset[symbol_to_send]
            else:
                symbol_preset = None

        if symbol_preset is not None:
            actor.visit_log.append("  [+]   During transition '{}', choosing an output symbol ('{}') with preset ('{}')".format(self.name, str(symbol_to_send), symbol_preset))
        else:
            actor.visit_log.append("  [+]   During transition '{}', choosing an output symbol ('{}')".format(self.name, str(symbol_to_send)))

        # Potentialy modify the selected symbol if a callback is defined
        self._logger.debug("[actor='{}'] Test if a callback function is defined at transition '{}'".format(str(actor), self.name))
        for cbk in self.cbk_modify_symbol:
            self._logger.debug("[actor='{}'] A callback function is executed at transition '{}'".format(str(actor), self.name))
            (symbol_to_send, symbol_preset) = cbk(self.outputSymbols,
                                                  symbol_to_send,
                                                  symbol_preset,
                                                  self.startState,
                                                  actor.abstractionLayer.last_sent_symbol,
                                                  actor.abstractionLayer.last_sent_message,
                                                  actor.abstractionLayer.last_sent_structure,
                                                  actor.abstractionLayer.last_received_symbol,
                                                  actor.abstractionLayer.last_received_message,
                                                  actor.abstractionLayer.last_received_structure,
                                                  actor.memory)
            actor.visit_log.append("  [+]   During transition '{}', modifying output symbol to '{}', through callback".format(self.name, str(symbol_to_send)))
        else:
            self._logger.debug("[actor='{}'] No callback function is defined at transition '{}'".format(str(actor), self.name))

        return (symbol_to_send, symbol_preset)

    @public_api
    def add_cbk_action(self, cbk_method):
        """Function called after sending or receiving a symbol in the
        transition. This function should be used to modify the memory context.

        :param cbk_method: the callback function
        :type cbk_method: :class:`Callable <collections.abc.Callable>`, required
        :raise: :class:`TypeError` if :attr:`cbk_method` is not a callable function

        The callback function that can be used in the
        :attr:`cbk_method` parameter has the following prototype:

        .. function:: cbk_method(symbol, data, data_structure, operation, current_state, memory)
           :noindex:

           :param symbol:
                  Corresponds to the last sent or received symbol.
           :param data:
                  Corresponds to the last sent or received data.
           :param data_structure:
                  Corresponds to the last sent or received data structure.
           :param operation:
                  Tells the way the symbol is manipulated: either
                  :attr:`Operation.ABSTRACT` for symbols that are abstracted or
                  :attr:`Operation.SPECIALIZE` for symbols that are specialized.
           :param current_state:
                  Current state in the automaton.
           :param memory:
                  Corresponds to the current memory context.

           :type symbol: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`
           :type data: :class:`bytes`
           :type data_structure: :class:`OrderedDict`
           :type operation: :class:`~netzob.Simulation.AbstractionLayer.Operation`
           :type current_state: :class:`~netzob.Model.Grammar.States.State.State`
           :type memory: :class:`Memory <netzob.Model.Vocabulary.Domain.Variables.Memory.Memory>`

        The callback method is not expected to return something.

        """
        if not callable(cbk_method):
            raise TypeError("'cbk_method' should be a callable function")
        self.cbk_action.append(cbk_method)

    # Properties

    @public_api
    @property
    def inputSymbol(self):
        """The input symbol is the symbol which triggers the execution
        of the transition.

        :type: :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
        """
        return self.__inputSymbol

    @inputSymbol.setter  # type: ignore
    @typeCheck(Symbol)
    def inputSymbol(self, inputSymbol):
        if inputSymbol is None:
            inputSymbol = EmptySymbol()

        self.__inputSymbol = inputSymbol

    @public_api
    @property
    def inputSymbolPreset(self):
        return self.__inputSymbolPreset

    @inputSymbolPreset.setter  # type: ignore
    def inputSymbolPreset(self, inputSymbolPreset):
        self.__inputSymbolPreset = None
        if inputSymbolPreset is not None:
            if not isinstance(self.inputSymbol, EmptySymbol):
                self.__inputSymbolPreset = inputSymbolPreset

    @public_api
    @property
    def outputSymbols(self):
        """Output symbols that can be generated when
        the current transition is executed.

        >>> from netzob.all import *
        >>> transition = Transition(State(), State())
        >>> transition.outputSymbols = None
        >>> len(transition.outputSymbols)
        1
        >>> transition.outputSymbols.append(Symbol())
        >>> transition.outputSymbols.extend([Symbol(), Symbol()])
        >>> len(transition.outputSymbols)
        4
        >>> transition.outputSymbols = []
        >>> len(transition.outputSymbols)
        1

        :type: list of :class:`Symbol <netzob.Model.Vocabulary.Symbol.Symbol>`
        :raise: TypeError if not valid.
        """
        return self.__outputSymbols

    @outputSymbols.setter  # type: ignore
    def outputSymbols(self, outputSymbols):
        if outputSymbols is None:
            self.__outputSymbols = [EmptySymbol()]
        elif outputSymbols == []:
            self.__outputSymbols = [EmptySymbol()]
        else:
            for symbol in outputSymbols:
                if not isinstance(symbol, Symbol):
                    raise TypeError("One of the output symbol is not a Symbol")
            self.__outputSymbols = []
            for symbol in outputSymbols:
                if symbol is not None:
                    self.__outputSymbols.append(symbol)

    @public_api
    @property
    def outputSymbolsPreset(self):
        return self.__outputSymbolsPreset

    @outputSymbolsPreset.setter  # type: ignore
    def outputSymbolsPreset(self, outputSymbolsPreset):
        self.__outputSymbolsPreset = {}
        if outputSymbolsPreset is not None:
            for outputSymbol, outputSymbolPreset in outputSymbolsPreset.items():
                if not isinstance(outputSymbol, EmptySymbol):
                    self.__outputSymbolsPreset[outputSymbol] = outputSymbolPreset

    @public_api
    @property
    def inputSymbolReactionTime(self):
        return self.__inputSymbolReactionTime

    @inputSymbolReactionTime.setter  # type: ignore
    def inputSymbolReactionTime(self, inputSymbolReactionTime):
        self.__inputSymbolReactionTime = inputSymbolReactionTime

    @public_api
    @property
    def outputSymbolsReactionTime(self):
        return self.__outputSymbolsReactionTime

    @outputSymbolsReactionTime.setter  # type: ignore
    def outputSymbolsReactionTime(self, outputSymbolsReactionTime):
        if outputSymbolsReactionTime is None:
            outputSymbolsReactionTime = {}
        elif not isinstance(outputSymbolsReactionTime, dict):
            raise TypeError("outputSymbolsReactionTime should be a dict of "
                            "Symbol and float, not {}"
                            .format(type(outputSymbolsReactionTime).__name__))
        self.__outputSymbolsReactionTime = outputSymbolsReactionTime

    @public_api
    @property
    def outputSymbolsProbabilities(self):
        return self.__outputSymbolsProbabilities

    @outputSymbolsProbabilities.setter  # type: ignore
    def outputSymbolsProbabilities(self, outputSymbolsProbabilities):
        if outputSymbolsProbabilities is None:
            outputSymbolsProbabilities = {}
        elif not isinstance(outputSymbolsProbabilities, dict):
            raise TypeError("outputSymbolsProbabilities should be a dict of "
                            "Symbol and float, not {}"
                            .format(type(outputSymbolsProbabilities).__name__))
        self.__outputSymbolsProbabilities = outputSymbolsProbabilities

    @public_api
    @property
    def description(self):
        return self.__description

    @description.setter  # type: ignore
    def description(self, description):
        if description is not None:
            self.__description = description
        else:
            desc = []
            for outputSymbol in self.outputSymbols:
                desc.append(str(outputSymbol.name))
            if self.inputSymbol is not None:
                inputSymbolName = self.inputSymbol.name
            else:
                inputSymbolName = "None"
            self.__description = "{} ({};{}{}{})".format(self.name, inputSymbolName, "{", ",".join(desc), "}")

    @public_api
    @property
    def inverseInitiator(self):
        return self.__inverseInitiator

    @inverseInitiator.setter  # type: ignore
    def inverseInitiator(self, inverseInitiator):
        self.__inverseInitiator = inverseInitiator


def _test():
    r"""

    # Test copy()

    >>> from netzob.all import *
    >>> s0 = State()
    >>> s1 = State()
    >>> t = Transition(s0, s1, name="transition")
    >>> t.copy()
    transition

    """
