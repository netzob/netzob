# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# |             ANSSI,   https://www.ssi.gouv.fr                              |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# |       - Rémy Delion <remy.delion (a) amossys.fr>                          |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
from enum import Enum

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.Mutator import Mutator
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Grammar.Automata import Automata
from netzob.Model.Grammar.States.State import State  # noqa: F401


class AutomataMutatorStrategy(Enum):
    """The :class:`AutomataMutator` strategy enumeration."""
    __repr__ = Enum.__str__
    RANDOM = 1
    """Randomly insert and remove transitions between states of the original automaton."""
    TOTAL = 2
    """At each state of the automaton, it is possible to reach any states, including the starting state."""
    CHAINED = 3
    """Build a chained automaton (or a chaplet), where each state has only one possible transition towards another different state of the protocol, and where all the states of the protocol are covered."""


class AutomataMutator(Mutator):
    """The AutomataMutator is used to mutate an existing state machine.

    """

    def __init__(self,
                 automata,  # type: Automata
                 **kwargs):
        super().__init__(**kwargs)

        # Sanity checks
        if not isinstance(automata, Automata):
            raise TypeError("Mutator automata should be of type Automata. Received object: '{}'"
                            .format(automata))

        # Handle parameters
        self._automata = automata

    def mutate(self,
               strategy=AutomataMutatorStrategy.RANDOM,  # type: AutomataMutatorStrategy
               startingState=None,                       # type: State
               endingState=None                          # type: State
               ) -> Automata:
        """This is the mutation method of the automaton. This method returns
        a new automaton that may be used for fuzzing purpose.

        The mutate method expects some parameters:

        :param strategy: The strategy used to build the new automaton.
                         Default strategy is :attr:`AutomataMutatorStrategy.RANDOM`.
        :param startingState: The state in the automaton from which to
                              start the fuzzing of message formats
                              (i.e. symbols). By default, no
                              startingState is defined.
        :param endingState: The state in the automaton from which to
                            end the fuzzing of message formats
                            (i.e. symbols). By default, no
                            endingState is defined.
        :type strategy: :class:`AutomataMutatorStrategy`, optional
        :type startingState: :class:`State <netzob.Model.Grammar.States.State>`, optional
        :type endingState: :class:`State <netzob.Model.Grammar.States.State>`, optional
        :return: The mutated automata.
        :rtype: :class:`Automata <netzob.Model.Grammar.Automata>`


        **Basic example of automata fuzzing**

        Mutators may be used in order to create fuzzed/mutated automaton.

        The following code shows the creation of the new automaton with
        random transitions between the existing states:

        >>> from netzob.all import *
        >>> s0 = State()
        >>> symbol = Symbol([Field(String('abcd'))])
        >>> automata = Automata(s0, vocabulary=[symbol])
        >>> mutator = AutomataMutator(automata, seed=42)
        >>> mutatedAutomata = mutator.mutate(strategy=AutomataMutatorStrategy.RANDOM)  # doctest: +SKIP


        **Combining message formats and automata fuzzing**

        By combining message formats and automata fuzzing, it is possible
        to fuzz specific message formats at specific states in the
        automaton.

        The following code shows the creation of the new automaton with
        random transitions between the existing states, and with a
        precision concerning the states between which fuzzing of message
        formats will be performed:

        >>> # Symbol definition
        >>> f1 = Field(String())
        >>> f2 = Field(Integer())
        >>> symbol = Symbol(fields=[f1, f2])
        >>>
        >>> # Automaton definition
        >>> s1 = State()
        >>> s2 = State()
        >>> automata = Automata(s1, vocabulary=[symbol])
        >>>
        >>> # Creation of a mutated automaton
        >>> mutator = AutomataMutator(automata, seed=42)
        >>> mutatedAutomata = mutator.mutate(strategy=AutomataMutatorStrategy.RANDOM, startingState=s1, endingState=s2)  # doctest: +SKIP
        >>> assert isinstance(mutatedAutomata, Automata)  # doctest: +SKIP
        >>>
        >>> # Creation of an automaton visitor/actor and a channel on which to emit the fuzzed symbol
        >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887, timeout=1.)
        >>> abstractionLayer = AbstractionLayer(channel, [symbol])
        >>> visitor = Actor(automata=mutatedAutomata, initiator=True, abstractionLayer=abstractionLayer)  # doctest: +SKIP
        >>>
        >>> # We start the visitor, thus the fuzzing of message formats will be applied when specific states are reached
        >>> visitor.start()  # doctest: +SKIP

        """
        raise NotImplementedError

    def generate(self):
        raise NotImplementedError
