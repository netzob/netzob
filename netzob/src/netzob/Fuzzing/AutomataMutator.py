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
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
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

    >>> from netzob.all import *
    >>> mutator = StateMachineMutator()
    >>> mutator.seed = 10
    >>> # getProcolAutomata() mechanism is specific to the test case
    >>> # -> it has to be implemented for each protocol to test.
    >>> automata = getProtocolAutomata("TCP")
    >>> mutator.inputAutomata = automata
    >>> mutatedAutomata = mutator.mutate()
    """

    def __init__(self):
        self._inputAutomata = None

    @property
    def inputAutomata(self):
        """The automata to mutate

        :type: :class:`netzob.Model.Grammar.Automata`
        """
        return self._inputAutomata

    @inputAutomata.setter
    @typeCheck(Automata)
    def inputAutomata(self, automata):
        self._inputAutomata = automata

    def mutate(self):
        """This is the mutation method of the automata.

        :return: a mutated Automata object
        :rtype: :class:`netzob.Model.Grammar.Automata`
        """
        # TODO : implement the Automata random generator
        return super().mutate()
