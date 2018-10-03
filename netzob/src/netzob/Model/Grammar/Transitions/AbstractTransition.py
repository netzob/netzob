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
import abc

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api


class AbstractTransition(object, metaclass=abc.ABCMeta):
    """Constructor of a Transition.

    The AbstractTransition constructor expects some parameters:

    :param str _type: the type of the transition.
    :param startState: The initial state of the transition.
    :param endState: The end state of the transition.
    :param str name: The name of the transition.
    :param float inputSymbolProbability: This value holds the probability of the current transition of being chosen when processing the state where it is attached. The value between ``0.0`` and ``100.0`` corresponds to the weight of the transition in terms of selection probability. The default value is set to 10.0.
    :param str description: The description of the transition.
    :type startState: :class:`~netzob.Model.Grammar.States.AbstractState.AbstractState`
    :type endState: :class:`~netzob.Model.Grammar.States.AbstractState.AbstractState`

    """

    def __init__(self,
                 _type,
                 startState,
                 endState,
                 name=None,
                 description=None):
        self._startState = None
        self._endState = None

        self.type = _type
        self.startState = startState
        self.endState = endState
        self.name = name
        self.inputSymbolProbability = 10.0
        self.__description = description

        self.active = False
        self.cbk_modify_symbol = []
        self.inverseInitiator = False

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self.name)

    # Execution abstract methods

    @abc.abstractmethod
    def executeAsInitiator(self, actor):
        pass

    @abc.abstractmethod
    def executeAsNotInitiator(self, actor):
        pass

    # Other methods

    @abc.abstractmethod
    def copy(self):
        pass

    # Priorities

    @property
    def type(self):
        """The type of the transition

        :type: :class:`str`
        """
        return self.__type

    @type.setter  # type: ignore
    @typeCheck(str)
    def type(self, _type):
        if _type is None:
            raise TypeError("Type cannot be None")
        if len(_type) == 0:
            raise ValueError("Type cannot be an empty string")
        self.__type = _type

    @public_api
    @property
    def startState(self):
        """
        The start state of the transition.

        When modifying the startState, it removes itself from previous start
        state.

        >>> from netzob.all import *
        >>> s0 = State(name="S0")
        >>> s1 = State(name="S1")
        >>> s2 = State(name="S2")
        >>> t = Transition(s0, s1, name="T0")
        >>> print(t.startState.name)
        S0
        >>> len(s0.transitions)
        1
        >>> t.startState = s2
        >>> len(s0.transitions)
        0

        :type: :class:`~netzob.Model.Grammar.State.AbstractState.AbstractState`
        :raise: TypeError if type of param is not valid
        """
        return self._startState

    @startState.setter  # type: ignore
    def startState(self, startState):
        if self._startState is not None:
            self._startState.removeTransition(self)
        if startState is not None:
            startState.transitions.append(self)

        self._startState = startState

    @public_api
    @property
    def endState(self):
        """
        The end state of the transition.

        >>> from netzob.all import *
        >>> s0 = State(name="S0")
        >>> s1 = State(name="S1")
        >>> t = Transition(s0, s1, name="T0")
        >>> print(t.endState.name)
        S1

        :type: :class:`~netzob.Model.Grammar.State.AbstractState.AbstractState`
        :raise: TypeError if type of param is not valid
        """
        return self._endState

    @endState.setter  # type: ignore
    def endState(self, endState):
        self._endState = endState

    @property
    def inputSymbolProbability(self):
        """This value holds the probability of the current transition of being
        chosen when processing the state where it is attached. The
        value between ``0.0`` and ``100.0`` corresponds to the weight
        of the transition in terms of selection probability. The
        default value is set to 10.0.

        For instance, an open and close channel transition are both declared
        with a weight of 100.0, whereas per default a transition has a weight
        of 10.0.

        >>> from netzob.all import *
        >>> s0 = State(name="Start")
        >>> s1 = State(name="End")
        >>> openTransition = OpenChannelTransition(s0, s1)
        >>> openTransition.inputSymbolProbability
        100.0
        >>> transition = Transition(s1, s1)
        >>> transition.inputSymbolProbability = 20.0
        >>> transition.inputSymbolProbability
        20.0
        >>> transition.inputSymbolProbability = 40.0
        >>> transition.inputSymbolProbability
        40.0

        :type: :class:`int`

        """
        return self.__inputSymbolProbability

    @inputSymbolProbability.setter  # type: ignore
    @typeCheck(float)
    def inputSymbolProbability(self, inputSymbolProbability):
        if inputSymbolProbability is None:
            raise TypeError("inputSymbolProbability cannot be None")
        if inputSymbolProbability < 0.0 or inputSymbolProbability > 100.0:
            raise TypeError(
                "The inputSymbolProbability value must respect range : 0.0 <= value <= 100.0")

        self.__inputSymbolProbability = inputSymbolProbability

    @public_api
    @property
    def active(self):
        """Represents the current execution status of the transition.
        If a transition is active, it means it did not yet finish to execute it

        :type: :class:`bool`
        """
        return self.__active

    @active.setter  # type: ignore
    @typeCheck(bool)
    def active(self, active):
        if active is None:
            raise TypeError("The active info cannot be None")
        self.__active = active

    @property
    def description(self):
        return self.__description

    @description.setter  # type: ignore
    @typeCheck(str)
    def description(self, description):
        self.__description = description

    @public_api
    @property
    def inverseInitiator(self):
        """
        :type: :class:`bool`
        """
        return self.__inverseInitiator

    @inverseInitiator.setter  # type: ignore
    @typeCheck(bool)
    def inverseInitiator(self, inverseInitiator):
        self.__inverseInitiator = inverseInitiator

    @public_api
    def add_cbk_modify_symbol(self, cbk_method):
        """Function called during transition execution, to help
        choose/modify the output symbol to send (in a non initiator
        context) or the input symbol to send (in an initiator context).

        :param cbk_method: the callback function
        :type cbk_method: ~typing.Callable, required
        :raise: :class:`TypeError` if :attr:`cbk_method` is not a callable function

        The callback function that can be used in the
        :attr:`cbk_method` parameter has the following prototype:

        .. function:: cbk_method(available_symbols, current_symbol, current_symbol_preset, current_state,\
                                 last_sent_symbol, last_sent_message, last_sent_structure,\
                                 last_received_symbol, last_received_message,\
                                 last_received_structure, memory)
           :noindex:

           :param available_symbols:
                  Corresponds to the list of possible symbols to send.
           :param current_symbol:
                  Currently selected symbol that will be sent, either the initial
                  symbol or the symbol returned by the previous callback.
           :param current_symbol_preset:
                  Preset configuration associated to selected symbol.
           :param current_state:
                  Current state in the automaton.
           :param last_sent_symbol:
                  This parameter is the last sent symbol by the actor on the communication channel, and thus making it
                  possible to create relationships with the previously sent symbol.
           :param last_sent_message:
                  This parameter is the last sent message by the actor on the communication channel, and thus making
                  it possible to create relationships with the previously sent
                  message.
           :param last_sent_structure:
                  This parameter is the last sent message structure by the actor on the communication channel,
                  and thus making it possible to create relationships with
                  the previously sent message structure.
           :param last_received_symbol:
                  This parameter is the last received symbol by the actor on the communication channel, and thus
                  making it possible to create relationships with the
                  previously received symbol.
           :param last_received_message:
                  This parameter is the last received message (:class:`bitarray`) by the actor on the communication channel,
                  and this makes it possible to create relationships with
                  received message.
           :param last_received_structure:
                  This parameter is the last received message structure by the actor on the communication channel, and thus making it possible to create relationships
                  with the previously received message structure.
           :param memory:
                  This parameter corresponds to the current memory context.

           :type available_symbols: ~typing.List[~netzob.Model.Vocabulary.Symbol.Symbol]
           :type current_symbol: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`
           :type current_symbol_preset: :class:`~netzob.Model.Vocabulary.Preset.Preset`
           :type current_state: :class:`~netzob.Model.Grammar.States.State.State`
           :type last_sent_symbol: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`
           :type last_sent_message: :class:`~bitarray.bitarray`
           :type last_sent_structure: :class:`OrderedDict` where keys are :class:`~netzob.Model.Vocabulary.Field.Field` and values are :class:`bytes`
           :type last_received_symbol: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`
           :type last_received_message: :class:`~bitarray.bitarray`
           :type last_received_structure: :class:`OrderedDict` where keys are :class:`~netzob.Model.Vocabulary.Field.Field` and values are :class:`bytes`
           :type memory: :class:`Memory <netzob.Model.Vocabulary.Domain.Variables.Memory.Memory>`

           :return: The callback function should return a tuple. The
                    first tuple element is the symbol (:class:`Symbol
                    <netzob.Model.Vocabulary.Symbol.Symbol>`) that
                    will be sent. This could be the same as the
                    :attr:`current_symbol` or another one. The second
                    tuple element is a preset (:class:`Preset
                    <netzob.Model.Vocabulary.Preset.Preset>`)
                    configuration used to parameterize fields during
                    symbol specialization. This configuration will
                    override any field definition, constraints or
                    relationship dependencies (see
                    :meth:`~netzob.Model.Vocabulary.Symbol.Symbol.specialize`,
                    for more information).
           :rtype: ~typing.Tuple[~netzob.Model.Vocabulary.Symbol.Symbol,~netzob.Model.Vocabulary.Preset.Preset]

        """
        if not callable(cbk_method):
            raise TypeError("'cbk_method' should be a callable function")
        self.cbk_modify_symbol.append(cbk_method)
