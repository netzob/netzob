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
    :param int priority: the priority of the transition.
    :param str description: The description of the transition.
    :type startState: :class:`~netzob.Model.Grammar.States.AbstractState.AbstractState`
    :type endState: :class:`~netzob.Model.Grammar.States.AbstractState.AbstractState`

    """

    def __init__(self,
                 _type,
                 startState,
                 endState,
                 name=None,
                 priority=10,
                 description=None):
        self._startState = None
        self._endState = None

        self.type = _type
        self.startState = startState
        self.endState = endState
        self.name = name
        self.priority = priority
        self.__description = description
        self.active = False
        self.cbk_modify_symbol = []
        self.cbk_action = []

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
    def priority(self):
        """The priority of the transition. The lower its its
        the highest priority it gets.
        For instance, an open and close channel transition are both declared
        with a priority of 0 whereas per default a transition has a priority
        of 10.

        >>> from netzob.all import *
        >>> s0 = State(name="Start")
        >>> s1 = State(name="End")
        >>> openTransition = OpenChannelTransition(s0, s1)
        >>> openTransition.priority
        0
        >>> transition = Transition(s1, s1)
        >>> transition.priority=1
        >>> transition.priority
        1
        >>> transition.priority = 50
        >>> transition.priority
        50

        :type: :class:`int`
        """
        return self.__priority

    @priority.setter  # type: ignore
    @typeCheck(int)
    def priority(self, priority):
        if priority is None:
            raise TypeError("Priority cannot be None")
        if priority < 0 or priority > 100:
            raise TypeError(
                "The priority must respect range : 0<=priority<100")

        self.__priority = priority

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
    def add_cbk_modify_symbol(self, cbk_method):
        """Function called during transition execution, to help
        choose/modify the output symbol to send (in a server
        context) or the input symbol to send (in a client context).

        :param cbk_method: the callback function
        :type cbk_method: ~typing.Callable, required
        :raise: :class:`TypeError` if :attr:`cbk_method` is not a callable function

        :attr:`cbk_method` should have the following prototype:

        .. function:: cbk_method(available_symbols, current_symbol, current_state,\
                                 last_sent_symbol, last_sent_message, last_sent_structure,\
                                 last_received_symbol, last_received_message, last_received_structure)
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
                  Last sent symbol on the abstraction layer, and thus making it
                  possible to create relationships with the previously sent symbol.
           :param last_sent_message:
                  Last sent message on the abstraction layer, and thus making
                  it possible to create relationships with the previously sent
                  message.
           :param last_sent_structure:
                  Last sent message structure on the abstraction layer,
                  and thus making it possible to create relationships with
                  the previously sent message structure.
           :param last_received_symbol:
                  Last received symbol on the abstraction layer, and thus
                  making it possible to create relationships with the
                  previously received symbol.
           :param last_received_message:
                  Last received message (:class:`bitarray`) on the abstraction layer,
                  and this makes it possible to create relationships with
                  received message.
           :param last_received_structure:
                  Last received message structure on the abstraction
                  layer, and thus making it possible to create relationships
                  with the previously received message structure.

           :type available_symbols: ~typing.List[~netzob.Model.Vocabulary.Symbol.Symbol], required
           :type current_symbol: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`, required
           :type current_symbol_preset: :class:`~netzob.Model.Vocabulary.Preset.Preset`, required
           :type current_state: :class:`~netzob.Model.Grammar.States.State.State`, required
           :type last_sent_symbol: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`, required
           :type last_sent_message: :class:`~bitarray.bitarray`, required
           :type last_sent_structure: :class:`OrderedDict` where keys are :class:`~netzob.Model.Vocabulary.Field.Field` and values are :class:`bytes`, required
           :type last_received_symbol: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`, required
           :type last_received_message: :class:`~bitarray.bitarray`, required
           :type last_received_structure: :class:`OrderedDict` where keys are :class:`~netzob.Model.Vocabulary.Field.Field` and values are :class:`bytes`, required

           :return:
             * The symbol that will be sent. This could be the same as the
               :attr:`current_symbol` or another one,
             * A preset configuration used to parameterize fields
               during symbol specialization. This configuration will
               override any field definition, constraints or relationship
               dependencies (see :meth:`~netzob.Model.Vocabulary.Symbol.Symbol.specialize`,
               for more information).
           :rtype: ~typing.Tuple[~netzob.Model.Vocabulary.Symbol.Symbol,~typing.Dict]

        """
        if not callable(cbk_method):
            raise TypeError("'cbk_method' should be a callable function")
        self.cbk_modify_symbol.append(cbk_method)

    def add_cbk_action(self, cbk_method):
        """Function called after sending or receiving a symbol in the
        transition. This function could be used to change memory or actor behavior.

        :param cbk_method: the callback function
        :type cbk_method: ~typing.Callable, required
        :raise: :class:`TypeError` if :attr:`cbk_method` is not a callable function

        :attr:`cbk_method` should have the following prototype:

        .. function:: cbk_method(symbol, data, data_structure, operation, actor)
           :noindex:

           :param symbol:
                  Corresponds to the last sent or received symbol.
           :param data:
                  Corresponds to the last sent or received data.
           :param data_structure:
                  Corresponds to the last sent or received data structure.
           :param operation:
                  Tells the direction of the symbol: either
                  :attr:`Operation.READ` for received symbols or
                  :attr:`Operation.WRITE` for send symbols.
           :param actor:
                  The actor that is sending or receiving the symbol.

           :type symbol_to_send: :class:`~netzob.Model.Vocabulary.Symbol.Symbol`, required
           :type data: :class:`str`, required
           :type data_structure: :class:`dict`, required
           :type operation: :class:`~netzob.Simulation.AbstractionLayer.Operation`, required
           :type actor: :class:`~netzob.Simulation.Actor.Actor`, required

        The callback method is not expected to return something.

        """
        if not callable(cbk_method):
            raise TypeError("'cbk_method' should be a callable function")
        self.cbk_action.append(cbk_method)
