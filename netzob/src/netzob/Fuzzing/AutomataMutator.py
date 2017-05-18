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

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.Mutator import Mutator
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Grammar.Automata import Automata


class AutomataMutator(Mutator):
    """The mutator of a protocol state machine. This mutator is a particular case :
    it does not use Mutator.field and the return value of mutate() has not the
    same type as the other mutators : it returns here an Automata object.


    **Mutators for automata fuzzing**

    Mutators may be used in order to create fuzzed/mutated automaton.

    The following code shows the creation of the new automaton with
    random transitions between the existing states:

    >>> from netzob.all import *
    >>> automata = Automata()
    >>> mutator = AutomataMutator(strategy='random')
    >>> mutator.seed = 10
    >>> mutator.automata = automata
    >>> mutatedAutomata = mutator.mutate()


    **Combining message formats and automata fuzzing**

    By combining message formats and automata fuzzing, it is possible
    to fuzz specific message formats at specific states in the
    automaton.

    The following code shows the creation of the new automaton with
    random transitions between the existing states, and with a
    precision concerning the states between which fuzzing of message
    formats will be done:

    >>> # Symbol definition
    >>> f1 = Field(String())
    >>> f2 = Field(Integer())
    >>> symbol = Symbol(fields=[f1, f2])

    >>> # Specification of fuzzed fields
    >>> mutators = {f1: StringMutator,
    ...             f2: (PseudoRandomIntegerMutator, minValue=12, maxValue=20)}

    >>> # Automaton definition
    >>> s1 = State()
    >>> s2 = State()
    >>> automata = Automata()

    >>> # Creation of a mutated automaton
    >>> mutator = AutomataMutator(strategy='random', startingState=s1, endingState=s2)
    >>> mutator.seed = 10
    >>> mutator.automata = automata
    >>> mutatedAutomata = mutator.mutate()

    >>> # Creation of an automaton visitor/actor and a channel on which to emit the fuzzed symbol
    >>> channel = UDPClient(remoteIP="127.0.0.1", remotePort=8887)
    >>> abstractionLayer = AbstractionLayer(channel, [symbol])
    >>> visitor = Actor(automata = mutatedAutomata, initiator = True, abstractionLayer=abstractionLayer)

    >>> # We start the visitor, thus the fuzzing of message formats will be applied when specific states are reached
    >>> visitor.start()

    """

    def __init__(self):
        pass

    def mutate(self, strategy='random', startingState=None, endingState=None):
        """This is the mutation method of the automaton. This methods returns
        a new automaton that may be used for fuzzing purpose.

        The mutate method expects some parameters:

        :param strategy: The strategy used to build the new
                         automaton. Default strategy is 'random'.
        :param startingState: The state in the automaton from which to
                              start the fuzzing of message formats
                              (i.e. symbols). By default, no
                              startingState is defined.
        :param endingState: The state in the automaton from which to
                            end the fuzzing of message formats
                            (i.e. symbols). By default, no
                            endingState is defined.
        :type strategy: a :class:`str`, optional
        :type startingState: :class:`State <netzob.Model.Grammar.State.State>`, optional
        :type endingState: :class:`State <netzob.Model.Grammar.State.State>`, optional
        :return: The mutated automata.
        :rtype: :class:`Automata <netzob.Model.Grammar.Automata>`

        Available automata fuzzing strategies are the following:

        * ``'random'``: randomly insert and remove transitions between
          states of the original automaton;
        * ``'total'``: at each state of the automaton, it is possible to
          reach any states, including the starting state;
        * ``'chained'``: build a chained automaton (or a chaplet),
          where each state has only one possible transition towards
          another different state of the protocol, and where all the
          states of the protocol are covered.

        """
        # TODO : implement the Automata random generator
        return super().mutate()
